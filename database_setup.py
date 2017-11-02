from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "id" : self.id,
            "name" : self.name,
        }


class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    score = Column(String(5))
    phone = Column(String(15))
    course_id = Column(Integer, ForeignKey('course.id'))
    course = relationship(Course)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "id" : self.id,
            "name" : self.name,
            "score": self.score,
            "phone": self.phone,
        }


engine = create_engine('sqlite:///course_student.db')

Base.metadata.create_all(engine)