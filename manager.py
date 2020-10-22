"""
Run application.

"""
import os
from config import config
from rythmize import create_app, db
from rythmize.models.user import User 
from rythmize.models.keys import YoutubeJsonWebToken, SpotifyJsonWebToken
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from dotenv import find_dotenv, load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise Exception('No env settings found.')

env_object = os.getenv('CONFIG_ENV')
if  env_object not in config.keys():
    raise Exception("CONFIG_ENV can be either Production or Development).")

app = create_app(config[env_object])
manager = Manager(app)
migrate = Migrate(app, db)

# to use in shell
def make_shell_context():
    return dict(app=app, db=db, User=User,
                youtube=YoutubeJsonWebToken, Spotify=SpotifyJsonWebToken)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
