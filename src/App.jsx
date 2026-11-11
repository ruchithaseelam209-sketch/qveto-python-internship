
import { useState } from "react";
import "./App.css";

// Use Vite proxy instead of directly connecting to Django.
const API = "/api";

function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("Dashboard");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

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

  // LOGIN
  async function login(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API}/auth/login/`, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          username: username.trim(),
          password,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.error || result.detail || "Invalid username or password."
        );
      }

      if (!result.user) {
        throw new Error("User information missing from login response.");
      }

      setUser(result.user);
      setPassword("");
      setPage("Dashboard");
      setData([]);
      setError("");
    } catch (err) {
      setError(err.message || "Unable to connect to server.");
    } finally {
      setLoading(false);
    }
  }

  // LOGOUT
  async function logout() {
    setLoading(true);

    try {
      await fetch(`${API}/auth/logout/`, {
        method: "POST",
        credentials: "same-origin",
      });
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      setUser(null);
      setData([]);
      setError("");
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
    setData([]);

    const endpoint = endpoints[section];

    if (!endpoint) return;

    setLoading(true);

    try {
      const response = await fetch(`${API}${endpoint}`, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
        },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail ||
            result.error ||
            `Unable to load ${section}. HTTP ${response.status}`
        );
      }

      const records = Array.isArray(result)
        ? result
        : Array.isArray(result.results)
          ? result.results
          : [];

      setData(records);
    } catch (err) {
      setError(err.message || `Unable to load ${section}.`);
    } finally {
      setLoading(false);
    }
  }

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

  // DASHBOARD
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
            className={`nav-item ${page === item ? "active" : ""}`}
            onClick={() => {
              if (item === "Dashboard") {
                setPage("Dashboard");
                setData([]);
                setError("");
              } else {
                loadData(item);
              }
            }}
          >
            <span>{["▦", "♙", "▤", "◷", "▧"][index]}</span>
            {item}
          </button>
        ))}

        <button className="logout-btn" onClick={logout}>
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

        {page === "Dashboard" ? (
          <>
            <section className="welcome">
              <div>
                <h1>Welcome, {user.username}!</h1>
                <p>Manage your workforce from one place.</p>
              </div>

              <span className="welcome-icon">✦</span>
            </section>

            <h3 className="section-title">Management Modules</h3>

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
                  <p>View and manage {item.toLowerCase()}</p>

                  <span className="card-arrow">Explore →</span>
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

            {loading ? (
              <p>Loading records...</p>
            ) : data.length === 0 ? (
              <p className="empty">No records found.</p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      {Object.keys(data[0]).map((key) => (
                        <th key={key}>{key.replaceAll("_", " ")}</th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    {data.map((row, index) => (
                      <tr key={row.id || index}>
                        {Object.values(row).map((value, i) => (
                          <td key={i}>
                            {typeof value === "object" && value !== null
                              ? JSON.stringify(value)
                              : String(value ?? "-")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
