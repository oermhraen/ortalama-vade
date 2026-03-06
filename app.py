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
    max-width: 1400px;
    padding-top: 0.8rem;
    padding-bottom: 1rem;
}

.list-card, .side-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px 16px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 12px;
}

.header-box {
    height: 28px;
    display: flex;
    align-items: center;
    font-weight: 700;
    color: #1f2937;
    font-size: 15px;
}

.row-no-box {
    height: 38px;
    display: flex;
    align-items: center;
    font-weight: 700;
    color: #1f2937;
    font-size: 16px;
}

.row-divider {
    border-bottom: 1px solid #f1f1f1;
    margin: 8px 0 10px 0;
}

div[data-testid="stMetric"] {
    background: #f7f7f9;
    border: 1px solid #e5e7eb;
    padding: 14px 16px;
    border-radius: 12px;
}

div[data-testid="stTextInput"] > div,
div[data-testid="stDateInput"] > div {
    margin-top: 0 !important;
}

div[data-testid="stCheckbox"] {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 38px;
    margin-top: 0 !important;
    padding-top: 6px;
}

div[data-testid="stCheckbox"] label {
    margin-bottom: 0 !important;
}

.stTextInput input, .stDateInput input {
    height: 38px !important;
}

.main-title {
    font-size: 44px;
    font-weight: 800;
    line-height: 1.05;
    margin-bottom: 10px;
    color: #1f2940;
}

.note-text {
    font-size: 13px;
    color: #6b7280;
}

.bottom-add-wrap {
    margin-top: 10px;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 0.45rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        padding-bottom: 0.8rem;
    }

    .main-title {
        font-size: 28px;
        line-height: 1.08;
        margin-bottom: 8px;
    }

    .section-title {
        font-size: 18px;
        margin-bottom: 8px;
    }

    .header-box {
        font-size: 12px;
        height: 24px;
    }

    .row-no-box {
        font-size: 14px;
        height: 36px;
    }

    .list-card, .side-card {
        padding: 10px 10px;
        border-radius: 12px;
    }

    .stTextInput input, .stDateInput input {
        height: 36px !important;
        font-size: 14px !important;
    }

    div[data-testid="stMetric"] {
        padding: 10px 12px;
    }

    .stButton > button {
        height: 42px;
        font-size: 15px;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Çek Ortalama Vade Hesaplayıcı</div>', unsafe_allow_html=True)

# -------------------------------------------------
# Üst butonlar
# -------------------------------------------------
top1, top2, top3 = st.columns([1, 1, 5])

with top1:
    if st.button("➕ Ekle", use_container_width=True):
        add_check()
        st.rerun()

with top2:
    if st.button("🗑️ Temizle", use_container_width=True):
        clear_all()
        st.rerun()

st.markdown("")

# -------------------------------------------------
# Ana layout
# -------------------------------------------------
left_col, right_col = st.columns([2.5, 1], gap="large")

# -------------------------------------------------
# Sol panel - Çek listesi
# -------------------------------------------------
with left_col:
    st.markdown('<div class="list-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Çek Listesi</div>', unsafe_allow_html=True)

    h1, h2, h3, h4 = st.columns([0.7, 2.4, 1.7, 0.6], vertical_alignment="center")
    h1.markdown('<div class="header-box">Sıra</div>', unsafe_allow_html=True)
    h2.markdown('<div class="header-box">Tutar (TL)</div>', unsafe_allow_html=True)
    h3.markdown('<div class="header-box">Vade Tarihi</div>', unsafe_allow_html=True)
    h4.markdown('<div class="header-box">Dahil</div>', unsafe_allow_html=True)

    updated_checks = []

    for i, item in enumerate(st.session_state.checks, start=1):
        c1, c2, c3, c4 = st.columns([0.7, 2.4, 1.7, 0.6], vertical_alignment="center")

        amount_key = f"amount_{item['id']}"
        due_key = f"due_{item['id']}"
        active_key = f"active_{item['id']}"

        if amount_key not in st.session_state:
            st.session_state[amount_key] = item["amount_text"]

        if due_key not in st.session_state:
            st.session_state[due_key] = item["due_date"]

        if active_key not in st.session_state:
            st.session_state[active_key] = item["active"]

        c1.markdown(f'<div class="row-no-box">#{i}</div>', unsafe_allow_html=True)

        c2.text_input(
            label="",
            key=amount_key,
            placeholder="Örn: 1.230.000",
            on_change=normalize_amount_field,
            args=(item["id"],),
            label_visibility="collapsed"
        )

        c3.date_input(
            label="",
            key=due_key,
            format="DD.MM.YYYY",
            label_visibility="collapsed"
        )

        c4.checkbox(
            label="",
            key=active_key,
            label_visibility="collapsed"
        )

        st.markdown('<div class="row-divider"></div>', unsafe_allow_html=True)

        updated_checks.append(
            {
                "id": item["id"],
                "active": st.session_state[active_key],
                "amount_text": st.session_state[amount_key],
                "due_date": st.session_state[due_key]
            }
        )

    st.session_state.checks = updated_checks

    st.markdown('<div class="bottom-add-wrap"></div>', unsafe_allow_html=True)

    if st.button("➕ Yeni Çek Ekle", key="bottom_add_button", use_container_width=True):
        add_check()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

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
# Sağ panel - Özet
# -------------------------------------------------
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
