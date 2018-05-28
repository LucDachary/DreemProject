"""
The Dreem records collector.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.renderers import JSONRenderer
import h5py
from api.models import Record, Device

class Collector():
    """
    Collect, read, extract and store Dreem records data.
    """
    __RECORDS_DIR = "/var/records"
    __records_path = None

    def __init__(self):
        """Initialize the Collector."""
        # TODO: ensure the directory exists. Ensure it's writable.
        self.__records_path = Path(self.__RECORDS_DIR)

        # TODO: start with oldest records first.

    @classmethod
    def __remove_record(cls, path):
        """Delete the record from records directory."""
        print("Removing record {}.".format(path))
        path.unlink()

    @classmethod
    def __process_record(cls, path):
        """Read, extract and store a single Dreem records data."""
        try:
            record = h5py.File(path, 'r')
        except OSError:
            # The file is still copying. It will be considered again on next poll.
            return

        # These two attributes are stored as ASCII strings.
        username = str(record.attrs["user"], "utf-8")
        devicename = str(record.attrs["device"], "utf-8")

        # Retrieving the user
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            print("Unknown user, skipping the record…")
            path.unlink()
            return

        # Retrieving the device
        try:
            device = Device.objects.get(name=devicename)
        except Device.DoesNotExist:
            # Temporary: we create the device
            print("Unknown device, inserting…")
            device = Device(name=devicename, dreempy_version=record.attrs["dreempy_version"])
            device.save()

        record = Record(
            start_time=datetime.fromtimestamp(int(record.attrs["start_time"]),
                                              timezone(timedelta(hours=1))),
            stop_time=datetime.fromtimestamp(int(record.attrs["stop_time"]),
                                             timezone(timedelta(hours=1))),
            sleep_start_time=datetime.fromtimestamp(int(record.attrs["sleep_start_time"]),
                                                    timezone(timedelta(hours=1))),
            sleep_stop_time=datetime.fromtimestamp(int(record.attrs["sleep_stop_time"]),
                                                   timezone(timedelta(hours=1))),

            sleep_score=record.attrs["sleep_score"],
            number_of_stimulations=int(record.attrs["number_of_stimulations"]),
            number_of_wake=int(record.attrs["number_of_wake"]),
            hypnogram=JSONRenderer().render(record["reporting"]["dreemnogram"][()]),
            user=user,
            device=device
        )
        record.save()
        path.unlink()

    def get_pending_records(self):
        """List and return the records to be processed."""
        return self.__records_path.glob("*.h5")

    def run(self):
        """
        Collect, read, extract and store all the records available.

        Return the processed records paths as a list of strings.
        """
        paths = self.get_pending_records()
        names = []
        for path in paths:
            self.__process_record(path)
            names.append(path.name)
        return names
