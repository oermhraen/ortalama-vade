import streamlit as st
from datetime import date, timedelta, datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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


def format_plain_amount(value):
    try:
        return f"{int(round(value)):,}".replace(",", ".")
    except:
        return "0"


def format_date_tr(d):
    return d.strftime("%d.%m.%Y")


def get_font(size=18, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except:
            pass
    return ImageFont.load_default()


def draw_text_center(draw, box, text, font, fill):
    x1, y1, x2, y2 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x1 + (x2 - x1 - tw) / 2
    ty = y1 + (y2 - y1 - th) / 2 - 1
    draw.text((tx, ty), text, font=font, fill=fill)


def generate_summary_png(total_count, total_amount, avg_due_date, active_rows):
    if not active_rows:
        active_rows = [{"index": "-", "amount": 0, "due_date": "-"}]

    row_count = len(active_rows)

    width = 540
    col_w = width // 3
    width = col_w * 3

    top_header_h = 28
    top_value_h = 30
    gap_h = 6
    table_header_h = 28
    row_h = 28
    height = top_header_h + top_value_h + gap_h + table_header_h + (row_count * row_h)

    navy = (24, 78, 121)
    white = (255, 255, 255)
    black = (18, 18, 18)
    fill_alt = (243, 243, 243)
    fill_white = (255, 255, 255)
    border = (0, 0, 0)

    font_header = get_font(12, bold=True)
    font_value = get_font(13, bold=False)
    font_value_bold = get_font(13, bold=True)
    font_cell = get_font(13, bold=False)
    font_cell_bold = get_font(13, bold=True)

    img = Image.new("RGB", (width, height), white)
    draw = ImageDraw.Draw(img)

    x0 = 0
    x1 = col_w
    x2 = col_w * 2
    x3 = col_w * 3

    top_labels = [
        (x0, 0, x1, top_header_h, "Qty - Adet"),
        (x1, 0, x2, top_header_h, "Total Amount - Toplam Tutar"),
        (x2, 0, x3, top_header_h, "Avg. Due Date - Ortalama Vade"),
    ]

    for bx1, by1, bx2, by2, label in top_labels:
        draw.rectangle([bx1, by1, bx2, by2], fill=navy, outline=border, width=1)
        draw_text_center(draw, (bx1, by1, bx2, by2), label, font_header, white)

    avg_text = format_date_tr(avg_due_date) if avg_due_date else "-"
    top_values = [
        (x0, top_header_h, x1, top_header_h + top_value_h, str(total_count)),
        (x1, top_header_h, x2, top_header_h + top_value_h, format_plain_amount(total_amount)),
        (x2, top_header_h, x3, top_header_h + top_value_h, avg_text),
    ]

    for bx1, by1, bx2, by2, value in top_values:
        draw.rectangle([bx1, by1, bx2, by2], fill=fill_white, outline=border, width=1)
        draw_text_center(
            draw,
            (bx1, by1, bx2, by2),
            value,
            font_value_bold if bx1 == x1 else font_value,
            black
        )

    start_y = top_header_h + top_value_h + gap_h

    detail_labels = [
        (x0, start_y, x1, start_y + table_header_h, "No - Sira"),
        (x1, start_y, x2, start_y + table_header_h, "Check Amount - Cek Tutari"),
        (x2, start_y, x3, start_y + table_header_h, "Due Date - Vade"),
    ]

    for bx1, by1, bx2, by2, label in detail_labels:
        draw.rectangle([bx1, by1, bx2, by2], fill=navy, outline=border, width=1)
        draw_text_center(draw, (bx1, by1, bx2, by2), label, font_header, white)

    y = start_y + table_header_h

    for i, row in enumerate(active_rows):
        fill = fill_alt if i % 2 == 0 else fill_white

        row_values = [
            (x0, y, x1, y + 28, str(row["index"])),
            (x1, y, x2, y + 28, format_plain_amount(row["amount"])),
            (x2, y, x3, y + 28, row["due_date"] if isinstance(row["due_date"], str) else format_date_tr(row["due_date"])),
        ]

        for bx1, by1, bx2, by2, value in row_values:
            draw.rectangle([bx1, by1, bx2, by2], fill=fill, outline=border, width=1)
            draw_text_center(
                draw,
                (bx1, by1, bx2, by2),
                value,
                font_cell_bold if bx1 == x1 else font_cell,
                black
            )

        y += 28

    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output


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
    max-width: 1000px;
    padding-top: 2.2rem;
    padding-bottom: 0.8rem;
}

