import os
from datetime import timedelta

from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'abcdefg23213conovo'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # Flask-Mail
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email'
    MAIL_PASSWORD = 'your_password'

    CELERYBEAT_SCHEDULE = {
        'send-mail': {
            'task': 'send_mail',
            'schedule': timedelta(seconds=15)
        },

        'recipient-information-email-sent-to-false': {
            'task': 'recipient_information_email_sent_to_false',
            'schedule': crontab(hour=23, minute=59),
        },
    }
