import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

st.set_page_config(page_title="Çek Ortalama Vade Hesaplayıcı", layout="wide")

st.title("Çek Ortalama Vade Hesaplayıcı")

# Session state başlangıçları
if "checks" not in st.session_state:
    st.session_state.checks = []

if "counter" not in st.session_state:
    st.session_state.counter = 1


def format_tl(value: float) -> str:
    """Türkçe formatta TL gösterimi"""
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} TL"


def format_date_tr(d: date) -> str:
    """gg.aa.yyyy formatı"""
    return d.strftime("%d.%m.%Y")


def add_check_row():
    today = date.today()
    st.session_state.checks.append({
        "id": st.session_state.counter,
        "active": True,
        "amount": 0.0,
        "due_date": today
    })
    st.session_state.counter += 1


def remove_all_rows():
    st.session_state.checks = []


# Üst butonlar
col_btn1, col_btn2 = st.columns([1, 1])

with col_btn1:
    if st.button("➕ Ekle", use_container_width=True):
        add_check_row()

with col_btn2:
    if st.button("🗑️ Tüm Listeyi Temizle", use_container_width=True):
        remove_all_rows()
        st.rerun()


# İlk açılışta boş görünmesin isteyenler için bir satır eklemek istersen bunu aç:
if len(st.session_state.checks) == 0:
    add_check_row()


st.markdown("### Çek Listesi")

updated_checks = []

header_cols = st.columns([0.8, 1.8, 1.8, 0.8])
header_cols[0].markdown("**Dahil**")
header_cols[1].markdown("**Tutar (TL)**")
header_cols[2].markdown("**Vade Tarihi**")
header_cols[3].markdown("**Kalem**")

for i, item in enumerate(st.session_state.checks):
    cols = st.columns([0.8, 1.8, 1.8, 0.8])

    active = cols[0].checkbox(
        label="",
        value=item["active"],
        key=f"active_{item['id']}"
    )

    amount = cols[1].number_input(
        label="",
        min_value=0.0,
        value=float(item["amount"]),
        step=1000.0,
        format="%.2f",
        key=f"amount_{item['id']}"
    )

    due_date = cols[2].date_input(
        label="",
        value=item["due_date"],
        format="DD.MM.YYYY",
        key=f"due_{item['id']}"
    )

    cols[3].markdown(f"**#{i+1}**")

    updated_checks.append({
        "id": item["id"],
        "active": active,
        "amount": amount,
        "due_date": due_date
    })

st.session_state.checks = updated_checks


# Hesaplama
active_checks = [
    x for x in st.session_state.checks
    if x["active"] and x["amount"] > 0
]

st.markdown("---")
st.markdown("## Sonuçlar")

if len(active_checks) == 0:
    st.warning("Hesaplama için en az 1 adet aktif ve tutarı 0'dan büyük çek girilmeli.")
else:
    total_amount = sum(x["amount"] for x in active_checks)

    # Ortalama vade = tutar ağırlıklı ortalama tarih
    # Referans olarak epoch yerine bugünü kullanmak daha okunabilir
    base_date = date.today()

    weighted_days_sum = 0.0
    for x in active_checks:
        day_diff = (x["due_date"] - base_date).days
        weighted_days_sum += x["amount"] * day_diff

    avg_days = weighted_days_sum / total_amount
    avg_due_date = base_date + timedelta(days=round(avg_days))
    remaining_days = (avg_due_date - base_date).days

    col1, col2, col3 = st.columns(3)

    col1.metric("Toplam Çek Tutarı", format_tl(total_amount))
    col2.metric("Ortalama Vade", format_date_tr(avg_due_date))
    col3.metric("Hesap Gününden İtibaren Kalan Gün", f"{remaining_days} gün")

    # Alt tablo
    st.markdown("### Detay Liste")

    detail_rows = []
    for idx, x in enumerate(st.session_state.checks, start=1):
        kalan_gun = (x["due_date"] - date.today()).days
        detail_rows.append({
            "Kalem": idx,
            "Hesaba Dahil": "Evet" if x["active"] else "Hayır",
            "Tutar": format_tl(x["amount"]),
            "Vade Tarihi": format_date_tr(x["due_date"]),
            "Vadeye Kalan Gün": kalan_gun
        })

    df = pd.DataFrame(detail_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
