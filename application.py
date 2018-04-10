
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import time

from sql import SQL
from helpers import *



# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///moocman.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html");


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "login":
            # ensure username was submitted
            if not request.form.get("username"):
                flash("ERROR: You must provide a username to login", "alert-danger")
                return render_template("login.html", flash = flash)

            # ensure password was submitted
            elif not request.form.get("password"):
                flash("ERROR: You must provide a password to login", "alert-danger")
                return render_template("login.html", flash = flash)

            # query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

            # ensure username exists and password is correct
            if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
                flash("ERROR: Invalid username and/or password", "alert-danger")
                return render_template("login.html", flash = flash)

            # remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # redirect user to home page
            return redirect(url_for("profile"))

        elif action == "register":
            if not request.form.get("username"):
                flash("ERROR: You must provide a username: Account not registered, please try again", "alert-danger")
                return render_template("login.html", flash = flash)

            #ensure that password and the re entered pass word both have content
            elif not request.form.get("password") or not request.form.get("password2"):
                flash("ERROR: You must provide a new password: Account not registered, please try again", "alert-danger")
                return redirect(url_for("login"))

            #ensure that both passwords match
            elif request.form.get("password") != request.form.get("password2"):
                flash("ERROR: Passwords do not match: Account not registered, please try again", "alert-danger")
                return render_template("login.html", flash = flash)

            #check to ensure username does not exist
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
            if len(rows) > 0:
                flash("ERROR: Passwords do not match: Account not registered, please try again", "alert-danger")
                return render_template("login.html", flash = flash)
            else:
                #hash the password and insert the username and password into the DB
                hash = pwd_context.encrypt(request.form.get("password"))
                db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=hash)
            flash("Account registered, please login", "alert-success")
            return render_template("login.html", flash = flash)
        # else if user reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("login.html")

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/my_courses", methods=["GET", "POST"])
@login_required
def my_courses():
    #query db by so we work with user data
    userinfo =  db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session["user_id"])
    users_name = userinfo[0]["username"]
    coursesdb = db.execute("SELECT * FROM courses WHERE users_name = :users_name AND complete = 'false' ORDER BY startDate", users_name = users_name)
    courses = []

    #build dict of each row in the portfolio to send to index so user can see their assets
    for row in coursesdb:
        course = {}
        course["id"] = row["id"]
        course["name"] = row["name"]
        course["site"] = row["site"]
        course["school"] = row["school"]
        course["progress"] = row["progress"]
        course["grade"] = row["grade"]
        course["notes"] = row["notes"]
        course["link1"] = row["link1"]
        course["link2"] = row["link2"]
        course["link3"] = row["link3"]
        course["link4"] = row["link4"]
        course["link5"] = row["link5"]
        course["desc_link1"] = row["desc_link1"]
        course["desc_link2"] = row["desc_link2"]
        course["desc_link3"] = row["desc_link3"]
        course["desc_link4"] = row["desc_link4"]
        course["desc_link5"] = row["desc_link5"]
        course["startDate"] = row["startDate"]
        courses.append(course)

    if request.method == 'POST':
        action = request.form.get("action")
        if action == "delete":
            db.execute("DELETE FROM courses WHERE name = :name AND users_name = :users_name", name = request.form.get("name"), users_name = users_name)
        elif action == "complete":
            db.execute("UPDATE courses SET complete = 'true', completeDate = :date WHERE name = :name AND users_name = :users_name", date = time.strftime("%x"), name = request.form.get("name"), users_name = users_name)
        elif action == "edit":
            name = request.form.get("name")
            site = request.form.get("site")
            progress = request.form.get("progress")
            grade = request.form.get("grade")
            school = request.form.get("school")
            l1 = request.form.get("link1")
            l2 = request.form.get("link2")
            l3 = request.form.get("link3")
            l4 = request.form.get("link4")
            l5 = request.form.get("link5")
            d1 = request.form.get("desc_link1")
            d2 = request.form.get("desc_link2")
            d3 = request.form.get("desc_link3")
            d4 = request.form.get("desc_link4")
            d5 = request.form.get("desc_link5")
            notes = request.form.get("notes")
            startDate = request.form.get("startDate")

            db.execute("UPDATE courses SET name = :name, progress = :progress, site = :site, grade = :grade, school = :school,"\
            "notes = :notes, startDate = :startDate, link1 = :link1, link2 = :link2, link3 = :link3, link4 = :link4, link5 = :link5,"\
            "desc_link1 = :desc_link1, desc_link2 = :desc_link2, desc_link3 = :desc_link3, desc_link4 = :desc_link4, desc_link5 = :desc_link5 "\
            "WHERE name = :name AND users_name = :users_name",\
            name = name, site = site, progress = progress, grade = grade, school = school, link1 = l1,\
            link2 = l2, link3 = l3, link4 = l4, link5 = l5, desc_link1 = d1, desc_link2 = d2,\
            desc_link3 = d3, desc_link4 = d4, desc_link5 = d5, notes = notes, startDate = startDate, users_name = users_name)
            flash("Course Updated!", "alert-success")
            return redirect(url_for("my_courses"))

        return redirect(url_for("my_courses"))

    return render_template("my_courses.html", courses = courses, totalcourses = len(courses))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    userinfo =  db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session["user_id"])
    users_name = userinfo[0]["username"]
    active = db.execute("SELECT * FROM courses WHERE users_name = :users_name AND complete = 'false'", users_name = users_name)
    completed = db.execute("SELECT * FROM courses WHERE users_name = :users_name AND complete = 'true'", users_name = users_name)

    ttlactive = len(active)
    ttlcompleted = len(completed)

    user = {}
    user["username"] = users_name
    user["firstName"] = userinfo[0]["firstName"]
    user["lastName"] = userinfo[0]["lastName"]
    user["title"] = userinfo[0]["title"]
    user["quote"] = userinfo[0]["quote"]
    user["active"] = ttlactive
    user["completed"] = ttlcompleted

    a_courses = []
    c_courses = []

    for row in active:
        course = {}
        course["name"] = row["name"]
        a_courses.append(course)

    for row in completed:
        course = {}
        course["name"] = row["name"]
        c_courses.append(course)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "profedit":
            fname = request.form.get("firstName")
            lname = request.form.get("lastName")
            title = request.form.get("title")
            quote = request.form.get("quote")

            db.execute("UPDATE users SET firstName = :fname, lastName = :lname, title = :title, quote = :quote "\
            "WHERE username = :users_name", fname = fname, lname = lname, title = title, quote = quote, users_name = users_name)

            flash("Profile Updated!", "alert-success")
            return redirect(url_for("profile"))

        elif action == "passedit":
            rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session["user_id"])

            #ensure user enters current valid password
            if not pwd_context.verify(request.form.get("curr_password"), rows[0]["hash"]):
                flash("ERROR: Current password is incorrect: Password not change, please try again", "alert-danger")
                return redirect(url_for("profile"))

            #ensure the user has entered a value for both new password fields
            elif not request.form.get("newpass1") or not request.form.get("newpass2"):
                flash("ERROR: You must provide a new password: Password not change, please try again", "alert-danger")
                return redirect(url_for("profile"))

            #ensure that both new passwords match
            elif request.form.get("newpass1") != request.form.get("newpass2"):
                flash("ERROR: New Passwords do not match: Password not change, please try again", "alert-danger")
                return redirect(url_for("profile"))

            #hash the password and insert the username and password into the DB
            hash = pwd_context.encrypt(request.form.get("newpass1"))
            db.execute("UPDATE users SET hash = :hash", hash=hash)
            flash("Password has been updated!", "alert-success")
            return redirect(url_for("profile"))

    return render_template("profile.html",user = user, a_courses = a_courses, c_courses = c_courses)


