import datetime
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WEBSITE_URLS = [
    "https://home.sam-isp.com/ar",
    "https://home.sam-isp.com/ar/offers",
    "https://home.sam-isp.com/ar/branches",
    "https://sam-isp.com/user/#/login",
]

EXTRA_COMPANY_INFO = """
معلومات مرجعية رسمية لشركة سام للاتصالات (SAM ISP):

1. آلية الاشتراك الجديد والتركيب:
- الخطوة 1: تسجيل دور تركيب في مراكز الشركة أو نقاط البيع، أو إرسال رسالة عبر واتساب أو تلغرام يطلب فيها الزبون التركيب ("بدي أركب").
- الخطوة 2: يتم التحقق من موقع الزبون للتأكد من وجود علب أو نقاط توزيع قريبة؛ وإذا لم تتوفر أو رغب الزبون بتركيب نقطة خاصة فتكون تجهيزاتها بالكامل على حسابه. يعتمد التركيب المباشر أو الحاجة لنقطة خاصة على تغطية المنطقة والعنوان.
- الخطوة 3: يطلب موظف خدمة الزبائن من المشترك (الاسم الكامل، العنوان بالتفصيل، ورقم الهاتف)، ثم ينسق فريق التركيب معه.
- الخطوة 4: يتوجه فريق التركيب لمد كبل الإنترنت إلى موقع المشترك.
- الخطوة 5: يراجع المشترك مقر الشركة ومعه (الهوية الشخصية + حساب Gmail) لكتابة عقد الاشتراك، وبرمجة الراوتر، ودفع الفاتورة (علماً أن فاتورة أول شهر تتضمن أجور التركيب).
- للتواصل والاستفسار: 0965313107.

2. خطوات سريعة عند بطء الإنترنت أو الانقطاع (قبل التحويل لموظف خدمة الزبائن):
- إعادة تشغيل الراوتر والهوائي/الصحن (فصل الكهرباء لمدة 30 ثانية ثم إعادة التشغيل).
- فحص الكابلات والتوصيلات الكهربائية والتأكد من ثباتها.
- التأكد من صلاحية الاشتراك والرصيد عبر صفحة حساب الزبون: https://sam-isp.com/user/#/login
- إذا استمر البطء أو الانقطاع بعد هذه الخطوات، يتم توجيه المشترك للتواصل مع خدمة الزبائن على الرقم 0965313107.

3. تسجيل الدخول إلى حساب الزبون وتنبيه حفظ البيانات:
- عبر الرابط https://sam-isp.com/user/#/login باستخدام اسم المستخدم وكلمة المرور اللذين وصلا إلى الزبون برسالة نصية وقت الاشتراك.
- يُنصح المشترك بالاحتفاظ باسم المستخدم وكلمة المرور في مكان آمن لمراجعة حالة الاشتراك والرصيد متى شاء.
- إذا لم تتوفر البيانات لدى الزبون، يُطلب منه التواصل مع رقم الشركة 0965313107.

4. أسعار الاشتراكات والعروض والباقات:
- عبر الرابط: https://home.sam-isp.com/ar/offers

5. مراكز الشركة والفروع في المحافظات:
- عبر الرابط: https://home.sam-isp.com/ar/branches

6. طرق الدفع وتفاصيل الشام كاش (ShamCash):
- تتوفر طرق الدفع عبر: مراكز الشركة، أو نقاط البيع، أو شام كاش (ShamCash).
- للدفع عن طريق شام كاش: يكون التواصل حصراً عبر واتساب الشركة ليتم إرسال باركود التحويل للمشترك، وبعد التحويل يرسل المشترك إشعار التحويل مع اسم المشترك كاملاً على واتساب الشركة ليتم تفعيل بطاقته.

7. أوقات العمل الرسمية:
- مركز دير الزور: يومياً من الساعة 9:00 صباحاً حتى 9:00 مساءً، ما عدا يوم الجمعة (عطلة رسمية).
- بقية المراكز في المحافظات: تُستخرج أوقات دوامها من صفحة الفروع في موقع الشركة https://home.sam-isp.com/ar/branches.

8. القنوات الرسمية ورقم التواصل:
- قناة الشركة على واتساب: https://whatsapp.com/channel/0029Valn9FwAe5VmAv77Se3Q/307
- صفحة الشركة على فيسبوك: https://www.facebook.com/samisp.net
- رقم التواصل الرئيسي للشركة: 0965313107
"""

