
from django.contrib.auth import get_user_model
from django.test import TestCase

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

        with self.assertRaises(Exception):
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

        with self.assertRaises(Exception):
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

        with self.assertRaises(Exception):
            self.department.delete()
