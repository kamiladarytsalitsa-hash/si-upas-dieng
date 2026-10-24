
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
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

WIB = ZoneInfo("Asia/Jakarta")
LATITUDE = -7.2048
LONGITUDE = 109.9156

# =====================================================
# 2. AMBIL DATA PRAKIRAAN CUACA
# =====================================================

@st.cache_data(ttl=900)
def ambil_cuaca():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m,relative_humidity_2m",
        "forecast_days": 2,
        "timezone": "Asia/Jakarta"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )
    response.raise_for_status()

    data = response.json()["hourly"]

    return pd.DataFrame({
        "Waktu": pd.to_datetime(data["time"]),
        "Suhu (°C)": data["temperature_2m"],
        "Kelembapan (%)": data["relative_humidity_2m"]
    })


# =====================================================
# 3. ANALISIS RISIKO
# =====================================================

def analisis_risiko(suhu, kelembapan):
    if suhu <= 0 and kelembapan >= 80:
        return {
            "status": "RISIKO SANGAT TINGGI",
            "level": 3,
            "pesan": (
                "Suhu berada pada atau di bawah titik beku "
                "dan kelembapan tinggi. Risiko frost perlu "
                "segera diperiksa."
            ),
            "tindakan": (
                "Periksa kondisi tanaman dan suhu permukaan "
                "lahan. Siapkan mitigasi yang sesuai."
            )
        }

    elif suhu <= 4 and kelembapan >= 80:
        return {
            "status": "SIAGA",
            "level": 2,
            "pesan": (
                "Suhu rendah dan kelembapan tinggi. "
                "Tingkatkan kewaspadaan terhadap embun upas."
            ),
            "tindakan": (
                "Pantau kondisi lahan dan siapkan "
                "langkah perlindungan tanaman."
            )
        }

    elif suhu <= 6 and kelembapan >= 75:
        return {
            "status": "WASPADA",
            "level": 1,
            "pesan": (
                "Suhu relatif rendah dan kelembapan cukup "
                "tinggi. Kondisi perlu dipantau."
            ),
            "tindakan": (
                "Pantau perubahan cuaca terutama malam "
                "hingga dini hari."
            )
        }

    return {
        "status": "AMAN",
        "level": 0,
        "pesan": (
            "Parameter belum memenuhi ambang peringatan "
            "dalam prototype ini."
        ),
        "tindakan": "Lanjutkan pemantauan secara berkala."
    }


# =====================================================
# 4. KIRIM NOTIFIKASI TELEGRAM
# =====================================================

def kirim_telegram(pesan):
    try:
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        response = requests.post(
            url,
            data={
                "chat_id": str(chat_id),
                "text": pesan
            },
            timeout=15
        )

        hasil = response.json()

        if response.ok and hasil.get("ok"):
            return True, "Notifikasi berhasil dikirim ke Telegram."

        return False, hasil.get(
            "description",
            "Telegram gagal mengirim pesan."
        )

    except KeyError:
        return False, (
            "Token atau Chat ID belum diatur di secrets.toml."
        )

    except requests.RequestException:
        return False, (
            "Koneksi Telegram gagal. Periksa internet."
        )

    except Exception:
        return False, (
            "Terjadi kesalahan saat mengirim notifikasi."
        )


def buat_pesan(suhu, kelembapan, hasil, waktu):
    return (
        "❄️ SI-UPAS DIENG\n"
        "PERINGATAN DINI EMBUN UPAS\n\n"
        f"Status: {hasil['status']}\n"
        f"Suhu: {suhu:.1f} °C\n"
        f"Kelembapan: {kelembapan:.0f}%\n"
        f"Waktu: {waktu}\n\n"
        f"Analisis: {hasil['pesan']}\n\n"
        f"Rekomendasi: {hasil['tindakan']}\n\n"
        "Catatan: Status merupakan hasil analisis "
        "prototype, bukan konfirmasi embun upas."
    )


# =====================================================
# 5. HEADER DAN SIDEBAR
# =====================================================

st.title("❄️ Si-Upas Dieng")
st.subheader(
    "Sistem Informasi Peringatan Dini Risiko Embun Upas "
    "untuk Pertanian Kentang"
)
st.caption(
    "Pemantauan cuaca • Analisis risiko • Notifikasi Telegram"
)
st.divider()

st.sidebar.title("🎛️ Panel Si-Upas")

mode = st.sidebar.radio(
    "Pilih mode aplikasi:",
    [
        "Otomatis - Prakiraan Cuaca",
        "Manual - Simulasi Juri"
    ]
)

st.sidebar.info(
    "Mode otomatis menggunakan prakiraan Open-Meteo. "
    "Mode manual digunakan untuk menguji logika sistem."
)

