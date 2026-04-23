from flask import Flask, render_template, request, redirect, session, jsonify, flash
import random
import sqlite3
import os
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "quiz_secret_key_2024_ultra_secure"

# ============================================================
# DATABASE SETUP
# ============================================================
# Use /tmp for Vercel deployment (serverless), otherwise use project root
DB_PATH = os.environ.get("VERCEL") and "/tmp/quiz.db" or "quiz.db"

def init_db():
    """Initialize database with full schema"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
    except sqlite3.OperationalError as e:
        print(f"Warning: Could not connect to database at {DB_PATH}: {e}")
        return

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Scores table (full schema)
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER,
            score INTEGER NOT NULL,
            category TEXT NOT NULL DEFAULT 'gk',
            difficulty TEXT DEFAULT 'medium',
            total_questions INTEGER DEFAULT 3,
            time_taken INTEGER DEFAULT 0,
            date TEXT DEFAULT (datetime('now'))
        )
    """)

    # Migrate old scores table: add missing columns safely
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(scores)").fetchall()]
    migrations = [
        ("user_id",         "INTEGER"),
        ("category",        "TEXT DEFAULT 'gk'"),
        ("difficulty",      "TEXT DEFAULT 'medium'"),
        ("total_questions", "INTEGER DEFAULT 3"),
        ("time_taken",      "INTEGER DEFAULT 0"),
        ("date",            "TEXT"),
    ]
    for col_name, col_def in migrations:
        if col_name not in existing_cols:
            try:
                c.execute(f"ALTER TABLE scores ADD COLUMN {col_name} {col_def}")
            except Exception:
                pass

    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