STYLE_GUIDE = """
أسلوب الرد والترحيب والتنسيق:
- اكتب رداً مفصلاً وواضحاً ولطيفاً ومرِحباً بأسلوب دافئ ومحترم يعكس اهتمام شركة سام للاتصالات (SAM ISP) بالزبون.
- قسّم الردود الطويلة إلى فقرات قصيرة ونقاط واضحة بأسطر مرتبة لكي يسهل على الزبون قراءتها بوضوح على شاشة الهاتف.
- تذكّر سياق المحادثة السابقة مع الزبون وأكمل معه بشكل طبيعي دون تكرار التحية الطويلة في كل رسالة متتالية إذا كنتم وسط نقاش.
- اعتمد فقط على المعلومات المرجعية والأمثلة المتعلّمة من ردود الموظف، ولا تخترع أسعاراً أو تفاصيل غير موجودة.
- عند الحديث عن الاشتراك أو التركيب، وضّح أن التغطية ونقطة التوزيع أو النقطة الخاصة تعتمد على موقع الزبون وعنوانه، وذكّر بأهمية الاحتفاظ ببيانات الحساب المرسلة برسالة نصية وقت الاشتراك.
- إذا اشتكى الزبون من بطء أو انقطاع الإنترنت: رحّب به بلطف وقدّم له خطوات الفحص السريعة أولاً، ثم أخبره أنه في حال استمرار المشكلة يسعدنا متابعتها على الرقم 0965313107.
- للأعطال التقنية المعقدة أو الاستفسارات الفردية الخاصة غير المذكورة: وجّه للتواصل المباشر على 0965313107.
"""

REFRESH_INTERVAL = 3600
PAUSE_DURATION = 20 * 60
SITE_RETRIES = 2
MAX_HISTORY_TURNS = 10
MEMORY_TTL = 24 * 3600
BURST_DEBOUNCE_SECONDS = 2.5

MEMORY_FILE = "chat_memory.json"
LEARNED_FILE = "learned_faq.json"
UNANSWERED_FILE = "unanswered_questions.txt"
REQUESTS_LOG_FILE = "customer_requests.log"
DAILY_SUMMARY_FILE = "daily_summary.txt"
ADMIN_FILE = "admin_owner.json"
LEADS_FILE = "install_leads.json"

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
MODEL_CANDIDATES = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-2.5-pro",
    "gemma-4-31b-it",
]

KNOWN_AREAS = [
    "الجورة", "القصور", "الحميدية", "الموظفين", "العمال", "الجبيلة",
    "الرشدية", "الشيخ ياسين", "الصناعة", "غسان عبود", "المطار القديم",
    "هرابش", "البغيلية", "العشارة", "الميادين", "البوكمال", "الحسكة",
    "القامشلي", "الرقة", "دير الزور",
]

KNOWN_ROUTINE_KEYWORDS = [
    "سعر", "اسعار", "أسعار", "باقة", "باقات", "عرض", "عروض",
    "جودة", "جودة النت", "قوية", "ضعيفة", "شبكة", "تغطية",
    "اشتراك", "اركب", "أركب", "تركيب", "نقل", "نقطة", "علبة", "علب",
    "بطيء", "بطئ", "انقطاع", "فاصل", "مشكلة", "عطل", "راوتر",
    "شام كاش", "shamcash", "دفع", "فاتورة", "تجديد", "باركود", "إشعار", "اشعار",
    "حساب", "دخول", "كلمة مرور", "اسم المستخدم", "رصيد", "صلاحية",
    "دوام", "ساعات", "مواعيد", "جمعة", "فرع", "فروع", "مركز", "مراكز",
    "واتساب", "فيسبوك", "قناة", "صفحة", "رقم",
]

TRIVIAL_PHRASES = {
    "أريد أن أتأكد", "اريد ان اتاكد", "أريد أتأكد", "اريد اتاكد",
    "تمام", "ماشي", "اوك", "اوكي", "ok", "شكراً", "شكرا", "يعطيكم العافية",
    "مرحبا", "مرحباً", "السلام عليكم", "الو", "ألو", "وينكم", "ردوا",
}

processed_messages = set()
paused_chats = {}
last_customer_msg = {}
pending_bursts = {}
session_stats = {
    "total_replies": 0,
    "intents": {},
    "escalations": 0,
}
cached_site_data = ""
last_fetch_time = 0


