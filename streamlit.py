import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from datetime import date

# === Konfigurasi dasar ===
st.set_page_config(page_title="Administrasi BUMDes", layout="wide")
st.title("📘 Sistem Akuntansi BUMDes")

# === Inisialisasi data awal untuk Jurnal Umum ===
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Tanggal": "", "Keterangan": "", "Ref": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
    ])

# === Fungsi format rupiah ===
def format_rupiah(x):
    try:
        return f"Rp {x:,.0f}".replace(",", ".")
    except Exception:
        return x

# === Styling agar mirip Streamlit ===
st.markdown("""
<style>
.ag-theme-streamlit {
    --ag-background-color: #F9FAFB;
    --ag-odd-row-background-color: #FFFFFF;
    --ag-header-background-color: #E9ECEF;
    --ag-border-color: #DDDDDD;
    --ag-header-foreground-color: #000000;
    --ag-font-family: "Inter", system-ui, sans-serif;
    --ag-font-size: 14px;
    --ag-row-hover-color: #EEF6ED;
    --ag-selected-row-background-color: #DDF0DC;
    --ag-cell-horizontal-padding: 10px;
    --ag-cell-vertical-padding: 6px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# === Tabs utama ===
tab1, tab2 = st.tabs(["🧾 Jurnal Umum", "📚 Buku Besar"])

with tab1:
    st.header("🧾 Jurnal Umum")
    st.info("💡 Tekan Enter sekali untuk menyimpan perubahan otomatis, seperti di tabel Streamlit.")

    # Setup Grid AgGrid untuk jurnal umum
    gb = GridOptionsBuilder.from_dataframe(st.session_state.data)
    gb.configure_default_column(editable=True, resizable=True)
    gb.configure_grid_options(stopEditingWhenCellsLoseFocus=False)
    gb.configure_column("Tanggal", header_name="Tanggal (YYYY-MM-DD)")
    gb.configure_column("Keterangan", header_name="Keterangan")
    gb.configure_column("Ref", header_name="Ref (contoh: 101)")
    gb.configure_column("Debit (Rp)", type=["numericColumn"], valueFormatter="value ? value.toLocaleString() : ''")
    gb.configure_column("Kredit (Rp)", type=["numericColumn"], valueFormatter="value ? value.toLocaleString() : ''")

    grid_options = gb.build()

    grid_response = AgGrid(
        st.session_state.data,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        theme="streamlit",
        height=320,
        key="aggrid_table"
    )

    # Sinkronisasi otomatis
    new_df = pd.DataFrame(grid_response["data"])
    if not new_df.equals(st.session_state.data):
        st.session_state.data = new_df.copy()
        st.toast("💾 Perubahan tersimpan otomatis!", icon="💾")

    # Bersihkan data kosong dan tampilkan total
    df_clean = new_df[new_df["Keterangan"].astype(str).str.strip() != ""]

    if not df_clean.empty:
        total_debit = df_clean["Debit (Rp)"].sum()
        total_kredit = df_clean["Kredit (Rp)"].sum()

        total_row = pd.DataFrame({
            "Tanggal": [""],
            "Keterangan": ["TOTAL"],
            "Ref": [""],
            "Debit (Rp)": [total_debit],
            "Kredit (Rp)": [total_kredit],
        })
        df_final = pd.concat([df_clean, total_row], ignore_index=True)

        st.write("### 📊 Hasil Jurnal")
        df_final_display = df_final.copy()
        df_final_display.index = range(1, len(df_final_display) + 1)
        df_final_display.index.name = "No"

        st.dataframe(df_final_display.style.format({
            "Debit (Rp)": format_rupiah,
            "Kredit (Rp)": format_rupiah
        }))

        # Fungsi buat PDF
        def buat_pdf(df):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Jurnal Umum BUMDes", ln=True, align="C")
            pdf.ln(8)

            col_width = 190 / len(df.columns)
            for col in df.columns:
                pdf.cell(col_width, 10, col, border=1, align="C")
            pdf.ln()

            pdf.set_font("Arial", size=10)
            for _, row in df.iterrows():
                for item in row:
                    pdf.cell(col_width, 8, str(item), border=1, align="C")
                pdf.ln()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                tmp.seek(0)
                return tmp.read()

        pdf_data = buat_pdf(df_final)
        st.download_button(
            "📥 Download PDF",
            data=pdf_data,
            file_name="jurnal_umum.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Belum ada data valid di tabel.")

with tab2:
    st.header("📚 Buku Besar")

    # Inisialisasi akun dan data jika belum ada
    if "accounts" not in st.session_state:
        cols = ["Tanggal", "Keterangan", "Ref", "Debit", "Kredit"]
        st.session_state.accounts = {
            "101 - Kas": pd.DataFrame(columns=cols),
            "102 - Peralatan": pd.DataFrame(columns=cols),
            "103 - Perlengkapan": pd.DataFrame(columns=cols),
            "301 - Modal": pd.DataFrame(columns=cols),
        }

    # Fungsi hitung saldo berjalan
    def hitung_saldo(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df.copy()
        dfx = df.copy()
        dfx["Tanggal"] = pd.to_datetime(dfx["Tanggal"], errors='coerce').dt.date
        for c in ["Debit", "Kredit"]:
            dfx[c] = pd.to_numeric(dfx[c], errors="coerce").fillna(0.0)
        dfx = dfx.sort_values(["Tanggal"], kind="mergesort").reset_index(drop=True)

        saldo_debit = []
        saldo_kredit = []
        running = 0.0
        for _, r in dfx.iterrows():
            running += float(r["Debit"]) - float(r["Kredit"])
            if running >= 0:
                saldo_debit.append(running)
                saldo_kredit.append(0.0)
            else:
                saldo_debit.append(0.0)
                saldo_kredit.append(abs(running))

        dfx["Saldo Debit"] = saldo_debit
        dfx["Saldo Kredit"] = saldo_kredit
        return dfx

    # Form input transaksi baru
    st.subheader("Input Transaksi Baru")
    with st.form("form_input_tb"):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            akun_pil = st.selectbox("Pilih Akun", list(st.session_state.accounts.keys()))
            ket = st.text_input("Keterangan", placeholder="contoh: Membeli peralatan")
        with c2:
            tgl = st.date_input("Tanggal", value=date.today())
            ref = st.text_input("Ref", value="JU-1")
        with c3:
            tipe = st.radio("Tipe", ["Debit", "Kredit"], horizontal=True)
            jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, format="%.0f")
        tambah = st.form_submit_button("Tambah Transaksi")

    if tambah:
        debit = jumlah if tipe == "Debit" else 0.0
        kredit = jumlah if tipe == "Kredit" else 0.0
        baris = pd.DataFrame({
            "Tanggal": [tgl],
            "Keterangan": [ket],
            "Ref": [ref],
            "Debit": [debit],
            "Kredit": [kredit],
        })
        st.session_state.accounts[akun_pil] = pd.concat(
            [st.session_state.accounts[akun_pil], baris], ignore_index=True
        )
        st.success(f"Transaksi berhasil ditambahkan di akun {akun_pil}!")

    st.divider()

    # Tampilkan tabel buku besar per akun dengan saldo berjalan, di Tabs
    akun_list = list(st.session_state.accounts.keys())
    tabs_akun = st.tabs(akun_list)

    for i, akun in enumerate(akun_list):
        with tabs_akun[i]:
            st.markdown(f"**Nama Akun : {akun.split(' - ',1)[1]}**  \nNo Akun : {akun.split(' - ',1)[0]}")
            df = st.session_state.accounts[akun]
            df_show = hitung_saldo(df) if not df.empty else df.copy()
            
            st.dataframe(
                df_show.style.format({
                    "Debit": "{:,.0f}",
                    "Kredit": "{:,.0f}",
                    "Saldo Debit": "{:,.0f}",
                    "Saldo Kredit": "{:,.0f}",
                }).set_properties(**{"text-align": "center"}),
                use_container_width=True
            )
