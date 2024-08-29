from datetime import datetime
import enum
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, Text, DateTime, ForeignKey, Boolean, Date, Enum
from database import Base

class Child(Base):
    __tablename__ = 'child'

    id = Column(String(255), primary_key=True)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    parent_phone_number = Column(String(255), nullable=True)
    parent_id = Column(String(255), ForeignKey('parent.id'))
    parent = relationship('Parent', back_populates='children')
    txts = relationship("Txt", back_populates="child")
    reports = relationship("Report", back_populates="child")


class Parent(Base):
    __tablename__ = 'parent'

    id = Column(String(255), primary_key=True)
    password = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    phone_number = Column(String(255),unique=True, nullable=True)
    children = relationship('Child', back_populates='parent')

class Report(Base):
    __tablename__ = "report"

    report_date = Column(Date, primary_key=True, nullable=False)
    child_id = Column(String(255), ForeignKey("child.id"), primary_key=True, nullable=False)
    report = Column(Text)
    abuse_count = Column(Integer)
    report_type = Column(Enum('1', '2', '3'), primary_key=True, nullable=False)#
    child = relationship("Child", back_populates="reports")

class Txt(Base):
    __tablename__ = 'txt'

    date = Column(DateTime, primary_key=True, default=datetime.utcnow)
    report_text = Column(String(255), nullable=False)
    child_id = Column(String(255), ForeignKey('child.id'))
    child = relationship("Child", back_populates="txts")

Child.txts = relationship("Txt", back_populates="child")

class FriendStatus(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'

class Friend(Base):
    __tablename__ = 'friend'

    child_id = Column(String(255), ForeignKey('child.id'))
    friend_id = Column(String(255), ForeignKey('child.id'))
    create_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(FriendStatus), default=FriendStatus.pending)

    __table_args__ = (
        PrimaryKeyConstraint('child_id', 'friend_id'),
    )
    child = relationship("Child", foreign_keys=[child_id])
    friend = relationship("Child", foreign_keys=[friend_id])
