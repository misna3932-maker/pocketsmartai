import json
from .db import get_db

def create_user(username, email, password_hash):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO users(username,email,password_hash) VALUES(?,?,?)",
            (username, email, password_hash),
        )
        return conn.execute("SELECT * FROM users WHERE id=?", (cur.lastrowid,)).fetchone()

def get_user_by_username(username):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

def get_user_by_id(user_id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

def user_exists(username, email):
    with get_db() as conn:
        return conn.execute("SELECT id FROM users WHERE username=? OR email=?", (username, email)).fetchone() is not None

def create_recommendation(user_id, planner_type, total_budget, payload, request_data):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO recommendations(user_id,planner_type,total_budget,payload_json,request_json) VALUES(?,?,?,?,?)",
            (user_id, planner_type, total_budget, json.dumps(payload), json.dumps(request_data)),
        )
        return cur.lastrowid

def get_recommendation(rec_id, user_id):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM recommendations WHERE id=? AND user_id=?", (rec_id, user_id)
        ).fetchone()

def list_recommendations(user_id, limit=30):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM recommendations WHERE user_id=? ORDER BY created_at DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