def load_json_file(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[تحذير حفظ ملف {path}]: {e}")


chat_memory = load_json_file(MEMORY_FILE, {})
learned_faq = load_json_file(LEARNED_FILE, [])
admin_data = load_json_file(ADMIN_FILE, {"owner_id": None})
install_leads = load_json_file(LEADS_FILE, [])


def get_damascus_now():
    tz = datetime.timezone(datetime.timedelta(hours=3))
    return datetime.datetime.now(tz)


def is_working_hours_deir_ezzor():
    now = get_damascus_now()
    if now.weekday() == 4:
        return False, "يوم الجمعة (عطلة رسمية)"
    start_minutes = 9 * 60
    end_minutes = 21 * 60
    current_minutes = now.hour * 60 + now.minute
    if start_minutes <= current_minutes < end_minutes:
        return True, ""
    return False, f"خارج ساعات دوام مركز دير الزور (9:00 ص - 9:00 م، الوقت الحالي {now.strftime('%H:%M')})"


def set_owner_if_needed(user_id):
    if user_id and not admin_data.get("owner_id"):
        admin_data["owner_id"] = user_id
        save_json_file(ADMIN_FILE, admin_data)
        print(f"[تم تسجيل المالك الإداري]: {user_id}")


def is_owner(user_id):
    owner_id = admin_data.get("owner_id")
    return owner_id is not None and user_id == owner_id


def send_direct_message(chat_id, text):
    chunks = [text[i:i + 3900] for i in range(0, len(text), 3900)] or [text]
    for chunk in chunks:
        try:
            requests.post(
                f"{TG_API}/sendMessage",
                json={"chat_id": chat_id, "text": chunk},
                timeout=15,
            )
        except Exception as e:
            print(f"[خطأ إرسال رسالة خاصة]: {e}")


def notify_owner(text):
    owner_id = admin_data.get("owner_id")
    if owner_id:
        send_direct_message(owner_id, text)


def detect_intent(text):
    t = text.lower()
    if any(k in t for k in ["اشتراك", "اركب", "أركب", "تركيب", "نقل", "نقطة", "علبة", "علب", "تغطية", "بدي ركب", "بدي اركب"]):
        return "اشتراك_وتركيب"
    if any(k in t for k in ["بطيء", "بطئ", "انقطاع", "فاصل", "مشكلة", "عطل", "نت ضعيف", "لا يعمل", "ما في نت", "راوتر"]):
        return "عطل_او_بطء"
    if any(k in t for k in ["شام كاش", "shamcash", "دفع", "فاتورة", "تجديد", "باركود", "اشعار", "إشعار", "بطاقة"]):
        return "دفع_وتجديد"
    if any(k in t for k in ["دخول", "حساب", "كلمة مرور", "كلمة السر", "اسم المستخدم", "رصيد", "صلاحية", "اشتراكى", "اشتراكي"]):
        return "حساب_ودخول"
    if any(k in t for k in ["دوام", "ساعات", "مواعيد", "جمعة", "فرع", "فروع", "مركز", "مراكز", "عنوان", "دير الزور"]):
        return "فروع_ودوام"
    if any(k in t for k in ["سعر", "اسعار", "أسعار", "باقة", "باقات", "عرض", "عروض"]):
        return "اسعار_وعروض"
    if any(k in t for k in ["واتساب", "واتس", "فيسبوك", "فيس", "قناة", "صفحة"]):
        return "قنوات_تواصل"
    return "استفسار_عام"


def is_routine_or_trivial_part(part):
    cleaned = part.strip()
    if len(cleaned) < 4:
        return True
    low = cleaned.lower()
    if low in TRIVIAL_PHRASES:
        return True
    if re.fullmatch(r"[\d\s\+\-]+", cleaned):
        return True
    if any(k in low for k in KNOWN_ROUTINE_KEYWORDS):
        return True
    return False


def maybe_log_unanswered_question(full_text, intent):
    if intent != "استفسار_عام":
        return

    parts = [p.strip() for p in re.split(r"[|\n]+", full_text) if p.strip()]
    noteworthy_parts = [p for p in parts if not is_routine_or_trivial_part(p)]
    if not noteworthy_parts:
        return

    candidate = " / ".join(noteworthy_parts)[:180]
    existing = set()
    if os.path.exists(UNANSWERED_FILE):
        try:
            with open(UNANSWERED_FILE, "r", encoding="utf-8") as f:
                existing = {line.strip().lstrip("-").strip() for line in f if line.strip()}
        except Exception:
            pass

    if candidate not in existing:
        try:
            with open(UNANSWERED_FILE, "a", encoding="utf-8") as f:
                f.write(f"- {candidate}\n")
        except Exception:
            pass


def extract_lead_info(text):
    phones = re.findall(r"(?:\+?963|0)?9\d{8}", re.sub(r"\s+", "", text))
    phone = phones[0] if phones else ""

    found_areas = [a for a in KNOWN_AREAS if a in text]
    area = "، ".join(found_areas) if found_areas else ""

    name = ""
    name_match = re.search(r"(?:اسمي|أنا|انا)\s+([\u0600-\u06FF]{2,15}(?:\s+[\u0600-\u06FF]{2,15})?)", text)
    if name_match:
        candidate = name_match.group(1).strip()
        stop_words = {"من", "في", "بدي", "اريد", "أريد", "عندي", "مشترك", "زبون", "بالجورة", "بالقصور"}
        words = [w for w in candidate.split() if w not in stop_words]
        if words:
            name = " ".join(words[:2])

    return {"name": name, "area": area, "phone": phone}


def maybe_record_lead_and_alert(chat_id, intent, text):
    info = extract_lead_info(text)
    has_lead_signal = (intent == "اشتراك_وتركيب") or bool(info["area"]) or bool(info["phone"])

    if has_lead_signal:
        record = {
            "time": get_damascus_now().strftime("%Y-%m-%d %H:%M"),
            "chat_id": chat_id,
            "intent": intent,
            "name": info["name"] or "غير مذكور",
            "area": info["area"] or "غير محدد",
            "phone": info["phone"] or "غير مذكور",
            "message": text.strip()[:200],
        }
        install_leads.append(record)
        if len(install_leads) > 200:
            install_leads.pop(0)
        save_json_file(LEADS_FILE, install_leads)

    t_low = text.lower()
    urgent_signals = []
    if any(w in t_low for w in ["عطل عام", "انقطاع عام", "فاصل بالمنطقة", "الحي كله", "الشارع كله"]):
        urgent_signals.append("بلاغ عطل/انقطاع في منطقة")
    if any(w in t_low for w in ["نصب", "احتيال", "سيء جداً", "زفت", "مهزلة", "غضبان", "مزعج"]):
        urgent_signals.append("شكوى أو انزعاج عالٍ")
    if intent == "اشتراك_وتركيب" and info["area"]:
        urgent_signals.append(f"طلب تركيب في: {info['area']}")

    if urgent_signals:
        alert_msg = (
            "🚨 تنبيه فوري من بوت شركة سام:\n"
            f"• السبب: {' | '.join(urgent_signals)}\n"
            f"• المحادثة: {chat_id}\n"
            f"• المنطقة: {info['area'] or 'غير محددة'} | الرقم: {info['phone'] or 'غير مذكور'}\n"
            f"• الرسالة: {text.strip()[:220]}"
        )
        print(alert_msg)
        notify_owner(alert_msg)


def log_customer_request(chat_id, intent, text):
    stamp = get_damascus_now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{stamp}] | Chat: {chat_id} | Intent: {intent} | Msg: {text.strip()}\n"
    try:
        with open(REQUESTS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"[تحذير سجل الطلبات]: {e}")


