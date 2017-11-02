from flask import Flask, render_template, request, redirect, url_for, flash, jsonify 
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Course, Student

# #Fake courses
# course = {'name': 'Math', 'id': '1'}

# courses = [{'name': 'Math', 'id': '1'}, {'name':'English', 'id':'2'},{'name':'Taichi', 'id':'3'}]


# #Fake students
# students = [ 
#     {'name':'student1', 'description':'dummy description1', 'id':'1'}, 
#     {'name':'student2', 'description':'dummy description2', 'id':'2'},
#     {'name':'student3', 'description':'dummy description3', 'id':'3'},
#     {'name':'student4', 'description':'dummy description4', 'id':'4'},
#     {'name':'student5', 'description':'dummy description5', 'id':'5'} ]
# student =  {'name':'student1', 'description':'dummy description1', 'id':'1'}

# connect to database
engine = create_engine("sqlite:///course_student.db")
Base.metadata.bind = engine

DBsession = sessionmaker(bind = engine)
session = DBsession()

# JSON APIs to view course information
@app.route("/course/JSON")
def courseJSON():
    courses = session.query(Course).all()
    return jsonify(courses = [c.serialize for c in courses])

@app.route("/course/<int:course_id>/student/JSON")
def courseStudentJSON(course_id):
    # course = session.query(Course).filter_by(id=course_id).one()
    students = session.query(Student).filter_by(course_id = course_id).all()
    return jsonify(students = [s.serialize for s in students])

@app.route("/course/<int:course_id>/student/<int:student_id>/JSON")
def studentJSON(course_id, student_id):
    student = session.query(Student).filter_by(id = student_id).one()
    return jsonify(student = student.serialize)



# show all the courses
@app.route("/")
@app.route("/course")
def showCourse():
    # return "all the courses"
    courses = session.query(Course).order_by(asc(Course.name))
    return render_template("course.html", courses = courses)

# create new course
@app.route("/course/new", methods=["POST", 'GET'])
def newCourse():
    # return "add new course"
    if request.method == "POST":
        newCourse = Course(name = request.form["name"])
        session.add(newCourse)
        session.commit()
        flash("new course created!")
        return redirect(url_for('showCourse'))
    else:
        return render_template("new_course.html")

# edit course
@app.route("/course/<int:course_id>/edit", methods=["POST", 'GET'])
def editCourse(course_id):
    # return "edit the course %s" %course_id
    editedCourse = session.query(Course).filter_by(id=course_id).one()
    if request.method == "POST":       
        if request.form["name"]:
            editedCourse.name = request.form["name"]
            session.add(editedCourse)
            session.commit()
            flash("course has been edited")  
            return redirect(url_for('showCourse')) 
        else:
            flash("input course is null")       
    else:       
        return render_template("edit_course.html",course=editedCourse)

# delete the course
@app.route("/course/<int:course_id>/delete", methods=["POST", 'GET'])
def deleteCourse(course_id):
    # return "delete course %s" %course_id
    deleteCourse = session.query(Course).filter_by(id=course_id).one()
    if request.method == "POST":
        session.delete(deleteCourse)
        session.commit()
        flash("course has been deleted")  
        return redirect(url_for('showCourse')) 
    else:
        return render_template("delete_course.html", course = deleteCourse)

# show a course students
@app.route("/course/<int:course_id>") 
@app.route("/course/<int:course_id>/student") 
def showStudent(course_id):
    # return "students for course: %s" %course_id
    course = session.query(Course).filter_by(id=course_id).one()
    students = session.query(Student).filter_by(course_id=course_id).order_by(asc(Student.name))
    return render_template("student.html", students = students, course = course)

# create student for course
@app.route("/course/<int:course_id>/student/new", methods=["POST", 'GET'])
def createStudent(course_id):
    # return "add students for course: %s" %course_id
    if request.method == "POST":
        newStudent = Student(
            name = request.form["name"],
            score = 'A',
            phone = '514-111-1111',
            course_id = course_id)
        session.add(newStudent)
        session.commit()
        flash("new student created!")
        return redirect(url_for('showStudent', course_id=course_id))
    else:
        return render_template("new_student.html", course_id=course_id)


# edit student
@app.route("/course/<int:course_id>/student/<int:student_id>/edit", methods=["POST", 'GET'])
def editStudent(course_id, student_id):
    # return "update student %s for course %s" %(student_id, course_id)
    editedStudent = session.query(Student).filter_by(id=student_id).one()
    if request.method == "POST":
        if request.form["name"]:
            editedStudent.name = request.form["name"]
            session.add(editedStudent)
            flash("student has been edited")
            return redirect(url_for('showStudent', course_id=course_id))
    else:
        return render_template("edit_student.html", student_id=student_id, course_id=course_id)
    


# delete student
@app.route("/course/<int:course_id>/student/<int:student_id>/delete", methods=["POST", 'GET'])
def deleteStudent(course_id, student_id):
    # return "delete student %s for course %s" %(student_id, course_id)
    deleteStudent = session.query(Student).filter_by(id=student_id).one()
    if request.method == "POST":
        session.delete(deleteStudent)
        session.commit()
        flash("student has been deleted")  
        return redirect(url_for('showStudent', course_id=course_id))
    else:
        return render_template("delete_student.html", student_id=student_id, course_id=course_id)






if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)