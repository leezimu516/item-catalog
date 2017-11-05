from flask import Flask, render_template
from flask import request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Course, Student, User

# this login_session works as dictionary, sicne we have already
# use session for database
from flask import session as login_session
import random
import string
# google oauth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "item catalog app"

# connect to database
engine = create_engine("sqlite:///course_student_user.db")
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


# create anti forgery state token
@app.route("/login")
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session["state"] = state
    return render_template("login.html", STATE=state)


# create google login
@app.route("/gconnect", methods=["POST"])
def gconnect():
    # validate the state token
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    # collect one-time code
    code = request.data

    try:
        # upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Fail toupgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # if there is an error in the access toke info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is used for the intented user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("token's user id doesn't match given user id"), 401)
        response.headers['Content-Type'] = 'application/josn'
        return response
    # verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if not, create a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src='
    output += login_session['picture']
    output += (
        '"style = \
        "width: 300px; \
        height: 300px; \
        border-radius: 150px; \
        -webkit-border-radius: 150px; \
        -moz-border-radius: 150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# GOOGLE DISCONNECT
# revoke a current user's token and reset their login session
@app.route("/gdisconnect")
def gdisconnect():
    access_token = login_session["access_token"]
    # only disconnect a connected user
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.', 401))
        response.headers['Content-Type'] = 'application/json'
        return response

    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    # execute HTTP GET request to revoke current user
    url = (
            'https://accounts.google.com/o/oauth2/revoke?token=%s'
            % login_session['access_token'])
    h = httplib2.Http()
    # store response
    result = h.request(url, 'GET')[0]
    print 'result is'
    print result

    if result['status'] == '200':
        # reset user's login_session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        print response
        flash("You are logged out!")
        return redirect(url_for("showCourse"))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        print response
        flash("You were not logged in")
        return redirect(url_for('showCourse'))


# JSON APIs to view course information
@app.route("/course/JSON")
def courseJSON():
    courses = session.query(Course).all()
    return jsonify(courses=[c.serialize for c in courses])


@app.route("/course/<int:course_id>/student/JSON")
def courseStudentJSON(course_id):
    # course = session.query(Course).filter_by(id=course_id).one()
    students = session.query(Student).filter_by(course_id=course_id).all()
    return jsonify(students=[s.serialize for s in students])


@app.route("/course/<int:course_id>/student/<int:student_id>/JSON")
def studentJSON(course_id, student_id):
    student = session.query(Student).filter_by(id=student_id).one()
    return jsonify(student=student.serialize)


# show all the courses
@app.route("/")
@app.route("/course")
def showCourse():
    # return "all the courses"
    courses = session.query(Course).order_by(asc(Course.name))
    if "username" in login_session:
        return render_template("course.html", courses=courses)
    else:
        return render_template("publicCourse.html", courses=courses)


# create new course
@app.route("/course/new", methods=["POST", 'GET'])
@login_required
def newCourse():
    # login to modify
    # if 'username' not in login_session:
    #     return redirect('/login')

    if request.method == "POST":
        newCourse = Course(
            name=request.form["name"], user_id=login_session['user_id'])
        session.add(newCourse)
        session.commit()
        flash("new course created!")
        return redirect(url_for('showCourse'))
    else:
        return render_template("new_course.html")


# edit course
@app.route("/course/<int:course_id>/edit", methods=["POST", 'GET'])
def editCourse(course_id):
    # login to modify
    # if 'username' not in login_session:
    #     return redirect('/login')

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
        return render_template("edit_course.html", course=editedCourse)


# delete the course
@app.route("/course/<int:course_id>/delete", methods=["POST", 'GET'])
@login_required
def deleteCourse(course_id):
    # login to modify
    # if 'username' not in login_session:
    #     return redirect('/login')

    deleteCourse = session.query(Course).filter_by(id=course_id).one()
    if request.method == "POST":
        session.delete(deleteCourse)
        session.commit()
        flash("course has been deleted")
        return redirect(url_for('showCourse'))
    else:
        return render_template("delete_course.html", course=deleteCourse)


# show a course students
@app.route("/course/<int:course_id>")
@app.route("/course/<int:course_id>/student")
def showStudent(course_id):
    # return "students for course: %s" %course_id
    course = session.query(Course).filter_by(id=course_id).one()
    students = session.query(Student).filter_by(
        course_id=course_id).order_by(asc(Student.name))
    creator = getUserInfo(course.user_id)
    if "username" in login_session and login_session["user_id"] == creator.id:
        return render_template(
            "student.html",
            students=students, course=course, creator=creator)
    else:
        return render_template(
            "publicStudent.html",
            students=students, course=course, creator=creator)


# create student for course
@app.route("/course/<int:course_id>/student/new", methods=["POST", 'GET'])
@login_required
def createStudent(course_id):
    # login to modify
    # if 'username' not in login_session:
    #     return redirect('/login')

    course = session.query(Course).filter_by(id=course_id).one()
    if request.method == "POST":
        newStudent = Student(
            name=request.form.get("name", None),
            score=request.form.get("score", None),
            phone=request.form.get("phone", None),
            course_id=course_id,
            user_id=course.user_id)
        session.add(newStudent)
        session.commit()
        flash("new student created!")
        return redirect(url_for('showStudent', course_id=course_id))
    else:
        return render_template("new_student.html", course_id=course_id)


# edit student
@app.route(
    "/course/<int:course_id>/student/<int:student_id>/edit",
    methods=["POST", 'GET'])
@login_required
def editStudent(course_id, student_id):
    # login to modify
    # if 'username' not in login_session:
    #     return redirect('/login')

    editedStudent = session.query(Student).filter_by(id=student_id).one()
    if request.method == "POST":
        if request.form.get("name", None):
            editedStudent.name = request.form.get("name", None)
            print "name edit"

        if request.form.get("score", None):
            editedStudent.score = request.form.get("score", None)
            print "score edit"
        if request.form.get("phone", None):
            editedStudent.phone = request.form.get("phone", None)
            print "phone edit"
        session.add(editedStudent)
        session.commit()
        flash("student has been edited")
        return redirect(url_for('showStudent', course_id=course_id))
    else:
        return render_template(
            "edit_student.html",
            student=editedStudent, student_id=student_id, course_id=course_id)


# delete student
@app.route(
    "/course/<int:course_id>/student/<int:student_id>/delete",
    methods=["POST", 'GET'])
@login_required
def deleteStudent(course_id, student_id):
    # login to modify
    # if 'username' not in login_session:
    #     return redirect('/login')

    deleteStudent = session.query(Student).filter_by(id=student_id).one()
    if request.method == "POST":
        session.delete(deleteStudent)
        session.commit()
        flash("student has been deleted")
        return redirect(url_for('showStudent', course_id=course_id))
    else:
        return render_template(
            "delete_student.html", student=deleteStudent, course_id=course_id)


# User helper functions
def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        # temp hack use first instead of one
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