def get_chat_history(chat_id):
    cid = str(chat_id)
    entry = chat_memory.get(cid)
    if not entry:
        return []
    if time.time() - entry.get("updated_at", 0) > MEMORY_TTL:
        del chat_memory[cid]
        save_json_file(MEMORY_FILE, chat_memory)
        return []
    return entry.get("messages", [])


def append_chat_history(chat_id, role, text):
    cid = str(chat_id)
    history = get_chat_history(chat_id)
    history.append({"role": role, "text": text})
    history = history[-MAX_HISTORY_TURNS:]
    chat_memory[cid] = {"updated_at": time.time(), "messages": history}
    save_json_file(MEMORY_FILE, chat_memory)


def record_learned_example(question, human_reply):
    q = question.strip()
    a = human_reply.strip()
    if len(q) < 3 or len(a) < 4:
        return
    for item in learned_faq:
        if item.get("q") == q:
            item["a"] = a
            save_json_file(LEARNED_FILE, learned_faq)
            print("[تعلّم ذاتي] تم تحديث إجابة متعلّمة من ردك اليدوي.")
            return
    learned_faq.append({"q": q, "a": a})
    if len(learned_faq) > 50:
        learned_faq.pop(0)
    save_json_file(LEARNED_FILE, learned_faq)
    print("[تعلّم ذاتي] تم حفظ ردك اليدوي كمرجع جديد للبوت.")


def format_learned_knowledge():
    if not learned_faq:
        return ""
    lines = ["أمثلة إضافية متعلّمة من ردود موظف خدمة الزبائن:"]
    for item in learned_faq[-15:]:
        lines.append(f"- سؤال مشابه: {item['q']} -> الرد المعتمد: {item['a']}")
    return "\n".join(lines)


def list_available_models():
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers_list = [
        {"x-goog-api-key": GEMINI_API_KEY, "Authorization": f"Bearer {GEMINI_API_KEY}"},
        {},
    ]
    for hdrs in headers_list:
        try:
            target = url if hdrs else f"{url}?key={GEMINI_API_KEY}"
            r = requests.get(target, headers=hdrs, timeout=15)
            if r.status_code == 200:
                models = [m.get("name", "").replace("models/", "") for m in r.json().get("models", [])]
                if models:
                    print("النماذج المتاحة:", ", ".join(models[:8]))
                    return
        except Exception:
            pass


def extract_clean_page_text(html_text, limit=3400):
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        tag.decompose()

    seen = set()
    useful_lines = []
    for elem in soup.find_all(["h1", "h2", "h3", "h4", "li", "p", "td", "th", "div"]):
        if elem.name == "div" and elem.find(["h1", "h2", "h3", "h4", "li", "p", "table"]):
            continue
        line = re.sub(r"\s+", " ", elem.get_text(" ", strip=True)).strip()
        if len(line) < 2 or len(line) > 400 or line in seen:
            continue
        seen.add(line)
        useful_lines.append(line)

    if not useful_lines:
        for raw_line in soup.get_text("\n").splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if len(line) >= 2 and line not in seen:
                seen.add(line)
                useful_lines.append(line)

    return "\n".join(useful_lines)[:limit]