/* Başlık */
h1 {
    margin: 0 0 1rem 0 !important;
    padding: 0 !important;
    line-height: 1.04 !important;
    font-size: 2.25rem !important;
    letter-spacing: -0.5px;
}

/* Dar ana çalışma alanı */
.compact-shell {
    max-width: 620px;
}

/* Başlıklar */
.section-title {
    font-size: 16px;
    font-weight: 700;
    margin: 0 0 0.45rem 0;
}

/* Grid başlıkları */
.header-box {
    height: 18px;
    display: flex;
    align-items: center;
    font-weight: 700;
    color: #1f2937;
    font-size: 11px;
}

/* Satır no */
.row-no-box {
    height: 28px;
    display: flex;
    align-items: center;
    font-weight: 700;
    color: #1f2937;
    font-size: 12px;
}

/* Ayraç */
.row-divider {
    border-bottom: 1px solid #e5e7eb;
    margin: 4px 0 6px 0;
}

/* Metric kartları */
div[data-testid="stMetric"] {
    border: 1px solid #d1d5db;
    border-radius: 12px;
    padding: 10px 12px;
}

/* input üst boşluklarını öldür */
div[data-testid="stTextInput"] > div,
div[data-testid="stDateInput"] > div {
    margin-top: 0 !important;
}

/* input yükseklik eşitleme */
.stTextInput input,
.stDateInput input {
    height: 28px !important;
    min-height: 28px !important;
    font-size: 12px !important;
    padding-top: 4px !important;
    padding-bottom: 4px !important;
    padding-left: 8px !important;
    padding-right: 8px !important;
    border-radius: 8px !important;
}

/* checkbox sola yakın */
div[data-testid="stCheckbox"] {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    height: 28px;
    margin-top: 0 !important;
    padding-top: 1px;
    padding-left: 0 !important;
}

div[data-testid="stCheckbox"] label {
    margin-bottom: 0 !important;
    padding-left: 0 !important;
}

/* küçük ikon buton */
.small-icon-btn button {
    width: 44px !important;
    min-width: 44px !important;
    max-width: 44px !important;
    height: 34px !important;
    min-height: 34px !important;
    max-height: 34px !important;
    padding: 0 !important;
    font-size: 16px !important;
    border-radius: 10px !important;
}

/* buton satırı */
.icon-row {
    margin-bottom: 0.9rem;
}

/* özet alt blok */
.summary-shell {
    max-width: 620px;
    margin-top: 1rem;
}

.note-text {
    font-size: 12px;
    color: #6b7280;
}

