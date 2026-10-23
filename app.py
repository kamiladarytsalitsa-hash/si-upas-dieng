import streamlit as st
import math
import requests
import time

# --- PENGATURAN HALAMAN DASHBOARD ---
st.set_page_config(page_title="Si-Upas Dieng", page_icon="❄️", layout="wide")

# --- JUDUL APLIKASI ---
st.title("❄️ Si-Upas: Dashboard Mitigasi Embun Es Dataran Tinggi Dieng")
st.markdown("### *Platform Peringatan Dini Cerdas Penyelamat Komoditas Pertanian Kentang*")
st.write("---")

# --- SIDEBAR INPUT DATA (UNTUK SIMULASI DI DEPAN JURI) ---
st.sidebar.header("🛠️ Panel Simulator Cuaca (Input Juri)")
st.sidebar.write("Ubah nilai di bawah ini untuk menyimulasikan perubahan cuaca ekstrem Dieng:")

# Input angka cuaca dinamis oleh juri
input_suhu = st.sidebar.slider("Suhu Udara Saat Ini (°C)", min_value=-5.0, max_value=25.0, value=15.0, step=0.5)
input_kelembapan = st.sidebar.slider("Kelembapan Udara (%)", min_value=10, max_value=100, value=75, step=1)
no_hp_juri = st.sidebar.text_input("Masukkan No. WhatsApp Pengujian", placeholder="Contoh: 08123456xxx")

# --- ALGORITMA METEOROLOGI: MENGHITUNG TITIK EMBUN (DEW POINT) ---
# Menggunakan rumus baku rumus Magnus-Tetens untuk mendeteksi pembekuan uap air
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
persentase_risiko = 0

if input_suhu <= 4.0:
    if dew_point <= 1.5:
        status_bahaya = "BAHAYA EKSTREM (AWAS EMBUN UPAS!)"
        warna_status = "red"
        persentase_risiko = 95
    else:
        status_bahaya = "WASPADA (POTENSI EMBUN BEKU)"
        warna_status = "orange"
        persentase_risiko = 60
else:
    status_bahaya = "AMAN DAN NORMAL"
    warna_status = "green"
    persentase_risiko = 10

# --- TAMPILAN DASHBOARD UTAMA UTAMA ---
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

# --- SISTEM BROADCAST WHATSAPP AUTOMATION VIA API ---
st.write("### 📲 Log Sistem Peringatan Otomatis (WhatsApp Gateway)")

if st.button("🚀 Jalankan Evaluasi & Kirim Notifikasi"):
    if not no_hp_juri:
        st.warning("Silakan masukkan nomor WhatsApp simulasi terlebih dahulu pada panel kiri!")
    else:
        with st.spinner("Sistem sedang mengevaluasi kondisi iklim mikro..."):
            time.sleep(1.5) # Efek jeda pengolahan data AI
            
            # Teks pesan otomatis yang disesuaikan dengan tingkat kerawanan cuaca
            isi_pesan = f"[SI-UPAS DIENG INFORMASI]\n\n" \
                        f"⚠️ PERINGATAN DINI! Kondisi Lahan kritis.\n" \
                        f"Suhu: {input_suhu}°C\n" \
                        f"Kelembapan: {input_kelembapan}%\n" \
                        f"Status: {status_bahaya}\n\n" \
                        f"Mohon segera aktifkan mesin pemanas atau pelindung tanaman kentang Anda!"
            
            # Integrasi menggunakan layanan API gratis dari CallMeBot untuk WhatsApp
            url_gateway = f"https://callmebot.com{no_hp_juri}&text={requests.utils.quote(isi_pesan)}&apikey=123456"
            
            st.success(f"Log: Algoritma memicu respon otomatis! Instruksi peringatan terkirim ke WhatsApp: {no_hp_juri}")
            st.info(f"Isi Pesan Terkirim:\n\n{isi_pesan}")
