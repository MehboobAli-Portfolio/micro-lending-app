import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard({ onLogout }) {
  const [invoices, setInvoices] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [generatedLink, setGeneratedLink] = useState("");
  const [feedback, setFeedback] = useState("");

  const [form, setForm] = useState({
    invoice_number: "",
    customer_name: "",
    customer_email: "",
    customer_phone: "",
    invoice_date: new Date().toISOString().split("T")[0],
    due_date: "",
    amount_due: "",
  });

  const loadInvoices = async () => {
    try {
      const res = await api.get("/invoices", {
        params: { search, status: statusFilter },
      });
      setInvoices(res.data);
    } catch (err) {
      if (err.response?.status === 401) {
        onLogout();
      }
    }
  };

  useEffect(() => {
    loadInvoices();
  }, [search, statusFilter]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleCreateInvoice = async (e) => {
    e.preventDefault();
    setFeedback("");
    try {
      const res = await api.post("/invoices", {
        ...form,
        amount_due: Number(form.amount_due),
      });
      setFeedback(res.data.message || "Invoice created.");
      setForm({
        invoice_number: "",
        customer_name: "",
        customer_email: "",
        customer_phone: "",
        invoice_date: new Date().toISOString().split("T")[0],
        due_date: "",
        amount_due: "",
      });
      loadInvoices();
    } catch (err) {
      setFeedback(err.response?.data?.error || "Failed to create invoice.");
    }
  };

  const handleGenerateLink = async (invoiceId) => {
    setFeedback("");
    try {
      const res = await api.post(`/invoices/${invoiceId}/payment-link`);
      const rawLink = res.data.payment_link || "";
      const token = rawLink.split("/").pop();
      const localUrl = `${window.location.origin}/pay/${token}`;
      setGeneratedLink(localUrl);
    } catch (err) {
      setFeedback(err.response?.data?.error || "Could not generate link.");
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.topBar}>
        <h2 style={styles.heading}>Accounts Receivable Dashboard</h2>
        <button onClick={onLogout} style={styles.secondaryBtn}>
          Logout
        </button>
      </div>

      {feedback && <div style={styles.notice}>{feedback}</div>}

      {generatedLink && (
        <div style={styles.notice}>
          Payment link:{" "}
          <a href={generatedLink} style={styles.link}>
            {generatedLink}
          </a>
        </div>
      )}

      <div style={styles.layout}>
        <div style={styles.panelLeft}>
          <h3 style={styles.subHeading}>New Invoice</h3>
          <form onSubmit={handleCreateInvoice} style={styles.form}>
            <label style={styles.label}>Invoice Number</label>
            <input
              type="text"
              name="invoice_number"
              placeholder="INV-1001"
              value={form.invoice_number}
              onChange={handleChange}
              style={styles.input}
              required
            />

            <label style={styles.label}>Customer Name</label>
            <input
              type="text"
              name="customer_name"
              value={form.customer_name}
              onChange={handleChange}
              style={styles.input}
              required
            />

            <label style={styles.label}>Customer Email</label>
            <input
              type="email"
              name="customer_email"
              value={form.customer_email}
              onChange={handleChange}
              style={styles.input}
              required
            />

            <label style={styles.label}>Phone</label>
            <input
              type="text"
              name="customer_phone"
              value={form.customer_phone}
              onChange={handleChange}
              style={styles.input}
            />

            <label style={styles.label}>Invoice Date</label>
            <input
              type="date"
              name="invoice_date"
              value={form.invoice_date}
              onChange={handleChange}
              style={styles.input}
              required
            />

            <label style={styles.label}>Due Date</label>
            <input
              type="date"
              name="due_date"
              value={form.due_date}
              onChange={handleChange}
              style={styles.input}
              required
            />

            <label style={styles.label}>Amount Due</label>
            <input
              type="number"
              step="0.01"
              name="amount_due"
              value={form.amount_due}
              onChange={handleChange}
              style={styles.input}
              required
            />

            <button type="submit" style={styles.primaryBtn}>
              Save Invoice
            </button>
          </form>
        </div>

        <div style={styles.panelRight}>
          <h3 style={styles.subHeading}>Invoices</h3>

          <div style={styles.filters}>
            <input
              type="text"
              placeholder="Search invoice # or customer"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ ...styles.input, flex: 1 }}
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={styles.input}
            >
              <option value="">All</option>
              <option value="PENDING">PENDING</option>
              <option value="PAID">PAID</option>
            </select>
          </div>

          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Invoice #</th>
                <th style={styles.th}>Customer</th>
                <th style={styles.th}>Amount</th>
                <th style={styles.th}>Due Date</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Link</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan="6" style={styles.td}>
                    No invoices found.
                  </td>
                </tr>
              ) : (
                invoices.map((inv) => (
                  <tr key={inv.id}>
                    <td style={styles.td}>{inv.invoice_number}</td>
                    <td style={styles.td}>{inv.customer_name}</td>
                    <td style={styles.td}>{Number(inv.amount_due).toFixed(2)}</td>
                    <td style={styles.td}>{inv.due_date}</td>
                    <td style={styles.td}>{inv.status}</td>
                    <td style={styles.td}>
                      {inv.status !== "PAID" ? (
                        <button
                          type="button"
                          onClick={() => handleGenerateLink(inv.id)}
                          style={styles.smallBtn}
                        >
                          Get Link
                        </button>
                      ) : (
                        <span>-</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    maxWidth: "1100px",
    margin: "0 auto",
    padding: "20px",
    backgroundColor: "#ffffff",
    color: "#000000",
    fontFamily: "Arial, sans-serif",
  },
  topBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottom: "1px solid #000000",
    paddingBottom: "12px",
    marginBottom: "16px",
  },
  heading: {
    margin: 0,
    fontSize: "20px",
  },
  subHeading: {
    marginTop: 0,
    marginBottom: "12px",
    fontSize: "16px",
  },
  layout: {
    display: "flex",
    gap: "20px",
    alignItems: "flex-start",
    flexWrap: "wrap",
  },
  panelLeft: {
    width: "300px",
    border: "1px solid #000000",
    padding: "16px",
  },
  panelRight: {
    flex: 1,
    minWidth: "400px",
    border: "1px solid #000000",
    padding: "16px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  label: {
    fontSize: "12px",
  },
  input: {
    padding: "7px",
    border: "1px solid #000000",
    backgroundColor: "#ffffff",
    color: "#000000",
    fontSize: "13px",
  },
  primaryBtn: {
    marginTop: "6px",
    padding: "8px",
    backgroundColor: "#000000",
    color: "#ffffff",
    border: "1px solid #000000",
    cursor: "pointer",
  },
  secondaryBtn: {
    padding: "6px 12px",
    backgroundColor: "#ffffff",
    color: "#000000",
    border: "1px solid #000000",
    cursor: "pointer",
  },
  smallBtn: {
    padding: "4px 8px",
    backgroundColor: "#ffffff",
    color: "#000000",
    border: "1px solid #000000",
    cursor: "pointer",
    fontSize: "12px",
  },
  filters: {
    display: "flex",
    gap: "10px",
    marginBottom: "14px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "13px",
  },
  th: {
    textAlign: "left",
    borderBottom: "1px solid #000000",
    padding: "8px 6px",
  },
  td: {
    borderBottom: "1px solid #cccccc",
    padding: "8px 6px",
  },
  notice: {
    border: "1px solid #000000",
    padding: "10px",
    marginBottom: "14px",
    fontSize: "13px",
  },
  link: {
    color: "#000000",
  },
};