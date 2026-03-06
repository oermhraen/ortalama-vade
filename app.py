import streamlit as st
from datetime import date, timedelta

st.set_page_config(
    page_title="Çek Ortalama Vade Hesaplayıcı",
    layout="wide"
)

# -------------------------------------------------
# Yardımcı fonksiyonlar
# -------------------------------------------------
def parse_amount(text):
    if text is None:
        return 0

    text = str(text).strip().upper()
    text = text.replace("TL", "").replace(" ", "")

    if text == "":
        return 0

    cleaned = text.replace(".", "").replace(",", "")

    try:
        return max(int(cleaned), 0)
    except:
        return 0


def format_amount_input(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except:
        return ""


def format_tl(value):
    try:
        return f"{int(round(value)):,}".replace(",", ".") + " TL"
    except:
        return "0 TL"


def format_date_tr(d):
    return d.strftime("%d.%m.%Y")


# -------------------------------------------------
# Session state
# -------------------------------------------------
if "checks" not in st.session_state:
    st.session_state.checks = [
        {
            "id": 1,
            "active": True,
            "amount_text": "",
            "due_date": date.today()
        }
    ]

if "counter" not in st.session_state:
    st.session_state.counter = 2


def add_check():
    st.session_state.checks.append(
        {
            "id": st.session_state.counter,
            "active": True,
            "amount_text": "",
            "due_date": date.today()
        }
    )
    st.session_state.counter += 1


def clear_all():
    st.session_state.checks = [
        {
            "id": 1,
            "active": True,
            "amount_text": "",
            "due_date": date.today()
        }
    ]
    st.session_state.counter = 2

    # widget state temizliği
    for key in list(st.session_state.keys()):
        if key.startswith("amount_") or key.startswith("due_") or key.startswith("active_"):
            del st.session_state[key]


def normalize_amount_field(item_id):
    key = f"amount_{item_id}"
    raw_value = st.session_state.get(key, "")
    parsed = parse_amount(raw_value)

    if parsed > 0:
        st.session_state[key] = format_amount_input(parsed)
    else:
        st.session_state[key] = ""


# -------------------------------------------------
# Stil
# -------------------------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1280px;
    padding-top: 0.8rem;
    padding-bottom: 1.2rem;
}

h1 {
    margin-bottom: 0.8rem !important;
}

div[data-testid="stMetric"] {
    background: #f7f7f9;
    border: 1px solid #e5e7eb;
    padding: 12px 14px;
    border-radius: 12px;
}

.main-card, .side-card, .item-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
}

.main-card, .side-card {
    padding: 14px;
}

.item-card {
    padding: 12px;
    margin-bottom: 12px;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 12px;
}

.item-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-weight: 700;
    color: #1f2937;
}

.item-label {
    font-size: 13px;
    font-weight: 700;
    color: #374151;
    margin-bottom: 4px;
    margin-top: 2px;
}

.note-text {
    font-size: 13px;
    color: #6b7280;
}

.compact-space {
    height: 6px;
}

div[data-testid="stTextInput"] > div,
div[data-testid="stDateInput"] > div {
    margin-top: 0 !important;
}

div[data-testid="stCheckbox"] {
    margin-top: 0 !important;
}

.stTextInput input, .stDateInput input {
    height: 42px !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 0.5rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        padding-bottom: 1rem;
    }

    h1 {
        font-size: 2.5rem !important;
        line-height: 1.05 !important;
        margin-bottom: 0.8rem !important;
    }

    .section-title {
        font-size: 18px;
        margin-bottom: 10px;
    }

    .main-card, .side-card {
        padding: 12px;
    }

    .item-card {
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 12px;
    }

    .stButton > button {
        height: 48px;
        font-size: 18px;
    }

    .stTextInput input, .stDateInput input {
        height: 46px !important;
        font-size: 17px !important;
    }

    div[data-testid="stMetric"] {
        padding: 10px 12px;
    }
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Başlık
# -------------------------------------------------
st.title("Çek Ortalama\nVade Hesaplayıcı")

