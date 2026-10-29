"""UHCMS - University Helpdesk & Complaint Management System (Flask + SQLite)."""
import os, sqlite3
from functools import wraps
from flask import (Flask, g, render_template, request, redirect, url_for,
                   session, flash, abort)
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
CATEGORIES = ["IT Services", "Classroom Equipment", "Laboratory",
              "Transport", "Hostel", "Other"]
STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
TEAM = [("Muhammad Zubair", "71773", "IT Department, 2nd Semester"),
        ("Zaheer Ahmed", "71168", "Project Team"),
        ("Naik Bakht", "70863", "Project Team"),
        ("Jasim Ali", "69724", "Project Team"),
        ("Abdul Ghafoor", "70963", "Project Team")]


def validate_complaint(data):
    """Return the list of required fields that are missing/empty."""
    return [f for f in ("title", "category", "description")
            if not (data.get(f) or "").strip()]


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")
    app.config["DATABASE"] = db_path or os.path.join(BASE, "uhcms.db")

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_):
        conn = g.pop("db", None)
        if conn:
            conn.close()

    with app.app_context():  # create tables + one default staff account
        with open(os.path.join(BASE, "schema.sql")) as f:
            db().executescript(f.read())
        if not db().execute("SELECT 1 FROM users WHERE role='staff'").fetchone():
            db().execute("INSERT INTO users(name,email,password_hash,role) "
                         "VALUES(?,?,?,'staff')",
                         ("Helpdesk Staff", "staff@uni.edu",
                          generate_password_hash("staff123")))
            db().commit()

    @app.before_request
    def load_user():
        uid = session.get("user_id")
        g.user = db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone() if uid else None

    def login_required(view):
        @wraps(view)
        def wrapped(*a, **kw):
            if g.user is None:
                return redirect(url_for("login"))
            return view(*a, **kw)
        return wrapped

    def get_complaint_or_404(cid):
        c = db().execute("SELECT c.*, u.name AS author FROM complaints c "
                         "JOIN users u ON u.id=c.user_id WHERE c.id=?", (cid,)).fetchone()
        if c is None or (g.user["role"] == "student" and c["user_id"] != g.user["id"]):
            abort(404)  # students can only see their own complaints
        return c

    @app.template_filter("cid")
    def cid_filter(n):
        return f"CMP-{n:03d}"

    @app.context_processor
    def inject_team():
        return {"TEAM": TEAM}

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name, email = request.form.get("name", "").strip(), request.form.get("email", "").strip().lower()
            pw = request.form.get("password", "")
            if not name or "@" not in email or len(pw) < 6:
                flash("Enter your name, a valid email and a password of 6+ characters.")
            elif db().execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
                flash("That email is already registered.")
            else:
                db().execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                             (name, email, generate_password_hash(pw)))
                db().commit()
                flash("Account created. Please log in.")
                return redirect(url_for("login"))
        return render_template("auth.html", mode="register")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            u = db().execute("SELECT * FROM users WHERE email=?",
                             (request.form.get("email", "").strip().lower(),)).fetchone()
            if u and check_password_hash(u["password_hash"], request.form.get("password", "")):
                session.clear()
                session["user_id"] = u["id"]
                return redirect(url_for("dashboard"))
            flash("Wrong email or password.")
        return render_template("auth.html", mode="login")

    @app.route("/forgot", methods=["GET", "POST"])
    def forgot():
        if request.method == "POST":
            flash("If that email is registered, reset instructions will be sent. Please also contact the helpdesk.")
            return redirect(url_for("login"))
        return render_template("forgot.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        q = "SELECT c.*, u.name AS author FROM complaints c JOIN users u ON u.id=c.user_id"
        args = ()
        if g.user["role"] == "student":
            q += " WHERE c.user_id=?"
            args = (g.user["id"],)
        rows = db().execute(q + " ORDER BY c.id DESC", args).fetchall()
        counts = {s: sum(1 for r in rows if r["status"] == s) for s in STATUSES}
        cats = {}
        for r in rows:
            cats[r["category"]] = cats.get(r["category"], 0) + 1
        return render_template("dashboard.html", complaints=rows, counts=counts, cats=cats)

    @app.route("/complaints/new", methods=["GET", "POST"])
    @login_required
    def new_complaint():
        if g.user["role"] != "student":
            abort(403)
        form = request.form if request.method == "POST" else {}
        if request.method == "POST":
            missing = validate_complaint(form)
            if missing:
                flash("Please fill in: " + ", ".join(missing) + ".")
            else:
                cur = db().execute("INSERT INTO complaints(user_id,title,category,description) VALUES(?,?,?,?)",
                                   (g.user["id"], form["title"].strip(), form["category"], form["description"].strip()))
                db().commit()
                flash(f"Complaint submitted. Your ID is CMP-{cur.lastrowid:03d}.")
                return redirect(url_for("detail", cid=cur.lastrowid))
        return render_template("new.html", categories=CATEGORIES, form=form)

    @app.route("/complaints/<int:cid>")
    @login_required
    def detail(cid):
        c = get_complaint_or_404(cid)
        comments = db().execute("SELECT m.*, u.name FROM comments m JOIN users u ON u.id=m.user_id "
                                "WHERE complaint_id=? ORDER BY m.id", (cid,)).fetchall()
        return render_template("detail.html", c=c, comments=comments, statuses=STATUSES)

    @app.route("/complaints/<int:cid>/status", methods=["POST"])
    @login_required
    def set_status(cid):
        if g.user["role"] != "staff":
            abort(403)
        get_complaint_or_404(cid)
        status = request.form.get("status")
        if status in STATUSES:
            db().execute("UPDATE complaints SET status=? WHERE id=?", (status, cid))
            db().commit()
            flash(f"Status changed to {status}.")
        return redirect(url_for("detail", cid=cid))

    @app.route("/complaints/<int:cid>/comment", methods=["POST"])
    @login_required
    def add_comment(cid):
        get_complaint_or_404(cid)
        text = request.form.get("text", "").strip()
        if text:
            db().execute("INSERT INTO comments(complaint_id,user_id,text) VALUES(?,?,?)",
                         (cid, g.user["id"], text))
            db().commit()
        return redirect(url_for("detail", cid=cid))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
