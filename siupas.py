import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ============================================================
# 1. PENGATURAN HALAMAN
# ============================================================

st.set_page_config(
    page_title="Si-Upas Dieng",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. KONFIGURASI LOKASI DIENG
# ============================================================

DIENG_LAT = -7.2048
DIENG_LON = 109.9156

# ============================================================
# 3. FUNGSI MENGAMBIL DATA CUACA
# ============================================================

@st.cache_data(ttl=3600)
def get_weather_data():
    """
    Mengambil data prakiraan cuaca dari Open-Meteo.
    Data diperbarui secara berkala oleh API.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": DIENG_LAT,
        "longitude": DIENG_LON,
        "hourly": "temperature_2m,relative_humidity_2m",
        "forecast_days": 2,
        "timezone": "Asia/Jakarta"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        df = pd.DataFrame({
            "Waktu": pd.to_datetime(data["hourly"]["time"]),
            "Suhu": data["hourly"]["temperature_2m"],
            "Kelembapan": data["hourly"]["relative_humidity_2m"]
        })

        return df

    except Exception as e:
        return None


# ============================================================
# 4. FUNGSI ANALISIS RISIKO
# ============================================================

def analisis_risiko(suhu, kelembapan):

    # Risiko sangat tinggi
    if suhu <= 0 and kelembapan >= 80:
        return {
            "status": "RISIKO SANGAT TINGGI",
            "warna": "error",
            "emoji": "🚨",
            "pesan": (
                "Suhu berada pada atau di bawah titik beku "
                "disertai kelembapan tinggi. Risiko pembentukan "
                "frost/embun upas sangat tinggi."
            ),
            "tindakan": (
                "Segera lakukan tindakan perlindungan tanaman "
                "sesuai metode mitigasi yang tersedia."
            )
        }

    # Risiko tinggi
    elif suhu <= 4 and kelembapan >= 80:
        return {
            "status": "SIAGA",
            "warna": "warning",
            "emoji": "⚠️",
            "pesan": (
                "Suhu rendah dan kelembapan tinggi. "
                "Kondisi mendukung peningkatan risiko embun upas."
            ),
            "tindakan": (
                "Petani disarankan meningkatkan pemantauan "
                "dan menyiapkan sistem mitigasi."
            )
        }

    # Risiko sedang
    elif suhu <= 6 and kelembapan >= 75:
        return {
            "status": "WASPADA",
            "warna": "warning",
            "emoji": "🟡",
            "pesan": (
                "Suhu mulai rendah dengan kelembapan cukup tinggi. "
                "Potensi risiko perlu dipantau."
            ),
            "tindakan": (
                "Pantau perubahan suhu dan kelembapan terutama "
                "pada malam hingga dini hari."
            )
        }

    # Aman
    else:
        return {
            "status": "AMAN",
            "warna": "success",
            "emoji": "✅",
            "pesan": (
                "Parameter cuaca saat ini belum menunjukkan "
                "indikasi risiko tinggi embun upas."
            ),
            "tindakan": (
                "Tetap lakukan pemantauan berkala terhadap "
                "perubahan kondisi cuaca."
            )
        }


# ============================================================
# 5. HEADER
# ============================================================

st.title("❄️ Si-Upas Dieng")

st.subheader(
    "Sistem Informasi Peringatan Dini Risiko Embun Upas "
    "untuk Komoditas Kentang"
)

st.markdown("---")


# ============================================================
# 6. SIDEBAR
# ============================================================

st.sidebar.title("🎛️ Panel Sistem")

mode = st.sidebar.radio(
    "Mode Tampilan",
    [
        "Otomatis",
        "Simulasi Juri"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Si-Upas merupakan prototype sistem peringatan dini "
    "yang menganalisis suhu dan kelembapan untuk membantu "
    "petani meningkatkan kesiapsiagaan terhadap risiko embun upas."
)


# ============================================================
# 7. MODE OTOMATIS
# ============================================================

if mode == "Otomatis":

    st.header("📡 Pemantauan Cuaca Dieng")

    data = get_weather_data()

    if data is None:

        st.error(
            "❌ Data cuaca tidak dapat diambil. "
            "Periksa koneksi internet kemudian coba lagi."
        )

    else:

        # Ambil data saat ini
        sekarang = datetime.now()

        data["selisih"] = abs(
            data["Waktu"] - pd.Timestamp(sekarang)
        )

        data_sekarang = data.loc[
            data["selisih"].idxmin()
        ]

        suhu = float(data_sekarang["Suhu"])
        kelembapan = float(data_sekarang["Kelembapan"])

        hasil = analisis_risiko(
            suhu,
            kelembapan
        )

        # ====================================================
        # METRIC
        # ====================================================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🌡️ Suhu",
                f"{suhu:.1f} °C"
            )

        with col2:
            st.metric(
                "💧 Kelembapan",
                f"{kelembapan:.0f} %"
            )

        with col3:
            st.metric(
                "📍 Lokasi",
                "Dieng"
            )

        st.markdown("---")

        # ====================================================
        # STATUS
        # ====================================================

        st.subheader("📢 Status Sistem")

        if hasil["warna"] == "error":

            st.error(
                f"{hasil['emoji']} **{hasil['status']}**\n\n"
                f"{hasil['pesan']}"
            )

        elif hasil["warna"] == "warning":

            st.warning(
                f"{hasil['emoji']} **{hasil['status']}**\n\n"
                f"{hasil['pesan']}"
            )

        else:

            st.success(
                f"{hasil['emoji']} **{hasil['status']}**\n\n"
                f"{hasil['pesan']}"
            )

        st.info(
            f"💡 **Rekomendasi:** {hasil['tindakan']}"
        )

        # ====================================================
        # GRAFIK
        # ====================================================

        st.markdown("---")

        st.subheader("📈 Prakiraan Suhu 24 Jam")

        grafik = data.head(24).copy()

        grafik = grafik.set_index("Waktu")

        st.line_chart(
            grafik["Suhu"]
        )

        st.subheader("💧 Prakiraan Kelembapan 24 Jam")

        st.line_chart(
            grafik["Kelembapan"]
        )

        # ====================================================
        # TABEL DATA
        # ====================================================

        with st.expander("🔎 Lihat Data Prakiraan"):

            tampil = data.head(24)[
                ["Waktu", "Suhu", "Kelembapan"]
            ].copy()

            tampil["Suhu"] = tampil["Suhu"].round(1)

            tampil["Kelembapan"] = (
                tampil["Kelembapan"].round(0)
            )

            st.dataframe(
                tampil,
                use_container_width=True
            )

        st.caption(
            "Sumber data prakiraan: Open-Meteo. "
            "Data digunakan sebagai bagian dari prototype sistem."
        )


# ============================================================
# 8. MODE SIMULASI JURI
# ============================================================

else:

    st.header("🧪 Mode Simulasi Pengujian")

    st.write(
        "Mode ini digunakan untuk menunjukkan bagaimana "
        "sistem Si-Upas mengambil keputusan berdasarkan "
        "suhu dan kelembapan yang dimasukkan oleh pengguna."
    )

    st.sidebar.subheader("⚙️ Parameter Simulasi")

    input_suhu = st.sidebar.slider(
        "🌡️ Suhu Udara (°C)",
        min_value=-10.0,
        max_value=25.0,
        value=2.0,
        step=0.5
    )

    input_kelembapan = st.sidebar.slider(
        "💧 Kelembapan (%)",
        min_value=0,
        max_value=100,
        value=90,
        step=1
    )

    # ========================================================
    # HASIL ANALISIS
    # ========================================================

    hasil = analisis_risiko(
        input_suhu,
        input_kelembapan
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "🌡️ Suhu Pengujian",
            f"{input_suhu:.1f} °C"
        )

    with col2:

        st.metric(
            "💧 Kelembapan Pengujian",
            f"{input_kelembapan}%"
        )

    st.markdown("---")

    st.subheader("📢 Hasil Analisis Sistem")

    if hasil["warna"] == "error":

        st.error(
            f"{hasil['emoji']} **{hasil['status']}**\n\n"
            f"{hasil['pesan']}"
        )

    elif hasil["warna"] == "warning":

        st.warning(
            f"{hasil['emoji']} **{hasil['status']}**\n\n"
            f"{hasil['pesan']}"
        )

    else:

        st.success(
            f"{hasil['emoji']} **{hasil['status']}**\n\n"
            f"{hasil['pesan']}"
        )

    st.info(
        f"💡 **Rekomendasi Sistem:** {hasil['tindakan']}"
    )

    # ========================================================
    # TABEL KLASIFIKASI
    # ========================================================

    st.markdown("---")

    st.subheader("📋 Matriks Klasifikasi Risiko")

    tabel_risiko = pd.DataFrame({
        "Kondisi": [
            "Suhu > 6°C",
            "Suhu 4–6°C + kelembapan ≥75%",
            "Suhu 0–4°C + kelembapan ≥80%",
            "Suhu ≤0°C + kelembapan ≥80%"
        ],

        "Status": [
            "AMAN",
            "WASPADA",
            "SIAGA",
            "RISIKO SANGAT TINGGI"
        ],

        "Tindakan": [
            "Pemantauan rutin",
            "Tingkatkan pemantauan",
            "Siapkan mitigasi",
            "Segera lakukan mitigasi"
        ]
    })

    st.dataframe(
        tabel_risiko,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 9. FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "© 2026 Tim Krenova — Si-Upas "
    "(Sistem Informasi Mitigasi Dampak Embun Es Dieng)"
)
