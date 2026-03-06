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


def format_tl_no_suffix(value):
    try:
        return f"{int(round(value)):,}".replace(",", ".")
    except:
        return "0"


def format_date_tr(d):
    return d.strftime("%d.%m.%Y")


def get_font(size=18, bold=False):
    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]

    for font_path in possible_fonts:
        try:
            return ImageFont.truetype(font_path, size=size)
        except:
            pass

    return ImageFont.load_default()


def generate_summary_png(total_amount, avg_due_date, active_rows):
    """
    Kompakt PNG özet görseli üretir.
    """
    row_count = max(len(active_rows), 1)

    width = 900
    header_h = 58
    summary_h = 78
    subheader_h = 46
    row_h = 44
    padding = 14
    height = padding + header_h + summary_h + subheader_h + (row_count * row_h) + padding

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Renkler
    navy = (22, 71, 113)
    black = (15, 23, 42)
    white = (255, 255, 255)
    light = (245, 247, 250)
    border = (25, 25, 25)

    # Fontlar
    font_title = get_font(26, bold=True)
    font_header = get_font(18, bold=True)
    font_cell = get_font(18, bold=False)
    font_cell_bold = get_font(18, bold=True)

    # Alanlar
    top_y = padding
    summary_y = top_y + header_h
    table_header_y = summary_y + summary_h
    table_y = table_header_y + subheader_h

    # Üst başlık şeritleri
    left_half = width // 2
    draw.rectangle([0, top_y, left_half, top_y + header_h], fill=navy, outline=border, width=1)
    draw.rectangle([left_half, top_y, width, top_y + header_h], fill=navy, outline=border, width=1)

    draw.text((24, top_y + 13), "Toplam Tutar", fill=white, font=font_header)
    draw.text((left_half + 24, top_y + 13), "Ortalama Vade", fill=white, font=font_header)

    total_text = format_tl_no_suffix(total_amount)
    avg_text = format_date_tr(avg_due_date) if avg_due_date else "-"

    draw.rectangle([0, summary_y, left_half, summary_y + summary_h], fill=white, outline=border, width=1)
    draw.rectangle([left_half, summary_y, width, summary_y + summary_h], fill=white, outline=border, width=1)

    total_bbox = draw.textbbox((0, 0), total_text, font=font_title)
    avg_bbox = draw.textbbox((0, 0), avg_text, font=font_title)
    total_w = total_bbox[2] - total_bbox[0]
    avg_w = avg_bbox[2] - avg_bbox[0]

    draw.text(((left_half - total_w) / 2, summary_y + 18), total_text, fill=black, font=font_title)
    draw.text((left_half + (left_half - avg_w) / 2, summary_y + 18), avg_text, fill=black, font=font_title)

    # Alt tablo başlığı
    col1 = 110
    col2 = 395
    col3 = width - col1 - col2

    x1 = 0
    x2 = col1
    x3 = col1 + col2
    x4 = width

    draw.rectangle([0, table_header_y, width, table_header_y + subheader_h], fill=navy, outline=border, width=1)
    draw.line([(x2, table_header_y), (x2, height - padding)], fill=border, width=1)
    draw.line([(x3, table_header_y), (x3, height - padding)], fill=border, width=1)

    sira_label = "SIRA"
    tutar_label = "TUTAR"
    tarih_label = "TARİH"

    for label, x_left, x_right in [
        (sira_label, x1, x2),
        (tutar_label, x2, x3),
        (tarih_label, x3, x4),
    ]:
        bbox = draw.textbbox((0, 0), label, font=font_header)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            ((x_left + x_right - tw) / 2, table_header_y + (subheader_h - th) / 2 - 2),
            label,
            fill=white,
            font=font_header
        )

    # Satırlar
    if not active_rows:
        active_rows = [{"index": "-", "amount": 0, "due_date": "-"}]

    y = table_y
    for idx, row in enumerate(active_rows):
        fill_color = light if idx % 2 == 0 else white
        draw.rectangle([0, y, width, y + row_h], fill=fill_color, outline=border, width=1)

        sira_text = str(row["index"])
        tutar_text = format_tl_no_suffix(row["amount"])
        tarih_text = row["due_date"] if isinstance(row["due_date"], str) else format_date_tr(row["due_date"])

        values = [
            (sira_text, x1, x2),
            (tutar_text, x2, x3),
            (tarih_text, x3, x4),
        ]

        for text, x_left, x_right in values:
            bbox = draw.textbbox((0, 0), text, font=font_cell_bold if x_left == x2 else font_cell)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(
                ((x_left + x_right - tw) / 2, y + (row_h - th) / 2 - 2),
                text,
                fill=black,
                font=font_cell_bold if x_left == x2 else font_cell
            )

        y += row_h

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
    max-width: 1400px;
    padding-top: 1.4rem;
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
    line-height: 1.08;
    margin: 0 0 18px 0;
    color: #1f2940;
    padding-top: 4px;
}

.note-text {
    font-size: 13px;
    color: #6b7280;
}

.bottom-add-wrap {
    margin-top: 10px;
}

.export-title {
    font-size: 16px;
    font-weight: 700;
    margin-top: 8px;
    margin-bottom: 8px;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 0.8rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        padding-bottom: 0.8rem;
    }

    .main-title {
        font-size: 30px;
        line-height: 1.08;
        margin: 0 0 14px 0;
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

# PNG üret
png_bytes = generate_summary_png(total_amount, avg_due_date, active_rows_for_export)

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
    st.markdown('<div class="export-title">PNG Özet Çıktı</div>', unsafe_allow_html=True)
    st.image(png_bytes, use_container_width=True)

    file_name = f"cek_ozet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    st.download_button(
        label="PNG İndir",
        data=png_bytes,
        file_name=file_name,
        mime="image/png",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown('<div class="note-text">PNG çıktıda sadece hesaba dahil edilen çekler yer alır.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
