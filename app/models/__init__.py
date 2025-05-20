from app.models.base import Base
from app.models.thread import Thread
from app.models.user_config import UserConfig
from app.models.relationships import *  # This will set up the relationships

__all__ = ["Base", "Thread", "UserConfig"]