@media (max-width: 768px) {
    .block-container {
        max-width: 100%;
        padding-top: 1.2rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        padding-bottom: 0.5rem;
    }

    h1 {
        font-size: 1.75rem !important;
        line-height: 1.02 !important;
        margin-bottom: 0.85rem !important;
        letter-spacing: -0.3px;
    }

    .compact-shell,
    .summary-shell {
        max-width: 100%;
    }

    .section-title {
        font-size: 15px;
        margin-bottom: 0.35rem;
    }

    .header-box {
        font-size: 10px;
        height: 16px;
    }

    .row-no-box {
        font-size: 11px;
        height: 26px;
    }

    .stTextInput input,
    .stDateInput input {
        height: 26px !important;
        min-height: 26px !important;
        font-size: 11px !important;
        padding-left: 6px !important;
        padding-right: 6px !important;
    }

    div[data-testid="stMetric"] {
        padding: 8px 10px;
    }

    .small-icon-btn button {
        width: 40px !important;
        min-width: 40px !important;
        max-width: 40px !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        font-size: 15px !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("Ortalama Vade Hesaplayıcı")

st.markdown('<div class="compact-shell">', unsafe_allow_html=True)

# -------------------------------------------------
# Üst ikon buton
# -------------------------------------------------
st.markdown('<div class="icon-row">', unsafe_allow_html=True)
icon_cols_top = st.columns([0.08, 0.92], gap="small")
with icon_cols_top[0]:
    st.markdown('<div class="small-icon-btn">', unsafe_allow_html=True)
    if st.button("🗑️", use_container_width=True):
        clear_all()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# Çek listesi
# -------------------------------------------------
st.markdown('<div class="section-title">Çek Listesi</div>', unsafe_allow_html=True)

# Sıra / Tutar / Vade / Dahil
header_cols = st.columns([0.09, 0.24, 0.18, 0.06, 0.43], gap="small")
header_cols[0].markdown('<div class="header-box">Sıra</div>', unsafe_allow_html=True)
header_cols[1].markdown('<div class="header-box">Tutar (TL)</div>', unsafe_allow_html=True)
header_cols[2].markdown('<div class="header-box">Vade Tarihi</div>', unsafe_allow_html=True)
header_cols[3].markdown('<div class="header-box">Dahil</div>', unsafe_allow_html=True)

updated_checks = []

for i, item in enumerate(st.session_state.checks, start=1):
    row_cols = st.columns([0.09, 0.24, 0.18, 0.06, 0.43], gap="small")

    amount_key = f"amount_{item['id']}"
    due_key = f"due_{item['id']}"
    active_key = f"active_{item['id']}"

    if amount_key not in st.session_state:
        st.session_state[amount_key] = item["amount_text"]

    if due_key not in st.session_state:
        st.session_state[due_key] = item["due_date"]

    if active_key not in st.session_state:
        st.session_state[active_key] = item["active"]

    row_cols[0].markdown(f'<div class="row-no-box">#{i}</div>', unsafe_allow_html=True)

    with row_cols[1]:
        st.text_input(
            label="",
            key=amount_key,
            placeholder="1.230.000",
            on_change=normalize_amount_field,
            args=(item["id"],),
            label_visibility="collapsed"
        )

    with row_cols[2]:
        st.date_input(
            label="",
            key=due_key,
            format="DD.MM.YYYY",
            label_visibility="collapsed"
        )

    with row_cols[3]:
        st.checkbox(
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

# -------------------------------------------------
# Alt ikon buton
# -------------------------------------------------
icon_cols_bottom = st.columns([0.08, 0.92], gap="small")
with icon_cols_bottom[0]:
    st.markdown('<div class="small-icon-btn">', unsafe_allow_html=True)
    if st.button("➕", key="bottom_add_button", use_container_width=True):
        add_check()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# Hesaplama
# -------------------------------------------------
today = date.today()
active_checks = []
active_rows_for_export = []

for idx, item in enumerate(st.session_state.checks, start=1):
    amount = parse_amount(item["amount_text"])
    if item["active"] and amount > 0:
        active_checks.append(
            {
                "amount": amount,
                "due_date": item["due_date"]
            }
        )
        active_rows_for_export.append(
            {
                "index": idx,
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

png_bytes = generate_summary_png(
    total_count=len(active_checks),
    total_amount=total_amount,
    avg_due_date=avg_due_date,
    active_rows=active_rows_for_export
)

# -------------------------------------------------
# Alt özet
# -------------------------------------------------
st.markdown('<div class="summary-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Hesap Özeti</div>', unsafe_allow_html=True)

metric_cols = st.columns(3, gap="small")
with metric_cols[0]:
    st.metric("Toplam Tutar", format_tl(total_amount))
with metric_cols[1]:
    st.metric("Ortalama Vade", format_date_tr(avg_due_date) if avg_due_date else "-")
with metric_cols[2]:
    st.metric("Kalan Gün", f"{remaining_days} gün" if remaining_days is not None else "-")

st.markdown("")

meta_cols = st.columns(2, gap="small")
with meta_cols[0]:
    st.write(f"**Toplam Kalem:** {len(st.session_state.checks)}")
with meta_cols[1]:
    st.write(f"**Hesaba Dahil:** {len(active_checks)}")

st.markdown("---")
st.markdown("**PNG Özet Çıktı**")
st.image(png_bytes, use_container_width=False)

file_name = f"cek_ozet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
st.download_button(
    label="PNG İndir",
    data=png_bytes,
    file_name=file_name,
    mime="image/png",
    use_container_width=True
)

st.markdown(
    '<div class="note-text">PNG çıktıda sadece hesaba dahil edilen çekler yer alır.</div>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)
