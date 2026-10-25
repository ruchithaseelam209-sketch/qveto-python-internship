
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Department, EmployeeProfile
from .serializers import DepartmentSerializer, EmployeeProfileSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.select_related(
        "user", "department"
    ).all()
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated]


# Create your views here.
