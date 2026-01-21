import os
import requests
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tajne-heslo-123'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class NewsForm(FlaskForm):
    title = StringField('Titulek', validators=[DataRequired()])
    content = TextAreaField('Obsah', validators=[DataRequired()])
    submit = SubmitField('Odeslat')

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    try:
        r = requests.get('https://api.open-meteo.com/v1/forecast?latitude=49.93&longitude=17.90&current_weather=true')
        weather = r.json().get('current_weather') if r.status_code == 200 else None
    except: pass
    
    form = NewsForm()
    if form.validate_on_submit():
        msg = News(title=form.title.data, content=form.content.data)
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for('index'))
    
    news = News.query.order_by(News.id.desc()).all()
    return render_template('index.html', weather=weather, form=form, news=news)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)