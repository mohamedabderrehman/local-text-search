"""
ملف تشغيل النظام الكامل (الويب + تيليجرام)
"""
import os
import threading
import time
from app import app, db
import config

def run_telegram_bot():
    """تشغيل بوت تيليجرام في thread منفصل"""
    time.sleep(2)  # انتظار قصير لبدء Flask
    from telegram_bot import run_bot
    run_bot()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 تشغيل النظام الكامل")
    print("=" * 60)
    
    # التحقق من إعدادات تيليجرام
    has_telegram = config.ENABLE_TELEGRAM and bool(os.getenv("TELEGRAM_API_ID") and os.getenv("TELEGRAM_API_HASH"))
    
    if has_telegram:
        print("✓ عميل تيليجرام: مفعّل")
        # تشغيل العميل في thread منفصل
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
    else:
        print("⚠️ عميل تيليجرام: غير مفعّل (TELEGRAM_API_ID أو TELEGRAM_API_HASH غير محدد)")
        print("   راجع TELEGRAM_SETUP.md للإعداد")
    
    print("\n🌐 تطبيق الويب يعمل على: http://127.0.0.1:5000")
    print("=" * 60)
    
    # تشغيل Flask
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=False, use_reloader=False)

