import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================================
# 1. KONFIGURASI APLIKASI
# =====================================================

st.set_page_config(
    page_title="Si-Upas Dieng",
    page_icon="🌱",
    layout="wide",
)

# Masukkan token bot Telegram BARU di sini.
# Jangan unggah token asli ke repositori GitHub.
TELEGRAM_BOT_TOKEN = "8954962424:AAGJKj6D9ZE-44iYeoLub9fqObfF3Xju3SY"
TELEGRAM_CHAT_ID = "6778628136"

# Koordinat perkiraan kawasan Dieng
LATITUDE = -7.2048
LONGITUDE = 109.9156
ZONA_WAKTU = "Asia/Jakarta"

URL_CUACA = "https://api.open-meteo.com/v1/forecast"


# =====================================================
# 2. FUNGSI ANALISIS RISIKO
# =====================================================

def analisis_risiko(suhu, kelembapan, titik_embun=None):
    """
    Klasifikasi indikatif untuk prototipe Si-Upas.
    Bukan prediksi pasti terjadinya embun upas.
    """

    if suhu <= 0 and kelembapan >= 80:
        return {
            "status": "RISIKO SANGAT TINGGI",
            "level": 3,
            "warna": "red",
            "rekomendasi": (
                "Periksa tanaman dan kondisi lahan segera. "
                "Siapkan langkah perlindungan tanaman sesuai "
                "panduan penyuluh pertanian setempat."
            ),
        }

    elif suhu <= 4 and kelembapan >= 80:
        return {
            "status": "SIAGA",
            "level": 2,
            "warna": "orange",
            "rekomendasi": (
                "Tingkatkan pemantauan suhu dan kondisi tanaman. "
                "Siapkan tindakan mitigasi jika kondisi memburuk."
            ),
        }

    elif suhu <= 6 and kelembapan >= 75:
        return {
            "status": "WASPADA",
            "level": 1,
            "warna": "orange",
            "rekomendasi": (
                "Pantau perubahan suhu dan kelembapan. "
                "Periksa informasi cuaca berikutnya."
            ),
        }

    else:
        return {
            "status": "AMAN MENURUT AMBANG PROTOTIPE",
            "level": 0,
            "warna": "green",
            "rekomendasi": (
                "Lakukan pemantauan rutin. Status ini bukan "
                "jaminan bahwa embun upas tidak akan terjadi."
            ),
        }


# =====================================================
# 3. MENGAMBIL DATA CUACA OTOMATIS
# =====================================================

@st.cache_data(ttl=900)
def ambil_cuaca():
    parameter = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "dew_point_2m"
        ),
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "dew_point_2m"
        ),
        "forecast_days": 2,
        "timezone": ZONA_WAKTU,
    }

    response = requests.get(
        URL_CUACA,
        params=parameter,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    if "current" not in data or "hourly" not in data:
        raise ValueError("Data cuaca tidak lengkap.")

    cuaca_sekarang = data["current"]
    prakiraan = data["hourly"]

    suhu = cuaca_sekarang.get("temperature_2m")
    kelembapan = cuaca_sekarang.get(
        "relative_humidity_2m"
    )
    titik_embun = cuaca_sekarang.get("dew_point_2m")

    if suhu is None or kelembapan is None:
        raise ValueError(
            "Suhu atau kelembapan tidak tersedia."
        )

    tabel = pd.DataFrame({
        "Waktu": pd.to_datetime(prakiraan["time"]),
        "Suhu (°C)": prakiraan["temperature_2m"],
        "Kelembapan (%)": prakiraan[
            "relative_humidity_2m"
        ],
        "Titik Embun (°C)": prakiraan["dew_point_2m"],
    })

    return (
        float(suhu),
        float(kelembapan),
        float(titik_embun)
        if titik_embun is not None else None,
        tabel,
    )


# =====================================================
# 4. FUNGSI TELEGRAM
# =====================================================

def kirim_telegram(pesan):
    if (
        not TELEGRAM_BOT_TOKEN
        or TELEGRAM_BOT_TOKEN == "MASUKKAN_TOKEN_BOT_BARU"
    ):
        return (
            False,
            "Masukkan token bot Telegram terlebih dahulu "
            "pada konfigurasi app.py."
        )

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    try:
        response = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": pesan,
            },
            timeout=15,
        )

        try:
            data = response.json()
        except ValueError:
            return False, "Respons Telegram tidak valid."

        if response.ok and data.get("ok"):
            return True, "Pesan berhasil dikirim ke Telegram."

        return False, data.get(
            "description",
            "Telegram gagal mengirim pesan.",
        )

    except requests.RequestException as error:
        return False, f"Koneksi gagal: {error}"


