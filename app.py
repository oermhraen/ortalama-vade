import streamlit as st
from datetime import date, timedelta

st.set_page_config(
    page_title="Ortalama Vade Hesaplayıcı",
    page_icon="📅",
    layout="wide"
)

# ----------------------------
# SESSION STATE
# ----------------------------
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

# ----------------------------
# HELPERS
# ----------------------------
def format_tl(value: float) -> str:
    try:
        return f"{value:,.0f}".replace(",", ".") + " TL"
    except:
        return "0 TL"

def format_date_tr(d: date) -> str:
    return d.strftime("%d.%m.%Y")

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

# ----------------------------
# ACTIONS
# ----------------------------
def clear_all():
    st.session_state.checks = [default_row()]

def add_new_row():
    st.session_state.checks.append(default_row())

# ----------------------------
# STYLE
# ----------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f7f7f8;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #232733;
        margin-bottom: 20px;
        letter-spacing: -0.5px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 700;
        color: #232733;
        margin-top: 10px;
        margin-bottom: 8px;
    }

    .table-header {
        font-size: 17px;
        font-weight: 700;
        color: #232733;
        margin-bottom: 8px;
    }

    .summary-title {
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

    div[data-testid="stButton"] > button {
        border-radius: 12px !important;
        border: 1px solid #ddd9de !important;
        background: #f3f2f4 !important;
        color: #7a4ce0 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        height: 46px !important;
        width: 46px !important;
        padding: 0 !important;
        min-height: 46px !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: #cfc8d7 !important;
        background: #ece9ef !important;
    }

    .trash-btn div[data-testid="stButton"] > button {
        color: #9b8ca7 !important;
        font-size: 20px !important;
    }

    .serial-box {
        font-size: 22px;
        font-weight: 700;
        color: #232733;
        padding-top: 7px;
    }

    div[data-baseweb="input"] input {
        background: #ecebed !important;
        border-radius: 10px !important;
        border: 1px solid #ecebed !important;
        color: #232733 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="input"] input:focus {
        border: 1px solid #d8d2da !important;
        box-shadow: none !important;
    }

    div[data-baseweb="input"] {
        border-radius: 10px !important;
    }

    .stDateInput > div > div {
        background: #ecebed !important;
        border-radius: 10px !important;
        border: 1px solid #ecebed !important;
    }

    .stDateInput input {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #232733 !important;
    }

    .block-container {
        padding-top: 24px;
        padding-bottom: 24px;
        max-width: 1200px;
    }

    .checkbox-wrap {
        padding-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HEADER
# ----------------------------
st.markdown('<div class="main-title">Ortalama Vade Hesaplayıcı</div>', unsafe_allow_html=True)

top_left, top_right = st.columns([1, 20], gap="small")
with top_left:
    st.markdown('<div class="trash-btn">', unsafe_allow_html=True)
    if st.button("🗑", key="clear_btn", help="Listeyi temizle"):
        clear_all()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("")

# ----------------------------
# MAIN LAYOUT
# ----------------------------
left_col, right_col = st.columns([1.3, 1], gap="large")

with left_col:
    st.markdown('<div class="section-title">Çek Listesi</div>', unsafe_allow_html=True)

    header_cols = st.columns([0.8, 1.7, 1.8, 0.8], gap="medium")
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
        cols = st.columns([0.8, 1.7, 1.8, 0.8], gap="medium")

        with cols[0]:
            st.markdown(f'<div class="serial-box">#{i+1}</div>', unsafe_allow_html=True)

        with cols[1]:
            amount = st.number_input(
                label=f"Tutar {i+1}",
                min_value=0.0,
                value=float(row["amount"]),
                step=1000.0,
                format="%.0f",
                label_visibility="collapsed",
                key=f"amount_{i}"
            )

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

    add_col, _ = st.columns([1, 20])
    with add_col:
        if st.button("+", key="add_btn", help="Yeni çek ekle"):
            add_new_row()
            st.rerun()

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
