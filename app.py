import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

from models import db, User, FinancialRecord
from engine import analyze_finances

app = Flask(__name__)
app.config['SECRET_KEY'] = 'financial_advice_tool_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validation
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('signup'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # Create a new record from form data
        try:
            record = FinancialRecord(
                user_id=current_user.id,
                monthly_income=float(request.form.get('monthly_income', 0)),
                total_savings=float(request.form.get('total_savings', 0)),
                monthly_savings=float(request.form.get('monthly_savings', 0)),
                total_debt=float(request.form.get('total_debt', 0)),
                housing_rent=float(request.form.get('housing_rent', 0)),
                food_dining=float(request.form.get('food_dining', 0)),
                transportation=float(request.form.get('transportation', 0)),
                utilities=float(request.form.get('utilities', 0)),
                entertainment=float(request.form.get('entertainment', 0)),
                miscellaneous=float(request.form.get('miscellaneous', 0))
            )
            db.session.add(record)
            db.session.commit()
            flash('Financial data saved successfully!', 'success')
            return redirect(url_for('analyze', record_id=record.id))
        except ValueError:
            flash('Invalid input. Please enter numbers for all fields.', 'danger')
            
    # Fetch user's latest record to pre-fill the form if available
    latest_record = FinancialRecord.query.filter_by(user_id=current_user.id).order_by(FinancialRecord.date_created.desc()).first()
    return render_template('dashboard.html', record=latest_record)

@app.route('/analyze/<int:record_id>')
@login_required
def analyze(record_id):
    record = FinancialRecord.query.get_or_404(record_id)
    if record.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
        
    analysis_results = analyze_finances(record)
    return render_template('results.html', results=analysis_results, record=record)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)