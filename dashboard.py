import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import base64

# =====================================================
# 1️⃣ KONFIGURASI DASAR
# =====================================================
st.set_page_config(page_title="PPNS IoT Dashboard", layout="wide", page_icon="🌊")

load_dotenv()

# --- Fungsi Konversi Gambar ke Base64 ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"File logo '{image_path}' tidak ditemukan. Pastikan file ada di folder yang sama.")
        return None

img_base64 = get_base64_image("ppns_logo.png")

# --- Koneksi Database ---
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASS")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT")      # <-- [1] TAMBAHKAN BARIS INI
db_name = os.getenv("MYSQL_DB")

# --- [2] UBAH BARIS db_uri MENJADI SEPERTI INI ---
db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"

engine = create_engine(db_uri)
# --- Session State ---
if "paused" not in st.session_state:
    st.session_state.paused = False

# =====================================================
# 2️⃣ CSS DENGAN EFEK MENGKILAT (GLOSSY) DAN ANIMASI GEOMETRI BARU
# =====================================================
st.markdown("""
<style>
/* === DIUBAH: Keyframes untuk animasi geometri === */
@keyframes geo-flow-1 {
    0% { background-position: 0% 0%; }
    100% { background-position: 100% 100%; } /* Bergerak diagonal 1 */
}
@keyframes geo-flow-2 {
    0% { background-position: 0% 0%; }
    100% { background-position: -100% 100%; } /* Bergerak diagonal 2 (berlawanan) */
}


/* === DIUBAH: Latar Belakang Geometri Elegan Seluruh Halaman === */
[data-testid="stAppViewContainer"] {
    background-color: #004080; /* Warna dasar (biru paling gelap) */
    
    /*
    Kita tumpuk 3 lapisan:
    1. Garis-garis diagonal tipis (opacity rendah)
    2. Garis-garis diagonal berlawanan (opacity rendah)
    3. Gradien radial biru sebagai dasar
    */
    background-image: 
        /* Lapisan 1: Garis-garis (angle 45deg) */
        repeating-linear-gradient(
            45deg, 
            rgba(77, 184, 255, 0.12), /* #4db8ff dengan opacity 12% */
            rgba(77, 184, 255, 0.12) 1px, 
            transparent 1px, 
            transparent 50px /* Jarak antar garis 50px */
        ),
        /* Lapisan 2: Garis-garis (angle -45deg) */
        repeating-linear-gradient(
            -45deg, 
            rgba(77, 184, 255, 0.08), /* Opacity lebih rendah */
            rgba(77, 184, 255, 0.08) 1px, 
            transparent 1px, 
            transparent 50px /* Jarak antar garis sama, buat grid */
        ),
        /* Lapisan 3: Dasar Gradien Radial */
        radial-gradient(
            ellipse at center, 
            #1a75ff, /* Biru tengah */
            #004080 /* Biru gelap di pinggir */
        );

    background-repeat: repeat, repeat, no-repeat;
    
    /* Ukuran background:
       - Lapisan 1 & 2: Dibuat besar (200%) agar bisa bergerak
       - Lapisan 3: 100% statis
    */
    background-size: 
        200% 200%, 
        200% 200%, 
        100% 100%;
    
    /* Terapkan animasi ke lapisan garis
       - Beda durasi dan arah untuk efek elegan
    */
    animation: 
        geo-flow-1 30s linear infinite, /* Lambat */
        geo-flow-2 40s linear infinite reverse; /* Sangat lambat, arah terbalik */
        
    background-attachment: fixed; /* Latar belakang tetap saat scroll */
}


[data-testid="stToolbar"] {
    background: transparent;
}

[data-testid="stHeader"], [data-testid="stSidebar"] {
    background: transparent;
}

/* === HEADER (Tetap sama) === */
.header-box {
    display: flex; align-items: center; gap: 20px; text-align: left;
    background: linear-gradient(90deg, #0099ff, #4db8ff);
    color: white; padding: 20px 30px; border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    margin-bottom: 25px;
    animation: fadeIn 1s ease-in-out;
    position: relative; 
    overflow: hidden; 
}

/* === Efek kilat untuk Header (Tetap sama) === */
.header-box::before {
    content: "";
    position: absolute;
    top: 0;
    left: -25%;
    width: 150%;
    height: 60%;
    background: linear-gradient(
        to bottom, 
        rgba(255, 255, 255, 0.35) 0%, 
        rgba(255, 255, 255, 0) 80%
    );
    transform: rotate(-10deg) translateY(-20px);
    z-index: 1; 
    opacity: 0.9;
}

.header-logo img {
    width: 90px; height: 90px; border-radius: 12px;
    background: white; padding: 5px;
    transition: transform 0.4s ease;
    position: relative; 
    z-index: 2; 
}
.header-logo img:hover {
    transform: scale(1.08) rotate(3deg);
}
.header-text {
    position: relative; 
    z-index: 2; 
}
.header-text h1 {
    font-size: 28px; font-weight: bold; margin-bottom: 6px;
}
.header-text p {
    font-size: 14px; opacity: 0.95; margin: 0;
}
.header-names {
    margin-top: 10px; font-size: 14px;
    line-height: 1.5; color: #e8f6ff;
}

/* === KARTU METRIK (Tetap sama) === */
.metric-card {
    padding:20px; border-radius:20px; text-align:center;
    color:white; font-weight:bold;
    transition: transform 0.3s ease, box-shadow 0.3s ease, opacity 0.8s;
    animation: fadeIn 1.2s ease-in-out;
    opacity: 0.95;
    position: relative; 
    overflow: hidden; 
}
.metric-card:hover {
    transform: scale(1.03);
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    opacity: 1;
}

/* === Efek kilat untuk Kartu Metrik (Tetap sama) === */
.metric-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 50%; 
    background: linear-gradient(
        to bottom, 
        rgba(255, 255, 255, 0.4) 0%, 
        rgba(255, 255, 255, 0) 100%
    );
    z-index: 1; 
    border-radius: 20px 20px 0 0; 
}

/* === Teks di atas efek kilat (Tetap sama) === */
.metric-card h4, .metric-card h2 {
    position: relative;
    z-index: 2; 
}


/* === ANIMASI FADE-IN (Tetap sama) === */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* === FOOTER (Tetap sama) === */
.footer {
    text-align:center; font-size:14px;
    color:#fff; margin-top:40px;
    opacity: 0.8; transition: opacity 0.3s ease;
}
.footer:hover {
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3️⃣ HEADER DASHBOARD
# =====================================================
# (Pastikan img_base64 tidak None sebelum digunakan)
if img_base64:
    st.markdown(f"""
    <div class="header-box">
        <div class="header-logo">
            <img src="data:image/png;base64,{img_base64}">
        </div>
        <div class="header-text">
            <h1>🌊 PPNS IoT Monitoring Dashboard</h1>
            <p>Politeknik Perkapalan Negeri Surabaya • Data Sensor Real-time</p>
            <div class="header-names">
                👨‍💻 <b>Rogeryo Christanto (0424030053)</b><br>
                👨‍💻 <b>Surya Abi Dwi Pradana (0424030054)</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 4️⃣ TOMBOL JEDA DATA
# =====================================================
col1, col2 = st.columns([1, 2])
with col1:
    if st.session_state.paused:
        if st.button("▶️ Lanjutkan Live Data"):
            st.session_state.paused = False
            st.rerun() 
    else:
        if st.button("⏸️ Jeda Live Data"):
            st.session_state.paused = True
            st.rerun() 
with col2:
    st.markdown(f"**Status:** {'<span style="color:#27ae60;">🟢</span> **Aktif**' if not st.session_state.paused else '<span style="color:#e74c3c;">🔴</span> **Dijeda**'}", unsafe_allow_html=True)

st.divider()

# =====================================================
# 5️⃣ AUTO REFRESH
# =====================================================
if not st.session_state.paused:
    st_autorefresh(interval=5000, key="data_refresh")

# =====================================================
# 6️⃣ DATA SENSOR
# =====================================================
try:
    # Menggunakan koneksi engine secara langsung lebih disarankan untuk read_sql
    with engine.connect() as connection:
        df = pd.read_sql("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 30", connection)

    if not df.empty:
        df['waktu'] = pd.to_datetime(df['waktu'])
        latest = df.iloc[0]

        # --- Warna Berdasarkan Kondisi ---
        def get_color_suhu(val):
            if val > 35: return "background:linear-gradient(145deg,#e74c3c,#c0392b)"
            elif val < 25: return "background:linear-gradient(145deg,#3498db,#2980b9)"
            else: return "background:linear-gradient(145deg,#27ae60,#1e8449)"
        def get_color_tekanan(val):
            if val > 1010: return "background:linear-gradient(145deg,#f39c12,#e67e22)"
            elif val < 990: return "background:linear-gradient(145deg,#8e44ad,#6c3483)"
            else: return "background:linear-gradient(145deg,#27ae60,#1e8449)"
        def get_color_kelembaban(val):
            if val > 80: return "background:linear-gradient(145deg,#3498db,#1f618d)"
            elif val < 40: return "background:linear-gradient(145deg,#f39c12,#d35400)"
            else: return "background:linear-gradient(145deg,#27ae60,#1e8449)"

        # --- Tampilkan Metrik ---
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-card' style='{get_color_suhu(latest['suhu'])}'><h4>🌤️ Suhu (°C)</h4><h2>{latest['suhu']:.2f}</h2></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-card' style='{get_color_tekanan(latest['tekanan'])}'><h4>🌫️ Tekanan (hPa)</h4><h2>{latest['tekanan']:.2f}</h2></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-card' style='{get_color_kelembaban(latest['kelembaban'])}'><h4>💧 Kelembaban (%)</h4><h2>{latest['kelembaban']:.2f}</h2></div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("📈 Grafik Sensor (30 Data Terakhir)")
        
        # Membuat chart lebih rapi dengan memilih kolom
        chart_data = df.set_index("waktu")[["suhu", "tekanan", "kelembaban"]]
        st.line_chart(chart_data)

        st.divider()
        st.subheader("📋 Data Sensor (Terbaru)")
        # Menampilkan dataframe dengan format waktu yang lebih baik
        df_display = df.copy()
        df_display['waktu'] = df_display['waktu'].dt.strftime('%d %B %Y, %H:%M:%S')
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("⚠️ Tidak ada data di database. Jalankan publisher.py untuk mulai mengirim data sensor.")
except Exception as e:
    st.error(f"❌ Gagal memuat data: {e}")

# =====================================================
# 7️⃣ FOOTER
# =====================================================
st.markdown(
    f"<p class='footer'>📅 Terakhir diperbarui: {datetime.now().strftime('%d %B %Y, %H:%M:%S')} | © PPNS 2025</p>",
    unsafe_allow_html=True
)
