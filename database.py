"""
قاعدة البيانات SQLite - تخزين المستخدمين، الوظائف، والنتائج فقط
لا فهرسة مسبقة - فقط الميتاداتا والنتائج النهائية
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import threading

class Database:
    def __init__(self, db_path: str = "data/search.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """إنشاء اتصال جديد بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """تهيئة الجداول"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إضافة عمود is_admin إذا لم يكن موجوداً (للمستخدمين القدامى)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # العمود موجود بالفعل
        
        # جدول الوظائف (jobs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                keywords TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP,
                matches_count INTEGER DEFAULT 0,
                files_searched INTEGER DEFAULT 0,
                total_files INTEGER DEFAULT 0,
                lines_processed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # إضافة عمود lines_processed إذا لم يكن موجوداً
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN lines_processed INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # العمود موجود بالفعل
        
        # جدول النتائج (فقط الأسطر المطابقة)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                line_text TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)
        
        # فهارس للأداء
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_user ON jobs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_job ON results(job_id)")
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password_hash: str, is_admin: bool = False) -> int:
        """إنشاء مستخدم جديد"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                    (username, password_hash, 1 if is_admin else 0)
                )
                user_id = cursor.lastrowid
                conn.commit()
                return user_id
            except sqlite3.IntegrityError:
                return None
            finally:
                conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """الحصول على مستخدم بالـ ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_user(self, user_id: int, username: str = None, password_hash: str = None, is_admin: bool = None) -> bool:
        """تحديث بيانات مستخدم"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                updates = []
                params = []
                
                if username is not None:
                    updates.append("username = ?")
                    params.append(username)
                
                if password_hash is not None:
                    updates.append("password_hash = ?")
                    params.append(password_hash)
                
                if is_admin is not None:
                    updates.append("is_admin = ?")
                    params.append(1 if is_admin else 0)
                
                if not updates:
                    return False
                
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
            finally:
                conn.close()
    
    def delete_user(self, user_id: int) -> bool:
        """حذف مستخدم"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                return cursor.rowcount > 0
            except:
                return False
            finally:
                conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """الحصول على إحصائيات مستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # عدد الوظائف
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE user_id = ?", (user_id,))
        total_jobs = cursor.fetchone()[0]
        
        # عدد الوظائف المكتملة
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE user_id = ? AND status = 'completed'", (user_id,))
        completed_jobs = cursor.fetchone()[0]
        
        # إجمالي النتائج
        cursor.execute("""
            SELECT SUM(matches_count) FROM jobs 
            WHERE user_id = ? AND status = 'completed'
        """, (user_id,))
        total_matches = cursor.fetchone()[0] or 0
        
        # إجمالي الأسطر المفحوصة
        cursor.execute("""
            SELECT SUM(lines_processed) FROM jobs 
            WHERE user_id = ? AND status = 'completed'
        """, (user_id,))
        total_lines = cursor.fetchone()[0] or 0
        
        # عدد الكلمات المفتاحية الفريدة
        cursor.execute("""
            SELECT COUNT(DISTINCT keywords) FROM jobs 
            WHERE user_id = ?
        """, (user_id,))
        unique_keywords = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'total_matches': total_matches,
            'total_lines_processed': total_lines,
            'unique_keywords': unique_keywords
        }
    
    def get_all_stats(self) -> Dict:
        """الحصول على إحصائيات عامة (للمسؤول)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # إجمالي المستخدمين
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # إجمالي الوظائف
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        
        # إجمالي الوظائف المكتملة
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'completed'")
        completed_jobs = cursor.fetchone()[0]
        
        # إجمالي النتائج
        cursor.execute("SELECT SUM(matches_count) FROM jobs WHERE status = 'completed'")
        total_matches = cursor.fetchone()[0] or 0
        
        # إجمالي الأسطر المفحوصة
        cursor.execute("SELECT SUM(lines_processed) FROM jobs WHERE status = 'completed'")
        total_lines = cursor.fetchone()[0] or 0
        
        # عدد الكلمات المفتاحية الفريدة
        cursor.execute("SELECT COUNT(DISTINCT keywords) FROM jobs")
        unique_keywords = cursor.fetchone()[0] or 0
        
        # إحصائيات لكل مستخدم
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        users_stats = []
        for user in users:
            user_id = user[0]
            username = user[1]
            stats = self.get_user_stats(user_id)
            users_stats.append({
                'user_id': user_id,
                'username': username,
                **stats
            })
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'total_matches': total_matches,
            'total_lines_processed': total_lines,
            'unique_keywords': unique_keywords,
            'users_stats': users_stats
        }
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """الحصول على مستخدم بالاسم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def create_job(self, user_id: int, keywords: str) -> int:
        """إنشاء وظيفة بحث جديدة"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO jobs (user_id, keywords, status) 
                   VALUES (?, ?, 'pending')""",
                (user_id, keywords)
            )
            job_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return job_id
    
    def update_job_status(self, job_id: int, status: str, 
                         matches_count: int = 0, 
                         files_searched: int = 0,
                         total_files: int = 0,
                         lines_processed: int = 0):
        """تحديث حالة الوظيفة"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            finished_at = datetime.now().isoformat() if status in ['completed', 'failed'] else None
            cursor.execute(
                """UPDATE jobs SET status = ?, matches_count = ?, 
                   files_searched = ?, total_files = ?, finished_at = ?, lines_processed = ?
                   WHERE id = ?""",
                (status, matches_count, files_searched, total_files, finished_at, lines_processed, job_id)
            )
            conn.commit()
            conn.close()
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """الحصول على وظيفة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_user_jobs(self, user_id: int, limit: int = 50) -> List[Dict]:
        """الحصول على وظائف المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM jobs WHERE user_id = ? 
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_result(self, job_id: int, file_name: str, line_number: int, line_text: str):
        """إضافة نتيجة (سطر مطابق)"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO results (job_id, file_name, line_number, line_text)
                   VALUES (?, ?, ?, ?)""",
                (job_id, file_name, line_number, line_text)
            )
            conn.commit()
            conn.close()
    
    def get_results(self, job_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """الحصول على نتائج الوظيفة (صفحات)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM results WHERE job_id = ?
               ORDER BY id LIMIT ? OFFSET ?""",
            (job_id, limit, offset)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_results_count(self, job_id: int) -> int:
        """عدد النتائج الكلي"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM results WHERE job_id = ?", (job_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

