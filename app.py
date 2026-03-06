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


def draw_centered_text(draw, box, text, font, fill):
    x1, y1, x2, y2 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x1 + (x2 - x1 - tw) / 2
    ty = y1 + (y2 - y1 - th) / 2 - 1
    draw.text((tx, ty), text, font=font, fill=fill)


def generate_summary_png(total_count, total_amount, avg_due_date, active_rows):
    """
    Kompakt PNG özet görseli:
    Üst blok: Adet | Toplam Tutar | Ortalama Vade
    Alt blok: Sıra | Çek Tutarı | Vade Tarihi
    """
    if not active_rows:
        active_rows = []

    row_count = max(len(active_rows), 1)

    # Boyutlar
    width = 900
    top_header_h = 38
    top_value_h = 42
    gap_h = 10
    table_header_h = 36
    row_h = 34
    height = top_header_h + top_value_h + gap_h + table_header_h + row_count * row_h + 2

    # Renkler
    navy = (22, 71, 113)
    white = (255, 255, 255)
    black = (0, 0, 0)
    alt_fill = (242, 242, 242)
    normal_fill = (255, 255, 255)
    line = (0, 0, 0)

    # Fontlar
    font_header = get_font(18, bold=True)
    font_value = get_font(19, bold=False)
    font_value_bold = get_font(19, bold=True)
    font_cell = get_font(17, bold=False)
    font_cell_bold = get_font(17, bold=True)

    img = Image.new("RGB", (width, height), white)
    draw = ImageDraw.Draw(img)

    # Üst özet kolonları
    c1 = 160
    c2 = 350
    c3 = width - c1 - c2

    x0 = 0
    x1 = c1
    x2 = c1 + c2
    x3 = width

    # Üst başlık
    top_header_boxes = [
        (x0, 0, x1, top_header_h, "Adet"),
        (x1, 0, x2, top_header_h, "Toplam Tutar"),
        (x2, 0, x3, top_header_h, "Ortalama Vade"),
    ]

    for bx1, by1, bx2, by2, label in top_header_boxes:
        draw.rectangle([bx1, by1, bx2, by2], fill=navy, outline=line, width=1)
        draw_centered_text(draw, (bx1, by1, bx2, by2), label, font_header, white)

    # Üst değer satırı
    avg_text = format_date_tr(avg_due_date) if avg_due_date else "-"
    top_value_boxes = [
        (x0, top_header_h, x1, top_header_h + top_value_h, str(total_count)),
        (x1, top_header_h, x2, top_header_h + top_value_h, format_tl_no_suffix(total_amount)),
        (x2, top_header_h, x3, top_header_h + top_value_h, avg_text),
    ]

    for bx1, by1, bx2, by2, value in top_value_boxes:
        draw.rectangle([bx1, by1, bx2, by2], fill=white, outline=line, width=1)
        draw_centered_text(draw, (bx1, by1, bx2, by2), value, font_value_bold if bx1 == x1 else font_value, black)

    # Alt tablo
    start_y = top_header_h + top_value_h + gap_h

    d1 = 110
    d2 = 420
    d3 = width - d1 - d2

    dx0 = 0
    dx1 = d1
    dx2 = d1 + d2
    dx3 = width

    table_header_boxes = [
        (dx0, start_y, dx1, start_y + table_header_h, "Sıra"),
        (dx1, start_y, dx2, start_y + table_header_h, "Çek Tutarı"),
        (dx2, start_y, dx3, start_y + table_header_h, "Vade Tarihi"),
    ]

    for bx1, by1, bx2, by2, label in table_header_boxes:
        draw.rectangle([bx1, by1, bx2, by2], fill=navy, outline=line, width=1)
        draw_centered_text(draw, (bx1, by1, bx2, by2), label, font_header, white)

    if not active_rows:
        active_rows = [{"index": "-", "amount": 0, "due_date": "-"}]

    y = start_y + table_header_h

    for idx, row in enumerate(active_rows):
        fill = alt_fill if idx % 2 == 0 else normal_fill

        row_boxes = [
            (dx0, y, dx1, y + row_h, str(row["index"])),
            (dx1, y, dx2, y + row_h, format_tl_no_suffix(row["amount"])),
            (
                dx2,
                y,
                dx3,
                y + row_h,
                row["due_date"] if isinstance(row["due_date"], str) else format_date_tr(row["due_date"])
            ),
        ]

        for bx1, by1, bx2, by2, value in row_boxes:
            draw.rectangle([bx1, by1, bx2, by2], fill=fill, outline=line, width=1)
            draw_centered_text(
                draw,
                (bx1, by1, bx2, by2),
                value,
                font_cell_bold if bx1 == dx1 else font_cell,
                black
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
    padding-top: 1.6rem;
    padding-bottom: 1rem;
}

h1 {
    margin-top: 0 !important;
    padding-top: 0 !important;
    line-height: 1.1 !important;
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
    border-bottom: 1px solid #e5e7eb;
    margin: 8px 0 10px 0;
}

div[data-testid="stMetric"] {
    border: 1px solid #d1d5db;
    border-radius: 12px;
    padding: 12px 14px;
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

.note-text {
    font-size: 13px;
    color: #6b7280;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        padding-bottom: 0.8rem;
    }

    h1 {
        font-size: 2.2rem !important;
        line-height: 1.08 !important;
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

st.title("Çek Ortalama Vade Hesaplayıcı")

# -------------------------------------------------
# Üst butonlar
# -------------------------------------------------
top1, top2 = st.columns([1, 5])

with top1:
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

    if st.button("➕ Yeni Çek Ekle", key="bottom_add_button", use_container_width=True):
        add_check()
        st.rerun()

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
# Sağ panel - Özet
# -------------------------------------------------
with right_col:
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
    st.markdown("**PNG Özet Çıktı**")
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
    st.markdown(
        '<div class="note-text">PNG çıktıda sadece hesaba dahil edilen çekler yer alır.</div>',
        unsafe_allow_html=True
    )
