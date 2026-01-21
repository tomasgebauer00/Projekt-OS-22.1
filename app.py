import os
import requests
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tajne-heslo-123'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- DATABÁZOVÝ MODEL (Tabulka výdajů) ---
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)   # Za co (Pivo, Jídlo...)
    amount = db.Column(db.Integer, nullable=False)     # Kolik (Cena)
    payer = db.Column(db.String(50), nullable=False)   # Kdo (Jméno)

# --- FORMULÁŘ ---
class ExpenseForm(FlaskForm):
    payer = StringField('Kdo platil?', validators=[DataRequired()])
    item = StringField('Za co?', validators=[DataRequired()])
    amount = StringField('Kolik to stálo (Kč)?', validators=[DataRequired()])
    submit = SubmitField('Přidat do kasy')

# --- AUTOMATICKÉ VYTVOŘENÍ DATABÁZE ---
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    # 1. Počasí (necháme ho tam, je to fajn funkce)
    weather = None
    try:
        r = requests.get('https://api.open-meteo.com/v1/forecast?latitude=49.93&longitude=17.90&current_weather=true')
        weather = r.json().get('current_weather') if r.status_code == 200 else None
    except: pass
    
    # 2. Zpracování formuláře
    form = ExpenseForm()
    if form.validate_on_submit():
        try:
            # Převedeme text na číslo (int)
            cena = int(form.amount.data)
            # Uložíme do databáze
            novy_vydaj = Expense(item=form.item.data, amount=cena, payer=form.payer.data)
            db.session.add(novy_vydaj)
            db.session.commit()
            return redirect(url_for('index'))
        except ValueError:
            pass # Pokud uživatel nezadal číslo, nic se nestane
    
    # 3. Načtení dat a výpočet sumy
    expenses = Expense.query.order_by(Expense.id.desc()).all()
    total_spent = sum(e.amount for e in expenses)
    
    return render_template('index.html', weather=weather, form=form, expenses=expenses, total=total_spent)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)