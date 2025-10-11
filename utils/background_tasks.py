from threading import Thread
import time
from typing import Callable
import schedule

class BackgroundTasks:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self, check_alerts_func: Callable):
        if self.running:
            return

        def run_scheduler():
            schedule.every(30).seconds.do(check_alerts_func)
            self.running = True
            while self.running:
                schedule.run_pending()
                time.sleep(1)

        self.thread = Thread(target=run_scheduler, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
