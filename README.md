# Smart HR & Employee Management System

### Qveto Technologies – Python Development Internship

## 1. Project Overview

The Smart HR & Employee Management System is a web-based application developed using Python and Django. It is designed to simplify employee management and HR operations through a centralized platform.

The application provides user authentication, employee management and role-based access control. It supports three main user roles: Admin, HR and Employee.

## 2. Project Objectives

* Develop a centralized employee management system.
* Provide secure user registration and login.
* Implement role-based access control.
* Manage employee-related information.
* Store application data using PostgreSQL.
* Develop REST APIs using Django REST Framework.
* Maintain code using Git and GitHub.

## 3. Technologies Used

| Technology            | Purpose                        |
| --------------------- | ------------------------------ |
| Python                | Programming language           |
| Django                | Backend web framework          |
| Django REST Framework | API development                |
| PostgreSQL            | Database management            |
| Psycopg               | PostgreSQL database connection |
| Git                   | Version control                |
| GitHub                | Code hosting and collaboration |
| Visual Studio Code    | Development environment        |

## 4. Project Structure

```text
qveto-python-internship/
│
├── backend/
│   ├── accounts/
│   │   ├── migrations/
│   │   ├── auth_urls.py
│   │   ├── views.py
│   │   └── models.py
│   │
│   ├── employees/
│   │
│   ├── config/
│   │
│   └── manage.py
│
├── venv/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 5. Main Modules

### 5.1 Accounts Module

The Accounts module manages user authentication and account-related operations.

Features:

* User registration.
* User login.
* User logout.
* Password authentication.
* User account management.

### 5.2 Employee Module

The Employee module handles employee-related backend functionality.

Features:

* Employee information management.
* Employee data handling.
* Employee-related operations.

### 5.3 Role-Based Access Control

The system supports different roles with appropriate permissions.

**Admin**

* Administrative access.
* User and system management.

**HR**

* HR-related operations.
* Employee management access.

**Employee**

* Access to permitted employee functionality.
* Restricted access to administrative operations.

## 6. Database Configuration

PostgreSQL is used as the primary database.

Database details:

* Database Name: `smart_hr_db`
* Database User: `postgres`
* Host: `localhost`
* Port: `5432`

Sensitive credentials are configured through environment variables and should not be uploaded to GitHub.

## 7. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/ruchithaseelam209-sketch/qveto-python-internship.git
```

### Step 2: Navigate to the Project Folder

```bash
cd qveto-python-internship
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 5: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 6: Configure Environment Variables

Configure the following database environment variables:

```text
DB_NAME=smart_hr_db
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
DB_HOST=localhost
DB_PORT=5432
```

Set the Django secret key using a secure environment variable.

Refer to `.env.example` for the configuration template.

### Step 7: Apply Database Migrations

```bash
python backend/manage.py migrate
```

### Step 8: Run the Development Server

```bash
python backend/manage.py runserver
```

The application development server runs at:

```text
http://127.0.0.1:8000/
```

## 8. Testing

The backend application can be tested using Django's testing framework.

Run the following command:

```bash
python backend/manage.py test accounts employees
```

Latest recorded test result:

* Total test cases: 38
* Passed: 38
* Failed: 0

## 9. Version Control and Collaboration

Git and GitHub are used for source code management and team collaboration.

Repository:

https://github.com/ruchithaseelam209-sketch/qveto-python-internship

Current development branch:

`ruchithaseelam209-sketch`

Team members work using separate branches to support organized development and integration.

## 10. Security Practices

* Passwords are handled through Django authentication.
* Database credentials should not be committed to GitHub.
* `.gitignore` is configured to exclude sensitive environment files.
* Role-based permissions restrict access to protected operations.
* Environment-specific configuration should be used for deployment.

## 11. Future Enhancements

* Attendance management.
* Leave management.
* Payroll management.
* Employee performance tracking.
* HR notifications and reporting.
* Frontend integration.

These features can be added as the project development progresses.

## 12. Internship Information

**Organization:** Qveto Technologies

**Program:** Python Development Internship

**Project:** Smart HR & Employee Management System

**Programming Language:** Python

**Backend Framework:** Django

**Database:** PostgreSQL

**Development Approach:** Team-Based Project Development

---

*Developed as part of the Qveto Technologies Python Development Internship.*
