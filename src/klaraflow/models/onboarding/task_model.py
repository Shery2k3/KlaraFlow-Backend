from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class OnboardingTask(Base):
    __tablename__ = 'onboarding_tasks'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("onboarding_sessions.id"), nullable=False)
    todo_item_id = Column(Integer, ForeignKey("todo_items.id"), nullable=True)  # Optional reference to template todo
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)

    session = relationship("OnboardingSession", back_populates="tasks")
    todo_item = relationship("TodoItem", back_populates="session_todos")