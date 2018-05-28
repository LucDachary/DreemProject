"""API module tests."""
import base64
import json
from time import time
from datetime import datetime, timezone, timedelta
from random import randint, random
from dateutil.parser import parse
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from api.models import Device, Record

class APITests(TestCase):
    """API tests."""
    __client = None
    __user = None
    __basic_digest = None
    __device = None

    def setUp(self):
        """Prepare the dummy user account."""
        username = "dummy"
        password = "secretpwd"
        self.__client = APIClient()
        self.__user = User.objects.create_user(username, 'dummy@test.com', password)
        self.__basic_digest = "Basic " + base64.b64encode(
            "{}:{}".format(username, password).encode('ascii')).decode('ascii')
        self.__device = Device(name="dummydevice", dreempy_version="1.2.3")
        self.__device.save()

    def test_anonymous_get_users(self):
        """Try to fetch users while being anonymous."""
        response = self.__client.get("/users/")
        self.assertEqual(response.status_code, 403, "Permissions looks wrong.")

    def test_anonymous_get_devices(self):
        """Try to fetch devices while being anonymous."""
        response = self.__client.get("/records/")
        self.assertEqual(response.status_code, 403, "Permissions looks wrong.")

    def test_anonymous_get_records(self):
        """Try to fetch records while being anonymous."""
        response = self.__client.get("/records/")
        self.assertEqual(response.status_code, 403, "Permissions looks wrong.")

    def test_anonymous_get_signal(self):
        """Try to fetch record signals while being anonymous."""
        response = self.__client.get("/signal/{}/{}/{}/".format("whoever", 0, 0))
        self.assertEqual(response.status_code, 403, "Permissions looks wrong.")

    def test_get_records(self):
        """Send a GET request on the /records/ resource."""
        response = self.__client.get("/records/", HTTP_AUTHORIZATION=self.__basic_digest)
        self.assertEqual(response.status_code, 200, "Can not GET /records/.")

    def test_get_devices(self):
        """Send a GET request on the /devices/ resource."""
        response = self.__client.get("/devices/", HTTP_AUTHORIZATION=self.__basic_digest)
        self.assertEqual(response.status_code, 200, "Can not GET /devices/.")

    def test_get_users(self):
        """Send a GET request on the /users/ resource. Only admins are authorised."""
        username = "admini"
        password = "maxipwd"
        User.objects.create_superuser(username, 'admini@strateur.com', password)
        basic_digest = "Basic " + base64.b64encode(
            "{}:{}".format(username, password).encode('ascii')).decode('ascii')

        response = self.__client.get("/users/", HTTP_AUTHORIZATION=basic_digest)
        self.assertEqual(response.status_code, 200, "Can not GET /users/.")

    def test_get_signal(self):
        """Send a GET on the /signal/ resource and ensure the proper record is provided."""
        # The record will start yesterday at this exact same hour.
        ts_start = int(time()) - 60*60*24
        # It will last from 6 to 10 hours.
        ts_stop = ts_start + 60*60*randint(6, 10)

        record = Record(
            start_time=datetime.fromtimestamp(ts_start, timezone(timedelta(hours=1))),
            stop_time=datetime.fromtimestamp(ts_stop, timezone(timedelta(hours=1))),
            sleep_start_time=datetime.fromtimestamp(ts_start + 60*60,
                                                    timezone(timedelta(hours=1))),
            sleep_stop_time=datetime.fromtimestamp(ts_stop - 60*60, timezone(timedelta(hours=1))),
            sleep_score=random(),
            number_of_stimulations=randint(0, 2000),
            number_of_wake=randint(0, 50),
            hypnogram="[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,2,3,3,3]",
            user=self.__user,
            device=self.__device
        )
        record.save()

        response = self.__client.get("/signal/{}/{}/{}/".format(
            self.__user.username,
            ts_start,
            ts_stop
        ), HTTP_AUTHORIZATION=self.__basic_digest)

        records = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200, "Can not retrieve my signal.")
        self.assertEqual(len(records), 1, "I should have add a single record.")
        self.assertGreaterEqual(
            parse(records[0]["start_time"]),
            datetime.fromtimestamp(ts_start, timezone(timedelta(hours=1))),
            "The start_time is wrong."
        )
        self.assertGreaterEqual(
            datetime.fromtimestamp(ts_stop, timezone(timedelta(hours=1))),
            parse(records[0]["stop_time"]),
            "The stop_time is wrong."
        )