@app.route("/completed_courses", methods=["GET", "POST"])
@login_required
def completed_courses():
    #query db by so we work with user data
    userinfo =  db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session["user_id"])
    users_name = userinfo[0]["username"]
    coursesdb = db.execute("SELECT * FROM courses WHERE users_name = :users_name AND complete = 'true'", users_name = users_name)
    courses = []

    #build dict of each row in the portfolio to send to index so user can see their assets
    for row in coursesdb:
        course = {}
        course["id"] = row["id"]
        course["name"] = row["name"]
        course["school"] = row["school"]
        course["progress"] = row["progress"]
        course["grade"] = row["grade"]
        course["notes"] = row["notes"]
        course["link1"] = row["link1"]
        course["link2"] = row["link2"]
        course["link3"] = row["link3"]
        course["link4"] = row["link4"]
        course["link5"] = row["link5"]
        course["desc_link1"] = row["desc_link1"]
        course["desc_link2"] = row["desc_link2"]
        course["desc_link3"] = row["desc_link3"]
        course["desc_link4"] = row["desc_link4"]
        course["desc_link5"] = row["desc_link5"]
        course["startDate"] = row["startDate"]
        course["completeDate"] = row["completeDate"]
        course["site"] = row ["site"]
        courses.append(course)

        if request.method == "POST":
            name = request.form.get("name")
            site = request.form.get("site")
            progress = request.form.get("progress")
            grade = request.form.get("grade")
            school = request.form.get("school")
            l1 = request.form.get("link1")
            l2 = request.form.get("link2")
            l3 = request.form.get("link3")
            l4 = request.form.get("link4")
            l5 = request.form.get("link5")
            d1 = request.form.get("desc_link1")
            d2 = request.form.get("desc_link2")
            d3 = request.form.get("desc_link3")
            d4 = request.form.get("desc_link4")
            d5 = request.form.get("desc_link5")
            notes = request.form.get("notes")
            startDate = request.form.get("startDate")
            completeDate = request.form.get("completeDate")

            db.execute("UPDATE courses SET name = :name, progress = :progress, site = :site, grade = :grade, school = :school,"\
            "notes = :notes, startDate = :startDate, link1 = :link1, link2 = :link2, link3 = :link3, link4 = :link4, link5 = :link5,"\
            "desc_link1 = :desc_link1, desc_link2 = :desc_link2, desc_link3 = :desc_link3, desc_link4 = :desc_link4, desc_link5 = :desc_link5,"\
            "completeDate = :completeDate WHERE name = :name AND users_name = :users_name",\
            name = name, site = site, progress = progress, grade = grade, school = school, link1 = l1,\
            link2 = l2, link3 = l3, link4 = l4, link5 = l5, desc_link1 = d1, desc_link2 = d2,\
            desc_link3 = d3, desc_link4 = d4, desc_link5 = d5, notes = notes, startDate = startDate,\
            completeDate = completeDate, users_name = users_name)
            flash("Course Updated!", "alert-success")
            return redirect(url_for("completed_courses"))
    return render_template("completed_courses.html", courses = courses, totalcourses = len(courses) )

