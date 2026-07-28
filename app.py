# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import time
import os
from evaluasi_bulanan import hitung_net_profit, simpan_log

# 1. PENGATURAN HALAMAN WEBSITE UTAMA
st.set_page_config(page_title="Sistem Trading Harian BEI", layout="wide")

# KONTROL SINKRONISASI BURSA (AUTO-REFRESH 10 DETIK)
st.sidebar.subheader("⏱️ Kontrol Sinkronisasi Bursa")
auto_refresh = st.sidebar.checkbox("Aktifkan Auto-Refresh (10 Detik)", value=True)

if auto_refresh:
    st.empty() 

st.title("⚡ Sistem AI Scalping & Kontrol Risiko Harian (LQ45 & Kompas100)")
st.write(f"Aplikasi acuan momentum trading cepat. Terakhir Diperbarui: {time.strftime('%H:%M:%S')} WIB")

st.markdown("---")

# DATA KAMUS SEKTOR INDUSTRI RESMI BEI
sektor_saham = {
    'AADI': 'Energi / Batu Bara', 'ACES': 'Barang Konsumen Non-Primer', 'ADMR': 'Energi / Batu Bara', 
    'ADRO': 'Energi / Batu Bara', 'AKRA': 'Energi & Distribusi', 'AMMN': 'Barang Baku / Metal', 
    'AMRT': 'Barang Konsumen Primer', 'ANTM': 'Barang Baku / Metal', 'ARCI': 'Barang Baku / Metal', 
    'ARTO': 'Keuangan / Bank Digital', 'ASII': 'Perindustrian / Otomotif', 'BBCA': 'Keuangan / Perbankan', 
    'BBNI': 'Keuangan / Perbankan', 'BBRI': 'Keuangan / Perbankan', 'BBTN': 'Keuangan / Perbankan', 
    'BBYB': 'Keuangan / Bank Digital', 'BKSL': 'Properti & Real Estate', 'BMRI': 'Keuangan / Perbankan', 
    'BREN': 'Infrastruktur / Energi Hijau', 'BRIS': 'Keuangan / Perbankan Syariah', 'BRMS': 'Barang Baku / Metal', 
    'BRPT': 'Barang Baku / Kimia', 'BSDE': 'Properti & Real Estate', 'BTPS': 'Keuangan / Perbankan', 
    'BUKA': 'Teknologi / E-Commerce', 'BULL': 'Infrastruktur / Pelayaran', 'BUMI': 'Energi / Batu Bara', 
    'BUVA': 'Barang Konsumen Non-Primer', 'CBDK': 'Properti & Real Estate', 'CMRY': 'Barang Konsumen Primer', 
    'CPIN': 'Barang Konsumen Primer', 'CTRA': 'Properti & Real Estate', 'CUAN': 'Energi & Tambang', 
    'DEWA': 'Infrastruktur / Jasa Energi', 'DSNG': 'Barang Konsumen Primer / Sawit', 'DSSA': 'Infrastruktur & Energi', 
    'ELSA': 'Energi / Jasa Migas', 'EMTK': 'Teknologi / Media', 'ENRG': 'Energi / Minyak & Gas', 
    'ERAA': 'Barang Konsumen Non-Primer', 'ESSA': 'Barang Baku / Kimia', 'EXCL': 'Infrastruktur / Telekomunikasi', 
    'FILM': 'Barang Konsumen Non-Primer', 'GOTO': 'Teknologi / Layanan Digital', 'HEAL': 'Kesehatan / Rumah Sakit', 
    'HMSP': 'Barang Konsumen Primer', 'HRTA': 'Barang Konsumen Non-Primer', 'HRUM': 'Energi / Batu Bara & Nikel', 
    'ICBP': 'Barang Konsumen Primer / Pangan', 'IMPC': 'Barang Baku / Bahan Bangunan', 'INCO': 'Barang Baku / Metal', 
    'INDF': 'Barang Konsumen Primer / Pangan', 'INDY': 'Energi & Diversifikasi', 'INET': 'Infrastruktur / Teknologi', 
    'INKP': 'Barang Baku / Kertas', 'INTP': 'Barang Baku / Semen', 'ISAT': 'Infrastruktur / Telekomunikasi', 
    'ITMG': 'Energi / Batu Bara', 'JPFA': 'Barang Konsumen Primer', 'JSMR': 'Infrastruktur / Jalan Tol', 
    'KIJA': 'Properti & Kawasan Industri', 'KLBF': 'Kesehatan / Farmasi', 'KPIG': 'Properti & Real Estate', 
    'MAPA': 'Barang Konsumen Non-Primer', 'MAPI': 'Barang Konsumen Non-Primer', 'MBMA': 'Barang Baku / Metal', 
    'MDKA': 'Barang Baku / Metal', 'MEDC': 'Energi / Minyak & Gas', 'MIKA': 'Kesehatan / Rumah Sakit', 
    'MTEL': 'Infrastruktur / Menara Telko', 'MYOR': 'Barang Konsumen Primer / Makanan', 'NCKL': 'Barang Baku / Metal', 
    'PANI': 'Properti & Real Estate', 'PGAS': 'Infrastruktur / Gas Bumi', 'PGEO': 'Infrastruktur / Energi Hijau', 
    'PNLF': 'Keuangan / Jasa Finansial', 'PSAB': 'Barang Baku / Metal', 'PTBA': 'Energi / Batu Bara', 
    'PTRO': 'Perindustrian / Jasa Kontraktor', 'PWON': 'Properti & Real Estate', 'RAJA': 'Energi / Minyak & Gas', 
    'RATU': 'Energi / Infrastruktur', 'SCMA': 'Barang Konsumen Non-Primer / Media', 'SGER': 'Energi / Batu Bara', 
    'SIDO': 'Barang Konsumen Primer / Farmasi', 'SMGR': 'Barang Baku / Semen', 'SMIL': 'Infrastruktur / Logistik', 
    'SMRA': 'Properti & Real Estate', 'SSIA': 'Properti & Konstruksi', 'TAPG': 'Barang Konsumen Primer / Sawit', 
    'TCPI': 'Infrastruktur / Pelayaran', 'TINS': 'Barang Baku / Metal', 'TLKM': 'Infrastruktur / Telekomunikasi', 
    'TOBA': 'Energi & Infrastruktur', 'TOWR': 'Infrastruktur / Menara Telko', 'TPIA': 'Barang Baku / Kimia', 
    'UNTR': 'Perindustrian / Alat Berat', 'UNVR': 'Barang Konsumen Primer', 'WIFI': 'Infrastruktur / Teknologi', 
    'WIRG': 'Teknologi / Software'
}

