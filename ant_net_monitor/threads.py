import threading
from time import sleep
import random

from ant_net_monitor.status.network_status import NetworkStatus

from .extensions import db
from .status.basic_status import BasicStatus
from .status.cpu_status import CPUStatus
from .status.ram_status import RAMStatus
from .status.disk_status import DiskStatus

from .alarm.alarm import Alarm

# TODO 整个函数变量进去，进一步封装


def set_basic_status_thread(app):
    """Register basic status thread."""

    def save_status_loop(app):
        with app.app_context():
            DiskStatus.init_counter()
            NetworkStatus.init_counter()
            while True:
                try:
                    new_basic_status = BasicStatus()
                    new_cpu_status = CPUStatus()
                    new_ram_status = RAMStatus()
                    new_disk_status = DiskStatus()
                    new_network_status = NetworkStatus()
                    
                    BasicStatus.save(new_basic_status)
                    CPUStatus.save(new_cpu_status)
                    RAMStatus.save(new_ram_status)
                    DiskStatus.save(new_disk_status)
                    NetworkStatus.save(new_network_status)

                    alarm_value = (
                        new_basic_status.cpu_percent,
                        new_cpu_status.iowait_percent,
                        new_cpu_status.steal_percent,
                    )
                    Alarm.check_cpu_alarm(*alarm_value)

                    sleep(1)
                except Exception as e:
                    db.session.rollback()
                    sleep(random.random())
                    app.logger.error(e)
                
                try:
                    if app.config["FINISH_TESTING"]:
                        break
                except KeyError:
                    pass

    save_status_thread = threading.Thread(target=save_status_loop, args=(app,))
    save_status_thread.start()


def set_all_threads(app):
    set_basic_status_thread(app)
