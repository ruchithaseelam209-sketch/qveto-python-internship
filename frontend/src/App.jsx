import { useState, useEffect } from "react";
import "./App.css";

const API = "/api";

function getCookie(name) {
  const cookies = document.cookie.split(";");

  for (const cookie of cookies) {
    const [key, ...value] = cookie.trim().split("=");

    if (key === name) {
      return decodeURIComponent(value.join("="));
    }
  }

  return null;
}

async function getCsrfToken() {
  const response = await fetch(`${API}/auth/csrf/`, {
    credentials: "same-origin",
  });

  if (!response.ok) {
    throw new Error("Unable to obtain CSRF token.");
  }

  const token = getCookie("csrftoken");

  if (!token) {
    throw new Error("CSRF token not received.");
  }

  return token;
}

async function apiRequest(endpoint, options = {}) {
  const method = (options.method || "GET").toUpperCase();

  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
  };

  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    headers["X-CSRFToken"] = await getCsrfToken();
  }

  if (options.body) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API}${endpoint}`, {
    ...options,
    method,
    headers,
    credentials: "same-origin",
  });

  if (response.status === 204) {
    return null;
  }

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      typeof result === "object"
        ? Object.entries(result)
            .map(([key, value]) =>
              `${key}: ${Array.isArray(value) ? value.join(", ") : value}`
            )
            .join("\n")
        : "Request failed.";

    throw new Error(message || `HTTP ${response.status}`);
  }

  return result;
}

const emptyEmployee = {
  username: "",
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  phone_number: "",
  employee_id: "",
  department_id: "",
  job_title: "",
  status: "ACTIVE",
  date_of_joining: "",
};

function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("Dashboard");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const [data, setData] = useState([]);
  const [departments, setDepartments] = useState([]);

  const [search, setSearch] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [employeeForm, setEmployeeForm] = useState(emptyEmployee);

  const menu = [
    "Dashboard",
    "Employees",
    "Departments",
    "Attendance",
    "Leave Requests",
  ];

  const endpoints = {
    Employees: "/employees/",
    Departments: "/departments/",
    Attendance: "/attendance/",
    "Leave Requests": "/leave-requests/",
  };

  const isHR =
    user?.is_superuser ||
    user?.role === "ADMIN" ||
    user?.role === "HR";

  // LOGIN
  async function login(e) {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const result = await apiRequest("/auth/login/", {
        method: "POST",
        body: JSON.stringify({
          username: username.trim(),
          password,
        }),
      });

      if (!result.user) {
        throw new Error("User information missing.");
      }

      setUser(result.user);
      setPassword("");
      setPage("Dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // LOGOUT
  async function logout() {
    setLoading(true);

    try {
      await apiRequest("/auth/logout/", {
        method: "POST",
      });
    } catch (err) {
      console.error(err);
    } finally {
      setUser(null);
      setData([]);
      setError("");
      setSuccess("");
      setUsername("");
      setPassword("");
      setPage("Dashboard");
      setLoading(false);
    }
  }

  // LOAD MODULE DATA
  async function loadData(section) {
    setPage(section);
    setError("");
    setSuccess("");
    setData([]);
    setSearch("");
    setDepartmentFilter("");
    setStatusFilter("");

    const endpoint = endpoints[section];

    if (!endpoint) return;

    setLoading(true);

    try {
      const result = await apiRequest(endpoint);

      const records = Array.isArray(result)
        ? result
        : result.results || [];

      setData(records);

      if (section === "Employees") {
        const departmentResult = await apiRequest("/departments/");

        setDepartments(
          Array.isArray(departmentResult)
            ? departmentResult
            : departmentResult.results || []
        );
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // EMPLOYEE FORM
  function openAddEmployee() {
    setEditingEmployee(null);
    setEmployeeForm(emptyEmployee);
    setError("");
    setSuccess("");
    setShowForm(true);
  }

  function openEditEmployee(employee) {
    setEditingEmployee(employee);

    setEmployeeForm({
      department_id: employee.department_id || "",
      job_title: employee.job_title || "",
      status: employee.status || "ACTIVE",
      date_of_joining: employee.date_of_joining || "",
    });

    setError("");
    setSuccess("");
    setShowForm(true);
  }

  function handleFormChange(e) {
    const { name, value } = e.target;

    setEmployeeForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  // SAVE EMPLOYEE
  async function saveEmployee(e) {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      if (editingEmployee) {
        const payload = {
          department_id: Number(employeeForm.department_id),
          job_title: employeeForm.job_title,
          status: employeeForm.status,
          date_of_joining: employeeForm.date_of_joining || null,
        };

        await apiRequest(
          `/employees/${editingEmployee.id}/`,
          {
            method: "PATCH",
            body: JSON.stringify(payload),
          }
        );

        setSuccess("Employee updated successfully.");
      } else {
        const payload = {
          ...employeeForm,
          department_id: Number(employeeForm.department_id),
          date_of_joining: employeeForm.date_of_joining || null,
        };

        await apiRequest("/employees/", {
          method: "POST",
          body: JSON.stringify(payload),
        });

        setSuccess("Employee created successfully.");
      }

      setShowForm(false);
      setEditingEmployee(null);
      setEmployeeForm(emptyEmployee);

      await refreshEmployees();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // REFRESH EMPLOYEES
  async function refreshEmployees() {
    try {
      const result = await apiRequest("/employees/");

      setData(
        Array.isArray(result)
          ? result
          : result.results || []
      );
    } catch (err) {
      setError(err.message);
    }
  }

  // DELETE EMPLOYEE PROFILE
  async function deleteEmployee(employee) {
    const confirmed = window.confirm(
      `Delete the employee profile for ${employee.username}?`
    );

    if (!confirmed) return;

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await apiRequest(`/employees/${employee.id}/`, {
        method: "DELETE",
      });

      setSuccess("Employee profile deleted successfully.");
      await refreshEmployees();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // EMPLOYEE SEARCH AND FILTER
  const filteredEmployees = data.filter((employee) => {
    const searchText = search.toLowerCase();

    const matchesSearch = [
      employee.username,
      employee.first_name,
      employee.last_name,
      employee.email,
      employee.employee_id,
      employee.job_title,
    ]
      .filter(Boolean)
      .some((value) =>
        String(value).toLowerCase().includes(searchText)
      );

    const matchesDepartment =
      !departmentFilter ||
      String(employee.department_id) === departmentFilter;

    const matchesStatus =
      !statusFilter || employee.status === statusFilter;

    return (
      matchesSearch &&
      matchesDepartment &&
      matchesStatus
    );
  });

  function closeForm() {
    setShowForm(false);
    setEditingEmployee(null);
    setEmployeeForm(emptyEmployee);
  }

  const inputStyle = {
    width: "100%",
    padding: "11px",
    border: "1px solid #dce5f1",
    borderRadius: "7px",
    marginTop: "6px",
    boxSizing: "border-box",
    fontSize: "14px",
  };

  const labelStyle = {
    display: "block",
    marginBottom: "15px",
    color: "#344968",
    fontSize: "13px",
    fontWeight: "600",
  };

  const primaryButton = {
    background: "#2459a6",
    color: "white",
    border: "none",
    borderRadius: "7px",
    padding: "10px 17px",
    cursor: "pointer",
  };

  const secondaryButton = {
    background: "#f3f7fd",
    color: "#2459a6",
    border: "1px solid #dce5f1",
    borderRadius: "7px",
    padding: "9px 14px",
    cursor: "pointer",
  };

  // LOGIN PAGE
  if (!user) {
    return (
      <div className="login-screen">
        <form className="login-card" onSubmit={login}>
          <div className="brand-icon">HR</div>

          <h1>Smart HR</h1>
          <p>Employee Management System</p>

          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter username"
            required
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
            required
          />

          {error && <div className="error">{error}</div>}

          <button className="primary-btn" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>

          <small>Authorized users only</small>
        </form>
      </div>
    );
  }

  // MAIN APPLICATION
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">HR</span>
          <span>Smart HR</span>
        </div>

        <p className="menu-label">MAIN MENU</p>

        {menu.map((item, index) => (
          <button
            key={item}
            className={`nav-item ${
              page === item ? "active" : ""
            }`}
            onClick={() => {
              if (item === "Dashboard") {
                setPage("Dashboard");
                setData([]);
                setError("");
                setSuccess("");
              } else {
                loadData(item);
              }
            }}
          >
            <span>{["▦", "♙", "▤", "◷", "▧"][index]}</span>
            {item}
          </button>
        ))}

        <button
          className="logout-btn"
          onClick={logout}
          disabled={loading}
        >
          ↪ Sign Out
        </button>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h2>{page}</h2>
            <p>Smart HR Management System</p>
          </div>

          <div className="profile">
            <div className="avatar">
              {user.username?.charAt(0).toUpperCase()}
            </div>

            <div>
              <strong>{user.username}</strong>
              <small>{user.role || "USER"}</small>
            </div>
          </div>
        </header>

        {error && <div className="error">{error}</div>}

        {success && (
          <div
            style={{
              background: "#e9f8ef",
              color: "#21834a",
              padding: "12px",
              borderRadius: "7px",
              marginBottom: "15px",
            }}
          >
            {success}
          </div>
        )}

        {/* DASHBOARD */}
        {page === "Dashboard" ? (
          <>
            <section className="welcome">
              <div>
                <h1>Welcome, {user.username}!</h1>
                <p>Manage your workforce from one place.</p>
              </div>

              <span className="welcome-icon">✦</span>
            </section>

            <h3 className="section-title">
              Management Modules
            </h3>

            <section className="dashboard-grid">
              {menu.slice(1).map((item, index) => (
                <button
                  className="module-card"
                  key={item}
                  onClick={() => loadData(item)}
                >
                  <span className="module-icon">
                    {["♙", "▤", "◷", "▧"][index]}
                  </span>

                  <h3>{item}</h3>

                  <p>
                    View and manage {item.toLowerCase()}
                  </p>

                  <span className="card-arrow">
                    Explore →
                  </span>
                </button>
              ))}
            </section>
          </>
        ) : (
          <section className="content-card">
            <div className="content-heading">
              <h3>{page} Records</h3>

              <button
                className="refresh-btn"
                onClick={() => loadData(page)}
                disabled={loading}
              >
                ↻ Refresh
              </button>
            </div>

            {/* EMPLOYEE MANAGEMENT */}
            {page === "Employees" && (
              <>
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "12px",
                    marginBottom: "20px",
                  }}
                >
                  {isHR && (
                    <button
                      style={primaryButton}
                      onClick={openAddEmployee}
                    >
                      + Add Employee
                    </button>
                  )}

                  <input
                    style={{
                      ...inputStyle,
                      width: "230px",
                      marginTop: 0,
                    }}
                    placeholder="Search employees..."
                    value={search}
                    onChange={(e) =>
                      setSearch(e.target.value)
                    }
                  />

                  <select
                    style={{
                      ...inputStyle,
                      width: "180px",
                      marginTop: 0,
                    }}
                    value={departmentFilter}
                    onChange={(e) =>
                      setDepartmentFilter(e.target.value)
                    }
                  >
                    <option value="">All Departments</option>

                    {departments.map((department) => (
                      <option
                        key={department.id}
                        value={department.id}
                      >
                        {department.name}
                      </option>
                    ))}
                  </select>

                  <select
                    style={{
                      ...inputStyle,
                      width: "150px",
                      marginTop: 0,
                    }}
                    value={statusFilter}
                    onChange={(e) =>
                      setStatusFilter(e.target.value)
                    }
                  >
                    <option value="">All Statuses</option>
                    <option value="ACTIVE">Active</option>
                    <option value="INACTIVE">Inactive</option>
                  </select>
                </div>

                {loading ? (
                  <p>Loading employees...</p>
                ) : filteredEmployees.length === 0 ? (
                  <p className="empty">
                    No employees found.
                  </p>
                ) : (
                  <div className="table-wrapper">
                    <table>
                      <thead>
                        <tr>
                          <th>Employee ID</th>
                          <th>Name</th>
                          <th>Email</th>
                          <th>Department</th>
                          <th>Job Title</th>
                          <th>Joining Date</th>
                          <th>Status</th>
                          {isHR && <th>Actions</th>}
                        </tr>
                      </thead>

                      <tbody>
                        {filteredEmployees.map((employee) => (
                          <tr key={employee.id}>
                            <td>
                              {employee.employee_id || "-"}
                            </td>

                            <td>
                              {[
                                employee.first_name,
                                employee.last_name,
                              ]
                                .filter(Boolean)
                                .join(" ") ||
                                employee.username ||
                                "-"}
                            </td>

                            <td>{employee.email || "-"}</td>

                            <td>
                              {employee.department_name || "-"}
                            </td>

                            <td>{employee.job_title || "-"}</td>

                            <td>
                              {employee.date_of_joining || "-"}
                            </td>

                            <td>
                              <span
                                style={{
                                  color:
                                    employee.status === "ACTIVE"
                                      ? "#21834a"
                                      : "#c03939",
                                  fontWeight: "600",
                                }}
                              >
                                {employee.status}
                              </span>
                            </td>

                            {isHR && (
                              <td>
                                <div
                                  style={{
                                    display: "flex",
                                    gap: "7px",
                                  }}
                                >
                                  <button
                                    style={secondaryButton}
                                    onClick={() =>
                                      openEditEmployee(employee)
                                    }
                                  >
                                    Edit
                                  </button>

                                  <button
                                    style={{
                                      ...secondaryButton,
                                      color: "#c03939",
                                    }}
                                    onClick={() =>
                                      deleteEmployee(employee)
                                    }
                                  >
                                    Delete
                                  </button>
                                </div>
                              </td>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}

            {/* OTHER MODULES */}
            {page !== "Employees" && (
              loading ? (
                <p>Loading records...</p>
              ) : data.length === 0 ? (
                <p className="empty">No records found.</p>
              ) : (
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(data[0]).map((key) => (
                          <th key={key}>
                            {key.replaceAll("_", " ")}
                          </th>
                        ))}
                      </tr>
                    </thead>

                    <tbody>
                      {data.map((row, index) => (
                        <tr key={row.id || index}>
                          {Object.values(row).map((value, i) => (
                            <td key={i}>
                              {typeof value === "object" &&
                              value !== null
                                ? JSON.stringify(value)
                                : String(value ?? "-")}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            )}
          </section>
        )}
      </main>

      {/* ADD / EDIT EMPLOYEE MODAL */}
      {showForm && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "#14233c99",
            display: "grid",
            placeItems: "center",
            padding: "20px",
            zIndex: 1000,
            overflowY: "auto",
          }}
        >
          <form
            onSubmit={saveEmployee}
            style={{
              background: "white",
              borderRadius: "14px",
              padding: "28px",
              width: "100%",
              maxWidth: "650px",
              maxHeight: "90vh",
              overflowY: "auto",
              boxSizing: "border-box",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "22px",
              }}
            >
              <h2 style={{ color: "#1c3153", margin: 0 }}>
                {editingEmployee
                  ? "Edit Employee"
                  : "Add New Employee"}
              </h2>

              <button
                type="button"
                onClick={closeForm}
                style={{
                  border: 0,
                  background: "transparent",
                  fontSize: "24px",
                  cursor: "pointer",
                }}
              >
                ×
              </button>
            </div>

            {!editingEmployee && (
              <>
                <h4>Account Information</h4>

                <label style={labelStyle}>
                  Username
                  <input
                    style={inputStyle}
                    name="username"
                    value={employeeForm.username}
                    onChange={handleFormChange}
                    required
                  />
                </label>

                <label style={labelStyle}>
                  Email
                  <input
                    style={inputStyle}
                    type="email"
                    name="email"
                    value={employeeForm.email}
                    onChange={handleFormChange}
                    required
                  />
                </label>

                <label style={labelStyle}>
                  Password
                  <input
                    style={inputStyle}
                    type="password"
                    name="password"
                    value={employeeForm.password}
                    onChange={handleFormChange}
                    minLength={8}
                    required
                  />
                </label>

                <label style={labelStyle}>
                  First Name
                  <input
                    style={inputStyle}
                    name="first_name"
                    value={employeeForm.first_name}
                    onChange={handleFormChange}
                  />
                </label>

                <label style={labelStyle}>
                  Last Name
                  <input
                    style={inputStyle}
                    name="last_name"
                    value={employeeForm.last_name}
                    onChange={handleFormChange}
                  />
                </label>

                <label style={labelStyle}>
                  Phone Number
                  <input
                    style={inputStyle}
                    name="phone_number"
                    value={employeeForm.phone_number}
                    onChange={handleFormChange}
                  />
                </label>

                <label style={labelStyle}>
                  Employee ID
                  <input
                    style={inputStyle}
                    name="employee_id"
                    value={employeeForm.employee_id}
                    onChange={handleFormChange}
                    required
                  />
                </label>
              </>
            )}

            <h4>Employment Information</h4>

            <label style={labelStyle}>
              Department

              <select
                style={inputStyle}
                name="department_id"
                value={employeeForm.department_id}
                onChange={handleFormChange}
                required
              >
                <option value="">Select Department</option>

                {departments
                  .filter((department) => department.is_active)
                  .map((department) => (
                    <option
                      key={department.id}
                      value={department.id}
                    >
                      {department.name}
                    </option>
                  ))}
              </select>
            </label>

            <label style={labelStyle}>
              Job Title

              <input
                style={inputStyle}
                name="job_title"
                value={employeeForm.job_title}
                onChange={handleFormChange}
                required
              />
            </label>

            <label style={labelStyle}>
              Date of Joining

              <input
                style={inputStyle}
                type="date"
                name="date_of_joining"
                value={employeeForm.date_of_joining || ""}
                onChange={handleFormChange}
              />
            </label>

            <label style={labelStyle}>
              Status

              <select
                style={inputStyle}
                name="status"
                value={employeeForm.status}
                onChange={handleFormChange}
              >
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
              </select>
            </label>

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                gap: "10px",
                marginTop: "25px",
              }}
            >
              <button
                type="button"
                style={secondaryButton}
                onClick={closeForm}
              >
                Cancel
              </button>

              <button
                type="submit"
                style={primaryButton}
                disabled={loading}
              >
                {loading
                  ? "Saving..."
                  : editingEmployee
                    ? "Update Employee"
                    : "Create Employee"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;