def fetch_url_with_retry(url, headers, retries=SITE_RETRIES):
    last_error = None
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=12)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(2)
    raise last_error


def get_website_knowledge(force_refresh=False):
    global cached_site_data, last_fetch_time
    now = time.time()
    if not force_refresh and cached_site_data and (now - last_fetch_time < REFRESH_INTERVAL):
        return cached_site_data

    print("جاري تحديث بيانات الموقع...")
    parts = [EXTRA_COMPANY_INFO.strip()]
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 13)"}
    for url in WEBSITE_URLS:
        try:
            html_text = fetch_url_with_retry(url, headers=headers)
            clean_text = extract_clean_page_text(html_text, limit=3400)
            if clean_text:
                parts.append(f"=== {url} ===\n{clean_text}")
        except Exception as e:
            print(f"[تحذير] {url}: {e}")

    cached_site_data = "\n\n".join(parts)[:14500]
    last_fetch_time = now
    print("تم تحديث بيانات الموقع بنجاح.")
    return cached_site_data


def build_prompt_payload(chat_id, user_text, intent, model_name):
    site_data = get_website_knowledge()
    learned_text = format_learned_knowledge()
    in_hours, hours_note = is_working_hours_deir_ezzor()
    shift_status = (
        "الموظفون ضمن أوقات الدوام الرسمية (9:00 ص - 9:00 م ما عدا الجمعة)."
        if in_hours
        else f"الرسالة واردة {hours_note}. وضّح بلطف أن متابعة الموظفين المباشرة تكون في أوقات الدوام الرسمية مع تقديم المساعدة الفورية والرقم 0965313107."
    )

    system_prompt = (
        "أنت مساعد خدمة عملاء رسمي لشركة سام للاتصالات (SAM ISP).\n"
        f"النية المكتشفة لرسالة الزبون الحالية: {intent}\n"
        f"حالة الدوام الحالية: {shift_status}\n"
        f"{site_data}\n\n"
        f"{learned_text}\n\n"
        f"{STYLE_GUIDE}"
    )

    history = get_chat_history(chat_id)
    contents = []
    for turn in history:
        api_role = "model" if turn["role"] == "bot" else "user"
        contents.append({"role": api_role, "parts": [{"text": turn["text"]}]})
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    if model_name.startswith("gemma-"):
        history_lines = []
        for turn in history:
            who = "المساعد" if turn["role"] == "bot" else "الزبون"
            history_lines.append(f"{who}: {turn['text']}")
        history_block = "\n".join(history_lines)
        combined = (
            f"{system_prompt}\n\nسجل المحادثة السابقة:\n{history_block}\n\n"
            f"رسالة الزبون الحالية:\n{user_text}"
        )
        return {
            "contents": [{"role": "user", "parts": [{"text": combined}]}],
            "generationConfig": {"temperature": 0.35},
        }

    return {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.35},
    }


def generate_ai_reply(chat_id, user_text, intent):
    last_err = None
    for model_name in MODEL_CANDIDATES:
        payload = build_prompt_payload(chat_id, user_text, intent, model_name)
        base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        calls = [
            (
                base_url,
                {
                    "Content-Type": "application/json",
                    "x-goog-api-key": GEMINI_API_KEY,
                    "Authorization": f"Bearer {GEMINI_API_KEY}",
                },
            ),
            (f"{base_url}?key={GEMINI_API_KEY}", {"Content-Type": "application/json"}),
        ]

        for url, hdrs in calls:
            try:
                r = requests.post(url, headers=hdrs, json=payload, timeout=25)
                data = r.json()
                if r.status_code == 200:
                    cands = data.get("candidates", [])
                    if cands:
                        txt = "".join(p.get("text", "") for p in cands[0].get("content", {}).get("parts", [])).strip()
                        if txt:
                            print(f"[تم التوليد عبر النموذج: {model_name}]")
                            if "0965313107" in txt and intent == "استفسار_عام":
                                session_stats["escalations"] += 1
                            maybe_log_unanswered_question(user_text, intent)
                            return txt
                    return (
                        "أهلاً وسهلاً بك في شركة سام للاتصالات!\n"
                        "تم استلام رسالتك وسيقوم فريق الدعم بالرد عليك بكل سرور.\n"
                        "يمكنك أيضاً التواصل معنا مباشرة على الرقم: 0965313107."
                    )
                last_err = (model_name, r.status_code, data)
                time.sleep(1.2)
            except Exception as e:
                last_err = (model_name, str(e))
                time.sleep(1.2)

    print(f"[خطأ Gemini API]: {last_err}")
    return (
        "أهلاً بك في شركة سام للاتصالات!\n"
        "نعتذر منك لوجود خلل مؤقت أثناء معالجة طلبك حالياً.\n"
        "يرجى المحاولة بعد قليل أو التواصل معنا على الرقم 0965313107 لنخدمك بكل محبة."
    )


