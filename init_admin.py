"""
سكريبت إنشاء مستخدم مسؤول
"""
from database import Database
from auth import hash_password
import getpass

def create_admin():
    """إنشاء مستخدم مسؤول"""
    db = Database()
    
    print("=" * 60)
    print("إنشاء مستخدم مسؤول")
    print("=" * 60)
    
    username = input("اسم المستخدم: ").strip()
    if not username:
        print("❌ اسم المستخدم مطلوب")
        return
    
    # التحقق من وجود المستخدم
    existing = db.get_user_by_username(username)
    if existing:
        print(f"⚠️ المستخدم '{username}' موجود مسبقاً")
        overwrite = input("هل تريد تغيير كلمة المرور؟ (y/n): ").strip().lower()
        if overwrite != 'y':
            return
    
    password = getpass.getpass("كلمة المرور: ")
    if not password:
        print("❌ كلمة المرور مطلوبة")
        return
    
    password_confirm = getpass.getpass("تأكيد كلمة المرور: ")
    if password != password_confirm:
        print("❌ كلمات المرور غير متطابقة")
        return
    
    # إنشاء المستخدم كمسؤول
    password_hash = hash_password(password)
    user_id = db.create_user(username, password_hash, is_admin=True)
    
    if user_id:
        print(f"✓ تم إنشاء المستخدم '{username}' بنجاح (ID: {user_id})")
    else:
        print("❌ فشل إنشاء المستخدم (قد يكون الاسم مستخدماً)")

if __name__ == '__main__':
    create_admin()