@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    userinfo =  db.execute("SELECT * FROM users WHERE id = :uid", uid = session["user_id"])
    users_name = userinfo[0]["username"]

    entriesdb = db.execute("SELECT * FROM journal WHERE users_name = :users_name", users_name = users_name)
    journal = []
    for row in entriesdb:
        entry = {}
        entry["id"] = row["id"]
        entry["date"] = row["date"]
        entry["course"] = row["course"]
        entry["notes"] = row["notes"]
        entry["hours"] = row["hours"]
        journal.append(entry)

    if request.method == "POST":
        action = request.form.get("action")

        jid = request.form.get("id")
        jdate = request.form.get("date")
        course = request.form.get("course")
        notes = request.form.get("notes")
        hours = request.form.get("hours")

        if action == "new":
            db.execute("INSERT INTO journal (date, course, notes, users_name, hours) "\
            "VALUES(:date, :course, :notes, :users_name, :hours)", date = time.strftime("%x"),\
            users_name = users_name, course = course, notes = notes, hours = hours)
            flash("Journal Entry Created", "alert-success")
            return redirect(url_for("journal"))
        elif action == "edit":
            db.execute("UPDATE journal SET date = :date, course = :course, hours = :hours, notes = :notes WHERE id = :jid", jid = jid, date = jdate, course = course, notes = notes, hours = hours)
            flash("Journal Entry Updated", "alert-success")
            return redirect(url_for("journal"))
        elif action == "delete":
            db.execute("DELETE FROM journal WHERE id = :id", id = jid)
            flash("Journal Entry Removed", "alert-success")
            return redirect(url_for("journal"))

    return render_template("journal.html", journal = journal)


@app.route("/add_course", methods=["GET", "POST"])
@login_required
def add_course():
    userinfo =  db.execute("SELECT * FROM users WHERE id = :uid", uid = session["user_id"])
    users_name = userinfo[0]["username"]

    if request.method == "POST":
        name = request.form.get("name")
        site = request.form.get("site")
        progress = request.form.get("progress")
        grade = request.form.get("grade")
        school = request.form.get("school")
        l1 = request.form.get("link1")
        l2 = request.form.get("link2")
        l3 = request.form.get("link3")
        l4 = request.form.get("link4")
        l5 = request.form.get("link5")
        d1 = request.form.get("desc_link1")
        d2 = request.form.get("desc_link2")
        d3 = request.form.get("desc_link3")
        d4 = request.form.get("desc_link4")
        d5 = request.form.get("desc_link5")
        notes = request.form.get("notes")

        course = {}
        course["name"] = name
        course["site"] = site
        course["progress"] = progress
        course["grade"] = grade
        course["school"] = school
        course["link1"] = l1
        course["link2"] = l2
        course["link3"] = l3
        course["link4"] = l4
        course["link5"] = l5
        course["desc_link1"] = d1
        course["desc_link2"] = d2
        course["desc_link3"] = d3
        course["desc_link4"] = d4
        course["desc_link5"] = d5
        course["notes"] = notes
    # ensure stock symbol was submitted
        if not request.form.get("name"):
            flash("You must provide a course name", "alert-danger")
            return render_template("add_course_onerror.html", course = course)

        rows = db.execute("SELECT * FROM courses WHERE name = :name AND users_name = :users_name", name = request.form.get("name"), users_name = users_name)
        if len(rows) > 0:
            flash("A course with that name already exists", "alert-danger")
            return render_template("add_course_onerror.html", course = course)

        else:
            db.execute("INSERT INTO courses (users_name, name, site, progress, grade, school, link1, link2, link3, link4, link5,"\
                "desc_link1, desc_link2, desc_link3, desc_link4, desc_link5, notes, startDate) VALUES(:users_name, :name, :site, :progress, :grade, :school,"\
                ":link1, :link2, :link3, :link4, :link5, :desc_link1, :desc_link2, :desc_link3, :desc_link4, :desc_link5, :notes, :startDate )",\
                users_name = users_name, name = name, site = site, progress = progress, grade = grade, school = school, link1 = l1,\
                link2 = l2, link3 = l3, link4 = l4, link5 = l5, desc_link1 = d1, desc_link2 = d2,\
                desc_link3 = d3, desc_link4 = d4, desc_link5 = d5, notes = notes, startDate = time.strftime("%x"))
            flash("Course Added!", "alert-success")
            return redirect(url_for("my_courses"))
    return render_template("add_course.html")
