import streamlit as st
import math
import time
import streamlit as st
import requests

# Koordinat Dataran Tinggi Dieng
LATITUDE = -7.2062
LONGITUDE = 109.9198
# Mengambil data cuaca saat ini secara otomatis
url = f"https://open-meteo.com{LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m&timezone=Asia%2FJakarta"response = requests.get(url).json()

# Membaca suhu dan kelembapan terbaru dari internet
suhu_sekarang = response['current']['temperature_2m']
kelembapan_sekarang = response['current']['relative_humidity_2m']
# --- PENGATURAN HALAMAN DASHBOARD ---
st.set_page_config(page_title="Si-Upas Dieng", page_icon="❄️", layout="wide")

# --- JUDUL APLIKASI ---
st.title("❄️ Si-Upas: Dashboard Mitigasi Embun Es Dataran Tinggi Dieng")
st.markdown("### *Platform Peringatan Dini Cerdas Penyelamat Komoditas Pertanian Kentang*")
st.write("---")

# --- SIDEBAR INPUT DATA ---
st.sidebar.header("🛠️ Panel Simulator Cuaca")
st.sidebar.write("Ubah nilai di bawah ini untuk menyimulasikan perubahan cuaca ekstrem Dieng:")

# Input angka cuaca dinamis oleh juri
input_suhu = st.sidebar.slider("Suhu Udara Saat Ini (°C)", min_value=-5.0, max_value=25.0, value=15.0, step=0.5)
input_kelembapan = st.sidebar.slider("Kelembapan Udara (%)", min_value=10, max_value=100, value=75, step=1)

# --- ALGORITMA METEOROLOGI: MENGHITUNG TITIK EMBUN (DEW POINT) ---
a = 17.27
b = 237.7
try:
    alpha = ((a * input_suhu) / (b + input_suhu)) + math.log(input_kelembapan / 100.0)
    dew_point = (b * alpha) / (a - alpha)
except ValueError:
    dew_point = 0.0

# --- LOGIKA EVALUASI RISIKO (OTAK AI DIGITAL) ---
status_bahaya = "AMAN"
warna_status = "green"
persentase_risiko = 10
rekomendasi_tani = "Kondisi cuaca aman untuk tanaman kentang. Lakukan perawatan rutin seperti biasa."

if input_suhu <= 4.0:
    if dew_point <= 1.5:
        status_bahaya = "BAHAYA EKSTREM (AWAS EMBUN UPAS!)"
        warna_status = "red"
        persentase_risiko = 95
        rekomendasi_tani = "⚠️ SEGARA AKTIFKAN pemanas lahan elektrik, nyalakan thermal smudging (kabut asap hangat), atau tutup bedengan kentang menggunakan mulsa plastik pelindung!"
    else:
        status_bahaya = "WASPADA (POTENSI EMBUN BEKU)"
        warna_status = "orange"
        persentase_risiko = 60
        rekomendasi_tani = "Pantau penurunan suhu secara berkala. Siapkan perangkat penyiraman tanaman untuk membilas sisa es di pagi hari."
else:
    status_bahaya = "AMAN DAN NORMAL"
    warna_status = "green"
    persentase_risiko = 10
    rekomendasi_tani = "Kondisi cuaca aman untuk tanaman kentang. Lakukan perawatan rutin seperti biasa."

# --- TAMPILAN DASHBOARD UTAMA ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Suhu Terbaca", value=f"{input_suhu} °C")
with col2:
    st.metric(label="Kelembapan Udara", value=f"{input_kelembapan} %")
with col3:
    st.metric(label="Prediksi Titik Beku (Dew Point)", value=f"{round(dew_point, 2)} °C")

st.write("---")

# Menampilkan Status Bahaya dengan Kotak Berwarna Dinamis
st.markdown(f"### STATUS ZONA LAHAN: <span style='color:{warna_status}; font-weight:bold;'>{status_bahaya}</span>", unsafe_allow_html=True)
st.progress(persentase_risiko)

st.write("---")

# --- PANEL REKOMENDASI OTOMATIS DI LAYAR ---
st.markdown("### 📋 Panduan Tindakan Otomatis untuk Petani:")
st.info(rekomendasi_tani)

# Halaman akan otomatis membaca data baru dari API setiap 10 menit (600 detik)
st.fragment(run_every=600)
def update_data_cuaca():
    # Masukkan logika if-else mitigasi embun upas Anda di sini
    if suhu_sekarang <= 4.0:
        st.error(f"⚠️ PERINGATAN: Suhu Dieng {suhu_sekarang}°C. Embun Upas Berpotensi Muncul!")
    else:
        st.success(f"✅ AMAN: Suhu Dieng {suhu_sekarang}°C. Kondisi cenderung normal.")
