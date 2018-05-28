"""
API views.
"""
from datetime import datetime, timezone, timedelta
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from api.models import Record, Device
from api.serializers import UserSerializer, GroupSerializer, RecordSerializer, DeviceSerializer, \
    SignalSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class RecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Record API views.
    """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Device API views.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = (permissions.IsAuthenticated,)

class HypnogramView(APIView):
    """
    Hypnogram API views.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, username, ts_from, ts_to):
        """
        Provide the hypnogram of a record made between two arbitrary timestamps, for a given user.
        """
        records = Record.objects.filter(user_id=username)
        records = records.filter(start_time__gte=
                                 datetime.fromtimestamp(int(ts_from), timezone(timedelta(hours=1))))
        records = records.filter(stop_time__lte=
                                 datetime.fromtimestamp(int(ts_to), timezone(timedelta(hours=1))))

        serializer = SignalSerializer(records, many=True)
        return JsonResponse(serializer.data, safe=False)
