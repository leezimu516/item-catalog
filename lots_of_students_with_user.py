from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Course, Student, User
# generate random phone number
from random_phone import gen_phone

engine = create_engine("sqlite:///course_student_user.db")
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
session = DBSession()

# create dummy user
user1 = User(name="dummy user", email="test@test.com",
             picture="https://images.pexels.com/photos/104827/" \
             + "cat-pet-animal-domestic-104827.jpeg" \
             + "?w=126&h=75&auto=compress&cs=tinysrgb")
session.add(user1)
session.commit()

# student for Math
course1 = Course(name = "Math", user = user1)

session.add(course1)
session.commit()

student1 = Student(name = "Adams", score = "A+", phone = "%s" %gen_phone(), course = course1, user = user1)
session.add(student1)
session.commit()

student2 = Student(name = "Baker", score = "B+", phone = "%s" %gen_phone(), course = course1, user = user1)
session.add(student2)
session.commit()

student3 = Student(name = "Usman", score = "A-", phone = "%s" %gen_phone(), course = course1, user = user1)
session.add(student3)
session.commit()


# student for Chinese
course2 = Course(name = "Chinese", user = user1)

session.add(course2)
session.commit()

student1 = Student(name = "Trott", score = "C+", phone = "%s" %gen_phone(), course = course2, user = user1)
session.add(student1)
session.commit()

student2 = Student(name = "Patel", score = "B-", phone = "%s" %gen_phone(), course = course2, user = user1)
session.add(student2)
session.commit()

student3 = Student(name = "Yakub", score = "B-", phone = "%s" %gen_phone(), course = course2, user = user1)
session.add(student3)
session.commit()

# student for Taichi
course3 = Course(name = "Taichi", user = user1)

session.add(course2)
session.commit()

student1 = Student(name = "Clark", score = "B+", phone = "%s" %gen_phone(), course = course3, user = user1)
session.add(student1)
session.commit()

student2 = Student(name = "Ochoa", score = "A", phone = "%s" %gen_phone(), course = course3, user = user1)
session.add(student2)
session.commit()

student3 = Student(name = "Smith", score = "A", phone = "%s" %gen_phone(), course = course3, user = user1)
session.add(student3)
session.commit()

print "added students"

    
