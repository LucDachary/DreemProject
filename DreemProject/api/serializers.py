"""
Serializers for Dreem project's models.
"""
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import Device, Record

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Dreem user model serializer."""
	# DEV
    # records = serializers.PrimaryKeyRelatedField(many=True, queryset=Record.objects.all())

    class Meta:
        """User model serializer meta class."""
        model = User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """Dreem group model serializer."""
    class Meta:
        """Group model serializer meta class."""
        model = Group
        fields = ('url', 'name')

class DeviceSerializer(serializers.ModelSerializer):
    """Dreem device model serializer."""
    class Meta:
        """Device model serializer meta class."""
        model = Device
        fields = ('id', 'name', 'dreempy_version', 'date_registered')

class RecordSerializer(serializers.ModelSerializer):
    """Dreem record model serializer."""
    class Meta:
        """Record model serializer meta class."""
        model = Record
        fields = ('id', 'start_time', 'stop_time', 'sleep_start_time',
                  'sleep_stop_time', 'sleep_score', 'number_of_stimulations',
                  'number_of_wake', 'hypnogram', 'user', 'device')

class SignalSerializer(serializers.ModelSerializer):
    """Dreem record's signal serializer."""
    class Meta:
        """Record'signal model serializer meta class."""
        model = Record
        fields = ('id', 'start_time', 'stop_time', 'hypnogram')

    # DEV: JSONParser().parse(stream)
