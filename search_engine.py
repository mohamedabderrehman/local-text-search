"""
محرك البحث المحسّن - استخدام mmap + Cython + كتابة مباشرة في ملف
بحث محلي باستخدام ملفات الذاكرة + تحديثات تقدم دقيقة
"""
import mmap
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import os
import re
from typing import List, Tuple, Optional, Callable
from pathlib import Path
import multiprocessing
from multiprocessing import Manager, Pool
import threading
import time
import concurrent.futures

# محاولة استيراد Cython module (تسريع اختياري)
try:
    from search_engine_cython import search_in_file_cython
    CYTHON_AVAILABLE = True
    print("✓ Cython module محمّل - التسريع الاختياري مفعّل")
except ImportError:
    CYTHON_AVAILABLE = False
    print("⚠️ Cython غير متوفر - استخدام Python العادي (أبطأ)")
    print("   لتثبيت Cython: pip install cython && python setup.py build_ext --inplace")

def case_insensitive_contains(haystack: bytes, needle: bytes) -> bool:
    """
    بحث case-insensitive بدون نسخ السطر بالكامل
    أسرع من .lower() للملفات الكبيرة
    """
    if len(needle) > len(haystack):
        return False
    
    needle_lower = needle.lower()
    haystack_lower = haystack.lower()
    
    # استخدام find للبحث السريع
    return haystack_lower.find(needle_lower) != -1

def boyer_moore_search_simple(haystack: bytes, needle: bytes) -> bool:
    """
    بحث محسّن للكلمات الطويلة (أطول من 4 أحرف)
    يستخدم Boyer-Moore مبسط
    """
    if len(needle) > len(haystack):
        return False
    
    if len(needle) <= 4:
        # للكلمات القصيرة، البحث العادي أسرع
        return case_insensitive_contains(haystack, needle)
    
    # Boyer-Moore مبسط للكلمات الطويلة
    needle_lower = needle.lower()
    haystack_lower = haystack.lower()
    
    # جدول bad character
    bad_char = {}
    for i in range(len(needle_lower) - 1):
        bad_char[needle_lower[i]] = len(needle_lower) - 1 - i
    
    i = 0
    while i <= len(haystack_lower) - len(needle_lower):
        j = len(needle_lower) - 1
        
        # مطابقة من اليمين لليسار
        while j >= 0 and haystack_lower[i + j] == needle_lower[j]:
            j -= 1
        
        if j < 0:
            return True
        
        # القفز باستخدام bad character
        # Horspool's shift table is defined for the last byte of the window,
        # rather than the byte where comparison happened to fail.
        skip = bad_char.get(haystack_lower[i + len(needle_lower) - 1], len(needle_lower))
        i += max(1, skip)
    
    return False

# دالة top-level للعمل مع multiprocessing على Windows
def search_in_file_worker(args: Tuple) -> Tuple[int, int, List[Tuple]]:
    """
    Worker function للبحث في ملف واحد - يجب أن تكون top-level للعمل مع multiprocessing
    """
    file_path, keywords_bytes, max_results, job_id = args
    matches_count = 0
    lines_processed = 0
    results_batch = []
    
    try:
        # تحويل keywords إلى bytes للبحث السريع
        keywords_lower = [k.lower().encode('utf-8') for k in keywords_bytes]
        file_path = Path(file_path)
        file_name = file_path.name
        
        # ترتيب الكلمات من الأقصر للأطول (للتحسين)
        keywords_lower.sort(key=len)
        min_keyword_len = len(keywords_lower[0]) if keywords_lower else 0
        
        # فتح الملف في وضع binary لاستخدام mmap
        # استخدام 0 للحجم = mmap يحدد الحجم تلقائياً (أسرع بكثير)
        with open(file_path, 'rb') as f:
            # استخدام mmap مع 0 للحجم - أسرع بكثير من حساب الحجم يدوياً
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                line_number = 0
                start = 0
                total_size = len(mm)
                last_checkpoint = 0
                checkpoint_interval = 100000  # checkpoint كل 100k سطر
                
                while start < len(mm) and matches_count < max_results:
                    # البحث عن السطر التالي
                    newline_pos = mm.find(b'\n', start)
                    if newline_pos == -1:
                        # آخر سطر
                        line_bytes = mm[start:]
                        start = len(mm)
                    else:
                        line_bytes = mm[start:newline_pos]
                        start = newline_pos + 1
                    
                    if not line_bytes:
                        continue
                    
                    # Early exit: تخطي الأسطر القصيرة جداً
                    if len(line_bytes) < min_keyword_len:
                        continue
                    
                    line_number += 1
                    lines_processed += 1
                    
                    # البحث المحسّن بدون .lower() لكل سطر
                    # فحص الكلمات بالترتيب (الأقصر أولاً)
                    all_keywords_match = True
                    for keyword in keywords_lower:
                        # استخدام البحث المحسّن
                        if len(keyword) > 4:
                            if not boyer_moore_search_simple(line_bytes, keyword):
                                all_keywords_match = False
                                break
                        else:
                            if not case_insensitive_contains(line_bytes, keyword):
                                all_keywords_match = False
                                break
                    
                    if all_keywords_match:
                        matches_count += 1
                        
                        # إضافة للدفعة
                        try:
                            line_text = line_bytes.decode('utf-8', errors='ignore').strip()
                            if line_text:
                                results_batch.append((file_name, line_number, line_text))
                        except:
                            pass
                    
                    # Checkpoint للتحقق من التقدم (لا شيء - فقط للتحسين المستقبلي)
                    if lines_processed - last_checkpoint >= checkpoint_interval:
                        last_checkpoint = lines_processed
    
    except Exception as e:
        print(f"خطأ في البحث في {file_path}: {e}")
    
    return matches_count, lines_processed, results_batch

