"""
بوت تيليجرام - مراقبة قناة خاصة وتحميل الملفات تلقائياً
يستخدم Pyrogram للوصول للقنوات الخاصة + إرسال ملخصات النتائج
"""
import os
from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram.filters import document
from pathlib import Path
import asyncio
from database import Database

# إعدادات
API_ID = os.getenv("TELEGRAM_API_ID", "")
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL", "")  # @channel_name أو channel_id
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID", "")  # ID حسابك لإرسال الملخصات
CORPUS_DIR = Path("data/corpus")
CORPUS_DIR.mkdir(parents=True, exist_ok=True)

db = Database()

class TelegramClient:
    def __init__(self):
        self.client = None
        self.downloaded_files = set()
        self.user_id = None
    
    async def handle_message(self, client, message):
        """معالجة الرسائل من القناة"""
        # التحقق من أن الرسالة من القناة المحددة
        chat_title = message.chat.title or ""
        chat_username = message.chat.username or ""
        chat_id = str(message.chat.id)
        
        # التحقق من القناة
        channel_match = (
            TELEGRAM_CHANNEL and (
                chat_id == TELEGRAM_CHANNEL or
                chat_username == TELEGRAM_CHANNEL.replace('@', '') or
                chat_title == TELEGRAM_CHANNEL
            )
        )
        
        if not channel_match:
            return
        
        # البحث عن ملفات .txt
        if message.document:
            file_name = message.document.file_name or "unknown.txt"
            
            # فقط ملفات .txt
            if not file_name.lower().endswith('.txt'):
                return
            
            local_path = CORPUS_DIR / file_name
            
            # تجنب التحميل المكرر
            if local_path.exists():
                print(f"الملف موجود مسبقاً: {file_name}")
                return
            
            try:
                print(f"جارٍ تحميل: {file_name}")
                
                # تحميل الملف
                await message.download(file_name=str(local_path))
                
                if local_path.exists():
                    file_size_mb = local_path.stat().st_size / (1024 * 1024)
                    print(f"✓ تم تحميل: {file_name} ({file_size_mb:.2f} MB)")
                else:
                    print(f"✗ فشل تحميل: {file_name}")
            except Exception as e:
                print(f"خطأ في تحميل {file_name}: {e}")
    
    async def send_search_summary(self, job_id: int, keywords: str, matches_count: int, 
                                 files_searched: int, total_files: int):
        """
        إرسال ملخص نتائج البحث إلى المستخدم
        """
        if not self.client or not TELEGRAM_USER_ID:
            return
        
        try:
            job = db.get_job(job_id)
            if not job:
                return
            
            # إنشاء رسالة الملخص
            summary = (
                f"🔍 **اكتملت وظيفة البحث**\n\n"
                f"**الكلمات المفتاحية:** `{keywords}`\n"
                f"**عدد النتائج:** {matches_count:,}\n"
                f"**الملفات المفحوصة:** {files_searched}/{total_files}\n"
                f"**الوظيفة #:** {job_id}\n"
                f"**الحالة:** {job['status']}\n"
                f"**تاريخ الإنشاء:** {job['created_at']}\n"
                f"**تاريخ الانتهاء:** {job.get('finished_at', 'N/A')}\n\n"
            )
            
            if matches_count > 0:
                summary += f"📥 يمكنك تحميل النتائج من الواجهة\n"
                summary += f"🔗 رابط الوظيفة: http://127.0.0.1:5000/job/{job_id}"
            else:
                summary += f"⚠️ لم يتم العثور على نتائج"
            
            # إرسال الرسالة
            await self.client.send_message(
                chat_id=int(TELEGRAM_USER_ID),
                text=summary,
                parse_mode="Markdown"
            )
            
            print(f"✓ تم إرسال ملخص البحث إلى تيليجرام")
        except Exception as e:
            print(f"خطأ في إرسال ملخص البحث: {e}")
            import traceback
            traceback.print_exc()
    
    async def start(self):
        """بدء العميل"""
        if not API_ID or not API_HASH:
            print("⚠️ تحذير: TELEGRAM_API_ID أو TELEGRAM_API_HASH غير محدد")
            print("   احصل عليهما من: https://my.telegram.org")
            print("   البوت لن يعمل بدون هذه المعلومات")
            return
        
        # إنشاء العميل
        self.client = Client(
            "telegram_downloader",
            api_id=int(API_ID),
            api_hash=API_HASH
        )
        
        # تسجيل معالج الرسائل
        self.client.add_handler(
            MessageHandler(self.handle_message, filters=document)
        )
        
        # بدء العميل
        await self.client.start()
        
        # الحصول على معلومات المستخدم
        me = await self.client.get_me()
        self.user_id = me.id
        print(f"🤖 عميل تيليجرام يعمل...")
        print(f"   المستخدم: {me.first_name} (@{me.username or 'N/A'})")
        print(f"   User ID: {me.id}")
        print(f"   جارٍ مراقبة القناة: {TELEGRAM_CHANNEL}")
        
        # إذا لم يكن TELEGRAM_USER_ID محدد، استخدم ID المستخدم الحالي
        global TELEGRAM_USER_ID
        if not TELEGRAM_USER_ID:
            TELEGRAM_USER_ID = str(me.id)
            print(f"   تم تعيين TELEGRAM_USER_ID تلقائياً: {me.id}")
        
        # الانتظار
        await self.client.idle()
    
    def run(self):
        """تشغيل العميل"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\n⏹️ إيقاف العميل...")
        except Exception as e:
            print(f"خطأ في تشغيل العميل: {e}")
            import traceback
            traceback.print_exc()

# متغير عام للوصول للعميل من خارج الملف
telegram_client_instance = None

def get_telegram_client():
    """الحصول على instance العميل"""
    return telegram_client_instance

def run_bot():
    """تشغيل البوت في thread منفصل"""
    global telegram_client_instance
    client = TelegramClient()
    telegram_client_instance = client
    client.run()

if __name__ == '__main__':
    run_bot()