def send_business_reply(connection_id, chat_id, text):
    payload = {"business_connection_id": connection_id, "chat_id": chat_id, "text": text}
    try:
        r = requests.post(f"{TG_API}/sendMessage", json=payload, timeout=15)
        data = r.json()
        if not data.get("ok"):
            print(f"[خطأ إرسال تلغرام]: {data}")
        else:
            session_stats["total_replies"] += 1
            print(f"تم إرسال الرد بنجاح إلى {chat_id}")
    except Exception as e:
        print(f"[خطأ شبكة]: {e}")


def check_expired_pauses():
    now = time.time()
    expired_ids = [cid for cid, until in paused_chats.items() if now >= until]
    for cid in expired_ids:
        del paused_chats[cid]
        msg = f"🔄 انتهت فترة الإيقاف المؤقت (20 دقيقة) وعاد البوت للرد التلقائي في المحادثة {cid}."
        print(msg)
        notify_owner(msg)


def is_chat_paused(chat_id):
    check_expired_pauses()
    pause_until = paused_chats.get(chat_id)
    if not pause_until:
        return False
    remaining = pause_until - time.time()
    if remaining > 0:
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        print(f"[إيقاف مؤقت] المحادثة {chat_id} متوقفة بسبب تدخل يدوي (متبقي {mins}د {secs}ث)")
        return True
    del paused_chats[chat_id]
    return False


def build_leads_and_areas_text():
    area_counts = {}
    for item in install_leads:
        raw_areas = item.get("area", "")
        if raw_areas and raw_areas != "غير محدد":
            for a in [x.strip() for x in raw_areas.split("،") if x.strip()]:
                area_counts[a] = area_counts.get(a, 0) + 1

    areas_sorted = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)
    areas_lines = "\n".join(f"• {a}: {c}" for a, c in areas_sorted[:8]) if areas_sorted else "• لا توجد مناطق محددة بعد"

    recent_leads = install_leads[-8:]
    leads_lines = "\n".join(
        f"• [{l['time']}] الاسم: {l['name']} | المنطقة: {l['area']} | الرقم: {l['phone']} | ({l['intent']})"
        for l in reversed(recent_leads)
    ) if recent_leads else "• لا توجد طلبات أو بيانات مستخرجة بعد"

    return (
        "📍 جرد الطلبات والمناطق الأكثر ذكراً:\n\n"
        f"🏙️ أكثر المناطق تكرراً:\n{areas_lines}\n\n"
        f"📋 أحدث الطلبات المسجلة:\n{leads_lines}"
    )


def build_daily_summary_text():
    recent_requests = []
    if os.path.exists(REQUESTS_LOG_FILE):
        try:
            with open(REQUESTS_LOG_FILE, "r", encoding="utf-8") as f:
                recent_requests = [line.strip() for line in f if line.strip()][-10:]
        except Exception:
            pass

    recent_unanswered = []
    if os.path.exists(UNANSWERED_FILE):
        try:
            with open(UNANSWERED_FILE, "r", encoding="utf-8") as f:
                recent_unanswered = [line.strip() for line in f if line.strip()][-8:]
        except Exception:
            pass

    intents_sorted = sorted(session_stats["intents"].items(), key=lambda x: x[1], reverse=True)
    intents_lines = "\n".join(f"• {k}: {v}" for k, v in intents_sorted) if intents_sorted else "• لا توجد بيانات بعد"
    req_lines = "\n".join(f"• {r}" for r in recent_requests) if recent_requests else "• لا توجد طلبات مسجلة"
    unans_lines = "\n".join(f"• {u}" for u in recent_unanswered) if recent_unanswered else "• لا توجد أسئلة جديدة تحتاج مراجعة"

    summary_text = (
        f"📊 ملخص أداء بوت شركة سام - {get_damascus_now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"✅ إجمالي الردود المرسلة: {session_stats['total_replies']}\n"
        f"📞 حالات التوجيه للدعم (0965313107): {session_stats['escalations']}\n"
        f"🧠 الردود المتعلّمة المحفوظة: {len(learned_faq)}\n"
        f"📌 إجمالي الطلبات والبيانات المستخرجة: {len(install_leads)}\n\n"
        f"📌 توزيع الاستفسارات:\n{intents_lines}\n\n"
        f"📝 آخر الطلبات المسجلة:\n{req_lines}\n\n"
        f"💡 أسئلة جديدة يُنصح بمراجعتها:\n{unans_lines}"
    )

    print("\n" + summary_text + "\n")
    try:
        with open(DAILY_SUMMARY_FILE, "w", encoding="utf-8") as f:
            f.write(summary_text + "\n")
    except Exception:
        pass
    return summary_text


