import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

st.title("📘 Jurnal Umum — Input Manual")

# ================================
# 1. INPUT BULAN DARI USER
# ================================
bulan = st.selectbox(
    "Pilih Bulan",
    ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
     "Agustus", "September", "Oktober", "November", "Desember"],
)

st.write(f"### Bulan dipilih: **{bulan}**")


# ======================================
# 2. SIAPKAN SESSION STATE UNTUK TABEL
# ======================================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        {
            "Tanggal": [""],
            "Akun": [""],
            "Debit": [0],
            "Kredit": [0],
            "Keterangan": [""],
        }
    )


# ======================================
# 3. CONFIG AGGRID
# ======================================
gb = GridOptionsBuilder.from_dataframe(st.session_state.df)
gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)

# Opsi pemilihan baris untuk hapus
gb.configure_selection('single', use_checkbox=True)

grid_options = gb.build()

# Show Grid
grid_response = AgGrid(
    st.session_state.df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme='material',
    allow_unsafe_jscode=True,
    height=300
)

# Update dataframe setelah diedit
st.session_state.df = grid_response["data"]


# ======================================
# 4. TOMBOL TAMBAH BARIS
# ======================================
if st.button("➕ Tambah Baris"):
    st.session_state.df.loc[len(st.session_state.df)] = ["", "", 0, 0, ""]
    st.experimental_rerun()


# ======================================
# 5. TOMBOL HAPUS BARIS
# ======================================
selected_rows = grid_response["selected_rows"]

if st.button("❌ Hapus Baris"):
    if selected_rows:
        index_to_delete = selected_rows[0]["_selectedRowNodeInfo"]["nodeRowIndex"]
        st.session_state.df = st.session_state.df.drop(index_to_delete).reset_index(drop=True)
        st.experimental_rerun()
    else:
        st.warning("Pilih baris dahulu yang ingin dihapus!")


# ======================================
# 6. VALIDASI OTOMATIS
# ======================================
def validate(df):
    errors = []

    for i, row in df.iterrows():

        # Tanggal wajib diisi
        if row["Tanggal"] in ["", None]:
            errors.append(f"Baris {i+1}: Tanggal harus diisi.")

        # Debit/Kredit harus >= 0
        try:
            if float(row["Debit"]) < 0:
                errors.append(f"Baris {i+1}: Debit tidak boleh negatif.")
            if float(row["Kredit"]) < 0:
                errors.append(f"Baris {i+1}: Kredit tidak boleh negatif.")
        except:
            errors.append(f"Baris {i+1}: Debit/Kredit harus angka.")

        # Debit dan Kredit tidak boleh dua-duanya terisi
        if float(row["Debit"]) > 0 and float(row["Kredit"]) > 0:
            errors.append(f"Baris {i+1}: Debit dan Kredit tidak boleh terisi bersamaan.")

    return errors


errors = validate(st.session_state.df)

if errors:
    st.error("⚠️ Ada kesalahan input:")
    for e in errors:
        st.write("- ", e)
else:
    st.success("✔️ Semua data valid!")


# ======================================
# 7. HASIL AKHIR
# ======================================
st.write("### 📄 Data Jurnal Umum Saat Ini:")
st.dataframe(st.session_state.df)
