from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database import Base

class Submission(Base):

    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(Text)

    concept = Column(Text)

    questions = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
