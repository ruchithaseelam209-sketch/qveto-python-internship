
import { useEffect, useState } from "react";
import { apiRequest, loginUser, logoutUser } from "./api";
import "./App.css";

const menuItems = [
  { name: "Dashboard", icon: "▦" },
  { name: "Employees", icon: "♙" },
  { name: "Attendance", icon: "◷" },
  { name: "Leave Requests", icon: "▤" },
  { name: "Payroll", icon: "₹" },
  { name: "Reports", icon: "▥" },
  { name: "Settings", icon: "⚙" },
];

function getRecords(data) {
  if (Array.isArray(data)) return data;
  return Array.isArray(data?.results) ? data.results : [];
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(`${String(value).slice(0, 10)}T00:00:00`);

  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString("en-IN");
}

function formatTime(value) {
  if (!value) return "—";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? "—"
    : date.toLocaleTimeString("en-IN", {
        hour: "2-digit",
        minute: "2-digit",
      });
}

function displayStatus(value) {
  if (!value) return "Unknown";

  return String(value)
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function statusClass(value) {
  const status = String(value || "").toUpperCase();

  if (["ACTIVE", "PRESENT", "APPROVED", "HALF_DAY"].includes(status)) {
    return "approved";
  }

  if (["INACTIVE", "ABSENT", "REJECTED"].includes(status)) {
    return "absent";
  }

  return "pending";
}

function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [activePage, setActivePage] = useState("Dashboard");
  const [search, setSearch] = useState("");
  const [showNotifications, setShowNotifications] = useState(false);

  // Real backend data
  const [employees, setEmployees] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [dataLoading, setDataLoading] = useState(false);
  const [dataError, setDataError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  // Restore existing Django login session.
  useEffect(() => {
    let active = true;

    async function checkSession() {
      try {
        const currentUser = await apiRequest("/auth/me/");
        if (active) setUser(currentUser);
      } catch {
        if (active) setUser(null);
      } finally {
        if (active) setAuthLoading(false);
      }
    }

    checkSession();

    return () => {
      active = false;
    };
  }, []);

  // Fetch all available backend modules after login.
  useEffect(() => {
    if (!user) {
      setEmployees([]);
      setAttendanceRecords([]);
      setLeaveRequests([]);
      setLeaveTypes([]);
      return;
    }

    let active = true;

    async function loadWorkspaceData() {
      setDataLoading(true);
      setDataError("");

      const results = await Promise.allSettled([
        apiRequest("/employees/"),
        apiRequest("/attendance/"),
        apiRequest("/leave-requests/"),
        apiRequest("/leave-types/"),
      ]);

      if (!active) return;

      const errors = [];

      // Employees
      if (results[0].status === "fulfilled") {
        const records = getRecords(results[0].value);

        setEmployees(
          records.map((employee) => ({
            id: employee.id,
            displayId: `#${employee.id}`,
            name:
              `${employee.first_name || ""} ${employee.last_name || ""}`.trim() ||
              employee.username ||
              `Employee ${employee.id}`,
            department: employee.department_name || "Unassigned",
            status: employee.status || "UNKNOWN",
          }))
        );
      } else {
        setEmployees([]);
        errors.push("Employees: " + results[0].reason.message);
      }

      // Attendance
      if (results[1].status === "fulfilled") {
        setAttendanceRecords(getRecords(results[1].value));
      } else {
        setAttendanceRecords([]);
        errors.push("Attendance: " + results[1].reason.message);
      }

      // Leave requests
      if (results[2].status === "fulfilled") {
        setLeaveRequests(getRecords(results[2].value));
      } else {
        setLeaveRequests([]);
        errors.push("Leave requests: " + results[2].reason.message);
      }

      // Leave types
      if (results[3].status === "fulfilled") {
        setLeaveTypes(getRecords(results[3].value));
      } else {
        setLeaveTypes([]);
        errors.push("Leave types: " + results[3].reason.message);
      }

      setDataError(errors.join(" | "));
      setDataLoading(false);
    }

    loadWorkspaceData();

    return () => {
      active = false;
    };
  }, [user, refreshKey]);

  async function handleLogin(event) {
    event.preventDefault();
    setAuthError("");
    setIsSubmitting(true);

    try {
      const result = await loginUser(
        loginUsername.trim(),
        loginPassword
      );

      const loggedInUser =
        result.user || await apiRequest("/auth/me/");

      setUser(loggedInUser);
      setLoginPassword("");
      setActivePage("Dashboard");
    } catch (error) {
      setAuthError(error.message || "Login failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleLogout() {
    try {
      await logoutUser();
      setUser(null);
      setLoginUsername("");
      setLoginPassword("");
      setActivePage("Dashboard");
      setSearch("");
    } catch (error) {
      window.alert(error.message || "Could not log out.");
    }
  }

  async function handleLeaveDecision(id, action) {
    try {
      await apiRequest(`/leave-requests/${id}/${action}/`, {
        method: "POST",
        body: { review_remarks: "" },
      });

      setRefreshKey((value) => value + 1);
    } catch (error) {
      window.alert(error.message || `Could not ${action} leave request.`);
    }
  }

  const displayName = user
    ? `${user.first_name || ""} ${user.last_name || ""}`.trim() ||
      user.username
    : "";

  const roleLabel =
    user?.role === "ADMIN"
      ? "Admin"
      : user?.role === "HR"
        ? "HR"
        : "Employee";

  const canReviewLeaves =
    user?.role === "ADMIN" ||
    user?.role === "HR" ||
    user?.is_superuser;

  const avatarInitials = user
    ? (
        user.first_name && user.last_name
          ? `${user.first_name[0]}${user.last_name[0]}`
          : user.username.slice(0, 2)
      ).toUpperCase()
    : "";

  const today = new Date();
  const todayKey = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0"),
  ].join("-");

  const todayLabel = today.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).toUpperCase();

  const todayAttendance = attendanceRecords.filter(
    (record) => String(record.date).slice(0, 10) === todayKey
  );

  const presentCount = todayAttendance.filter(
    (record) =>
      record.status === "PRESENT" || record.status === "HALF_DAY"
  ).length;

  const absentCount = todayAttendance.filter(
    (record) => record.status === "ABSENT"
  ).length;

  const onLeaveCount = todayAttendance.filter(
    (record) => record.status === "ON_LEAVE"
  ).length;

  const attendanceRate = todayAttendance.length
    ? Math.round((presentCount / todayAttendance.length) * 100)
    : 0;

  const pendingCount = leaveRequests.filter(
    (request) => request.status === "PENDING"
  ).length;

  const filteredEmployees = employees.filter((employee) =>
    `${employee.name} ${employee.displayId} ${employee.department}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  function getEmployeeName(employeeId) {
    const id =
      typeof employeeId === "object"
        ? employeeId?.id
        : employeeId;

    return (
      employees.find((employee) => String(employee.id) === String(id))
        ?.name || `Employee #${id ?? "—"}`
    );
  }

  function getLeaveTypeName(typeId) {
    if (typeof typeId === "object" && typeId?.name) {
      return typeId.name;
    }

    return (
      leaveTypes.find((type) => String(type.id) === String(typeId))
        ?.name || `Leave type #${typeId ?? "—"}`
    );
  }

  const pageDescriptions = {
    Employees: "View and manage your employee directory.",
    Attendance: "Track daily attendance and employee presence.",
    "Leave Requests": "Review leave applications and their status.",
    Payroll: "View payroll processing and payslip information.",
    Reports: "Review workforce summaries and HR insights.",
    Settings: "Manage your account and dashboard preferences.",
  };

  const stats = [
    {
      label: "Total Employees",
      value: employees.length,
      change: "Registered employee profiles",
      icon: "♙",
      color: "purple",
    },
    {
      label: "Present Today",
      value: presentCount,
      change: `${attendanceRate}% of today's recorded attendance`,
      icon: "✓",
      color: "green",
    },
    {
      label: "On Leave",
      value: onLeaveCount,
      change: `${pendingCount} pending leave requests`,
      icon: "◷",
      color: "orange",
    },
    {
      label: "Payroll Processed",
      value: "Not connected",
      change: "Payroll API not configured",
      icon: "₹",
      color: "blue",
    },
  ];

  function renderAttendancePage() {
    return (
      <>
        <section className="stats-grid">
          {[
            ["Present", presentCount, "green"],
            ["On Leave", onLeaveCount, "orange"],
            ["Absent", absentCount, "purple"],
            ["Attendance Rate", `${attendanceRate}%`, "blue"],
          ].map(([label, value, color]) => (
            <article className="stat-card" key={label}>
              <div className={`stat-icon ${color}`}>✓</div>
              <p className="stat-label">{label}</p>
              <h2>{value}</h2>
              <p className="stat-change">Today's backend records</p>
            </article>
          ))}
        </section>

        <section className="panel employee-panel">
          <div className="panel-heading">
            <div>
              <h3>Today's Attendance Records</h3>
              <p className="muted">{todayKey}</p>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>EMPLOYEE</th>
                  <th>CHECK IN</th>
                  <th>CHECK OUT</th>
                  <th>STATUS</th>
                </tr>
              </thead>
              <tbody>
                {todayAttendance.length ? (
                  todayAttendance.map((record) => (
                    <tr key={record.id}>
                      <td>{getEmployeeName(record.employee)}</td>
                      <td>{formatTime(record.check_in)}</td>
                      <td>{formatTime(record.check_out)}</td>
                      <td>
                        <span className={`status ${statusClass(record.status)}`}>
                          {displayStatus(record.status)}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="empty-state">
                      No attendance records have been submitted for today.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </>
    );
  }

  function renderLeavePage() {
    return (
      <section className="panel employee-panel">
        <div className="panel-heading">
          <div>
            <h3>Leave Requests</h3>
            <p className="muted">
              {pendingCount} requests waiting for review
            </p>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>EMPLOYEE</th>
                <th>LEAVE TYPE</th>
                <th>START DATE</th>
                <th>END DATE</th>
                <th>STATUS</th>
                {canReviewLeaves && <th>ACTION</th>}
              </tr>
            </thead>
            <tbody>
              {leaveRequests.length ? (
                leaveRequests.map((request) => (
                  <tr key={request.id}>
                    <td>{getEmployeeName(request.employee)}</td>
                    <td>{getLeaveTypeName(request.leave_type)}</td>
                    <td>{formatDate(request.start_date)}</td>
                    <td>{formatDate(request.end_date)}</td>
                    <td>
                      <span className={`status ${statusClass(request.status)}`}>
                        {displayStatus(request.status)}
                      </span>
                    </td>
                    {canReviewLeaves && (
                      <td>
                        {request.status === "PENDING" ? (
                          <>
                            <button
                              className="text-button"
                              onClick={() => handleLeaveDecision(request.id, "approve")}
                            >
                              Approve
                            </button>
                            {" "}
                            <button
                              className="text-button"
                              onClick={() => handleLeaveDecision(request.id, "reject")}
                            >
                              Reject
                            </button>
                          </>
                        ) : "—"}
                      </td>
                    )}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={canReviewLeaves ? 6 : 5} className="empty-state">
                    No leave requests found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    );
  }

  function renderPage() {
    if (activePage === "Dashboard") {
      return (
        <>
          <section className="stats-grid">
            {stats.map((stat) => (
              <article className="stat-card" key={stat.label}>
                <div className={`stat-icon ${stat.color}`}>{stat.icon}</div>
                <p className="stat-label">{stat.label}</p>
                <h2>{stat.value}</h2>
                <p className="stat-change">{stat.change}</p>
              </article>
            ))}
          </section>

          <section className="content-grid">
            <article className="panel attendance-panel">
              <div className="panel-heading">
                <div>
                  <h3>Attendance Overview</h3>
                  <p className="muted">Today's workforce summary</p>
                </div>
                <span className="period-tag">Today</span>
              </div>

              <div className="attendance-summary">
                <div
                  className="donut"
                  style={{
                    background: `conic-gradient(#6654dc ${attendanceRate}%, #eee ${attendanceRate}% 100%)`,
                  }}
                >
                  <div className="donut-inner">
                    <strong>{attendanceRate}%</strong>
                    <span>Present</span>
                  </div>
                </div>

                <div className="attendance-legend">
                  <p><span className="dot green-dot" /> Present <strong>{presentCount}</strong></p>
                  <p><span className="dot orange-dot" /> On Leave <strong>{onLeaveCount}</strong></p>
                  <p><span className="dot red-dot" /> Absent <strong>{absentCount}</strong></p>
                </div>
              </div>
            </article>

            <article className="panel activity-panel">
              <div className="panel-heading">
                <div>
                  <h3>Quick Actions</h3>
                  <p className="muted">Common HR tasks</p>
                </div>
              </div>

              <button className="action-button" onClick={() => setActivePage("Employees")}>
                <span>＋</span> View Employees
                <span className="action-arrow">→</span>
              </button>

              <button className="action-button" onClick={() => setActivePage("Attendance")}>
                <span>◷</span> Check Attendance
                <span className="action-arrow">→</span>
              </button>

              <button className="action-button" onClick={() => setActivePage("Leave Requests")}>
                <span>▤</span> Review Leave Requests
                <span className="action-arrow">→</span>
              </button>

              <button className="action-button" onClick={() => setActivePage("Payroll")}>
                <span>₹</span> Open Payroll
                <span className="action-arrow">→</span>
              </button>
            </article>
          </section>

          <EmployeeTable
            employees={filteredEmployees}
            search={search}
            setSearch={setSearch}
            onViewAll={() => setActivePage("Employees")}
          />
        </>
      );
    }

    if (activePage === "Employees") {
      return (
        <EmployeeTable
          employees={filteredEmployees}
          search={search}
          setSearch={setSearch}
          onViewAll={() => setActivePage("Employees")}
        />
      );
    }

    if (activePage === "Attendance") {
      return renderAttendancePage();
    }

    if (activePage === "Leave Requests") {
      return renderLeavePage();
    }

    if (activePage === "Payroll") {
      return (
        <section className="panel placeholder-panel">
          <div className="placeholder-icon">₹</div>
          <h3>Payroll integration pending</h3>
          <p className="muted">
            The current backend does not expose a payroll API.
          </p>
          <p className="demo-note">
            No sample salary or payslip figures are displayed. Payroll can be
            connected once its backend module is available.
          </p>
        </section>
      );
    }

    if (activePage === "Reports") {
      return (
        <section className="stats-grid">
          {[
            ["Employees", employees.length],
            ["Today's Attendance", todayAttendance.length],
            ["Pending Leaves", pendingCount],
            ["Approved Leaves", leaveRequests.filter((r) => r.status === "APPROVED").length],
          ].map(([label, value]) => (
            <article className="stat-card" key={label}>
              <p className="stat-label">{label}</p>
              <h2>{value}</h2>
              <p className="stat-change">Live backend summary</p>
            </article>
          ))}
        </section>
      );
    }

    if (activePage === "Settings") {
      return (
        <section className="panel placeholder-panel">
          <div className="placeholder-icon">⚙</div>
          <h3>Account Settings</h3>
          <p className="muted">Your authenticated account details</p>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email || "Not provided"}</p>
          <p><strong>Role:</strong> {roleLabel}</p>
        </section>
      );
    }

    return null;
  }

  if (authLoading) {
    return (
      <div className="auth-screen">
        <div className="auth-card">
          <div className="brand-mark">H</div>
          <h1>HarmonyHR</h1>
          <p>Checking your login session...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="auth-screen">
        <form className="auth-card" onSubmit={handleLogin}>
          <div className="auth-brand">
            <div className="brand-mark">H</div>
            <div>
              <h2>harmony<span>HR</span></h2>
              <p>PEOPLE MANAGEMENT</p>
            </div>
          </div>

          <h1>Welcome back!</h1>
          <p className="auth-subtitle">Sign in to access your HR workspace.</p>

          {authError && (
            <div className="auth-error" role="alert">{authError}</div>
          )}

          <label className="auth-field">
            Username
            <input
              type="text"
              placeholder="Enter your username"
              value={loginUsername}
              onChange={(event) => setLoginUsername(event.target.value)}
              autoComplete="username"
              required
            />
          </label>

          <label className="auth-field">
            Password
            <input
              type="password"
              placeholder="Enter your password"
              value={loginPassword}
              onChange={(event) => setLoginPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>

          <button
            type="submit"
            className="primary-button auth-submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>

          <p className="auth-help">Use your Django account credentials.</p>
        </form>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">H</div>
          <div>
            <h2>harmony<span>HR</span></h2>
            <p>PEOPLE MANAGEMENT</p>
          </div>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="navigation">
          {menuItems.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${activePage === item.name ? "active" : ""}`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.name}</span>
              {item.name === "Leave Requests" && pendingCount > 0 && (
                <span className="nav-count">{pendingCount}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">?</div>
            <strong>Need help?</strong>
            <p>Visit the help center for assistance.</p>
            <button onClick={() => window.alert("Help center coming soon!")}>
              Open Help Center ↗
            </button>
          </div>

          <div className="sidebar-user">
            <div className="avatar">{avatarInitials}</div>
            <div className="user-details">
              <strong>{displayName}</strong>
              <span>{roleLabel}</span>
            </div>
            <span className="user-menu">•••</span>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activePage}</strong>
          </div>

          <div className="topbar-actions">
            <div className="role-label">
              <span>Signed in as</span>
              <strong>{roleLabel}</strong>
            </div>

            <button className="logout-button" onClick={handleLogout}>
              Log out
            </button>

            <button
              className="notification-button"
              aria-label="Notifications"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              ♧<span className="notification-dot" />
            </button>

            <div className="avatar top-avatar">{avatarInitials}</div>
          </div>

          {showNotifications && (
            <div className="notification-popover">
              <strong>Notifications</strong>
              <p>{pendingCount} leave requests are waiting for review.</p>
              <p>{dataLoading ? "Refreshing backend data..." : "Backend data loaded."}</p>
            </div>
          )}
        </header>

        <div className="page-content">
          <section className="welcome-row">
            <div>
              <p className="eyebrow">{todayLabel}</p>
              <h1>
                {activePage === "Dashboard"
                  ? `Welcome, ${displayName}!`
                  : activePage}
              </h1>
              <p className="welcome-subtitle">
                {activePage === "Dashboard"
                  ? "Here's what's happening with your team today."
                  : pageDescriptions[activePage] || "Manage your HR workspace."}
              </p>
            </div>

            <button
              className="primary-button"
              onClick={() => setActivePage("Employees")}
            >
              <span>＋</span> Manage Employees
            </button>
          </section>

          {dataError && (
            <section className="panel">
              <p className="demo-note">
                Some backend data could not be loaded: {dataError}
              </p>
            </section>
          )}

          {dataLoading && (
            <p className="muted">Loading live data from the backend...</p>
          )}

          {renderPage()}

          <footer className="footer">
            <span>© 2026 harmonyHR</span>
            <span>Smart HR & Employee Management System · Live backend integration</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

function EmployeeTable({ employees, search, setSearch, onViewAll }) {
  return (
    <section className="panel employee-panel">
      <div className="panel-heading">
        <div>
          <h3>Employee Directory</h3>
          <p className="muted">Employee records from the backend</p>
        </div>
        <button className="text-button" onClick={onViewAll}>
          View all employees →
        </button>
      </div>

      <div className="table-toolbar">
        <input
          aria-label="Search employees"
          type="search"
          placeholder="Search by name, ID or department..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <span className="result-count">{employees.length} employees</span>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>EMPLOYEE</th>
              <th>PROFILE ID</th>
              <th>DEPARTMENT</th>
              <th>STATUS</th>
            </tr>
          </thead>

          <tbody>
            {employees.length ? (
              employees.map((employee) => (
                <tr key={employee.id}>
                  <td>
                    <div className="employee-name">
                      <div className="mini-avatar">
                        {employee.name
                          .split(" ")
                          .map((part) => part[0])
                          .join("")
                          .slice(0, 2)}
                      </div>
                      <strong>{employee.name}</strong>
                    </div>
                  </td>
                  <td>{employee.displayId}</td>
                  <td>{employee.department}</td>
                  <td>
                    <span className={`status ${statusClass(employee.status)}`}>
                      {displayStatus(employee.status)}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="empty-state">
                  {search
                    ? "No employees match your search."
                    : "No employee profiles found. Add employees to see them here."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default App;
