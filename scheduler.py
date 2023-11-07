import schedule
import threading
import time


class botScheduler:
    def __init__(self):
        self.schedule = schedule

    def add_job(self, interval_number, time_unit, job):
        if time_unit == "S":
            self.schedule.every(interval_number).seconds.do(job)
        elif time_unit == "M":
            self.schedule.every(interval_number).minutes.do(job)
        elif time_unit == "H":
            self.schedule.every(interval_number).hours.do(job)

    def stop_job(self):
        self.schedule.clear()

    def __run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def run(self):
        t = threading.Thread(target=self.__run_scheduler)
        t.start()
        return t
