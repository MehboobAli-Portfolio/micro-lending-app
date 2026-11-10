from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.auth import auth_bp
app = Flask(__name__)
CORS(app)

init_db()

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
app.register_blueprint(public_pay_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(port=5000, debug=True)