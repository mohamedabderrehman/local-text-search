"""
نظام المصادقة - تشفير كلمات المرور وإدارة الجلسات
"""
import bcrypt
from functools import wraps
from flask import session, redirect, url_for, request
from database import Database

import config
db = Database(str(config.DATABASE_PATH))

def hash_password(password: str) -> str:
    """تشفير كلمة المرور باستخدام bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """التحقق من كلمة المرور"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        return False

def login_required(f):
    """ديكوراتور للمسارات التي تتطلب تسجيل الدخول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """الحصول على المستخدم الحالي من الجلسة"""
    if 'user_id' not in session:
        return None
    user = db.get_user_by_username(session.get('username'))
    return user

def is_admin(user_id: int = None) -> bool:
    """التحقق من أن المستخدم مسؤول"""
    if user_id is None:
        user = get_current_user()
        if not user:
            return False
        return bool(user.get('is_admin', 0))
    else:
        user = db.get_user(user_id)
        if not user:
            return False
        return bool(user.get('is_admin', 0))

def admin_required(f):
    """ديكوراتور للمسارات التي تتطلب صلاحيات مسؤول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = get_current_user()
        if not user or not user.get('is_admin', 0):
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

