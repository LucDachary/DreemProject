"""
Runs the Dreem records collector.
"""
from time import sleep
from collector import Collector

if __name__ == 'django.core.management.commands.shell':
    C = Collector()
    while True:
        print("Collector: polling…")
        PROCESSED_RECORDS = C.run()
        # TODO: solve pylint using-constant-test warning on PROCESSED_RECORDS.
        if PROCESSED_RECORDS:
            print("The following record(s) has/have been processed: {}."
                  .format(", ".join(PROCESSED_RECORDS)))
        sleep(5)
