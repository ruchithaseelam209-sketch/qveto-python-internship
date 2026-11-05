# Smart HR System - API Documentation

## Base URL

http://127.0.0.1:8000/

## API Endpoints

All employee-related endpoints are registered under `/api/`.

| Module | Endpoint |
|---|---|
| Authentication | /api/auth/ |
| Departments | /api/departments/ |
| Employees | /api/employees/ |
| Attendance | /api/attendance/ |
| Leave Types | /api/leave-types/ |
| Leave Requests | /api/leave-requests/ |
| Admin Panel | /admin/ |

## Employee API

Endpoint: `/api/employees/`

Used for employee profile management.

## Department API

Endpoint: `/api/departments/`

Used for department management.

## Attendance API

Endpoint: `/api/attendance/`

Used for attendance management.

## Leave Type API

Endpoint: `/api/leave-types/`

Used for managing leave categories.

## Leave Request API

Endpoint: `/api/leave-requests/`

Used for managing employee leave requests.

## Authentication

Authentication routes are included through the accounts application under:

`/api/auth/`

Refer to the accounts URL configuration for individual authentication endpoints.

## Admin Panel

URL: `/admin/`

Used for Django administration.

## Server

Start the development server:

```bash
python backend/manage.py runserver
