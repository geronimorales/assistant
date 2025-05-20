from assistant.models.base import Base
from assistant.models.thread import Thread
from assistant.models.user_config import UserConfig
from assistant.models.relationships import *  # This will set up the relationships

__all__ = ["Base", "Thread", "UserConfig"]