def build_status_text():
    check_expired_pauses()
    active_pauses = sum(1 for u in paused_chats.values() if u > time.time())
    unanswered_count = 0
    if os.path.exists(UNANSWERED_FILE):
        try:
            with open(UNANSWERED_FILE, "r", encoding="utf-8") as f:
                unanswered_count = sum(1 for line in f if line.strip())
        except Exception:
            pass
    in_hours, hours_note = is_working_hours_deir_ezzor()
    shift_txt = "ضمن الدوام الرسمي" if in_hours else f"خارج الدوام ({hours_note})"
    return (
        "⚙️ حالة البوت الحالية:\n"
        f"• حالة الدوام: {shift_txt}\n"
        f"• المحادثات الموقوفة مؤقتاً: {active_pauses}\n"
        f"• الردود المتعلّمة منك: {len(learned_faq)}\n"
        f"• الأسئلة الجديدة المحفوظة للمراجعة: {unanswered_count}\n"
        f"• إجمالي الردود في هذه الجلسة: {session_stats['total_replies']}"
    )


def reset_session_stats():
    session_stats["total_replies"] = 0
    session_stats["intents"] = {}
    session_stats["escalations"] = 0


def handle_private_bot_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    sender = msg.get("from", {})
    sender_id = sender.get("id")
    text = (msg.get("text") or "").strip()

    if not chat_id or not sender_id or sender.get("is_bot"):
        return

    set_owner_if_needed(sender_id)

    if not is_owner(sender_id):
        send_direct_message(
            chat_id,
            "أهلاً بك في بوت شركة سام للاتصالات (SAM ISP).\nللاستفسار والدعم المباشر يرجى مراسلة حساب الشركة الرسمي أو الاتصال على الرقم: 0965313107.",
        )
        return

    cmd = text.lower()
    if cmd in ("/start", "/help", "/مساعدة", "مساعدة"):
        send_direct_message(
            chat_id,
            "أهلاً بك يا مدير! أوامر لوحة التحكم المتاحة لك في الخاص:\n"
            "• /ملخص — عرض ملخص الأداء والطلبات والأسئلة الجديدة\n"
            "• /طلبات أو /مناطق — جرد أحدث الطلبات والمناطق الأكثر تكرراً\n"
            "• /حالة — عرض حالة البوت والدوام والمحادثات الموقوفة\n"
            "• /تحديث — تحديث بيانات موقع الشركة فوراً\n"
            "• /تصفير — تصفير عدّاد الجلسة الحالية\n"
            "• (وداخل أي محادثة زبون: /تشغيل لإلغاء الإيقاف المؤقت فوراً)",
        )
    elif cmd in ("/ملخص", "ملخص", "/summary"):
        summary = build_daily_summary_text()
        send_direct_message(chat_id, summary)
    elif cmd in ("/طلبات", "طلبات", "/مناطق", "مناطق", "/leads"):
        leads_txt = build_leads_and_areas_text()
        print("\n" + leads_txt + "\n")
        send_direct_message(chat_id, leads_txt)
    elif cmd in ("/حالة", "حالة", "/status"):
        status = build_status_text()
        print(status)
        send_direct_message(chat_id, status)
    elif cmd in ("/تحديث", "تحديث", "/refresh"):
        get_website_knowledge(force_refresh=True)
        send_direct_message(chat_id, "✅ تم تحديث بيانات موقع الشركة بنجاح.")
    elif cmd in ("/تصفير", "تصفير", "/reset"):
        reset_session_stats()
        print("[أمر إداري] تم تصفير عدّاد الجلسة.")
        send_direct_message(chat_id, "🧹 تم تصفير إحصائيات الجلسة بنجاح.")
    else:
        send_direct_message(
            chat_id,
            "أمر غير معروف. أرسل /مساعدة لعرض الأوامر المتاحة (/ملخص، /طلبات، /حالة، /تحديث، /تصفير).",
        )


