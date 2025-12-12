from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from base.models import BaseModel


class Post(BaseModel):
    __tablename__ = "posts"
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), index=True)
    content = Column(Text)
    author = relationship("User", back_populates="posts")
