import streamlit as st
import pandas as pd
from datetime import date

# === Konfigurasi dasar ===
st.set_page_config(page_title="Administrasi BUMDes", layout="wide")
st.title("📘 Sistem Akuntansi BUMDes")

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

# =========================
#         JURNAL UMUM
# =========================
with tab1:
    st.header("🧾 Jurnal Umum (Input Transaksi)")

    # Inisialisasi DataFrame jurnal di session_state jika belum ada
    if "jurnal" not in st.session_state:
        cols = ["Tanggal", "Keterangan", "Ref", "Debit", "Kredit"]
        st.session_state.jurnal = pd.DataFrame(columns=cols)

    # Form input transaksi
    with st.form("form_input_jurnal"):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            tgl = st.date_input("Tanggal", value=date.today())
            ket = st.text_input("Keterangan", placeholder="Deskripsi transaksi")
        with c2:
            ref = st.text_input("Ref", placeholder="Mis. JU-1")
            tipe = st.radio("Tipe", ["Debit", "Kredit"], horizontal=True)
        with c3:
            jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, format="%.0f")
            submit = st.form_submit_button("Tambah")

    if submit:
        if ket.strip() == "":
            st.error("Mohon isi kolom keterangan!")
        elif jumlah <= 0:
            st.error("Jumlah harus lebih dari nol!")
        else:
            debit = jumlah if tipe == "Debit" else 0.0
            kredit = jumlah if tipe == "Kredit" else 0.0

            new_row = {
                "Tanggal": tgl,
                "Keterangan": ket.strip(),
                "Ref": ref.strip(),
                "Debit": float(debit),
                "Kredit": float(kredit),
            }
            st.session_state.jurnal = pd.concat(
                [st.session_state.jurnal, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("Transaksi berhasil ditambahkan!")

    st.divider()

    # Tampilkan tabel jurnal dengan total dan opsi hapus baris
    df_jurnal = st.session_state.jurnal.copy()

    if not df_jurnal.empty:
        st.subheader("Data Jurnal Umum")

        # Nomori baris mulai dari 1 (untuk tampilan saja)
        df_display = df_jurnal.copy()
        df_display.index = range(1, len(df_display) + 1)

        # Hitung total debit dan kredit
        total_debit = df_jurnal["Debit"].sum()
        total_kredit = df_jurnal["Kredit"].sum()

        # Tambah baris total (untuk tampilan)
        total_row = pd.DataFrame({
            "Tanggal": [""],
            "Keterangan": ["TOTAL"],
            "Ref": [""],
            "Debit": [total_debit],
            "Kredit": [total_kredit],
        })
        df_final = pd.concat([df_display, total_row], ignore_index=False)

        # Format tampilan
        def fmt_tgl(v):
            try:
                return pd.to_datetime(v).strftime("%d-%m-%Y")
            except Exception:
                return v

        styler = df_final.style.format({
            "Tanggal": fmt_tgl,
            "Debit": "Rp {:,.0f}".format,
            "Kredit": "Rp {:,.0f}".format
        }).set_properties(**{"text-align": "center"})

        st.dataframe(styler, use_container_width=True)

        cdel1, cdel2, cdel3 = st.columns([2, 1, 1])
        with cdel1:
            del_idx = st.number_input(
                "Hapus baris nomor",
                min_value=1,
                max_value=len(df_jurnal),
                step=1,
                value=1,
                help="Pilih nomor baris (bukan baris TOTAL)"
            )
        with cdel2:
            if st.button("Hapus Baris"):
                # Map nomor tampilan (1..N) ke index asli (0..N-1)
                st.session_state.jurnal = st.session_state.jurnal.drop(
                    st.session_state.jurnal.index[int(del_idx) - 1]
                ).reset_index(drop=True)
                st.success(f"Baris {int(del_idx)} berhasil dihapus!")
                st.rerun()
        with cdel3:
            if st.button("Hapus Semua"):
                st.session_state.jurnal = st.session_state.jurnal.iloc[0:0].copy()
                st.success("Semua baris jurnal berhasil dihapus!")
                st.rerun()
    else:
        st.info("Belum ada data transaksi di Jurnal Umum.")

# =========================
#        BUKU BESAR
# =========================
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
            dfx[c] = pd.to_numeric
