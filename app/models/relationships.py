from sqlalchemy.orm import relationship

from app.models.thread import Thread
from app.models.user_config import UserConfig

# Define relationships after both models are defined
UserConfig.threads = relationship("Thread", back_populates="user_config", lazy="dynamic")
Thread.user_config = relationship("UserConfig", back_populates="threads", lazy="select") 