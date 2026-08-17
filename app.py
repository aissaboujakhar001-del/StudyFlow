import streamlit as st
from io import BytesIO
from pypdf import PdfReader
from docx import Document
import gemini_service as gs

st.set_page_config(
    page_title="StudyFlow Pro | المنصة التعليمية الذكية",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
    <style>
    .main { padding: 1.5rem; }
    .pricing-card { border: 2px solid #E5E7EB; border-radius: 15px; padding: 1.5rem; text-align: center; background: rgba(255, 255, 255, 0.05); }
    .pricing-featured { border: 2px solid #4F46E5; }
    .discount-tag { background-color: #EF4444; color: white; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

with st.sidebar:
    st.title("StudyFlow Pro")
    st.caption("⚡ المنصة التعليمية المتكاملة")
    st.divider()
    menu_choice = st.radio("القائمة:", ["🎯 مساحة العمل", "📚 الدروس المحفوظة", "💎 الاشتراكات", "⚙️ الإعدادات والحساب"])

if menu_choice == "🎯 مساحة العمل":
    st.title("🎯 مساحة العمل الذكية")
    
    col_input, col_config = st.columns([2, 1])

    uploaded_text = ""
    with col_input:
        file_upload = st.file_uploader("📁 ارفع ملف الدرس (PDF أو DOCX):", type=["pdf", "docx"])
        if file_upload:
            if file_upload.name.endswith(".pdf"):
                reader = PdfReader(file_upload)
                uploaded_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            elif file_upload.name.endswith(".docx"):
                doc = Document(file_upload)
                uploaded_text = "\n".join([p.text for p in doc.paragraphs])
        
        user_input = st.text_area(
            "📄 أو انسخ نص الدرس هنا:",
            value=uploaded_text,
            height=300,
            max_chars=15000
        )

    with col_config:
        task_mode = st.selectbox("نوع المخرجات:", [
            "📝 ملخص شامل + 3 أسئلة اختيار من متعدد",
            "🎴 بطاقات استذكار سريعة (Flashcards)",
            "🧠 شرح وتفكيك المفاهيم الصعبة",
            "🎯 اختبار تقييمي مكثف مع الإجابات النموذجية"
        ])
        target_lang = st.selectbox("اللغة:", ["العربية", "English", "Français", "Español"])
        academic_level = st.select_slider("المستوى الدراسي:", options=["المتوسط", "الثانوي", "الجامعي"])
        
        generate_btn = st.button("🚀 معالجة وتوليد", disabled=not API_KEY)

    if generate_btn:
        if not user_input.strip():
            st.warning("⚠️ يرجى إدخال نص أو رفع ملف أولاً.")
        else:
            with st.spinner("⚡ جاري المعالجة والانضباط في التوليد..."):
                success, result = gs.process_study_request(API_KEY, user_input, task_mode, target_lang, academic_level)
                if success:
                    st.session_state.last_result = result
                    st.session_state.history.append({"mode": task_mode, "content": result})
                    st.success("✨ تم التوليد بنجاح!")
                else:
                    st.error(result)

    if st.session_state.last_result:
        st.divider()
        st.markdown(st.session_state.last_result)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 تحميل النتيجة (TXT)", st.session_state.last_result, file_name="StudyFlow_Output.txt")
        with c2:
            if st.button("🔄 إعادة التوليد"):
                st.rerun()

elif menu_choice == "💎 الاشتراكات":
    st.title("💎 خطط الاشتراك المتاحة")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div class='pricing-card'><h3>🗓️ أسبوعي</h3><h2>$3.49 <small>/أسبوع</small></h2></div>""", unsafe_allow_html=True)
        if st.button("اختر الأسبوعي", key="p_w"):
            st.link_button("💳 الانتقال لبوابة الدفع الآمنة", "https://stripe.com")

    with col2:
        st.markdown("""<div class='pricing-card pricing-featured'><h3>📅 شهري</h3><h2>$8.99 <small>/شهر</small></h2></div>""", unsafe_allow_html=True)
        if st.button("اختر الشهري", key="p_m"):
            st.link_button("💳 الانتقال لبوابة الدفع الآمنة", "https://stripe.com")

    with col3:
        st.markdown("""<div class='pricing-card'><h3>🏆 سنوي</h3><h2>$69.99 <small>/سنة</small></h2></div>""", unsafe_allow_html=True)
        if st.button("اختر السنوي", key="p_y"):
            st.link_button("💳 الانتقال لبوابة الدفع الآمنة", "https://stripe.com")

elif menu_choice == "📚 الدروس المحفوظة":
    st.title("📚 أرشيف النتائج والدروس")
    if not st.session_state.history:
        st.info("لا توجد دروس محفوظة في هذه الجلسة بعد.")
    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"عنصر #{idx+1} - {item['mode']}"):
            st.markdown(item["content"])

else:
    st.title("⚙️ حالة الحساب والحدود")
    st.write("👤 **حالة الحساب:** مشترك نشط")
    st.write("📊 **استهلاك API اليومي:** 4 / 50 طلب")
    st.progress(4 / 50)