def handle_business_admin_command(chat_id, text):
    cmd = text.strip().lower()
    owner_id = admin_data.get("owner_id")
    if cmd in ("/تحديث", "تحديث", "/refresh"):
        get_website_knowledge(force_refresh=True)
        print("[أمر إداري] تم تحديث بيانات الموقع يدوياً.")
        if owner_id:
            send_direct_message(owner_id, "✅ تم تحديث بيانات موقع الشركة بنجاح.")
        return True
    if cmd in ("/حالة", "حالة", "/status"):
        status = build_status_text()
        print(status)
        if owner_id:
            send_direct_message(owner_id, status)
        return True
    if cmd in ("/تشغيل", "تشغيل", "/resume"):
        if chat_id in paused_chats:
            del paused_chats[chat_id]
            print(f"[أمر إداري] تم إلغاء الإيقاف المؤقت عن المحادثة {chat_id}.")
        else:
            print(f"[أمر إداري] المحادثة {chat_id} غير متوقفة أصلاً.")
        return True
    if cmd in ("/ملخص", "ملخص", "/summary"):
        summary = build_daily_summary_text()
        if owner_id:
            send_direct_message(owner_id, summary)
        return True
    if cmd in ("/طلبات", "طلبات", "/مناطق", "مناطق", "/leads"):
        leads_txt = build_leads_and_areas_text()
        print("\n" + leads_txt + "\n")
        if owner_id:
            send_direct_message(owner_id, leads_txt)
        return True
    if cmd in ("/تصفير", "تصفير", "/reset"):
        reset_session_stats()
        print("[أمر إداري] تم تصفير عدّاد الجلسة.")
        if owner_id:
            send_direct_message(owner_id, "🧹 تم تصفير إحصائيات الجلسة بنجاح.")
        return True
    return False


def flush_ready_bursts():
    check_expired_pauses()
    now = time.time()
    ready_chat_ids = [
        cid for cid, info in pending_bursts.items()
        if (now - info["last_time"]) >= BURST_DEBOUNCE_SECONDS
    ]
    for cid in ready_chat_ids:
        info = pending_bursts.pop(cid)
        if is_chat_paused(cid):
            continue

        combined_text = " | ".join(info["texts"]).strip()
        if not combined_text:
            continue

        intent = detect_intent(combined_text)
        session_stats["intents"][intent] = session_stats["intents"].get(intent, 0) + 1
        log_customer_request(cid, intent, combined_text)
        maybe_record_lead_and_alert(cid, intent, combined_text)

        print(f"[رسالة واردة من {cid}] (نية: {intent}): {combined_text}")
        reply = generate_ai_reply(cid, combined_text, intent)
        append_chat_history(cid, "user", combined_text)
        append_chat_history(cid, "bot", reply)
        send_business_reply(info["conn_id"], cid, reply)


def run_bot():
    list_available_models()
    get_website_knowledge(force_refresh=True)
    offset = None
    print("البوت قيد التشغيل الآن وينتظر رسائل المحادثة الآلية...")

    while True:
        try:
            flush_ready_bursts()

            params = {"timeout": 5}
            if offset is not None:
                params["offset"] = offset
            data = requests.get(f"{TG_API}/getUpdates", params=params, timeout=15).json()
            if not data.get("ok"):
                print(f"[خطأ getUpdates]: {data}")
                time.sleep(5)
                continue

            for upd in data.get("result", []):
                offset = upd["update_id"] + 1

                direct_msg = upd.get("message")
                if direct_msg and direct_msg.get("chat", {}).get("type") == "private":
                    handle_private_bot_message(direct_msg)
                    continue

                msg = upd.get("business_message") or upd.get("edited_business_message")
                if not msg:
                    continue

                msg_id = msg.get("message_id")
                chat_id = msg.get("chat", {}).get("id")
                sender = msg.get("from", {})
                sender_id = sender.get("id")
                conn_id = msg.get("business_connection_id")
                text = msg.get("text")

                if not conn_id or not chat_id:
                    continue

                unique_key = f"{upd['update_id']}:{conn_id}:{chat_id}:{msg_id}"
                if unique_key in processed_messages:
                    continue
                processed_messages.add(unique_key)
                if len(processed_messages) > 5000:
                    processed_messages.clear()

                if sender.get("is_bot") or (sender_id and sender_id != chat_id):
                    if not sender.get("is_bot") and sender_id:
                        set_owner_if_needed(sender_id)
                    if text and handle_business_admin_command(chat_id, text):
                        continue
                    paused_chats[chat_id] = time.time() + PAUSE_DURATION
                    print(f"[تدخل يدوي] تم إيقاف البوت على المحادثة {chat_id} لمدة 20 دقيقة.")
                    if text and chat_id in last_customer_msg:
                        record_learned_example(last_customer_msg[chat_id], text)
                        append_chat_history(chat_id, "bot", text)
                    continue

                if not text:
                    continue

                last_customer_msg[chat_id] = text

                if is_chat_paused(chat_id):
                    append_chat_history(chat_id, "user", text)
                    continue

                if chat_id not in pending_bursts:
                    pending_bursts[chat_id] = {
                        "conn_id": conn_id,
                        "texts": [text.strip()],
                        "last_time": time.time(),
                    }
                else:
                    pending_bursts[chat_id]["conn_id"] = conn_id
                    pending_bursts[chat_id]["texts"].append(text.strip())
                    pending_bursts[chat_id]["last_time"] = time.time()

            flush_ready_bursts()
        except KeyboardInterrupt:
            print("\nتم إيقاف البوت.")
            break
        except Exception as e:
            print(f"[خطأ عام]: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