def buat_pesan(suhu, kelembapan, titik_embun, hasil, waktu):
    titik_embun_text = (
        f"{titik_embun:.1f} °C"
        if titik_embun is not None
        else "Tidak tersedia"
    )

    return (
        "🌱 SI-UPAS DIENG\n"
        "PERINGATAN PEMANTAUAN EMBUN UPAS\n\n"
        f"Waktu: {waktu}\n"
        f"Suhu udara: {suhu:.1f} °C\n"
        f"Kelembapan: {kelembapan:.1f}%\n"
        f"Titik embun: {titik_embun_text}\n"
        f"Status: {hasil['status']}\n\n"
        f"Rekomendasi:\n{hasil['rekomendasi']}\n\n"
        "Catatan: Ini merupakan hasil analisis indikatif "
        "berdasarkan data cuaca dan ambang prototipe, "
        "bukan konfirmasi terjadinya embun upas."
    )


# =====================================================
# 5. JUDUL DAN INFORMASI APLIKASI
# =====================================================

st.title("🌱 Si-Upas Dieng")
st.subheader(
    "Sistem Pemantauan dan Peringatan Dini Risiko Embun Upas"
)

st.markdown(
    """
    Dashboard prototipe untuk membantu pemantauan kondisi
    cuaca yang berpotensi meningkatkan risiko embun upas
    pada lahan pertanian dataran tinggi Dieng.
    """
)

st.info(
    "Data otomatis berasal dari prakiraan Open-Meteo untuk "
    "koordinat Dieng, bukan pengukuran langsung pada lahan."
)

st.divider()


# =====================================================
# 6. PILIH MODE
# =====================================================

mode = st.radio(
    "Pilih mode pemantauan:",
    [
        "🌦️ Otomatis - Data Cuaca",
        "🧪 Simulasi - Pengujian Juri",
    ],
    horizontal=True,
)

suhu = None
kelembapan = None
titik_embun = None
tabel_prakiraan = None


# =====================================================
# 7. MODE OTOMATIS
# =====================================================

if mode == "🌦️ Otomatis - Data Cuaca":

    st.header("🌦️ Pemantauan Cuaca Dieng")

    kolom_refresh, kolom_info = st.columns([1, 2])

    with kolom_refresh:
        if st.button(
            "🔄 Perbarui Data Cuaca",
            use_container_width=True,
        ):
            ambil_cuaca.clear()
            st.rerun()

    with kolom_info:
        st.caption(
            "Data di-cache selama 15 menit untuk mengurangi "
            "permintaan ke layanan cuaca."
        )

    try:
        with st.spinner("Mengambil data cuaca..."):
            (
                suhu,
                kelembapan,
                titik_embun,
                tabel_prakiraan,
            ) = ambil_cuaca()

        waktu = datetime.now(
            ZoneInfo(ZONA_WAKTU)
        ).strftime("%d-%m-%Y %H:%M:%S WIB")

        st.success("Data cuaca berhasil diperoleh.")

    except Exception as error:
        st.error(
            "Data cuaca gagal diperoleh. Periksa koneksi "
            "internet atau coba perbarui data."
        )
        st.caption(f"Detail teknis: {error}")
        st.stop()


# =====================================================
# 8. MODE SIMULASI
# =====================================================

else:

    st.header("🧪 Simulasi Kondisi Cuaca")

    st.write(
        "Atur parameter untuk mendemonstrasikan cara kerja "
        "sistem. Data ini bukan hasil pengukuran aktual."
    )

    kolom_suhu, kolom_hum = st.columns(2)

    with kolom_suhu:
        suhu = st.slider(
            "Suhu udara (°C)",
            min_value=-10.0,
            max_value=25.0,
            value=2.0,
            step=0.5,
        )

    with kolom_hum:
        kelembapan = st.slider(
            "Kelembapan udara (%)",
            min_value=0,
            max_value=100,
            value=85,
            step=1,
        )

    titik_embun = None
    tabel_prakiraan = None

    waktu = datetime.now(
        ZoneInfo(ZONA_WAKTU)
    ).strftime("%d-%m-%Y %H:%M:%S WIB")


