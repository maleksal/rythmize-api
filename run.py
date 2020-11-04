import os
from config import config
from rythmize import create_app, db
from dotenv import find_dotenv, load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

env_object = os.getenv('CONFIG_ENV')
if  env_object not in config.keys():
    raise Exception("CONFIG_ENV can be either Production or Development).")

app = create_app(config[env_object])

