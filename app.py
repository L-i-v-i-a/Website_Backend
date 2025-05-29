from flask import Flask
from flask_mail import Mail
from flask_cors import CORS
from routes.about import about_bp
from routes.news import news_bp
from routes.contact import contact_bp
from routes.departments import departments_bp
from routes.subscribe import subscribe_bp
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app)

@app.route("/")
def index():
    return "Welcome to the Faculty Website Backend"

# Register blueprints
app.register_blueprint(about_bp, url_prefix='/about')
app.register_blueprint(news_bp, url_prefix='/news')
app.register_blueprint(contact_bp, url_prefix='/contact')
app.register_blueprint(departments_bp, url_prefix='/departments')
app.register_blueprint(subscribe_bp, url_prefix='/subscribe')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
