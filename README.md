# Micro Lending App

A full-stack invoice and micro-lending management application built with Flask, SQLite, React, and Vite.

Finance managers can register and sign in, create customer invoices, search and filter invoices, generate secure payment links, and track paid and pending balances. Customers can open a public payment link to review an invoice and confirm payment.

## Features

- User registration and JWT-based authentication
- Invoice creation with customer details
- Invoice search and status filtering
- Secure, expiring payment links
- Public invoice payment confirmation
- SQLite database initialization
- React dashboard and public payment interface

## Tech Stack

### Backend

- Python
- Flask
- Flask-CORS
- SQLite
- bcrypt
- PyJWT

### Frontend

- React 19
- Vite
- Axios
- Oxlint

## Project Structure

```text
micro-lending-app/
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── database.db
│   └── routes/
│       ├── auth.py
│       ├── invoices.py
│       └── public_pay.py
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

## Prerequisites

- Python 3.9 or newer
- Node.js 18 or newer
- npm

## Installation

Clone the repository:

```bash
git clone https://github.com/MehboobAli-Portfolio/micro-lending-app.git
cd micro-lending-app
```

### Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install flask flask-cors bcrypt pyjwt
```

Start the Flask server:

```bash
python app.py
```

The backend runs at `http://localhost:5000`. The SQLite database is initialized automatically at startup.

### Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs through Vite, typically at `http://localhost:5173`.

## Configuration

The backend supports the following environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `JWT_SECRET` | Secret used to sign authentication tokens | Development fallback included in source |
| `BASE_PAYMENT_URL` | Public payment-link base URL | `http://localhost:3000/pay` |

Set a secure JWT secret before deploying:

```bash
export JWT_SECRET="replace-with-a-long-random-secret"
export BASE_PAYMENT_URL="https://your-domain.example/pay"
```

On Windows PowerShell:

```powershell
$env:JWT_SECRET="replace-with-a-long-random-secret"
$env:BASE_PAYMENT_URL="https://your-domain.example/pay"
```

> The public payment URL must match the URL where the React application is hosted. For local development, ensure the frontend is available at `http://localhost:3000` or update `BASE_PAYMENT_URL` and the frontend API configuration.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a finance manager |
| `POST` | `/api/auth/login` | Login and receive a JWT |

### Invoices

Protected routes require:

```text
Authorization: Bearer <token>
```

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/invoices` | Create an invoice |
| `GET` | `/api/invoices` | List invoices; supports `search` and `status` query parameters |
| `POST` | `/api/invoices/<invoice_id>/payment-link` | Generate a seven-day payment link |

### Public Payments

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/pay/<token>` | Retrieve public invoice payment details |
| `POST` | `/api/pay/<token>/confirm` | Confirm payment and mark the invoice paid |

## Running a Production Build

```bash
cd frontend
npm run build
npm run preview
```

## Development Commands

### Frontend

```bash
npm run dev
npm run build
npm run lint
npm run preview
```

### Backend

```bash
cd backend
python app.py
```

## Security Notes

- Replace the default JWT secret in production.
- Configure the frontend and backend origins explicitly for production CORS policies.
- Use HTTPS for authentication and payment pages.
- Do not commit real customer or payment data.
- Replace the demonstration payment confirmation flow with a verified payment provider before production use.

## Contributing

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature
   ```

3. Commit your changes.
4. Push the branch and open a pull request.

## License

No license has been specified for this repository.
