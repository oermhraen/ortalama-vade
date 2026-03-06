import streamlit as st
from datetime import date, timedelta

st.set_page_config(
    page_title="Çek Ortalama Vade Hesaplayıcı",
    layout="wide"
)

# ---------------------------
# Yardımcı fonksiyonlar
# ---------------------------
def parse_amount(text):
    """
    Kullanıcının girdiği tutarı sayıya çevirir.
    Kabul edilen örnekler:
    1000000
    1.000.000
    1,000,000
    1.000.000 TL
    """
    if text is None:
        return 0

    text = str(text).strip().upper().replace("TL", "").replace(" ", "")

    if not text:
        return 0

    # Ondalık istemiyoruz, tüm virgül/nokta ayraçlarını kaldırıyoruz
    cleaned = text.replace(".", "").replace(",", "")

    try:
        value = int(cleaned)
        return max(value, 0)
    except:
        return 0


def format_tl(value):
    """1.000.000 TL formatı"""
    try:
        return f"{int(round(value)):,}".replace(",", ".") + " TL"
    except:
        return "0 TL"


def format_date_tr(d):
    return d.strftime("%d.%m.%Y")


# ---------------------------
# Session state
# ---------------------------
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


# ---------------------------
# Stil
# ---------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1400px;
}
div[data-testid="stMetric"] {
    background: #f7f7f9;
    border: 1px solid #e5e7eb;
    padding: 14px 16px;
    border-radius: 12px;
}
.small-label {
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 4px;
}
.list-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px;
}
.side-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px;
}
.section-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 10px;
}
.row-sep {
    border-bottom: 1px solid #f0f0f0;
    margin: 8px 0 12px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("Çek Ortalama Vade Hesaplayıcı")

# ---------------------------
# Üst butonlar
# ---------------------------
top1, top2, top3 = st.columns([1, 1, 5])

with top1:
    if st.button("➕ Ekle", use_container_width=True):
        add_check()
        st.rerun()

with top2:
    if st.button("🗑️ Temizle", use_container_width=True):
        st.session_state.checks = [
            {
                "id": 1,
                "active": True,
                "amount_text": "",
                "due_date": date.today()
            }
        ]
        st.session_state.counter = 2
        st.rerun()

st.markdown("")

# ---------------------------
# Ana yerleşim
# ---------------------------
left_col, right_col = st.columns([2.2, 1], gap="large")

# ---------------------------
# Sol: Çek listesi
# ---------------------------
with left_col:
    st.markdown('<div class="list-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Çek Listesi</div>', unsafe_allow_html=True)

    h1, h2, h3, h4 = st.columns([0.6, 2.2, 1.5, 0.7])
    h1.markdown("**Dahil**")
    h2.markdown("**Tutar (TL)**")
    h3.markdown("**Vade Tarihi**")
    h4.markdown("**Kalem**")

    updated_checks = []

    for i, item in enumerate(st.session_state.checks, start=1):
        c1, c2, c3, c4 = st.columns([0.6, 2.2, 1.5, 0.7])

        active = c1.checkbox(
            label="",
            value=item["active"],
            key=f"active_{item['id']}"
        )

        amount_text = c2.text_input(
            label="",
            value=item["amount_text"],
            placeholder="Örn: 1.000.000",
            key=f"amount_{item['id']}"
        )

        due_date = c3.date_input(
            label="",
            value=item["due_date"],
            format="DD.MM.YYYY",
            key=f"due_{item['id']}"
        )

        c4.markdown(f"**#{i}**")

        st.markdown('<div class="row-sep"></div>', unsafe_allow_html=True)

        updated_checks.append(
            {
                "id": item["id"],
                "active": active,
                "amount_text": amount_text,
                "due_date": due_date
            }
        )

    st.session_state.checks = updated_checks
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Hesaplama
# ---------------------------
active_checks = []
today = date.today()

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

    weighted_days_sum = 0
    for x in active_checks:
        day_diff = (x["due_date"] - today).days
        weighted_days_sum += x["amount"] * day_diff

    avg_days = round(weighted_days_sum / total_amount)
    avg_due_date = today + timedelta(days=avg_days)
    remaining_days = (avg_due_date - today).days
else:
    total_amount = 0
    avg_due_date = None
    remaining_days = 0

# ---------------------------
# Sağ: Özet bilgiler
# ---------------------------
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

    aktif_adet = len(active_checks)
    toplam_adet = len(st.session_state.checks)

    st.write(f"**Toplam Kalem:** {toplam_adet}")
    st.write(f"**Hesaba Dahil Çek:** {aktif_adet}")

    st.markdown("---")

    st.caption("Not: Ortalama vade, çek tutarları ağırlık kabul edilerek hesaplanır.")
    st.markdown('</div>', unsafe_allow_html=True)
