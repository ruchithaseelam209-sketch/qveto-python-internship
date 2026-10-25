
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Department, EmployeeProfile


User = get_user_model()


class DepartmentModelTests(TestCase):
    def test_department_creation(self):
        department = Department.objects.create(
            name="Engineering",
            description="Software development team",
        )

        self.assertEqual(department.name, "Engineering")
        self.assertTrue(department.is_active)
        self.assertEqual(str(department), "Engineering")

    def test_department_name_must_be_unique(self):
        Department.objects.create(name="Engineering")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Department.objects.create(name="Engineering")


class EmployeeProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testemployee",
            email="employee@example.com",
            password="TestPassword123!",
        )
        self.department = Department.objects.create(
            name="Engineering",
        )

    def test_employee_profile_creation(self):
        profile = EmployeeProfile.objects.create(
            user=self.user,
            department=self.department,
            job_title="Software Developer",
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.department, self.department)
        self.assertEqual(profile.status, EmployeeProfile.Status.ACTIVE)
        self.assertEqual(self.user.employee_profile, profile)

    def test_user_can_have_only_one_employee_profile(self):
        EmployeeProfile.objects.create(
            user=self.user,
            department=self.department,
            job_title="Software Developer",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                EmployeeProfile.objects.create(
                    user=self.user,
                    department=self.department,
                    job_title="Developer",
                )

    def test_department_cannot_be_deleted_while_in_use(self):
        EmployeeProfile.objects.create(
            user=self.user,
            department=self.department,
            job_title="Software Developer",
        )

        with self.assertRaises(ProtectedError):
            self.department.delete()


class EmployeeAPIPermissionTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
        )

        self.admin = self.create_user("admin", "ADMIN")
        self.hr = self.create_user("hr", "HR")
        self.employee1 = self.create_user("employee1", "EMPLOYEE")
        self.employee2 = self.create_user("employee2", "EMPLOYEE")

        self.profile1 = EmployeeProfile.objects.create(
            user=self.employee1,
            department=self.department,
            job_title="Developer",
        )
        self.profile2 = EmployeeProfile.objects.create(
            user=self.employee2,
            department=self.department,
            job_title="Tester",
        )

        self.department_url = reverse("department-list")
        self.profile_list_url = reverse("employee-list")
        self.profile1_url = reverse(
            "employee-detail",
            args=[self.profile1.pk],
        )
        self.profile2_url = reverse(
            "employee-detail",
            args=[self.profile2.pk],
        )

    def create_user(self, username, role):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="TestPassword123!",
            role=role,
        )

    def test_unauthenticated_users_cannot_access_departments(self):
        response = self.client.get(self.department_url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_unauthenticated_users_cannot_access_profiles(self):
        response = self.client.get(self.profile_list_url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_admin_can_list_all_employee_profiles(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.profile_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_hr_can_list_all_employee_profiles(self):
        self.client.force_authenticate(user=self.hr)

        response = self.client.get(self.profile_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_employee_can_only_list_own_profile(self):
        self.client.force_authenticate(user=self.employee1)

        response = self.client.get(self.profile_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.profile1.pk)

    def test_employee_cannot_access_another_employees_profile(self):
        self.client.force_authenticate(user=self.employee1)

        response = self.client.get(self.profile2_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_employee_cannot_create_profile(self):
        self.client.force_authenticate(user=self.employee1)

        response = self.client.post(
            self.profile_list_url,
            {
                "user_id": self.employee2.pk,
                "department_id": self.department.pk,
                "job_title": "Intern",
                "status": "ACTIVE",
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_employee_cannot_delete_own_profile(self):
        self.client.force_authenticate(user=self.employee1)

        response = self.client.delete(self.profile1_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            EmployeeProfile.objects.filter(pk=self.profile1.pk).exists()
        )

    def test_employee_can_update_own_profile(self):
        self.client.force_authenticate(user=self.employee1)

        response = self.client.patch(
            self.profile1_url,
            {"job_title": "Senior Developer"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile1.refresh_from_db()
        self.assertEqual(
            self.profile1.job_title,
            "Senior Developer",
        )

    def test_admin_can_update_employee_profile(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.profile1_url,
            {"job_title": "Senior Developer"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile1.refresh_from_db()
        self.assertEqual(
            self.profile1.job_title,
            "Senior Developer",
        )

    def test_employee_cannot_change_profile_owner(self):
        self.client.force_authenticate(user=self.employee1)

        response = self.client.patch(
            self.profile1_url,
            {"user_id": self.employee2.pk},
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN,
            ],
        )

        self.profile1.refresh_from_db()
        self.assertEqual(
            self.profile1.user_id,
            self.employee1.pk,
        )

    def test_employee_cannot_modify_departments(self):
        self.client.force_authenticate(user=self.employee1)

        response = self.client.post(
            self.department_url,
            {"name": "Finance"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
