"""
تطبيق Flask الرئيسي - واجهة الويب
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import os
import threading
from datetime import datetime
from pathlib import Path
from database import Database
from search_engine import SearchEngine
from auth import login_required, verify_password, get_current_user, hash_password, admin_required, is_admin
import json

app = Flask(__name__)
import config
app.secret_key = config.SECRET_KEY

db = Database(str(config.DATABASE_PATH))
search_engine = SearchEngine(str(config.CORPUS_DIR), str(config.RESULTS_DIR))

# مسار مجلد النتائج
RESULTS_DIR = config.RESULTS_DIR
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def run_search_async(keywords: str, job_id: int):
    """تشغيل البحث في thread منفصل"""
    try:
        result = search_engine.search(keywords, job_id, db)
        
        # إرسال ملخص النتائج إلى تيليجرام
        try:
            if not config.ENABLE_TELEGRAM:
                return
            from telegram_bot import get_telegram_client
            telegram_client = get_telegram_client()
            if telegram_client and telegram_client.client:
                # استخدام asyncio لإرسال الرسالة
                import asyncio
                try:
                    # محاولة الحصول على event loop موجود
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # إنشاء event loop جديد
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # إرسال الملخص
                if loop.is_running():
                    # إذا كان loop يعمل، استخدم create_task
                    asyncio.create_task(
                        telegram_client.send_search_summary(
                            job_id=job_id,
                            keywords=keywords,
                            matches_count=result.get('matches', 0),
                            files_searched=result.get('files_searched', 0),
                            total_files=result.get('total_files', 0)
                        )
                    )
                else:
                    # إذا لم يكن يعمل، استخدم run_until_complete
                    loop.run_until_complete(
                        telegram_client.send_search_summary(
                            job_id=job_id,
                            keywords=keywords,
                            matches_count=result.get('matches', 0),
                            files_searched=result.get('files_searched', 0),
                            total_files=result.get('total_files', 0)
                        )
                    )
        except Exception as e:
            print(f"⚠️ لم يتم إرسال ملخص البحث إلى تيليجرام: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"خطأ في البحث: {e}")
        import traceback
        traceback.print_exc()
        db.update_job_status(job_id, 'failed')

def read_results_from_file(job_id: int, limit: int = 100, offset: int = 0):
    """قراءة النتائج من الملف (صفحات)"""
    results_file = RESULTS_DIR / f"job_{job_id}_results.txt"
    
    if not results_file.exists():
        return [], 0
    
    results = []
    current_offset = 0
    total_count = 0
    
    try:
        with open(results_file, 'r', encoding='utf-8', errors='ignore') as f:
            # تخطي الرأس (3 أسطر)
            for _ in range(3):
                f.readline()
            
            current_result = {}
            in_result = False
            collecting_text = False
            
            for line in f:
                line = line.rstrip('\n\r')
                
                if not line or line.startswith('='):
                    continue
                
                if line.startswith('FILE:'):
                    # بداية نتيجة جديدة
                    if in_result and current_result and current_result.get('line_text'):
                        total_count += 1
                        if offset <= current_offset < offset + limit:
                            results.append(current_result.copy())
                        current_offset += 1
                        if len(results) >= limit:
                            break
                    
                    # تحليل سطر الملف
                    parts = line.split('|')
                    file_part = parts[0].replace('FILE:', '').strip()
                    line_part = parts[1].replace('LINE:', '').strip() if len(parts) > 1 else '0'
                    
                    current_result = {
                        'file_name': file_part,
                        'line_number': int(line_part) if line_part.isdigit() else 0,
                        'line_text': ''
                    }
                    in_result = True
                    collecting_text = True
                elif collecting_text and line and not line.startswith('-'):
                    # نص السطر
                    if current_result['line_text']:
                        current_result['line_text'] += '\n' + line
                    else:
                        current_result['line_text'] = line
                elif line.startswith('-' * 10):
                    # نهاية النتيجة
                    collecting_text = False
            
            # آخر نتيجة
            if in_result and current_result and current_result.get('line_text'):
                total_count += 1
                if offset <= current_offset < offset + limit:
                    results.append(current_result)
    
    except Exception as e:
        print(f"خطأ في قراءة النتائج: {e}")
        import traceback
        traceback.print_exc()
    
    return results, total_count

def count_results_in_file(job_id: int) -> int:
    """عد النتائج في الملف"""
    results_file = RESULTS_DIR / f"job_{job_id}_results.txt"
    
    if not results_file.exists():
        return 0
    
    count = 0
    try:
        with open(results_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('FILE:'):
                    count += 1
    except:
        pass
    
    return count

@app.route('/')
def index():
    """الصفحة الرئيسية - إعادة توجيه للدخول"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error='يرجى إدخال اسم المستخدم وكلمة المرور')
        
        user = db.get_user_by_username(username)
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم"""
    user = get_current_user()
    jobs = db.get_user_jobs(user['id'], limit=20)
    
    # إحصائيات المستخدم
    user_stats = db.get_user_stats(user['id'])
    
    return render_template('dashboard.html', user=user, jobs=jobs, user_stats=user_stats, is_admin_user=is_admin())

@app.route('/search', methods=['POST'])
@login_required
def search():
    """بدء عملية بحث جديدة"""
    user = get_current_user()
    keywords = request.form.get('keywords', '').strip()
    
    if not keywords:
        return redirect(url_for('dashboard'))
    
    # إنشاء وظيفة جديدة
    job_id = db.create_job(user['id'], keywords)
    
    # تشغيل البحث في thread منفصل
    thread = threading.Thread(target=run_search_async, args=(keywords, job_id))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('job_status', job_id=job_id))

@app.route('/job/<int:job_id>')
@login_required
def job_status(job_id):
    """صفحة حالة الوظيفة والنتائج"""
    user = get_current_user()
    job = db.get_job(job_id)
    
    if not job or job['user_id'] != user['id']:
        return redirect(url_for('dashboard'))
    
    # الحصول على النتائج من الملف (صفحة واحدة)
    try:
        page = int(request.args.get('page', 1))
        if page < 1: raise ValueError('Page must be positive')
    except ValueError:
        return 'Invalid page', 400
    per_page = 100
    offset = (page - 1) * per_page
    
    results, total_results = read_results_from_file(job_id, limit=per_page, offset=offset)
    total_pages = (total_results + per_page - 1) // per_page if total_results > 0 else 1
    
    return render_template('job.html', 
                         job=job, 
                         results=results,
                         page=page,
                         total_pages=total_pages,
                         total_results=total_results)

@app.route('/api/job/<int:job_id>/status')
@login_required
def api_job_status(job_id):
    """API للحصول على حالة الوظيفة (للتحديث التلقائي)"""
    user = get_current_user()
    job = db.get_job(job_id)
    
    if not job or job['user_id'] != user['id']:
        return jsonify({"error": "غير مصرح"}), 403
    
    # تحديث عدد النتائج من الملف إذا كانت الوظيفة مكتملة
    if job['status'] == 'completed':
        file_count = count_results_in_file(job_id)
        if file_count != job['matches_count']:
            db.update_job_status(job_id, 'completed', matches_count=file_count)
            job['matches_count'] = file_count
    
    return jsonify({
        "status": job['status'],
        "matches_count": job['matches_count'],
        "files_searched": job['files_searched'],
        "total_files": job['total_files']
    })

@app.route('/job/<int:job_id>/download')
@login_required
def download_results(job_id):
    """تحميل النتائج كملف نصي"""
    user = get_current_user()
    job = db.get_job(job_id)
    
    if not job or job['user_id'] != user['id']:
        return redirect(url_for('dashboard'))
    
    # ملف النتائج موجود بالفعل (تم إنشاؤه أثناء البحث)
    results_file = RESULTS_DIR / f"job_{job_id}_results.txt"
    
    if not results_file.exists():
        return redirect(url_for('job_status', job_id=job_id))
    
    return send_file(str(results_file), as_attachment=True, 
                    download_name=f"search_results_{job_id}.txt")

# ==================== إدارة المستخدمين (للمسؤول فقط) ====================

@app.route('/admin/users')
@admin_required
def admin_users():
    """صفحة إدارة المستخدمين"""
    users = db.get_all_users()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    """إنشاء مستخدم جديد"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        is_admin_user = request.form.get('is_admin') == 'on'
        
        if not username or not password:
            return render_template('admin_create_user.html', error='يرجى إدخال جميع الحقول')
        
        password_hash = hash_password(password)
        user_id = db.create_user(username, password_hash, is_admin_user)
        
        if user_id:
            return redirect(url_for('admin_users'))
        else:
            return render_template('admin_create_user.html', error='اسم المستخدم موجود مسبقاً')
    
    return render_template('admin_create_user.html')

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    """تعديل مستخدم"""
    user = db.get_user(user_id)
    if not user:
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        is_admin_user = request.form.get('is_admin') == 'on'
        
        if not username:
            return render_template('admin_edit_user.html', user=user, error='اسم المستخدم مطلوب')
        
        # تحديث البيانات
        password_hash = None
        if password:
            password_hash = hash_password(password)
        
        success = db.update_user(user_id, username, password_hash, is_admin_user)
        
        if success:
            return redirect(url_for('admin_users'))
        else:
            return render_template('admin_edit_user.html', user=user, error='فشل التحديث (قد يكون الاسم مستخدماً)')
    
    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """حذف مستخدم"""
    current_user = get_current_user()
    if user_id == current_user['id']:
        return redirect(url_for('admin_users'))
    
    db.delete_user(user_id)
    return redirect(url_for('admin_users'))

# ==================== الإحصائيات ====================

@app.route('/stats')
@login_required
def stats():
    """صفحة الإحصائيات"""
    user = get_current_user()
    
    if is_admin():
        # إحصائيات عامة للمسؤول
        all_stats = db.get_all_stats()
        return render_template('stats_admin.html', stats=all_stats, user=user)
    else:
        # إحصائيات المستخدم العادي
        user_stats = db.get_user_stats(user['id'])
        return render_template('stats_user.html', user_stats=user_stats, user=user)

if __name__ == '__main__':
    print("=" * 60)
    print("نظام البحث النصي المحلي - النسخة المحسّنة")
    print("=" * 60)
    print(f"مجلد الملفات: {search_engine.corpus_dir}")
    print(f"مجلد النتائج: {search_engine.results_dir}")
    print(f"قاعدة البيانات: {db.db_path}")
    print("\nلتشغيل النظام:")
    print("1. ضع ملفات .txt في مجلد: data/corpus/")
    print("2. أنشئ مستخدم مسؤول: python init_admin.py")
    print("3. شغل التطبيق: python app.py")
    print("\nالخادم يعمل على: http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
