import streamlit as st
from datetime import date, timedelta

st.set_page_config(
    page_title="Ortalama Vade Hesaplayıcı",
    page_icon="📅",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
def default_row():
    return {
        "amount": 0.0,
        "due_date": date.today(),
        "included": True
    }

if "checks" not in st.session_state:
    st.session_state.checks = [
        default_row(),
        default_row(),
        default_row()
    ]

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def format_tl(value: float) -> str:
    try:
        return f"{value:,.0f}".replace(",", ".") + " TL"
    except:
        return "0 TL"

def format_date_tr(d: date) -> str:
    return d.strftime("%d.%m.%Y")

def parse_amount(value: str) -> float:
    """
    Kullanıcı girişini sayıya çevirir.
    Örnek destekler:
    - 1000000
    - 1.000.000
    - 1,000,000
    - 1 000 000
    """
    if value is None:
        return 0.0

    cleaned = str(value).strip()
    if not cleaned:
        return 0.0

    cleaned = cleaned.replace("TL", "").replace("tl", "")
    cleaned = cleaned.replace(" ", "")
    cleaned = cleaned.replace(".", "")
    cleaned = cleaned.replace(",", "")

    digits_only = "".join(ch for ch in cleaned if ch.isdigit())

    if not digits_only:
        return 0.0

    return float(digits_only)

def amount_input_display(value: float) -> str:
    if not value:
        return "0"
    return f"{int(value):,}".replace(",", ".")

def calculate_weighted_average_maturity(checks):
    valid_checks = [
        row for row in checks
        if row["included"] and row["amount"] > 0 and row["due_date"] is not None
    ]

    if not valid_checks:
        return None, 0.0, None

    total_amount = sum(row["amount"] for row in valid_checks)

    if total_amount <= 0:
        return None, 0.0, None

    base_date = date.today()

    weighted_days_sum = 0.0
    for row in valid_checks:
        days_diff = (row["due_date"] - base_date).days
        weighted_days_sum += row["amount"] * days_diff

    avg_days = round(weighted_days_sum / total_amount)
    avg_date = base_date + timedelta(days=avg_days)

    return avg_date, total_amount, avg_days

# --------------------------------------------------
# ACTIONS
# --------------------------------------------------
def clear_all():
    st.session_state.checks = [default_row()]

def add_new_row():
    st.session_state.checks.append(default_row())

# --------------------------------------------------
# STYLE
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f7f7f8;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #232733;
        margin-bottom: 18px;
        letter-spacing: -0.5px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 800;
        color: #232733;
        margin-top: 8px;
        margin-bottom: 10px;
    }

    .table-header {
        font-size: 17px;
        font-weight: 700;
        color: #232733;
        margin-bottom: 8px;
    }

    .summary-card {
        background: #f1eff2;
        border: 1px solid #e8e5e8;
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 16px;
        min-height: 98px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .summary-label {
        font-size: 15px;
        color: #666;
        margin-bottom: 8px;
        font-weight: 500;
    }

    .summary-value {
        font-size: 26px;
        color: #232733;
        font-weight: 800;
        line-height: 1.2;
    }

    .row-divider {
        border-bottom: 1px solid #e0dde1;
        margin-top: 10px;
        margin-bottom: 14px;
    }

    .serial-box {
        font-size: 22px;
        font-weight: 700;
        color: #232733;
        padding-top: 8px;
    }

    .block-container {
        padding-top: 24px;
        padding-bottom: 24px;
        max-width: 1200px;
    }

    div[data-baseweb="input"] input {
        background: #ecebed !important;
        border-radius: 10px !important;
        border: 1px solid #ecebed !important;
        color: #232733 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        height: 50px !important;
    }

    div[data-baseweb="input"] input:focus {
        border: 1px solid #d8d2da !important;
        box-shadow: none !important;
    }

    .stDateInput > div > div {
        background: #ecebed !important;
        border-radius: 10px !important;
        border: 1px solid #ecebed !important;
        height: 50px !important;
    }

    .stDateInput input {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #232733 !important;
    }

    div[data-testid="stButton"] > button {
        border-radius: 12px !important;
        border: 1px solid #d6d2d8 !important;
        background: #f3f2f4 !important;
        color: #232733 !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        height: 48px !important;
        padding: 0 18px !important;
        box-shadow: none !important;
        width: 100% !important;
        white-space: nowrap !important;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: #c9c3cc !important;
        background: #ece9ef !important;
    }

    .top-action-wrap {
        max-width: 220px;
        margin-bottom: 28px;
    }

    .bottom-action-wrap {
        max-width: 220px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown('<div class="main-title">Ortalama Vade Hesaplayıcı</div>', unsafe_allow_html=True)

st.markdown('<div class="top-action-wrap">', unsafe_allow_html=True)
if st.button("🗑 Listeyi Temizle", key="clear_btn"):
    clear_all()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------
left_col, right_col = st.columns([1.35, 1], gap="large")

with left_col:
    st.markdown('<div class="section-title">Çek Listesi</div>', unsafe_allow_html=True)

    header_cols = st.columns([0.8, 1.8, 1.8, 0.8], gap="medium")
    with header_cols[0]:
        st.markdown('<div class="table-header">Sıra</div>', unsafe_allow_html=True)
    with header_cols[1]:
        st.markdown('<div class="table-header">Tutar (TL)</div>', unsafe_allow_html=True)
    with header_cols[2]:
        st.markdown('<div class="table-header">Vade Tarihi</div>', unsafe_allow_html=True)
    with header_cols[3]:
        st.markdown('<div class="table-header">Dahil</div>', unsafe_allow_html=True)

    updated_checks = []

    for i, row in enumerate(st.session_state.checks):
        cols = st.columns([0.8, 1.8, 1.8, 0.8], gap="medium")

        with cols[0]:
            st.markdown(f'<div class="serial-box">#{i+1}</div>', unsafe_allow_html=True)

        with cols[1]:
            amount_text = st.text_input(
                label=f"Tutar {i+1}",
                value=amount_input_display(row["amount"]),
                label_visibility="collapsed",
                key=f"amount_{i}",
                placeholder="Örn: 1.250.000"
            )
            amount = parse_amount(amount_text)

        with cols[2]:
            due_date = st.date_input(
                label=f"Vade {i+1}",
                value=row["due_date"],
                format="DD.MM.YYYY",
                label_visibility="collapsed",
                key=f"date_{i}"
            )

        with cols[3]:
            included = st.checkbox(
                label=f"Dahil {i+1}",
                value=row["included"],
                key=f"included_{i}",
                label_visibility="collapsed"
            )

        updated_checks.append({
            "amount": amount,
            "due_date": due_date,
            "included": included
        })

        st.markdown('<div class="row-divider"></div>', unsafe_allow_html=True)

    st.session_state.checks = updated_checks

    st.markdown('<div class="bottom-action-wrap">', unsafe_allow_html=True)
    if st.button("＋ Yeni Çek Ekle", key="add_btn"):
        add_new_row()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-title">Hesap Özeti</div>', unsafe_allow_html=True)

    avg_date, total_amount, avg_days = calculate_weighted_average_maturity(st.session_state.checks)

    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-label">Toplam Çek Tutarı</div>
            <div class="summary-value">{format_tl(total_amount)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-label">Ortalama Vade</div>
            <div class="summary-value">{format_date_tr(avg_date) if avg_date else "-"}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    kalan_gun_text = f"{avg_days} gün" if avg_days is not None else "-"

    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-label">Kalan Gün</div>
            <div class="summary-value">{kalan_gun_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