# ============================================================
# QUIZ CATEGORIES
# ============================================================
QUIZ_CATEGORIES = {
    "gk": {
        "name": "General Knowledge",
        "emoji": "🌍",
        "color": "#FF6B6B",
        "easy": [
            {"question": "Capital of India?", "options": ["Mumbai", "Delhi", "Pune", "Chennai"], "answer": "Delhi"},
            {"question": "Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Mars"},
            {"question": "Largest continent?", "options": ["Africa", "Asia", "Europe", "North America"], "answer": "Asia"}
        ],
        "medium": [
            {"question": "Which country is called the Land of Rising Sun?", "options": ["China", "Japan", "Korea", "Thailand"], "answer": "Japan"},
            {"question": "The Statue of Liberty is located in which country?", "options": ["Canada", "UK", "USA", "France"], "answer": "USA"},
            {"question": "How many strings does a violin have?", "options": ["4", "5", "6", "7"], "answer": "4"}
        ],
        "hard": [
            {"question": "Which is the smallest country in the world?", "options": ["Monaco", "Vatican City", "Liechtenstein", "San Marino"], "answer": "Vatican City"},
            {"question": "What is the capital of Kazakhstan?", "options": ["Almaty", "Astana", "Karaganda", "Aktobe"], "answer": "Astana"},
            {"question": "How many bones does a shark have?", "options": ["200", "206", "0", "150"], "answer": "0"}
        ]
    },
    "python": {
        "name": "Python Programming",
        "emoji": "🐍",
        "color": "#4ECDC4",
        "easy": [
            {"question": "Which keyword is used to create a function?", "options": ["function", "def", "define", "func"], "answer": "def"},
            {"question": "What is the output of 2 ** 3?", "options": ["6", "8", "9", "12"], "answer": "8"},
            {"question": "Which data structure uses LIFO?", "options": ["Queue", "Stack", "Array", "List"], "answer": "Stack"}
        ],
        "medium": [
            {"question": "What does 'PEP 8' refer to?", "options": ["Python Enhancement Proposal", "Python Error Protocol", "Python Example Project", "None"], "answer": "Python Enhancement Proposal"},
            {"question": "Which method removes an item from a list?", "options": ["remove()", "delete()", "pop()", "All of the above"], "answer": "All of the above"},
            {"question": "What is the correct file extension for Python?", "options": [".pyt", ".py", ".python", ".p"], "answer": ".py"}
        ],
        "hard": [
            {"question": "What is the time complexity of accessing an element in a dictionary?", "options": ["O(n)", "O(1)", "O(log n)", "O(n²)"], "answer": "O(1)"},
            {"question": "Which of these is NOT a Python built-in function?", "options": ["len()", "type()", "size()", "int()"], "answer": "size()"},
            {"question": "What does 'GIL' stand for in Python?", "options": ["Global Integer Lock", "Global Interpreter Lock", "General Input Layer", "Global Implementation Limit"], "answer": "Global Interpreter Lock"}
        ]
    },
    "math": {
        "name": "Mathematics",
        "emoji": "🔢",
        "color": "#95E1D3",
        "easy": [
            {"question": "What is 15 × 4?", "options": ["50", "55", "60", "65"], "answer": "60"},
            {"question": "What is √144?", "options": ["10", "11", "12", "13"], "answer": "12"},
            {"question": "What is 25% of 200?", "options": ["25", "50", "75", "100"], "answer": "50"}
        ],
        "medium": [
            {"question": "What is the formula for the area of a circle?", "options": ["πr", "2πr", "πr²", "πr³"], "answer": "πr²"},
            {"question": "What is 0.5 × 0.5?", "options": ["0.10", "0.25", "0.50", "0.75"], "answer": "0.25"},
            {"question": "How many sides does a hexagon have?", "options": ["5", "6", "7", "8"], "answer": "6"}
        ],
        "hard": [
            {"question": "What is the derivative of x²?", "options": ["x", "2x", "x²", "2x²"], "answer": "2x"},
            {"question": "What is log₁₀(100)?", "options": ["1", "2", "10", "100"], "answer": "2"},
            {"question": "What is the sum of angles in a pentagon?", "options": ["360°", "540°", "720°", "900°"], "answer": "540°"}
        ]
    },
    "history": {
        "name": "History",
        "emoji": "📚",
        "color": "#F38181",
        "easy": [
            {"question": "In which year did WWII end?", "options": ["1943", "1944", "1945", "1946"], "answer": "1945"},
            {"question": "Who was the first President of USA?", "options": ["Thomas Jefferson", "George Washington", "John Adams", "Benjamin Franklin"], "answer": "George Washington"},
            {"question": "In which year did Titanic sink?", "options": ["1910", "1911", "1912", "1913"], "answer": "1912"}
        ],
        "medium": [
            {"question": "Which empire built the Great Wall of China?", "options": ["Indian", "Roman", "Chinese", "Ottoman"], "answer": "Chinese"},
            {"question": "In which year did the Berlin Wall fall?", "options": ["1987", "1988", "1989", "1990"], "answer": "1989"},
            {"question": "Who discovered America?", "options": ["Amerigo Vespucci", "Christopher Columbus", "John Cabot", "Leif Erikson"], "answer": "Christopher Columbus"}
        ],
        "hard": [
            {"question": "Which treaty ended WWI?", "options": ["Treaty of Paris", "Treaty of Versailles", "Treaty of Westphalia", "Treaty of Utrecht"], "answer": "Treaty of Versailles"},
            {"question": "In which year did the French Revolution begin?", "options": ["1787", "1788", "1789", "1790"], "answer": "1789"},
            {"question": "Who was the first Holy Roman Emperor?", "options": ["Otto I", "Charlemagne", "Frederick I", "Charles V"], "answer": "Charlemagne"}
        ]
    },
    "science": {
        "name": "Science",
        "emoji": "🔬",
        "color": "#AA96DA",
        "easy": [
            {"question": "What is the chemical symbol for Gold?", "options": ["Gd", "Go", "Au", "Ag"], "answer": "Au"},
            {"question": "How many bones are in the human body?", "options": ["186", "206", "226", "246"], "answer": "206"},
            {"question": "What is the speed of light?", "options": ["300,000 km/s", "200,000 km/s", "400,000 km/s", "100,000 km/s"], "answer": "300,000 km/s"}
        ],
        "medium": [
            {"question": "What is the chemical formula of salt?", "options": ["NaCl", "CaCl", "KCl", "MgCl"], "answer": "NaCl"},
            {"question": "Which planet is closest to the Sun?", "options": ["Venus", "Mercury", "Mars", "Earth"], "answer": "Mercury"},
            {"question": "How many chromosomes do humans have?", "options": ["23", "46", "48", "52"], "answer": "46"}
        ],
        "hard": [
            {"question": "What is Avogadro's number?", "options": ["6.02 × 10²³", "6.02 × 10²⁴", "6.02 × 10²²", "6.02 × 10²⁵"], "answer": "6.02 × 10²³"},
            {"question": "What is the SI unit of electric current?", "options": ["Volt", "Ampere", "Ohm", "Watt"], "answer": "Ampere"},
            {"question": "What is the chemical symbol for Potassium?", "options": ["Po", "Pt", "K", "P"], "answer": "K"}
        ]
    }
}

# ============================================================
# HELPERS
# ============================================================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_score(name, user_id, category, score, total, difficulty, time_taken):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO scores (name, user_id, category, score, total_questions, difficulty, time_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, user_id, category, score, total, difficulty, time_taken))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving score: {e}")
        return False

def get_leaderboard(limit=20):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT name, category, score, total_questions, difficulty, time_taken, date
            FROM scores
            ORDER BY score DESC, time_taken ASC
            LIMIT ?
        """, (limit,))
        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return []

def get_category_stats(category):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) as total_plays, AVG(score) as avg_score, MAX(score) as best_score
            FROM scores WHERE category = ?
        """, (category,))
        stats = c.fetchone()
        conn.close()
        return dict(stats) if stats else {"total_plays": 0, "avg_score": 0, "best_score": 0}
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {"total_plays": 0, "avg_score": 0, "best_score": 0}

def require_login(f):
    """Redirect to login if user is not authenticated"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def require_session(f):
    """Redirect home if quiz session (category/questions) not started"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/login")
        if "name" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# AUTH ROUTES
