from sqlalchemy import Column, DateTime, ForeignKey, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Action(Base):
    """Represents an action in a room of the Cohort."""

    __tablename__ = "actions"

    id = Column(Integer, Sequence("action_id_seq"), primary_key=True)
    member_id = Column(Integer, ForeignKey("members.card_id"))
    action_type_id = Column(Integer, nullable=False)  # 0 = enter, 1 = exit
    room_id = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False)
    member = relationship("Member", back_populates="actions")

    def __repr__(self) -> str:
        return f"<Action(action_type_id={self.action_type_id}, member_id={self.member_id}, time={self.time})>"


class Member(Base):
    """Represents a Member of the Cohort."""

    __tablename__ = "members"

    card_id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    registration_dt = Column(DateTime, nullable=False)
    room_id = Column(Integer, nullable=True)
    actions = relationship("Action", order_by=Action.id, back_populates="member")

    def __repr__(self) -> str:
        return f"<Member(first_name={self.first_name}, last_name={self.last_name})>"
