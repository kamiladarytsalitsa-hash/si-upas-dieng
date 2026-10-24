import streamlit as st
import requests
import math
import time

# Koordinat Dataran Tinggi Dieng
LATITUDE = -7.2062
LONGITUDE = 109.9198

# Mengambil data cuaca saat ini secara otomatis dari internet
url = f"https://open-meteo.com{LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m&timezone=Asia%2FJakarta"
response = requests.get(url).json()

suhu_sekarang = response['current']['temperature_2m']
kelembapan_sekarang = response['current']['relative_humidity_2m']

# --- PENGATURAN HALAMAN DASHBOARD ---
st.set_page_config(page_title="Si-Upas Dieng", page_icon="❄️", layout="wide")

# --- JUDUL APLIKASI ---
st.title("❄️ Si-Upas: Dashboard Mitigasi Embun Es Dataran Tinggi Dieng")
st.markdown("### 🏛️ Platform Peringatan Dini Cerdas Penyelamat Komoditas Pertanian Kentang")

# --- MENAMPILKAN KONDISI CUACA REAL-TIME ---
st.subheader("📊 Kondisi Cuaca Dieng Saat Ini (Otomatis)")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Suhu Udara Saat Ini", value=f"{suhu_sekarang} °C")
with col2:
    st.metric(label="Kelembapan Udara Saat Ini", value=f"{kelembapan_sekarang} %")

# --- LOGIKA MITIGASI PERINGATAN DINI ---
# Bagian ini otomatis mendeteksi ancaman embun upas berdasarkan data cuaca asli
if suhu_sekarang <= 4.0:
    st.error(f"⚠️ PERINGATAN DINI: Suhu sangat dingin ({suhu_sekarang}°C). Embun Upas Berpotensi Muncul! Petani dimohon bersiap menyalakan sprinkler atau menutup tanaman kentang.")
else:
    st.success(f"✅ KONDISI AMAN: Suhu ({suhu_sekarang}°C) masih berada di batas aman. Belum ada indikasi pembentukan embun beku.")
