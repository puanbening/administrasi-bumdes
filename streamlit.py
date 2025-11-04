import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile

# === Konfigurasi Halaman ===
st.set_page_config(page_title="Administrasi BUMDes", layout="wide")
st.title("📘 Sistem Akuntansi BUMDes")

# === Inisialisasi Data Awal ===
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Tanggal": "", "Keterangan": "", "Ref": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
    ])

# === Fungsi Format ===
def format_rupiah(x):
    try:
        return f"Rp {x:,.0f}".replace(",", ".")
    except Exception:
        return x  # fallback kalau kolom kosong / non-numeric

# === Fungsi Styling (kalau mau digunakan di masa depan) ===
def style_excel(df):
    return df.style.set_table_styles([
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
    ]).format({"Debit (Rp)": format_rupiah, "Kredit (Rp)": format_rupiah})

# === Navigasi Halaman ===
tab1, tab2 = st.tabs(["🧾 Jurnal Umum", "📚 Buku Besar"])

# ================= TAB 1 =====================
with tab1:
    st.header("🧾 Jurnal Umum")

    st.info("✏️ Klik langsung di tabel untuk menambah atau mengubah data.")

    # Editor Data Interaktif
    edited_df = st.data_editor(
        st.session_state.data,
        num_rows="dynamic",
        use_container_width=True,
        key="editable_table",
        column_config={
            "Tanggal": st.column_config.TextColumn("Tanggal (misal: 2025-01-01)"),
            "Keterangan": st.column_config.TextColumn("Keterangan"),
            "Ref": st.column_config.TextColumn("Ref (contoh: 101)"),
            "Debit (Rp)": st.column_config.NumberColumn("Debit (Rp)", step=1000),
            "Kredit (Rp)": st.column_config.NumberColumn("Kredit (Rp)", step=1000),
        }
    )

    st.session_state.data = edited_df

    # === Bersihkan Data Kosong ===
    df_clean = edited_df.dropna(subset=["Keterangan"], how="all")
    df_clean = df_clean[df_clean["Keterangan"].str.strip() != ""]

    if not df_clean.empty:
        total_debit = df_clean["Debit (Rp)"].sum()
        total_kredit = df_clean["Kredit (Rp)"].sum()

        # Tambahkan baris total
        total_row = pd.DataFrame({
            "Tanggal": [""],
            "Keterangan": ["TOTAL"],
            "Ref": [""],
            "Debit (Rp)": [total_debit],
            "Kredit (Rp)": [total_kredit],
        })

        df_final = pd.concat([df_clean, total_row], ignore_index=True)

        st.write("### 📊 Hasil Jurnal")
        st.dataframe(df_final.style.format({
            "Debit (Rp)": format_rupiah,
            "Kredit (Rp)": format_rupiah
        }))

        # === Fungsi Buat PDF ===
        def buat_pdf(df):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Jurnal Umum BUMDes", ln=True, align="C")
            pdf.ln(8)

            # Header
            col_width = 190 / len(df.columns)
            for col in df.columns:
                pdf.cell(col_width, 10, col, border=1, align="C")
            pdf.ln()

            # Isi tabel
            pdf.set_font("Arial", size=10)
            for _, row in df.iterrows():
                for item in row:
                    pdf.cell(col_width, 8, str(item), border=1, align="C")
                pdf.ln()

            # Simpan ke file sementara
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                tmp.seek(0)
                return tmp.read()

        pdf_data = buat_pdf(df_final)

        # Tombol download
        st.download_button(
            "📥 Download PDF",
            data=pdf_data,
            file_name="jurnal_umum.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    else:
        st.warning("Belum ada data valid di tabel.")

# ================= TAB 2 =====================
with tab2:
    st.header("📚 Buku Besar")
    st.info("Fitur ini sedang dalam pengembangan 🚧")
