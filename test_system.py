"""
سكريبت اختبار بسيط للنظام
"""
import os
from database import Database
from search_engine import SearchEngine
from auth import hash_password, verify_password

def test_database():
    """اختبار قاعدة البيانات"""
    print("🧪 اختبار قاعدة البيانات...")
    
    db = Database("data/test.db")
    
    # اختبار إنشاء مستخدم
    user_id = db.create_user("test_user", hash_password("test123"))
    assert user_id is not None, "فشل إنشاء مستخدم"
    print("  ✓ إنشاء مستخدم: نجح")
    
    # اختبار الحصول على مستخدم
    user = db.get_user_by_username("test_user")
    assert user is not None, "فشل الحصول على مستخدم"
    print("  ✓ الحصول على مستخدم: نجح")
    
    # اختبار إنشاء وظيفة
    job_id = db.create_job(user_id, "test keywords")
    assert job_id is not None, "فشل إنشاء وظيفة"
    print("  ✓ إنشاء وظيفة: نجح")
    
    # اختبار إضافة نتيجة
    db.add_result(job_id, "test.txt", 1, "test line")
    results = db.get_results(job_id)
    assert len(results) == 1, "فشل إضافة نتيجة"
    print("  ✓ إضافة نتيجة: نجح")
    
    # تنظيف
    os.remove("data/test.db")
    print("  ✓ تنظيف: نجح")
    
    print("✅ اختبار قاعدة البيانات: نجح\n")

def test_auth():
    """اختبار المصادقة"""
    print("🧪 اختبار المصادقة...")
    
    password = "test123"
    password_hash = hash_password(password)
    
    # اختبار التشفير
    assert password_hash != password, "كلمة المرور غير مشفرة"
    print("  ✓ تشفير كلمة المرور: نجح")
    
    # اختبار التحقق
    assert verify_password(password, password_hash), "فشل التحقق من كلمة المرور"
    print("  ✓ التحقق من كلمة المرور: نجح")
    
    # اختبار كلمة خاطئة
    assert not verify_password("wrong", password_hash), "قبل كلمة مرور خاطئة"
    print("  ✓ رفض كلمة مرور خاطئة: نجح")
    
    print("✅ اختبار المصادقة: نجح\n")

def test_search_engine():
    """اختبار محرك البحث"""
    print("🧪 اختبار محرك البحث...")
    
    # إنشاء ملف تجريبي
    test_dir = "data/test_corpus"
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "test.txt")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("This is a test line with error message\n")
        f.write("Login failed for user admin\n")
        f.write("Another line without keywords\n")
        f.write("Error occurred during login process\n")
    
    # اختبار محرك البحث
    engine = SearchEngine(corpus_dir=test_dir)
    files = engine.get_txt_files()
    assert len(files) == 1, "لم يتم العثور على الملف"
    print("  ✓ العثور على الملفات: نجح")
    
    # تنظيف
    os.remove(test_file)
    os.rmdir(test_dir)
    print("  ✓ تنظيف: نجح")
    
    print("✅ اختبار محرك البحث: نجح\n")

def main():
    """تشغيل جميع الاختبارات"""
    print("=" * 60)
    print("🧪 اختبار النظام")
    print("=" * 60)
    print()
    
    try:
        test_database()
        test_auth()
        test_search_engine()
        
        print("=" * 60)
        print("✅ جميع الاختبارات نجحت!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ فشل الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