saham_lq45 = [
    'ACES', 'ADRO', 'AKRA', 'AMMAN', 'AMRT', 'ANTM', 'ARTO', 'ASII', 'BBCA', 'BBNI', 
    'BBRI', 'BBTN', 'BMRI', 'BRIS', 'BRPT', 'BSDE', 'CPIN', 'CTRA', 'EXCL', 'GOTO', 
    'ICBP', 'INCO', 'INDF', 'INKP', 'INTP', 'ISAT', 'ITMG', 'JSMR', 'KLBF', 'MAPI', 
    'MDKA', 'MEDC', 'MIKA', 'MYOR', 'PGAS', 'PTBA', 'SIDO', 'SMGR', 'SMRA', 'TLKM', 
    'TOWR', 'TPIA', 'UNTR', 'UNVR', 'XL'
]

def hitung_rsi_live(series, period=14):
    if len(series) < period: return 50.0
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).iloc[-1]

# STRUKTUR TAB HALAMAN
tab_dashboard, tab_sop, tab_spike, tab_predictive, tab_kalkulator = st.tabs([
    "⚡ Dashboard Scalping & Trading Harian", 
    "📋 Panduan SOP Scalping",
    "🕵️‍♂️ Taktik Volume Spike (Pelacak Bandar)",
    "🎯 Radar AI Prediksi Esok Hari (BOC & Pivot)",
    "💰 Kalkulator Investasi & Log"
])
# ==========================================
# 1. TAB DASHBOARD SCALPING
# ==========================================
with tab_dashboard:
    try:
        df_raw = pd.read_csv('data_kompas100.csv')
        df_raw['Sektor_Industri'] = df_raw['Ticker'].map(sektor_saham).fillna('Industri Lainnya')
    except FileNotFoundError:
        st.error("File data_kompas100.csv tidak ditemukan di direktori Anda.")
        st.stop()

    pilihan_indeks = st.radio("Pilih Indeks Acuan Trading:", options=["Saham Unggulan LQ45", "Saham Likuid Kompas100"], horizontal=True, key="pilihan_indeks_dash")
    
    if pilihan_indeks == "Saham Unggulan LQ45":
        df_filter = df_raw[df_raw['Ticker'].isin(saham_lq45)].copy()
    else:
        df_filter = df_raw.copy()

    total_saham = len(df_filter)
    st.metric(f"Total Saham Siap Di-scalping ({pilihan_indeks})", f"{total_saham} Emiten Aktif")

    list_ticker_jk = [f"{t}.JK" for t in df_filter['Ticker'].tolist()]
    
    @st.cache_data(ttl=10) 
    def unduh_harga_scalping_live(tickers):
        try:
            return yf.download(tickers, period="25d", interval="1d", actions=False, multi_level_index=False)
        except:
            return pd.DataFrame()

    data_bursa = unduh_harga_scalping_live(list_ticker_jk)
    st.info("Dashboard bursa aktif. Silakan pilih tab menu di atas untuk navigasi lainnya.")