class SearchEngine:
    def __init__(self, corpus_dir=None, results_dir=None):
        import config
        corpus_dir = str(corpus_dir or config.CORPUS_DIR)
        results_dir = str(results_dir or config.RESULTS_DIR)
        self.corpus_dir = Path(corpus_dir)
        self.results_dir = Path(results_dir)
        # لا ننشئ مجلد Downloads - يجب أن يكون موجوداً
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.max_results = config.MAX_RESULTS  # حد أقصى للنتائج
        self._result_budgets = {}
        self.batch_size = 5000  # حجم الدفعة للكتابة
        self.update_interval = 100000  # تحديث كل 100k سطر
    
    def get_txt_files(self) -> List[Path]:
        """الحصول على جميع ملفات .txt في مجلد corpus"""
        if not self.corpus_dir.exists():
            return []
        return list(self.corpus_dir.glob("*.txt"))
    
    def write_results_batch(self, results_file: Path, batch: List[Tuple], lock):
        """كتابة دفعة من النتائج في الملف (thread-safe) مع buffering محسّن"""
        with lock:
            budget = self._result_budgets.get(results_file)
            if budget is not None:
                batch = batch[:max(0, budget['limit'] - budget['written'])]
            try:
                # استخدام buffering أكبر للكتابة السريعة
                with open(results_file, 'a', encoding='utf-8', errors='ignore', buffering=8192*4) as f:
                    # كتابة دفعة واحدة (أسرع من loop)
                    lines_to_write = []
                    for file_name, line_number, line_text in batch:
                        lines_to_write.append(f"FILE: {file_name} | LINE: {line_number}\n")
                        lines_to_write.append(f"{line_text}\n")
                        lines_to_write.append("-" * 80 + "\n")
                    f.writelines(lines_to_write)
                if budget is not None:
                    budget['written'] += len(batch)
            except Exception as e:
                print(f"خطأ في كتابة النتائج: {e}")
                raise
    
    def search_in_file_with_progress(self, file_path: Path, keywords: List[str], 
                                     job_id: int, db, max_results: int, 
                                     results_file: Path, write_lock) -> Tuple[int, int]:
        """
        البحث في ملف واحد مع تحديثات تقدم دورية
        يستخدم Cython إذا كان متوفراً (تسريع اختياري)
        """
        matches_count = 0
        lines_processed = 0
        results_batch = []
        
        # استخدام Cython إذا كان متوفراً
        if CYTHON_AVAILABLE:
            try:
                matches_count, lines_processed, results_list = search_in_file_cython(
                    str(file_path), keywords, max_results
                )
                
                # كتابة النتائج
                if results_list:
                    self.write_results_batch(results_file, results_list, write_lock)
                
                # تحديث قاعدة البيانات
                db.update_job_status(
                    job_id,
                    'running',
                    matches_count=matches_count,
                    files_searched=0,
                    total_files=0
                )
                
                return matches_count, lines_processed
            except Exception as e:
                print(f"خطأ في Cython، استخدام Python العادي: {e}")
                # Fallback إلى Python العادي
        
        # Python العادي (fallback)
        try:
            keywords_lower = [k.lower().encode('utf-8') for k in keywords]
            file_name = file_path.name
            
            # ترتيب الكلمات من الأقصر للأطول
            keywords_lower.sort(key=len)
            min_keyword_len = len(keywords_lower[0]) if keywords_lower else 0
            
            with open(file_path, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    line_number = 0
                    start = 0
                    total_size = len(mm)
                    last_status_update = time.time()
                    status_update_interval = 2.0  # تحديث كل ثانيتين
                    batch_write_threshold = 5000  # كتابة كل 5k نتيجة
                    
                    while start < len(mm) and matches_count < max_results:
                        newline_pos = mm.find(b'\n', start)
                        if newline_pos == -1:
                            line_bytes = mm[start:]
                            start = len(mm)
                        else:
                            line_bytes = mm[start:newline_pos]
                            start = newline_pos + 1
                        
                        if not line_bytes:
                            continue
                        
                        # Early exit: تخطي الأسطر القصيرة جداً
                        if len(line_bytes) < min_keyword_len:
                            continue
                        
                        line_number += 1
                        lines_processed += 1
                        
                        # البحث المحسّن
                        all_keywords_match = True
                        for keyword in keywords_lower:
                            if len(keyword) > 4:
                                if not boyer_moore_search_simple(line_bytes, keyword):
                                    all_keywords_match = False
                                    break
                            else:
                                if not case_insensitive_contains(line_bytes, keyword):
                                    all_keywords_match = False
                                    break
                        
                        if all_keywords_match:
                            matches_count += 1
                            try:
                                line_text = line_bytes.decode('utf-8', errors='ignore').strip()
                                if line_text:
                                    results_batch.append((file_name, line_number, line_text))
                            except:
                                pass
                        
                        # تحديث التقدم كل ثانيتين
                        current_time = time.time()
                        if current_time - last_status_update >= status_update_interval:
                            if results_batch:
                                self.write_results_batch(results_file, results_batch, write_lock)
                                results_batch = []
                            
                            db.update_job_status(
                                job_id,
                                'running',
                                matches_count=matches_count,
                                files_searched=0,
                                total_files=0
                            )
                            last_status_update = current_time
                        
                        elif len(results_batch) >= batch_write_threshold:
                            self.write_results_batch(results_file, results_batch, write_lock)
                            results_batch = []
                    
                    if results_batch:
                        self.write_results_batch(results_file, results_batch, write_lock)
        
        except Exception as e:
            print(f"خطأ في البحث في {file_path}: {e}")
        
        return matches_count, lines_processed
    
    def search(self, keywords: str, job_id: int, db, max_results: Optional[int] = None) -> dict:
        """
        البحث المحسّن في جميع الملفات مع تحديثات تقدم دقيقة + threading على Windows
        """
        if max_results is None:
            max_results = self.max_results
        if max_results < 1:
            raise ValueError('max_results must be positive')
        
        # تقسيم الكلمات المفتاحية
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if not keyword_list:
            return {"error": "لا توجد كلمات مفتاحية"}
        
        files = self.get_txt_files()
        if not files:
            db.update_job_status(job_id, 'failed')
            return {"error": "لا توجد ملفات للبحث"}
        
        total_files = len(files)
        
        # تحديث الحالة فوراً (قبل أي شيء)
        db.update_job_status(job_id, 'running', total_files=total_files)
        
        # إنشاء ملف النتائج
        results_file = self.results_dir / f"job_{job_id}_results.txt"
        self._result_budgets[results_file] = {'limit': max_results, 'written': 0}
        
        # كتابة رأس الملف
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"نتائج البحث - الوظيفة #{job_id}\n")
            f.write(f"الكلمات المفتاحية: {keywords}\n")
            f.write("=" * 80 + "\n\n")
        
        # Lock للكتابة الآمنة
        write_lock = threading.Lock()
        
        total_matches = 0
        files_searched = 0
        total_lines_processed = 0
        
        # استخدام threading على Windows للبحث المتوازي
        if os.name == 'nt' and len(files) > 1:
            # Windows: استخدام ThreadPoolExecutor للبحث المتوازي
            max_workers = min(4, len(files))  # حد أقصى 4 threads
            
            def search_single_file(file_path):
                """البحث في ملف واحد"""
                matches, lines = self.search_in_file_with_progress(
                    file_path, keyword_list, job_id, db, 
                    max_results - total_matches,
                    results_file, write_lock
                )
                return matches, lines, file_path
            
            # البحث المتوازي
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(search_single_file, f): f for f in files}
                
                for future in concurrent.futures.as_completed(futures):
                    if total_matches >= max_results:
                        # إلغاء المهام المتبقية
                        for f in futures:
                            f.cancel()
                        break
                    
                    try:
                        matches, lines, file_path = future.result()
                        total_matches += matches
                        total_lines_processed += lines
                        files_searched += 1
                        
                        # تحديث بعد كل ملف
                        db.update_job_status(
                            job_id,
                            'running',
                            matches_count=total_matches,
                            files_searched=files_searched,
                            total_files=total_files
                        )
                    except Exception as e:
                        print(f"خطأ في البحث في {file_path}: {e}")
        else:
            # البحث المتسلسل (للملفات القليلة أو الأنظمة غير Windows)
            for file_path in files:
                if total_matches >= max_results:
                    break
                
                # تحديث عند بدء ملف جديد
                db.update_job_status(
                    job_id,
                    'running',
                    matches_count=total_matches,
                    files_searched=files_searched,
                    total_files=total_files
                )
                
                # البحث مع تحديثات تقدم
                matches, lines = self.search_in_file_with_progress(
                    file_path, keyword_list, job_id, db, 
                    max_results - total_matches,
                    results_file, write_lock
                )
                
                total_matches += matches
                total_lines_processed += lines
                files_searched += 1
                
                # تحديث بعد كل ملف
                db.update_job_status(
                    job_id,
                    'running',
                    matches_count=total_matches,
                    files_searched=files_searched,
                    total_files=total_files
                )
        
        # Count only records actually accepted by the shared output budget.
        total_matches = self._result_budgets.pop(results_file)['written']
        # إنهاء الوظيفة
        db.update_job_status(
            job_id,
            'completed',
            matches_count=total_matches,
            files_searched=files_searched,
            total_files=total_files,
            lines_processed=total_lines_processed
        )
        
        return {
            "matches": total_matches,
            "files_searched": files_searched,
            "total_files": total_files,
            "lines_processed": total_lines_processed
        }