# -------------------------------------------------
# Üst butonlar
# -------------------------------------------------
b1, b2 = st.columns(2)

with b1:
    if st.button("➕ Ekle", use_container_width=True):
        add_check()
        st.rerun()

with b2:
    if st.button("🗑️ Temizle", use_container_width=True):
        clear_all()
        st.rerun()

st.markdown('<div class="compact-space"></div>', unsafe_allow_html=True)

# -------------------------------------------------
# Hesaplama
# -------------------------------------------------
today = date.today()
active_checks = []

for item in st.session_state.checks:
    amount = parse_amount(item["amount_text"])
    if item["active"] and amount > 0:
        active_checks.append(
            {
                "amount": amount,
                "due_date": item["due_date"]
            }
        )

if active_checks:
    total_amount = sum(x["amount"] for x in active_checks)
    weighted_days_sum = sum(
        x["amount"] * ((x["due_date"] - today).days)
        for x in active_checks
    )
    avg_days = round(weighted_days_sum / total_amount)
    avg_due_date = today + timedelta(days=avg_days)
    remaining_days = (avg_due_date - today).days
else:
    total_amount = 0
    avg_due_date = None
    remaining_days = None

# -------------------------------------------------
# Ana layout
# Mobilde kolonlar zaten alt alta iner
# -------------------------------------------------
left_col, right_col = st.columns([1.9, 1], gap="large")

with left_col:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Çek Listesi</div>', unsafe_allow_html=True)

    updated_checks = []

    for i, item in enumerate(st.session_state.checks, start=1):
        amount_key = f"amount_{item['id']}"
        due_key = f"due_{item['id']}"
        active_key = f"active_{item['id']}"

        if amount_key not in st.session_state:
            st.session_state[amount_key] = item["amount_text"]

        if due_key not in st.session_state:
            st.session_state[due_key] = item["due_date"]

        if active_key not in st.session_state:
            st.session_state[active_key] = item["active"]

        st.markdown('<div class="item-card">', unsafe_allow_html=True)

        top_left, top_right = st.columns([4, 1], vertical_alignment="center")
        with top_left:
            st.markdown(f'<div class="item-top">Kalem #{i}</div>', unsafe_allow_html=True)
        with top_right:
            st.checkbox(
                "Dahil",
                key=active_key
            )

        st.markdown('<div class="item-label">Tutar (TL)</div>', unsafe_allow_html=True)
        st.text_input(
            label="Tutar",
            key=amount_key,
            placeholder="Örn: 1.230.000",
            on_change=normalize_amount_field,
            args=(item["id"],),
            label_visibility="collapsed"
        )

        st.markdown('<div class="item-label">Vade Tarihi</div>', unsafe_allow_html=True)
        st.date_input(
            label="Vade",
            key=due_key,
            format="DD.MM.YYYY",
            label_visibility="collapsed"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        updated_checks.append(
            {
                "id": item["id"],
                "active": st.session_state[active_key],
                "amount_text": st.session_state[amount_key],
                "due_date": st.session_state[due_key]
            }
        )

    st.session_state.checks = updated_checks
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="side-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Hesap Özeti</div>', unsafe_allow_html=True)

    st.metric("Toplam Çek Tutarı", format_tl(total_amount))

    if avg_due_date:
        st.metric("Ortalama Vade", format_date_tr(avg_due_date))
        st.metric("Kalan Gün", f"{remaining_days} gün")
    else:
        st.metric("Ortalama Vade", "-")
        st.metric("Kalan Gün", "-")

    st.markdown("---")
    st.write(f"**Toplam Kalem:** {len(st.session_state.checks)}")
    st.write(f"**Hesaba Dahil Çek:** {len(active_checks)}")
    st.markdown("---")
    st.markdown('<div class="note-text">Ortalama vade, çek tutarları ağırlıklı hesaplanır.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
