from datetime import datetime
import psutil
from ..extensions import db
from dataclasses import dataclass


@dataclass
class BasicStatus(db.Model):
    id: int
    cpu_percent: float
    ram_percent: float  # The percent of memory used to the system.
    swap_percent: float
    disk: int
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cpu_percent = db.Column(db.Float)
    ram_percent = db.Column(db.Float)
    swap_percent = db.Column(db.Float)
    disk = db.Column(db.Float)

    def __init__(self):
        self.cpu_percent = psutil.cpu_percent(interval=1)
        self.ram_percent = psutil.virtual_memory().percent
        self.swap_percent = psutil.swap_memory().percent

        # self.disk = psutil.disk_usage("/").used
        # self.network = psutil.net_io_counters().bytes_recv
        # self.time = psutil.cpu_times_percent(interval=1)

    def __str__(self):
        return f"cpu:{self.cpu_percent}%, memory:{round(self.ram_percent/(1024**3),2)}G, disk:{round(self.disk/(1024**3),2)}G"


def save_basic_status(status):
    db.session.add(status)
    db.session.commit()


def get_last_basic_status():
    return BasicStatus.query.order_by(BasicStatus.time_stamp.desc()).first()