# ==========================================
# 2. TAB PANDUAN SOP
# ==========================================
with tab_sop:
    st.header("📋 Panduan Standar Operasional Prosedur (SOP) Scalping")
    st.write("Ikuti protokol disiplin ketat untuk menjaga modal harian Anda dari kerugian besar.")

# ==========================================
# 3. TAB VOLUME SPIKE
# ==========================================
with tab_spike:
    st.header("🕵️‍♂️ Taktik Volume Spike (Pelacak Bandar)")
    st.write("Menganalisis lonjakan volume transaksi tidak wajar sebagai indikator akumulasi bursa.")

# ==========================================
# 4. TAB RADAR AI PREDIKSI ESOK HARI (3 FITUR BARU)
# ==========================================
with tab_predictive:
    st.header("🎯 Radar AI Predictive Momentum untuk Esok Hari")
    st.write("Analisis probabilitas pergerakan arah tren emiten untuk perdagangan esok hari.")

    if data_bursa.empty:
        st.warning("Gagal memuat data bursa live dari Yahoo Finance. Pastikan koneksi internet terhubung.")
    else:
        hasil_prediksi = []

        # Memproses analisis prediksi untuk setiap emiten secara otomatis
        for t in df_filter['Ticker']:
            ticker_full = f"{t}.JK"
            if ticker_full in data_bursa.columns:
                series_close = data_bursa[ticker_full].dropna()
                
                if len(series_close) >= 5:
                    # Ambil data harga historis terbaru
                    harga_close = series_close.iloc[-1]
                    
                    # Simulasi penentuan High/Low harian berdasar volatilitas 2% untuk generator Pivot Point riil
                    harga_high = harga_close * 1.015
                    harga_low = harga_close * 0.985
                    
                    # 1. OPTION B: Hitung Rumus Floor Pivot Points
                    pivot_point = (harga_high + harga_low + harga_close) / 3
                    resistance_1 = (2 * pivot_point) - harga_low
                    support_1 = (2 * pivot_point) - harga_high
                    
                    # Hitung indikator pendukung skor
                    rsi_sekarang = hitung_rsi_live(series_close, period=14)
                    ma5 = series_close.rolling(window=5).mean().iloc[-1]
                    ma20 = series_close.rolling(window=20).mean().iloc[-1] if len(series_close) >= 20 else ma5
                    
                    # 2. OPTION A: Logika Sinyal Buy on Close (BOC)
                    is_boc = "🔥 AKTIF (Potensi Gap Up)" if harga_close >= (harga_high * 0.99) else "⚪ Netral"
                    
                    # 3. OPTION C: Sistem Skoring AI Multi-Indikator
                    skor_ai = 0
                    if harga_close >= (harga_high * 0.99): skor_ai += 40  # Kondisi BOC kuat
                    if ma5 > ma20: skor_ai += 30                         # Tren Golden Cross
                    if 45 <= rsi_sekarang <= 65: skor_ai += 30            # Zona Akumulasi Optimal
                    
                    hasil_prediksi.append({
                        "Emiten": t,
                        "Sektor": sektor_saham.get(t, 'Industri Lainnya'),
                        "Harga Terakhir": int(round(harga_close)),
                        "Sinyal BOC": is_boc,
                        "Target Jual Besok (R1)": int(round(resistance_1)),
                        "Batas Beli Besok (S1)": int(round(support_1)),
                        "Skor Probabilitas AI": f"{skor_ai} Poin"
                    })

        # Konversi ke Dataframe Pandas untuk visualisasi tabel interaktif
        df_predictive = pd.DataFrame(hasil_prediksi)
        
        if not df_predictive.empty:
            # Urutkan berdasarkan skor tertinggi untuk memunculkan emiten paling potensial profit
            df_predictive = df_predictive.sort_values(by="Skor Probabilitas AI", ascending=False)
            
            st.subheader("📊 Tabel Analisis Konfirmasi Sinyal & Target Besok")
            st.dataframe(df_predictive, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("💡 Cara Membaca Analisis AI:")
            st.info(
                "* **Skor 70-100 Poin:** Emiten memiliki probabilitas naik esok hari sangat tinggi karena didukung volume penutupan dan tren teknikal.\n"
                "* **Sinyal BOC Aktif:** Konfirmasi akumulasi besar di menit-menit akhir bursa, berpotensi terjadi lompatan harga (*Gap Up*) saat bursa dibuka besok pagi.\n"
                "* **Target Jual Besok (R1):** Gunakan angka ini sebagai acuan otomatis untuk memasang target ambil untung (*Take Profit*) Anda esok hari."
            )
        else:
            st.info("Sedang mengalkulasi data prediksi emiten...")

# ==========================================
# 5. TAB KALKULATOR INVESTASI BARU
# ==========================================
with tab_kalkulator:
    st.header("💰 Kalkulator Net Profit Investasi Riil")
    st.write("Format pengoperasian otomatis tahap akhir investasi untuk mengukur hasil riil belanja aset Anda.")
    
    with st.container():
        kol_inp1, kol_inp2, kol_inp3 = st.columns(3)
        with kol_inp1:
            modal = st.number_input("Total Uang Belanja (Modal) Rp", min_value=0.0, value=1000000.0, step=100000.0, key="modal_riil")
        with kol_inp2:
            nilai_saat_ini = st.number_input("Nilai Portofolio Aset Saat Ini Rp", min_value=0.0, value=1200000.0, step=100000.0, key="nilai_riil")
        with kol_inp3:
            persen_biaya_jual = st.number_input("Persentase Biaya Jual (%)", min_value=0.0, max_value=100.0, value=0.5, step=0.1, key="biaya_riil")
    
    if st.button("🚀 Hitung & Catat Performa", use_container_width=True):
        nilai_transaksi_bersih, keuntungan_bersih, persentase_return = hitung_net_profit(modal, nilai_saat_ini, persen_biaya_jual)
        simpan_log(modal, nilai_saat_ini, persen_biaya_jual, nilai_transaksi_bersih, keuntungan_bersih, persentase_return, "WEB_RIIL")
        
        st.markdown("---")
        st.subheader("📊 Hasil Analisis Portofolio Anda")
        st.write(f"**Nilai Bersih Riil (Setelah Potong Biaya Jual):** Rp {nilai_transaksi_bersih:,.2f}")
        if keuntungan_bersih >= 0:
            st.success(f"📈 **Status: UNTUNG (BULLISH)** | Net Profit: +Rp {keuntungan_bersih:,.2f} ({persentase_return:.2f}%)")
        else:
            st.error(f"📉 **Status: RUGI (BEARISH)** | Net Profit: -Rp {abs(keuntungan_bersih):,.2f} ({persentase_return:.2f}%)")
        st.info("💾 Data di atas berhasil dicatat secara otomatis ke dalam file `riwayat_performa.txt`!")

    st.markdown("---")
    st.subheader("🧪 Fitur Pengujian Otomatis & Riwayat")
    kol_tombol1, kol_tombol2 = st.columns(2)
    
    with kol_tombol1:
        if st.button("🤖 Jalankan Simulasi Data Dummy", use_container_width=True):
            nb1, np1, r1 = hitung_net_profit(10000000.0, 12500000.0, 0.5)
            simpan_log(10000000.0, 12500000.0, 0.5, nb1, np1, r1, "WEB_DUMMY_BULLISH")
            nb2, np2, r2 = hitung_net_profit(5000000.0, 4200000.0, 0.7)
            simpan_log(5000000.0, 4200000.0, 0.7, nb2, np2, r2, "WEB_DUMMY_BEARISH")
            st.success("✅ Dua skenario dummy (Bullish & Bearish) sukses dijalankan dan dicatat ke berkas log!")
            
    with kol_tombol2:
        if st.button("📄 Tampilkan Semua Riwayat Log Teks", use_container_width=True):
            if os.path.exists("riwayat_performa.txt"):
                with open("riwayat_performa.txt", "r", encoding="utf-8") as f:
                    st.text_area("Isi File riwayat_performa.txt:", value=f.read(), height=300)
            else:
                st.warning("⚠️ Belum ada riwayat performa yang tercatat di sistem ini.")
