from modules import transfers
from modules import timestamp
from modules.logs import Log

from threading import Thread
import time
import os


class Cleaner:
    def __init__(self) -> None:
        checker = Thread(target=self.checker, daemon=True)
        checker.start()
        Log.info("Intialized data cleaner.")

    def analyze_data(self) -> None:
        """ Check all shared files and remove expired. """
        models = transfers.transfers_db.get_all_models()
        for model in models:
            if model.date_expire < timestamp.generate_timestamp():
                model.remove()

    def checker(self) -> None:
        while True:
            self.analyze_data()
            time.sleep(3600)
                    
