import { useState } from "react";
import api from "../services/api";

export default function Login({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    try {
      if (isRegister) {
        await api.post("/auth/register", { username, password });
        setMessage("Account created. You can log in now.");
        setIsRegister(false);
        setPassword("");
      } else {
        const res = await api.post("/auth/login", { username, password });
        localStorage.setItem("token", res.data.token);
        onLoginSuccess();
      }
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong.");
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.box}>
        <h2 style={styles.heading}>{isRegister ? "Register" : "Login"}</h2>

        {error && <p style={styles.error}>{error}</p>}
        {message && <p style={styles.note}>{message}</p>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={styles.input}
            required
          />

          <label style={styles.label}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
            required
          />

          <button type="submit" style={styles.btn}>
            {isRegister ? "Create Account" : "Sign In"}
          </button>
        </form>

        <p style={styles.switchText}>
          {isRegister ? "Already have an account?" : "Need an account?"}{" "}
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError("");
              setMessage("");
            }}
            style={styles.linkBtn}
          >
            {isRegister ? "Login" : "Register"}
          </button>
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#ffffff",
    color: "#000000",
    fontFamily: "Arial, sans-serif",
  },
  box: {
    width: "320px",
    border: "1px solid #000000",
    padding: "20px",
    backgroundColor: "#ffffff",
  },
  heading: {
    marginTop: 0,
    marginBottom: "16px",
    fontSize: "20px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  label: {
    fontSize: "13px",
  },
  input: {
    padding: "8px",
    border: "1px solid #000000",
    backgroundColor: "#ffffff",
    color: "#000000",
    fontSize: "14px",
  },
  btn: {
    marginTop: "6px",
    padding: "9px",
    backgroundColor: "#000000",
    color: "#ffffff",
    border: "1px solid #000000",
    cursor: "pointer",
    fontSize: "14px",
  },
  switchText: {
    marginTop: "14px",
    marginBottom: 0,
    fontSize: "13px",
  },
  linkBtn: {
    background: "none",
    border: "none",
    color: "#000000",
    textDecoration: "underline",
    cursor: "pointer",
    padding: 0,
    fontSize: "13px",
  },
  error: {
    color: "#000000",
    border: "1px solid #000000",
    padding: "8px",
    fontSize: "13px",
  },
  note: {
    color: "#000000",
    border: "1px solid #000000",
    padding: "8px",
    fontSize: "13px",
  },
};