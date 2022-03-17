import unittest
import logging
import sys
from time import sleep
from datetime import datetime, timedelta

from ant_net_monitor import create_app
from ant_net_monitor.extensions import db
from ant_net_monitor.status.cpu_status import CPUStatus, save_cpu_status
from ant_net_monitor.status.ram_status import RAMStatus, save_ram_status
from ant_net_monitor.status.basic_status import BasicStatus, save_basic_status

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestClientMethods(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app.config["FINISH_TESTING"] = False
        with self.app_context:
            db.create_all()

    def tearDown(self):
        with self.app_context:
            db.session.remove()
            db.drop_all()
        self.app.config["FINISH_TESTING"] = True
        logging.info("Finish testing.")

    def date_range(self, start, end, delta):
        current = start.replace(second=0, microsecond=0)
        while current < end.replace(second=0, microsecond=0):
            yield current
            current += delta

    # def test_hello(self):
    #    logging.info(self.app.config["APPLICATION_ENV"])
    #    ret = self.app.test_client().get("/hello")
    #    self.assertEqual(b"Hello, World!", ret.data)

    def test_get_status(self):
        with self.app_context:
            save_basic_status(BasicStatus())
        ret = self.app.test_client().get("/status/basic_status")
        logging.info(ret.data)

    def test_get_last_cpu_status(self):
        with self.app_context:
            save_cpu_status(CPUStatus())
        ret = self.app.test_client().get("/status/cpu_status?type=update")
        logging.info(ret.data)

    def test_get_batch_cpu_status(self):
        with self.app_context:
            for i in range(10):
                save_cpu_status(CPUStatus())
        ret = self.app.test_client().get("/status/cpu_status?type=init")
        logging.info(ret.data)

    def test_get_last_ram_status(self):
        with self.app_context:
            save_ram_status(RAMStatus())
        ret = self.app.test_client().get("/status/ram_status?type=update")
        logging.info(ret.data)

    def test_get_batch_ram_status(self):
        with self.app_context:
            for i in range(10):
                save_ram_status(RAMStatus())
                sleep(1)
        ret = self.app.test_client().get("/status/ram_status?type=init")
        logging.info(ret.get_json())

    def test_get_ram_status_in_one_day(self):
        with self.app_context:
            start = datetime.utcnow() - timedelta(minutes=30)
            end = datetime.utcnow()
            delta = timedelta(minutes=1)
            for time_stamp in self.date_range(start, end, delta):
                save_ram_status(RAMStatus(is_random=True, time_stamp=time_stamp))
        ret = self.app.test_client().get("/status/ram_status?type=day")
        logging.info(ret.get_json())
