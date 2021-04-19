from datetime import datetime

from flask import Flask, flash, render_template, request, redirect
from celery import Celery
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# configure celery client
client = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
client.conf.update(app.config)

# configure flask mail integration
mail = Mail(app)


class RecipientInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    msg = db.Column(db.String(520))
    time = db.Column(db.String(128))
    day = db.Column(db.String(128), nullable=True)
    email_sent = db.Column(db.Boolean, default=False)
    duration_unit = db.Column(db.String(128))


@client.task(name='send_mail')
def send_mail():
    recipient_information = RecipientInformation.query.filter_by(email_sent=False).all()
    for r_i in recipient_information:
        if r_i.duration_unit == 'daily':
            current_time = datetime.now().strftime("%I:%M %p")
            if current_time == r_i.time:
                msg = Message("Notify me!", sender="Notify me <no-reply@notifyme.com>", recipients=[r_i.email])
                msg.body = r_i.msg
                with app.app_context():
                    mail.send(msg)
                    r_i.email_sent = True
                    db.session.commit()
        elif r_i.duration_unit == 'weekly':
            if datetime.now().strftime('%A') == r_i.day:
                current_time = datetime.now().strftime("%I:%M %p")
                if current_time == r_i.time:
                    msg = Message("Notify me!", sender="Notify me <no-reply@notifyme.com>", recipients=[r_i.email])
                    msg.body = r_i.msg
                    with app.app_context():
                        mail.send(msg)
                        r_i.email_sent = True
                        db.session.commit()


@client.task(name='recipient_information_email_sent_to_false')
def recipient_information_email_sent_to_false():
    recipient_information = RecipientInformation.query.filter_by(email_sent=True).all()
    for r_i in recipient_information:
        r_i.email_sent = False
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        if request.form['email'] == '' or request.form['first_name'] == '' or request.form['last_name'] == '' \
                or request.form['message'] == '' or request.form['duration'] == '' \
                or request.form['duration_unit'] == '':
            flash(f"Please fill all the required fields")
            return redirect('.')

        duration = request.form['duration']
        duration_unit = request.form['duration_unit']

        if duration_unit == 'daily':
            r_i = RecipientInformation(email=request.form['email'],
                                       msg=request.form['message'],
                                       time=str(duration),
                                       duration_unit=request.form['duration_unit'])
            db.session.add(r_i)
            db.session.commit()
            flash(f"Email will be sent to {request.form['email']} at {request.form['duration']}.")

        elif duration_unit == 'weekly':
            r_i = RecipientInformation(email=request.form['email'],
                                       msg=request.form['message'],
                                       time=str(duration),
                                       day=datetime.now().strftime("%A"),
                                       duration_unit=request.form['duration_unit'])
            db.session.add(r_i)
            db.session.commit()
            flash(f"Email will be sent to {request.form['email']} at {request.form['duration']} "
                  f"on {datetime.now().strftime('%A')}.")
        
        return redirect('.')


if __name__ == '__main__':
    app.run(debug=True)
