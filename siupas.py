import streamlit as st
import math
import requests
import time

# --- PENGATURAN HALAMAN DASHBOARD ---
st.set_page_config(page_title="Si-Upas Dieng (Telegram)", page_icon="❄️", layout="wide")

# --- JUDUL APLIKASI ---
st.title("❄️ Si-Upas: Dashboard Mitigasi Embun Es Dataran Tinggi Dieng")
st.markdown("### *Platform Peringatan Dini Cerdas Menggunakan Telegram Gateway*")
st.write("---")

# --- KREDENSIAL TELEGRAM (SUDAH DIKUNCI OTOMATIS) ---
TOKEN_BOT = "8954962424:AAGJKj6D9ZE-44iYeoLub9fqObfF3Xju3SY"
CHAT_ID_JURI = "6778628136"

# --- SIDEBAR INPUT DATA (UNTUK SIMULASI DI DEPAN JURI) ---
st.sidebar.header("🛠️ Panel Simulator Cuaca")
st.sidebar.write("Ubah nilai di bawah ini untuk menyimulasikan perubahan cuaca ekstrem Dieng:")

# Input angka cuaca dinamis oleh juri
input_suhu = st.sidebar.slider("Suhu Udara Saat Ini (°C)", min_value=-5.0, max_value=25.0, value=15.0, step=0.5)
input_kelembapan = st.sidebar.slider("Kelembapan Udara (%)", min_value=10, max_value=100, value=75, step=1)

st.sidebar.write("---")
st.sidebar.info("🤖 **Status Sistem:** Jalur API Telegram Terhubung Aktif.")

# --- ALGORITMA METEOROLOGI: MENGHITUNG TITIK EMBUN (DEW POINT) ---
a = 17.27
b = 237.7
try:
    alpha = ((a * input_suhu) / (b + input_suhu)) + math.log(input_kelembapan / 100.0)
    dew_point = (b * alpha) / (a - alpha)
except ValueError:
    dew_point = 0.0

# --- LOGIKA EVALUASI RISIKO ---
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

# --- TAMPILAN DASHBOARD ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Suhu Terbaca", value=f"{input_suhu} °C")
with col2:
    st.metric(label="Kelembapan Udara", value=f"{input_kelembapan} %")
with col3:
    st.metric(label="Prediksi Titik Beku (Dew Point)", value=f"{round(dew_point, 2)} °C")

st.write("---")
st.markdown(f"### STATUS ZONA LAHAN: <span style='color:{warna_status}; font-weight:bold;'>{status_bahaya}</span>", unsafe_allow_html=True)
st.progress(persentase_risiko)
# --- SISTEM BROADCAST TELEGRAM ---
st.write("### 📬 Log Sistem Peringatan Otomatis (Telegram Gateway)")

if st.button("🚀 Jalankan Evaluasi & Kirim Peringatan"):
    with st.spinner("Mengirimkan sinyal peringatan dini ke Telegram..."):
        time.sleep(1)
        
        # Teks pesan peringatan resmi untuk juri
        isi_pesan = f"❄️ *[SI-UPAS DIENG LIVE REPORT]* ❄️\n\n" \
                    f"⚠️ *PERINGATAN DINI!* Kondisi iklim mikro kritis.\n" \
                    f"📍 *Lokasi:* Zona Pertanian Dieng\n" \
                    f"🌡️ *Suhu:* {input_suhu}°C\n" \
                    f"💧 *Kelembapan:* {input_kelembapan}%\n" \
                    f"🚨 *Status:* {status_bahaya}\n\n" \
                    f"_*Tindakan:* Mohon segera nyalakan sistem pemanas mekanis atau hamparkan mulsa pelindung pada petak kentang Anda._"
        
# --- SISTEM BROADCAST TELEGRAM AUTOMATION VIA API ---
st.write("### 📲 Log Sistem Peringatan Otomatis (Telegram Gateway)")

if st.button("🚀 Jalankan Evaluasi & Kirim Notifikasi"):
    if not no_hp_juri:
        st.warning("Silakan masukkan Chat ID Telegram pengujian terlebih dahulu pada panel kiri!")
    else:
        with st.spinner("Sistem sedang mengevaluasi kondisi iklim mikro..."):
            time.sleep(1.5) # Efek jeda pengolahan data AI
            
            # Teks pesan otomatis yang disesuaikan dengan tingkat kerawanan cuaca
            isi_pesan = f"❄️ *[SI-UPAS DIENG INFORMASI]* ❄️\n\n" \
                        f"⚠️ *PERINGATAN DINI!* Kondisi Lahan kritis.\n" \
                        f"• Suhu: {input_suhu}°C\n" \
                        f"• Kelembapan: {input_kelembapan}%\n" \
                        f"• Status: *{status_bahaya}*\n\n" \
                        f"Mohon segera aktifkan mesin pemanas atau pelindung tanaman kentang Anda!"
            
            # Koding URL Protocol API Resmi Telegram
            TOKEN_BOT = "5222690292:AAHpTsw3ynWX0WA-2WonGErslqmoFjLHkvA" # Bot token simulasi
            url_telegram = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
            
            payload = {
                "chat_id": no_hp_juri,
                "text": isi_pesan,
                "parse_mode": "Markdown"
            }
            
            try:
                # Proses Requests mengirimkan kode langsung ke akun Telegram Anda/Juri
                respon = requests.post(url_telegram, json=payload)
                
                if respon.status_code == 200:
                    st.success(f"Log: Algoritma memicu respon otomatis! Instruksi peringatan terkirim ke Telegram ID: {no_hp_juri}")
                    st.info(f"Isi Pesan Terkirim:\n\n{isi_pesan}")
                else:
                    st.error(f"Gagal mengirim! Kode Error Telegram: {respon.status_code}. Pastikan Chat ID benar dan Bot sudah di-start.")
            except Exception as e:
                st.error(f"Terjadi masalah jaringan: {e}")