# =====================================================
# 9. ANALISIS DAN STATUS RISIKO
# =====================================================

hasil = analisis_risiko(
    suhu,
    kelembapan,
    titik_embun,
)

st.divider()
st.header("📊 Hasil Analisis Risiko")

kolom1, kolom2, kolom3 = st.columns(3)

with kolom1:
    st.metric(
        "Suhu Udara",
        f"{suhu:.1f} °C",
    )

with kolom2:
    st.metric(
        "Kelembapan",
        f"{kelembapan:.1f}%",
    )

with kolom3:
    st.metric(
        "Titik Embun",
        (
            f"{titik_embun:.1f} °C"
            if titik_embun is not None
            else "Tidak tersedia"
        ),
    )

if hasil["level"] == 3:
    st.error(f"🚨 {hasil['status']}")
elif hasil["level"] == 2:
    st.warning(f"⚠️ {hasil['status']}")
elif hasil["level"] == 1:
    st.warning(f"🔎 {hasil['status']}")
else:
    st.success(f"✅ {hasil['status']}")

st.markdown("**Rekomendasi mitigasi:**")
st.write(hasil["rekomendasi"])

st.caption(
    "Ambang suhu dan kelembapan dalam prototipe ini "
    "masih perlu divalidasi menggunakan data kejadian "
    "embun upas dan pengukuran lapangan."
)


# =====================================================
# 10. GRAFIK PRAKIRAAN
# =====================================================

if tabel_prakiraan is not None:

    st.divider()
    st.header("📈 Prakiraan Suhu dan Kelembapan")

    st.line_chart(
        tabel_prakiraan.set_index("Waktu")[
            ["Suhu (°C)"]
        ]
    )

    st.line_chart(
        tabel_prakiraan.set_index("Waktu")[
            ["Kelembapan (%)"]
        ]
    )

    with st.expander("Lihat tabel prakiraan cuaca"):
        st.dataframe(
            tabel_prakiraan,
            use_container_width=True,
            hide_index=True,
        )


# =====================================================
# 11. NOTIFIKASI TELEGRAM
# =====================================================

st.divider()
st.header("📱 Notifikasi Telegram")

st.write(
    "Gunakan tombol berikut untuk mengirim status "
    "pemantauan Si-Upas ke chat Telegram."
)

if hasil["level"] >= 1:
    st.warning(
        "Kondisi berada pada tingkat kewaspadaan. "
        "Periksa hasil analisis sebelum mengirim peringatan."
    )
else:
    st.success(
        "Status AMAN menurut ambang prototipe. "
        "Kamu tetap dapat mengirim laporan status."
    )

if st.button(
    "📨 KIRIM NOTIFIKASI KE TELEGRAM",
    type="primary",
    use_container_width=True,
    key="kirim_telegram",
):
    pesan = buat_pesan(
        suhu,
        kelembapan,
        titik_embun,
        hasil,
        waktu,
    )

    with st.spinner("Mengirim pesan ke Telegram..."):
        berhasil, keterangan = kirim_telegram(pesan)

    if berhasil:
        st.success("✅ " + keterangan)
    else:
        st.error("❌ " + keterangan)


if st.button(
    "🔧 TEST KONEKSI TELEGRAM",
    use_container_width=True,
    key="test_telegram",
):
    pesan_test = (
        "🔔 TES NOTIFIKASI SI-UPAS\n\n"
        "Pesan ini merupakan pengujian koneksi bot.\n"
        f"Waktu tes: {waktu}"
    )

    with st.spinner("Menguji koneksi Telegram..."):
        berhasil, keterangan = kirim_telegram(pesan_test)

    if berhasil:
        st.success("✅ " + keterangan)
    else:
        st.error("❌ " + keterangan)


# =====================================================
# 12. FOOTER
# =====================================================

st.divider()

st.caption(
    "Si-Upas Dieng | Prototipe Krenova 2026"
)

st.caption(
    "Sistem pendukung pemantauan cuaca, bukan pengganti "
    "pengukuran lapangan atau arahan petugas pertanian."
)

