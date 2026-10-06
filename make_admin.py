"""
سكريبت لجعل مستخدم مسؤول
"""
from database import Database
from auth import hash_password
import sys

def make_admin():
    """جعل مستخدم مسؤول"""
    db = Database()
    
    print("=" * 60)
    print("جعل مستخدم مسؤول")
    print("=" * 60)
    print()
    
    username = input("اسم المستخدم المراد جعله مسؤول: ").strip()
    if not username:
        print("❌ اسم المستخدم مطلوب")
        return
    
    user = db.get_user_by_username(username)
    if not user:
        print(f"❌ المستخدم '{username}' غير موجود")
        return
    
    if user.get('is_admin', 0):
        print(f"✓ المستخدم '{username}' مسؤول بالفعل")
        return
    
    # جعله مسؤول
    success = db.update_user(user['id'], is_admin=True)
    
    if success:
        print(f"✓ تم جعل المستخدم '{username}' مسؤول بنجاح")
    else:
        print(f"❌ فشل تحديث المستخدم")

if __name__ == '__main__':
    make_admin()

