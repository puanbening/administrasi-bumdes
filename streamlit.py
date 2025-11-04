import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile

st.title("📘 Jurnal Umum BUMDes - Januari 2025")

# Inisialisasi session state untuk menyimpan entri
if "data" not in st.session_state:
    st.session_state.data = []

# Form input
with st.form("input_form"):
    tanggal = st.date_input("Tanggal")
    keterangan = st.text_input("Keterangan")
    ref = st.text_input("Ref")
    debit = st.number_input("Debit (Rp)", min_value=0, step=1000)
    kredit = st.number_input("Kredit (Rp)", min_value=0, step=1000)
    submitted = st.form_submit_button("Tambah Data")

    if submitted:
        st.session_state.data.append({
            "Tanggal": tanggal,
            "Keterangan": keterangan,
            "Ref": ref,
            "Debit (Rp)": debit,
            "Kredit (Rp)": kredit
        })
        st.success("✅ Data berhasil ditambahkan!")

# Tampilkan tabel
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)

    # Hitung total debit dan kredit
    total_debit = df["Debit (Rp)"].sum()
    total_kredit = df["Kredit (Rp)"].sum()
    st.write(f"**Total Debit:** Rp {total_debit:,.0f}")
    st.write(f"**Total Kredit:** Rp {total_kredit:,.0f}")

    # Tombol download PDF
    if st.button("📄 Download PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Jurnal Umum BUMDes - Januari 2025", ln=True, align="C")
        pdf.ln(10)

        # Header tabel
        pdf.set_font("Arial", "B", 10)
        col_widths = [25, 60, 20, 40, 40]
        headers = ["Tanggal", "Keterangan", "Ref", "Debit (Rp)", "Kredit (Rp)"]
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 10, header, 1, 0, "C")
        pdf.ln()

        # Data tabel
        pdf.set_font("Arial", "", 9)
        for _, row in df.iterrows():
            pdf.cell(25, 10, str(row["Tanggal"]), 1)
            pdf.cell(60, 10, str(row["Keterangan"]), 1)
            pdf.cell(20, 10, str(row["Ref"]), 1)
            pdf.cell(40, 10, f"{int(row['Debit (Rp)']):,}", 1, 0, "R")
            pdf.cell(40, 10, f"{int(row['Kredit (Rp)']):,}", 1, 0, "R")
            pdf.ln()

        # Total
        pdf.set_font("Arial", "B", 10)
        pdf.cell(105, 10, "Jumlah", 1)
        pdf.cell(40, 10, f"{int(total_debit):,}", 1, 0, "R")
        pdf.cell(40, 10, f"{int(total_kredit):,}", 1, 0, "R")

        # Simpan PDF sementara
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)

        # Tombol download
        with open(temp_file.name, "rb") as f:
            st.download_button(
                label="⬇️ Klik untuk Download PDF",
                data=f,
                file_name="Jurnal_BUMDes_Januari2025.pdf",
                mime="application/pdf"
            )

else:
    st.info("Silakan masukkan data terlebih dahulu melalui form di atas.")
