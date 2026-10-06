"""
Cython module للبحث السريع جداً - تسريع اختياري يجب قياسه
"""
import mmap
from libc.string cimport memchr
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef inline bint case_insensitive_contains_fast(const unsigned char* haystack, 
                                                 size_t haystack_len,
                                                 const unsigned char* needle,
                                                 size_t needle_len):
    """
    بحث case-insensitive سريع جداً في bytes
    يستخدم C functions مباشرة
    """
    cdef size_t i, j
    cdef unsigned char h_char, n_char
    cdef bint match
    
    if needle_len > haystack_len:
        return False
    
    # البحث عن أول حرف (case-insensitive)
    for i in range(haystack_len - needle_len + 1):
        # مقارنة case-insensitive
        match = True
        for j in range(needle_len):
            h_char = haystack[i + j]
            n_char = needle[j]
            
            # تحويل إلى lowercase (ASCII فقط للسرعة)
            if h_char >= 65 and h_char <= 90:  # A-Z
                h_char += 32
            if n_char >= 65 and n_char <= 90:  # A-Z
                n_char += 32
            
            if h_char != n_char:
                match = False
                break
        
        if match:
            return True
    
    return False

@cython.boundscheck(False)
@cython.wraparound(False)
def search_in_file_cython(str file_path, list keywords_list, int max_results):
    """
    البحث السريع في ملف واحد باستخدام Cython
    Returns: (matches_count, lines_processed, results_list)
    """
    cdef int matches_count = 0
    cdef int lines_processed = 0
    cdef list results_list = []
    cdef list keywords_bytes = []
    cdef int min_keyword_len = 999999
    cdef bytes line_bytes
    cdef const unsigned char* line_ptr
    cdef size_t line_len
    cdef bint all_keywords_match
    cdef bytes kw_bytes
    cdef const unsigned char* kw_ptr
    cdef size_t kw_len
    cdef size_t start
    cdef size_t mm_len
    cdef size_t newline_pos
    cdef int line_number = 0
    cdef str file_name
    
    # تحضير keywords
    for keyword in keywords_list:
        kw_bytes = keyword.lower().encode('utf-8')
        keywords_bytes.append(kw_bytes)
        if len(kw_bytes) < min_keyword_len:
            min_keyword_len = len(kw_bytes)
    
    if min_keyword_len == 999999:
        return 0, 0, []
    
    # ترتيب من الأقصر للأطول
    keywords_bytes.sort(key=len)
    
    try:
        file_path_str = str(file_path)
        file_name = file_path_str.split('\\')[-1].split('/')[-1]
        
        # فتح الملف
        with open(file_path_str, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                start = 0
                mm_len = len(mm)
                
                while start < mm_len and matches_count < max_results:
                    # البحث عن السطر التالي
                    newline_pos = mm.find(b'\n', start)
                    
                    if newline_pos == -1:
                        line_bytes = mm[start:]
                        start = mm_len
                    else:
                        line_bytes = mm[start:newline_pos]
                        start = newline_pos + 1
                    
                    if not line_bytes:
                        continue
                    
                    line_len = len(line_bytes)
                    
                    # Early exit: تخطي الأسطر القصيرة
                    if line_len < min_keyword_len:
                        continue
                    
                    line_number += 1
                    lines_processed += 1
                    
                    # البحث السريع
                    line_ptr = <const unsigned char*>line_bytes
                    all_keywords_match = True
                    
                    for kw_bytes in keywords_bytes:
                        kw_ptr = <const unsigned char*>kw_bytes
                        kw_len = len(kw_bytes)
                        
                        if not case_insensitive_contains_fast(line_ptr, line_len, kw_ptr, kw_len):
                            all_keywords_match = False
                            break
                    
                    if all_keywords_match:
                        matches_count += 1
                        try:
                            line_text = line_bytes.decode('utf-8', errors='ignore').strip()
                            if line_text:
                                results_list.append((file_name, line_number, line_text))
                        except:
                            pass
    
    except Exception as e:
        print(f"خطأ في البحث Cython: {e}")
    
    return matches_count, lines_processed, results_list
