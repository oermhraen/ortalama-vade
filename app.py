import io
import os
from datetime import date, timedelta

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

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
    except Exception:
        return "0 TL"


def format_amount_plain(value: float) -> str:
    try:
        return f"{value:,.0f}".replace(",", ".")
    except Exception:
        return "0"


def format_date_tr(d: date) -> str:
    return d.strftime("%d.%m.%Y")


def parse_amount(value: str) -> float:
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


def get_included_checks(checks):
    return [
        row for row in checks
        if row["included"] and row["amount"] > 0 and row["due_date"] is not None
    ]


# --------------------------------------------------
# PNG GENERATION
# --------------------------------------------------
def get_font_paths():
    return [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]


def load_font(size=18, bold=False):
    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    candidates = bold_candidates if bold else regular_candidates

    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)

    return ImageFont.load_default()


def draw_centered_text(draw, box, text, font, fill):
    x1, y1, x2, y2 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = x1 + (x2 - x1 - text_w) / 2
    y = y1 + (y2 - y1 - text_h) / 2 - 1
    draw.text((x, y), text, font=font, fill=fill)


def draw_table(draw, x, y, col_widths, header, rows, row_h=42):
    header_bg = "#0b3a63"
    cell_bg = "#dedede"
    border = "#1f1f1f"
    header_text = "#ffffff"
    cell_text = "#222222"

    font_header = load_font(size=16, bold=True)
    font_cell = load_font(size=16, bold=False)

    total_width = sum(col_widths)

    # Header
    cx = x
    for i, title in enumerate(header):
        box = (cx, y, cx + col_widths[i], y + row_h)
        draw.rectangle(box, fill=header_bg, outline=border, width=1)
        draw_centered_text(draw, box, title, font_header, header_text)
        cx += col_widths[i]

    # Rows
    current_y = y + row_h
    for row in rows:
        cx = x
        for i, value in enumerate(row):
            box = (cx, current_y, cx + col_widths[i], current_y + row_h)
            draw.rectangle(box, fill=cell_bg, outline=border, width=1)
            draw_centered_text(draw, box, str(value), font_cell, cell_text)
            cx += col_widths[i]
        current_y += row_h

    return x + total_width, current_y


def generate_checks_png(checks, avg_date, total_amount):
    included_checks = get_included_checks(checks)

    qty = len(included_checks)
    total_amount_text = format_amount_plain(total_amount)
    avg_date_text = format_date_tr(avg_date) if avg_date else "-"

    top_header = ["Qty - Adet", "Toplam Tutar", "Ortalama Vade"]
    top_rows = [[qty, total_amount_text, avg_date_text]]

    bottom_header = ["No - Sira", "Cek Tutari", "Vade"]
    bottom_rows = []

    for idx, row in enumerate(included_checks, start=1):
        bottom_rows.append([
            idx,
            format_amount_plain(row["amount"]),
            format_date_tr(row["due_date"])
        ])

    if not bottom_rows:
        bottom_rows = [["-", "-", "-"]]

    top_col_widths = [110, 170, 170]
    bottom_col_widths = [110, 170, 170]

    row_h = 42
    gap = 18
    margin = 18

    width = margin * 2 + max(sum(top_col_widths), sum(bottom_col_widths))
    height = (
        margin
        + row_h * (1 + len(top_rows))
        + gap
        + row_h * (1 + len(bottom_rows))
        + margin
    )

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    _, current_y = draw_table(
        draw=draw,
        x=margin,
        y=margin,
        col_widths=top_col_widths,
        header=top_header,
        rows=top_rows,
        row_h=row_h
    )

    current_y += gap

    draw_table(
        draw=draw,
        x=margin,
        y=current_y,
        col_widths=bottom_col_widths,
        header=bottom_header,
        rows=bottom_rows,
        row_h=row_h
    )

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf


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

    .block-container {
        padding-top: 24px;
        padding-bottom: 24px;
        max-width: 1200px;
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

    .serial-box {
        font-size: 22px;
        font-weight: 700;
        color: #232733;
        padding-top: 8px;
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

    div[data-baseweb="input"] {
        height: 50px !important;
    }

    div[data-baseweb="input"] > div {
        height: 50px !important;
        min-height: 50px !important;
        background: #ecebed !important;
        border-radius: 10px !important;
        border: 1px solid #ecebed !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-baseweb="input"] input {
        height: 50px !important;
        line-height: 50px !important;
        background: #ecebed !important;
        border: none !important;
        color: #232733 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        box-sizing: border-box !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    div[data-baseweb="input"] input:focus {
        box-shadow: none !important;
    }

    .stDateInput > div {
        height: 50px !important;
    }

    .stDateInput > div > div {
        height: 50px !important;
        min-height: 50px !important;
        background: #ecebed !important;
        border-radius: 10px !important;
        border: 1px solid #ecebed !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
    }

    .stDateInput input {
        height: 50px !important;
        line-height: 50px !important;
        color: #232733 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        box-sizing: border-box !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    div[data-testid="stCheckbox"] {
        padding-top: 8px;
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

    png_data = generate_checks_png(st.session_state.checks, avg_date, total_amount)

    st.download_button(
        label="PNG Olarak İndir",
        data=png_data,
        file_name="cek_ozet.png",
        mime="image/png"
    )
