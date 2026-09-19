from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    current_skill_level = Column(String(50))
    
    # Relationship to progressions
    progressions = relationship("SavedProgression", back_populates="user")

class SavedProgression(Base):
    __tablename__ = 'saved_progressions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    root_note = Column(String(10), nullable=False)
    movement_label = Column(String(100), nullable=False)
    
    # JSON column is perfect for storing our [(Chord, Numeral), ...] tuples
    chord_sequence = Column(JSON, nullable=False) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship back to user
    user = relationship("User", back_populates="progressions")