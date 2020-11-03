"""Blueprint module for API version 1."""
from flask import Blueprint

api_views = Blueprint('api_views', __name__, url_prefix='/api/v1/')

from .auth.spotify import *
from .auth.users import *
from .spotify_crud import *
from .users_crud import *
