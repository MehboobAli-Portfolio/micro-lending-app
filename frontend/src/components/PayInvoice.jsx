import { useEffect, useState } from "react";
import api from "../services/api";

export default function PayInvoice({ token }) {
  const [invoice, setInvoice] = useState(null);
  const [error, setError] = useState("");
  const [paidMessage, setPaidMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const res = await api.get(`/pay/${token}`);
        setInvoice(res.data);
      } catch (err) {
        setError(err.response?.data?.error || "Payment link is invalid or expired.");
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [token]);

  const handleConfirmPay = async () => {
    setError("");
    try {
      const res = await api.post(`/pay/${token}/confirm`);
      setPaidMessage(res.data.message || "Payment completed.");
      setInvoice((prev) => (prev ? { ...prev, status: "PAID" } : null));
    } catch (err) {
      setError(err.response?.data?.error || "Could not complete payment.");
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h2 style={styles.heading}>Invoice Payment</h2>

        {loading && <p style={styles.text}>Loading invoice...</p>}

        {!loading && error && <p style={styles.boxMsg}>{error}</p>}

        {!loading && paidMessage && <p style={styles.boxMsg}>{paidMessage}</p>}

        {!loading && invoice && !paidMessage && (
          <div>
            <p style={styles.text}>
              <strong>Invoice:</strong> {invoice.invoice_number}
            </p>
            <p style={styles.text}>
              <strong>Customer:</strong> {invoice.customer_name}
            </p>
            <p style={styles.text}>
              <strong>Due Date:</strong> {invoice.due_date}
            </p>
            <p style={styles.text}>
              <strong>Amount Due:</strong> {Number(invoice.amount_due).toFixed(2)}
            </p>
            <p style={styles.text}>
              <strong>Status:</strong> {invoice.status}
            </p>

            {invoice.status !== "PAID" && (
              <button onClick={handleConfirmPay} style={styles.btn}>
                Confirm Payment
              </button>
            )}
          </div>
        )}

        <div style={styles.footer}>
          <a href="/" style={styles.link}>
            Go to Manager Portal
          </a>
        </div>
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
  card: {
    width: "360px",
    border: "1px solid #000000",
    padding: "20px",
    backgroundColor: "#ffffff",
  },
  heading: {
    marginTop: 0,
    marginBottom: "14px",
    fontSize: "20px",
  },
  text: {
    margin: "6px 0",
    fontSize: "14px",
  },
  boxMsg: {
    border: "1px solid #000000",
    padding: "10px",
    fontSize: "14px",
  },
  btn: {
    marginTop: "14px",
    width: "100%",
    padding: "9px",
    backgroundColor: "#000000",
    color: "#ffffff",
    border: "1px solid #000000",
    cursor: "pointer",
    fontSize: "14px",
  },
  footer: {
    marginTop: "16px",
    paddingTop: "10px",
    borderTop: "1px solid #cccccc",
    fontSize: "13px",
  },
  link: {
    color: "#000000",
  },
};