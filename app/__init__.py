from flask import Flask
from flask_login import LoginManager
from config import Config
import os
from autotools.secrets import set_secrets
set_secrets()

from autotools.db import Database, DatabaseInstances, HostSource, set_credentials

from dynaconf import settings

os.environ["STAGE"] = "LOCALHOST"


# Set up credentials for Cloud SQL connections
db_credentials = {
    DatabaseInstances.AUTO360: {'user': settings.CLIENT_CLOUD_SQL_USER,
                                'password': settings.CLIENT_CLOUD_SQL_PSWD},
}
if os.environ.get("STAGE") == "LOCALHOST":
    db_credentials[DatabaseInstances.AUTO360]['port'] = settings.TRANSACTIONS_DB_PORT
    set_credentials(db_credentials, HostSource.LOCALHOST)
else:
    set_credentials(db_credentials, HostSource.TCP_SOCKET)


app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'

from app import routes