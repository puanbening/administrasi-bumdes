import base64
import json
import requests
import streamlit as st

# -----------------------------------------
# CONFIG
# -----------------------------------------
GITHUB_REPO = "puanbening/administrasi-bumdes"
GITHUB_FILE_PATH = "backup/jurnal.json"   # folder + nama file di repo
GITHUB_BRANCH = "main"

# Load token dari Streamlit Secret
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# -----------------------------------------
# GET FILE SHA (dibutuhkan untuk update)
# -----------------------------------------
def get_file_sha():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        return r.json()["sha"]
    return None  # file belum ada


# -----------------------------------------
# BACKUP KE GITHUB
# -----------------------------------------
def backup_to_github(data_dict):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

    # Konversi dict → JSON → base64
    content_json = json.dumps(data_dict, indent=4)
    content_base64 = base64.b64encode(content_json.encode()).decode()

    sha = get_file_sha()

    payload = {
        "message": "Auto-backup jurnal via Streamlit",
        "content": content_base64,
        "branch": GITHUB_BRANCH
    }

    if sha:
        payload["sha"] = sha  # untuk update file

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload))

    if response.status_code in [200, 201]:
        st.success("Backup berhasil disimpan ke GitHub!")
    else:
        st.error(f"Backup gagal. Status: {response.status_code}")
        st.write(response.json())