# =====================================================
# 6. DATA OTOMATIS ATAU SIMULASI
# =====================================================

df = None

if mode == "Otomatis - Prakiraan Cuaca":
    st.header("📡 Pemantauan Prakiraan Cuaca Dieng")

    try:
        df = ambil_cuaca()

        sekarang = pd.Timestamp(
            datetime.now(WIB).replace(tzinfo=None)
        )

        mendatang = df[df["Waktu"] >= sekarang]

        if mendatang.empty:
            st.error("Data prakiraan untuk waktu mendatang tidak tersedia.")
            st.stop()

        baris = mendatang.iloc[0]

        suhu = float(baris["Suhu (°C)"])
        kelembapan = float(baris["Kelembapan (%)"])
        waktu = baris["Waktu"].strftime("%d-%m-%Y %H:%M WIB")

    except Exception:
        st.error(
            "Data cuaca gagal diambil. Periksa koneksi internet "
            "atau coba muat ulang aplikasi."
        )
        st.stop()

    st.caption("Sumber: Open-Meteo — data prakiraan, bukan sensor langsung.")

else:
    st.header("🧪 Simulasi Pengujian Juri")

    suhu = st.sidebar.slider(
        "Suhu udara (°C)",
        min_value=-10.0,
        max_value=25.0,
        value=2.0,
        step=0.5
    )

    kelembapan = st.sidebar.slider(
        "Kelembapan udara (%)",
        min_value=0,
        max_value=100,
        value=90,
        step=1
    )

    waktu = datetime.now(WIB).strftime("%d-%m-%Y %H:%M WIB")

    st.caption("Sumber: parameter simulasi yang dimasukkan pengguna.")

# =====================================================
# 7. METRIK UTAMA
# =====================================================

hasil = analisis_risiko(suhu, kelembapan)

col1, col2, col3 = st.columns(3)

col1.metric("🌡️ Suhu", f"{suhu:.1f} °C")
col2.metric("💧 Kelembapan", f"{kelembapan:.0f}%")
col3.metric("📍 Lokasi", "Dieng")

st.caption(f"Waktu pemeriksaan: {waktu}")
st.divider()

# =====================================================
# 8. STATUS DAN REKOMENDASI
# =====================================================

st.subheader("📢 Hasil Analisis Sistem")

if hasil["level"] == 3:
    st.error(f"🚨 **{hasil['status']}**\n\n{hasil['pesan']}")

elif hasil["level"] in (1, 2):
    st.warning(f"⚠️ **{hasil['status']}**\n\n{hasil['pesan']}")

else:
    st.success(f"✅ **{hasil['status']}**\n\n{hasil['pesan']}")

st.info(f"💡 **Rekomendasi:** {hasil['tindakan']}")

# =====================================================
# 9. NOTIFIKASI TELEGRAM
# =====================================================

st.divider()
st.subheader("📱 Notifikasi ke HP Petani")

if hasil["level"] >= 1:
    st.write(
        "Sistem mendeteksi kondisi yang perlu diwaspadai. "
        "Kirimkan informasi ini ke Telegram petani."
    )

    if st.button(
        "📨 Kirim Peringatan Telegram",
        type="primary",
        use_container_width=True
    ):
        pesan = buat_pesan(
            suhu,
            kelembapan,
            hasil,
            waktu
        )

        with st.spinner("Mengirim notifikasi..."):
            berhasil, keterangan = kirim_telegram(pesan)

        if berhasil:
            st.success(keterangan)
        else:
            st.error(keterangan)

else:
    st.success(
        "Status AMAN menurut ambang prototype. "
        "Notifikasi peringatan tidak diperlukan."
    )

# =====================================================
# 10. GRAFIK DAN TABEL PRAKIRAAN
# =====================================================

if df is not None:
    st.divider()
    st.subheader("📈 Prakiraan Cuaca 24 Jam")

    grafik = df.head(24).set_index("Waktu")

    st.write("Perubahan suhu")
    st.line_chart(grafik[["Suhu (°C)"]])

    st.write("Perubahan kelembapan")
    st.line_chart(grafik[["Kelembapan (%)"]])

    with st.expander("Lihat tabel prakiraan cuaca"):
        st.dataframe(
            df.head(24),
            use_container_width=True,
            hide_index=True
        )

# =====================================================
# 11. FOOTER
# =====================================================

st.divider()

st.caption(
    "© 2026 Tim Krenova — Si-Upas Dieng"
)
st.caption(
    "Ambang risiko merupakan parameter awal yang perlu "
    "divalidasi dengan data historis dan pengukuran lapangan. "
    "Suhu serta kelembapan udara saja tidak memastikan "
    "terjadinya embun upas."
)