# ============================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("logged_in"):
        return redirect("/")

    error = None
    form_data = {}

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")
        form_data = {"username": username, "email": email}

        # Validation
        if not username or not email or not password:
            error = "All fields are required."
        elif len(username) < 3:
            error = "Username must be at least 3 characters."
        elif len(username) > 30:
            error = "Username must be 30 characters or fewer."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif "@" not in email:
            error = "Please enter a valid email address."
        else:
            try:
                conn = get_db_connection()
                c = conn.cursor()
                password_hash = generate_password_hash(password)
                c.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash)
                )
                user_id = c.lastrowid
                conn.commit()
                conn.close()

                # Auto-login after registration
                session["user_id"]  = user_id
                session["username"] = username
                session["email"]    = email
                session["logged_in"] = True
                session["name"]     = username
                return redirect("/")

            except sqlite3.IntegrityError as e:
                err_str = str(e).lower()
                if "username" in err_str:
                    error = "That username is already taken. Try another."
                elif "email" in err_str:
                    error = "That email is already registered. Try logging in."
                else:
                    error = "Registration failed. Please try again."
            except Exception as e:
                print(f"Register error: {e}")
                error = "An unexpected error occurred. Please try again."

    return render_template("register.html", error=error, form_data=form_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect("/")

    error = None
    saved_username = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        saved_username = username

        if not username or not password:
            error = "Please enter your username and password."
        else:
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = c.fetchone()
                conn.close()

                if user and check_password_hash(user["password_hash"], password):
                    session["user_id"]   = user["id"]
                    session["username"]  = user["username"]
                    session["email"]     = user["email"]
                    session["logged_in"] = True
                    session["name"]      = user["username"]
                    return redirect("/")
                else:
                    error = "Incorrect username or password."
            except Exception as e:
                print(f"Login error: {e}")
                error = "Login failed. Please try again."

    return render_template("login.html", error=error, saved_username=saved_username)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ============================================================
# MAIN ROUTES
# ============================================================
@app.route("/", methods=["GET", "POST"])
@require_login
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            name = session.get("username", "Player")
        session["name"]       = name
        session["score"]      = 0
        session["q_index"]    = 0
        session["difficulty"] = "medium"
        return redirect("/category")
    return render_template("index.html", username=session.get("username"))


@app.route("/category", methods=["GET", "POST"])
@require_login
def category():
    if request.method == "POST":
        cat        = request.form.get("category", "").lower()
        difficulty = request.form.get("difficulty", "medium").lower()

        if cat in QUIZ_CATEGORIES and difficulty in ["easy", "medium", "hard"]:
            session["category"]   = cat
            session["difficulty"] = difficulty
            session["quiz_data"]  = QUIZ_CATEGORIES[cat][difficulty].copy()
            session["q_index"]    = 0
            session["score"]      = 0
            session["start_time"] = datetime.now().isoformat()
            random.shuffle(session["quiz_data"])
            return redirect("/quiz")

    return render_template("category.html", categories=QUIZ_CATEGORIES)


@app.route("/quiz", methods=["GET", "POST"])
@require_session
def quiz():
    if request.method == "POST":
        answer = request.form.get("answer", "").strip()
        if session["q_index"] < len(session["quiz_data"]):
            current_q = session["quiz_data"][session["q_index"]]
            if answer == current_q["answer"]:
                session["score"] += 1
            session["q_index"] += 1

    if session["q_index"] >= len(session["quiz_data"]):
        return redirect("/result")

    current_q = session["quiz_data"][session["q_index"]]
    return render_template(
        "quiz.html",
        q=current_q,
        index=session["q_index"] + 1,
        total=len(session["quiz_data"]),
        difficulty=session.get("difficulty", "medium"),
        category_name=QUIZ_CATEGORIES[session.get("category", "gk")]["name"]
    )


@app.route("/result")
@require_session
def result():
    start_time = datetime.fromisoformat(session.get("start_time", datetime.now().isoformat()))
    time_taken = int((datetime.now() - start_time).total_seconds())

    category   = session.get("category", "gk")
    difficulty = session.get("difficulty", "medium")
    score      = session.get("score", 0)
    total      = len(session.get("quiz_data", []))

    save_score(
        session.get("name"),
        session.get("user_id"),
        category,
        score,
        total,
        difficulty,
        time_taken
    )

    percentage = (score / total * 100) if total > 0 else 0

    return render_template(
        "result.html",
        name=session.get("name"),
        score=score,
        total=total,
        category=QUIZ_CATEGORIES[category]["name"],
        difficulty=difficulty.upper(),
        time_taken=time_taken,
        percentage=percentage
    )


@app.route("/leaderboard")
def leaderboard():
    data = get_leaderboard()
    return render_template("leaderboard.html", data=data)


@app.route("/stats/<category>")
def stats(category):
    if category not in QUIZ_CATEGORIES:
        return redirect("/leaderboard")
    category_stats = get_category_stats(category)
    return render_template(
        "stats.html",
        category_name=QUIZ_CATEGORIES[category]["name"],
        category_emoji=QUIZ_CATEGORIES[category]["emoji"],
        stats=category_stats
    )


@app.route("/api/get-time")
def get_time():
    return jsonify({"timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)