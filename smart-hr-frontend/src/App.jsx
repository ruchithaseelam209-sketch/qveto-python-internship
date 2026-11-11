
import { useState } from "react";
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

const employees = [
  { name: "Aarav Sharma", id: "EMP001", department: "Engineering", status: "Present" },
  { name: "Ananya Patel", id: "EMP002", department: "Human Resources", status: "Present" },
  { name: "Rohan Mehta", id: "EMP003", department: "Finance", status: "On Leave" },
  { name: "Priya Deshmukh", id: "EMP004", department: "Design", status: "Present" },
  { name: "Kabir Joshi", id: "EMP005", department: "Engineering", status: "Absent" },
];

const stats = [
  { label: "Total Employees", value: "248", change: "+12 this month", icon: "♙", color: "purple" },
  { label: "Present Today", value: "216", change: "87.1% attendance", icon: "✓", color: "green" },
  { label: "On Leave", value: "18", change: "5 pending approvals", icon: "◷", color: "orange" },
  { label: "Payroll Processed", value: "92%", change: "For this month", icon: "₹", color: "blue" },
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("Admin");
  const [showNotifications, setShowNotifications] = useState(false);

  const filteredEmployees = employees.filter((employee) =>
    `${employee.name} ${employee.id} ${employee.department}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const pageDescriptions = {
    Employees: "View and manage your employee directory.",
    Attendance: "Track daily attendance and employee presence.",
    "Leave Requests": "Review leave applications and their status.",
    Payroll: "View payroll processing and payslip information.",
    Reports: "Review workforce summaries and HR insights.",
    Settings: "Manage your account and dashboard preferences.",
  };

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
                <div className="donut">
                  <div className="donut-inner">
                    <strong>87%</strong>
                    <span>Present</span>
                  </div>
                </div>
                <div className="attendance-legend">
                  <p><span className="dot green-dot" /> Present <strong>216</strong></p>
                  <p><span className="dot orange-dot" /> On Leave <strong>18</strong></p>
                  <p><span className="dot red-dot" /> Absent <strong>14</strong></p>
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
      return (
        <section className="stats-grid">
          {[
            ["Present", "216", "green"],
            ["On Leave", "18", "orange"],
            ["Absent", "14", "purple"],
            ["Attendance Rate", "87.1%", "blue"],
          ].map(([label, value, color]) => (
            <article className="stat-card" key={label}>
              <div className={`stat-icon ${color}`}>✓</div>
              <p className="stat-label">{label}</p>
              <h2>{value}</h2>
              <p className="stat-change">Sample attendance data</p>
            </article>
          ))}
        </section>
      );
    }

    if (activePage === "Leave Requests") {
      return (
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h3>Recent Leave Requests</h3>
              <p className="muted">Sample requests for demonstration</p>
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Employee</th><th>Leave Type</th><th>Dates</th><th>Status</th></tr></thead>
              <tbody>
                <tr><td>Aarav Sharma</td><td>Casual Leave</td><td>28–29 Oct</td><td><span className="status pending">Pending</span></td></tr>
                <tr><td>Ananya Patel</td><td>Sick Leave</td><td>27 Oct</td><td><span className="status approved">Approved</span></td></tr>
                <tr><td>Rohan Mehta</td><td>Annual Leave</td><td>30 Oct–1 Nov</td><td><span className="status pending">Pending</span></td></tr>
              </tbody>
            </table>
          </div>
        </section>
      );
    }

    if (activePage === "Payroll") {
      return (
        <section className="stats-grid">
          {[
            ["Monthly Payroll", "₹18.4L", "Estimated total"],
            ["Processed", "228", "Payslips generated"],
            ["Pending", "20", "Awaiting processing"],
            ["Pay Period", "October", "Sample pay period"],
          ].map(([label, value, note], index) => (
            <article className="stat-card" key={label}>
              <div className={`stat-icon ${["purple", "green", "orange", "blue"][index]}`}>₹</div>
              <p className="stat-label">{label}</p>
              <h2>{value}</h2>
              <p className="stat-change">{note}</p>
            </article>
          ))}
        </section>
      );
    }

    return (
      <section className="panel placeholder-panel">
        <div className="placeholder-icon">▦</div>
        <h3>{activePage}</h3>
        <p className="muted">{pageDescriptions[activePage]}</p>
        <p className="demo-note">
          This section is a frontend demonstration. Real data and backend integration will be added later.
        </p>
      </section>
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
              {item.name === "Leave Requests" && <span className="nav-count">5</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">?</div>
            <strong>Need help?</strong>
            <p>Visit the help center for assistance.</p>
            <button onClick={() => alert("Help center coming soon!")}>Open Help Center ↗</button>
          </div>
          <div className="sidebar-user">
            <div className="avatar">TK</div>
            <div className="user-details">
              <strong>Tanmayi Khairnar</strong>
              <span>{role}</span>
            </div>
            <span className="user-menu">•••</span>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> <strong>{activePage}</strong></div>
          <div className="topbar-actions">
            <label className="role-select">
              <span>Preview role</span>
              <select value={role} onChange={(event) => setRole(event.target.value)}>
                <option>Admin</option>
                <option>HR</option>
                <option>Employee</option>
              </select>
            </label>
            <button className="notification-button" aria-label="Notifications" onClick={() => setShowNotifications(!showNotifications)}>
              ♧<span className="notification-dot" />
            </button>
            <div className="avatar top-avatar">TK</div>
          </div>
          {showNotifications && (
            <div className="notification-popover">
              <strong>Notifications</strong>
              <p>5 leave requests are waiting for review.</p>
              <p>Your dashboard is using sample data.</p>
            </div>
          )}
        </header>

        <div className="page-content">
          <section className="welcome-row">
            <div>
              <p className="eyebrow">SUNDAY, OCTOBER 25, 2026</p>
              <h1>{activePage === "Dashboard" ? "Good morning, Tanmayi!" : activePage}</h1>
              <p className="welcome-subtitle">
                {activePage === "Dashboard"
                  ? "Here's what's happening with your team today."
                  : pageDescriptions[activePage] || "Manage your HR workspace."}
              </p>
            </div>
            <button className="primary-button" onClick={() => setActivePage("Employees")}>
              <span>＋</span> Manage Employees
            </button>
          </section>

          {renderPage()}

          <footer className="footer">
            <span>© 2026 harmonyHR</span>
            <span>Smart HR & Employee Management System · Demo</span>
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
          <p className="muted">A quick look at your team</p>
        </div>
        <button className="text-button" onClick={onViewAll}>View all employees →</button>
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
            <tr><th>EMPLOYEE</th><th>EMPLOYEE ID</th><th>DEPARTMENT</th><th>STATUS</th></tr>
          </thead>
          <tbody>
            {employees.length > 0 ? employees.map((employee) => (
              <tr key={employee.id}>
                <td><div className="employee-name"><div className="mini-avatar">{employee.name.split(" ").map((part) => part[0]).join("")}</div><strong>{employee.name}</strong></div></td>
                <td>{employee.id}</td>
                <td>{employee.department}</td>
                <td><span className={`status ${employee.status === "Present" ? "approved" : employee.status === "Absent" ? "absent" : "pending"}`}>{employee.status}</span></td>
              </tr>
            )) : (
              <tr><td colSpan="4" className="empty-state">No employees match your search.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default App;

