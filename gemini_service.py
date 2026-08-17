import logging
from google import genai
from google.genai import types

# إعداد نظام الـ Logging للمطور فقط
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MAX_TEXT_LENGTH = 15000  # حد أقصى للحماية من التجاوز

def process_study_request(api_key: str, text: str, task_mode: str, target_lang: str, academic_level: str):
    # 1. التحقق من طول النص المدخل
    if len(text) > MAX_TEXT_LENGTH:
        return False, f"⚠️ النص المدخل طويل جداً (يتجاوز {MAX_TEXT_LENGTH} حرف). يرجى تقليصه."

    # 2. القاموس المخصص لكل نمط دراسي
    prompts_map = {
        "📝 ملخص شامل + 3 أسئلة اختيار من متعدد": (
            "قم بإعداد ملخص هيكلي شديد التركيز للنص واستخرج أهم المفاهيم. "
            "ثم أضف في النهاية قسمًا مستقلًا يحتوي على 3 أسئلة اختيار من متعدد مع خياراتها وتحديد الإجابة الصحيحة."
        ),
        "🎴 بطاقات استذكار سريعة (Flashcards)": (
            "قم بتحويل النص إلى قائمة من بطاقات الاستذكار السريعة (Flashcards) بصيغة سياقية واضحة: "
            "\n- **السؤال/المفهوم**: ... \n  **الإجابة/الشرح**: ..."
        ),
        "🧠 شرح وتفكيك المفاهيم الصعبة": (
            "قم بتفكيك المصطلحات والمفاهيم المعقدة الواردة في النص بسلاسة وبأسلوب تعليمي مبسط مع إعطاء أمثلة توضيحية."
        ),
        "🎯 اختبار تقييمي مكثف مع الإجابات النموذجية": (
            "أنشئ اختبارًا تقييميًا كاملاً بناءً على النص يتكون من أسئلة مقالية وموضوعية متنوعة، "
            "وأرفق في نهاية الاختبار قسمًا مخصصًا للإجابات النموذجية للتصحيح الذاتي."
        )
    }

    selected_instruction = prompts_map.get(task_mode, "قم بتحليل وتنقيح النص دراسياً.")

    system_instruction = f"""
    أنت نظام تعليمي ذكي عالي الدقة.
    المستوى الدراسي المستهدف: {academic_level}.
    اللغة المطلوبة للمخرجات: {target_lang}.
    المهمة المطلوبة: {selected_instruction}

    تعليمات صارمة:
    1. صغ جميع المخرجات بالكامل باللغة المحدد ({target_lang}).
    2. استخدم تنسيق Markdown احترافي وجداول منظمة عند الحاجة.
    """

    try:
        logging.info(f"إرسال طلب جديد - النمط: {task_mode} | اللغة: {target_lang}")
        
        # الاتصال بالعميل باستخدام المفتاح الآمن
        client = genai.Client(api_key=api_key)

        # التوليد باستخدام نموذج Gemini 2.5 Flash المعتمد والمدعوم بمفتاحك
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=f"النص الأصلي للدرس:\n---\n{text}\n---",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            )
        )

        # التحقق من وجود استجابة صحيحة
        if response and response.text:
            return True, response.text
        else:
            return False, "⚠️ لم يتم استلام استجابة صالحة من النموذج. يرجى إعادة المحاولة."

    except Exception as exc:
        # تسجيل التفاصيل التقنية في الـ Log للمطور وعدم عرضها للمستخدم النهائي
        logging.error(f"خطأ في API: {str(exc)}")
        return False, "❌ تعذر الاتصال بمركز معالجة البيانات حالياً. يرجى التحقق من المفتاح أو حالة الشبكة."

