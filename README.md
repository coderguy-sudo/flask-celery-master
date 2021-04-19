## Getting Started
### Running the Application


First of all create virtual environment and activate it as follows:
```
$ mkdir environments
$ cd environments
$ virtualenv -p python3 flask_demo
$ source flask_demo/bin/activate
```

Install the requirements
```
Navigate back to the project directory and run the following command
$ pip install -r requirements.txt
```

Db Configure
```
Navigate back to the project directory and run the following command
$ flask db init
$ flask db migrate -m "recipient_information table"
$ flask db upgrade
```

Start the Flask app
```
$ python app.py
```

Start the Celery Cluster in a separate terminal window
```
$ celery beat -A app.client --loglevel=info
Than on new terminal window
$ celery worker -A app.client --loglevel=info
```

Navigate to http://localhost:5000 and schedule an email with a message

Check the recipient email inbox for the scheduled message after the time has ellapsed

