import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Administrasi BUMDes", layout="wide")
st.title("📘 Sistem Akuntansi Sederhana BUMDes - Januari 2025")

if "data" not in st.session_state:
    st.session_state.data = []

# Fungsi format rupiah
def format_rupiah(x):
    return f"Rp {x:,.0f}".replace(",", ".")

# Fungsi styling tabel agar mirip Excel
def style_excel(df):
    styled = df.style.set_table_styles([
        {"selector": "thead th",
         "props": [("background-color", "#b7e1cd"),
                   ("color", "black"),
                   ("border", "1px solid black"),
                   ("text-align", "center"),
                   ("font-weight", "bold")]},
        {"selector": "td",
         "props": [("border", "1px solid black"),
                   ("text-align", "center"),
                   ("padding", "4px")]}
    ]).format(
        {"Debit (Rp)": format_rupiah, "Kredit (Rp)": format_rupiah}
    )
    return styled

tab1, tab2 = st.tabs(["🧾 Jurnal Umum", "📚 Buku Besar"])

# ================= TAB 1 =====================
with tab1:
    st.header("🧾 Jurnal Umum")

    with st.form("input_form"):
        tanggal = st.date_input("Tanggal")
        keterangan = st.text_input("Keterangan")
        ref = st.text_input("Ref (contoh: 101 untuk Kas)")
        debit = st.number_input("Debit (Rp)", min_value=0, step=1000)
        kredit = st.number_input("Kredit (Rp)", min_value=0, step=1000)
        submit = st.form_submit_button("Tambah Data")

        if submit:
            st.session_state.data.append({
                "Tanggal": tanggal,
                "Keterangan": keterangan,
                "Ref": ref,
                "Debit (Rp)": debit,
                "Kredit (Rp)": kredit
            })
            st.success("✅ Data berhasil ditambahkan!")

    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        st.markdown("### 📋 Data Jurnal Umum")
        st.write(style_excel(df).to_html(), unsafe_allow_html=True)

        total_debit = df["Debit (Rp)"].sum()
        total_kredit = df["Kredit (Rp)"].sum()
        st.markdown(f"**Total Debit:** {format_rupiah(total_debit)}")
        st.markdown(f"**Total Kredit:** {format_rupiah(total_kredit)}")

# ================= TAB 2 =====================
with tab2:
    st.header("📚 Buku Besar")

    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        grouped = df.groupby("Ref")

        for ref, group in grouped:
            st.subheader(f"Nama Akun (Ref): {ref}")
            st.write(style_excel(group).to_html(), unsafe_allow_html=True)

            total_debit = group["Debit (Rp)"].sum()
            total_kredit = group["Kredit (Rp)"].sum()
            saldo = total_debit - total_kredit

            col1, col2, col3 = st.columns(3)
            col2.markdown(
                f"<div style='text-align:center; font-weight:bold; background:#e0f7fa; padding:5px; border:1px solid black;'>"
                f"Saldo Akhir: {format_rupiah(saldo)}</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("Masukkan data terlebih dahulu di tab **Jurnal Umum**.")
