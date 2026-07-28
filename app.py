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
# 1. TAB DASHBOARD SCALPING (DENGAN FIX MULTI-INDEX YFINANCE)
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
    
    @st.cache_data(ttl=60) 
    def unduh_harga_scalping_live(tickers):
        try:
            # Mengubah periode pencarian menjadi 6 bulan bursa
            df_data = yf.download(tickers, period="6mo", interval="1d", actions=False)
            
            # FITUR FIX: Merapikan multi-index kolom yfinance agar berformat tunggal string
            if isinstance(df_data.columns, pd.MultiIndex):
                df_data.columns = ['_'.join(col).strip() for col in df_data.columns.values]
            return df_data
        except:
            return pd.DataFrame()

    data_bursa = unduh_harga_scalping_live(list_ticker_jk)
    
    tabel_dashboard_list = []
    
    if not data_bursa.empty:
        for t in df_filter['Ticker']:
            ticker_full = f"{t}.JK"
            kolom_close = f"Close_{ticker_full}"
            
            if kolom_close in data_bursa.columns:
                series_close = data_bursa[kolom_close].dropna()
                if not series_close.empty:
                    harga_kini = int(round(series_close.iloc[-1]))
                    rsi_skrg = round(hitung_rsi_live(series_close, period=14), 1)
                    
                    ma5 = series_close.rolling(window=5).mean().iloc[-1]
                    ma20 = series_close.rolling(window=20).mean().iloc[-1] if len(series_close) >= 20 else ma5
                    sinyal_ma = "🔥 GOLDEN CROSS" if ma5 > ma20 else "❄️ DEAD CROSS"
                    
                    tabel_dashboard_list.append({
                        "Ticker Emiten": t,
                        "Sektor Industri": sektor_saham.get(t, 'Industri Lainnya'),
                        "Harga Terakhir": harga_kini,
                        "Tren MA (5/20)": sinyal_ma,
                        "RSI Live (14)": rsi_skrg
                    })
        
        df_dash_view = pd.DataFrame(tabel_dashboard_list)
        if not df_dash_view.empty:
            st.subheader("📋 Daftar Emiten Bursa Aktif")
            st.dataframe(df_dash_view, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Data emiten bursa sedang kosong. Silakan muat ulang halaman.")
    else:
        st.warning("⚠️ Tidak ada data bursa yang berhasil dimuat dari server.")

# ==========================================
# 2. TAB PANDUAN SOP & 3. TAB VOLUME SPIKE
# ==========================================
with tab_sop:
    st.header("📋 Panduan Standar Operasional Prosedur (SOP) Scalping")
    st.write("Ikuti protokol disiplin ketat untuk menjaga modal harian Anda dari kerugian besar.")

with tab_spike:
    st.header("🕵️‍♂️ Taktik Volume Spike (Pelacak Bandar)")
    st.write("Menganalisis lonjakan volume transaksi tidak wajar sebagai indikator akumulasi bursa.")
# ==========================================
# 4. TAB RADAR AI PREDIKSI ESOK HARI (DATA 6 BULAN + FIX MULTI INDEX)
# ==========================================
with tab_predictive:
    st.header("🎯 Radar AI Predictive Momentum untuk Esok Hari (Analisis Historis 6 Bulan)")
    st.write("Mengukur probabilitas keberhasilan profit berdasarkan tren jangka menengah 6 bulan terakhir.")

    if data_bursa.empty:
        st.warning("Gagal memuat data prediksi bursa. Periksa jaringan internet komputer Anda.")
    else:
        hasil_prediksi = []

        for t in df_filter['Ticker']:
            ticker_full = f"{t}.JK"
            kolom_close = f"Close_{ticker_full}"
            
            if kolom_close in data_bursa.columns:
                series_close = data_bursa[kolom_close].dropna()
                
                if len(series_close) >= 20:
                    harga_close = series_close.iloc[-1]
                    
                    # Perhitungan volatilitas harga harian untuk penentuan Pivot Point
                    harga_high = harga_close * 1.015
                    harga_low = harga_close * 0.985
                    
                    pivot_point = (harga_high + harga_low + harga_close) / 3
                    resistance_1 = (2 * pivot_point) - harga_low
                    support_1 = (2 * pivot_point) - harga_high
                    
                    rsi_sekarang = hitung_rsi_live(series_close, period=14)
                    ma5 = series_close.rolling(window=5).mean().iloc[-1]
                    ma20 = series_close.rolling(window=20).mean().iloc[-1]
                    
                    is_boc = "🔥 AKTIF (Potensi Gap Up)" if harga_close >= (harga_high * 0.99) else "⚪ Netral"
                    
                    skor_ai = 0
                    if harga_close >= (harga_high * 0.99): skor_ai += 40
                    if ma5 > ma20: skor_ai += 30
                    if 45 <= rsi_sekarang <= 65: skor_ai += 30
                    
                    hasil_prediksi.append({
                        "Emiten": t,
                        "Sektor": sektor_saham.get(t, 'Industri Lainnya'),
                        "Harga Terakhir": int(round(harga_close)),
                        "Sinyal BOC": is_boc,
                        "Target Jual Besok (R1)": int(round(resistance_1)),
                        "Batas Beli Besok (S1)": int(round(support_1)),
                        "Skor Probabilitas AI": f"{skor_ai} Poin"
                    })

        df_predictive = pd.DataFrame(hasil_prediksi)
        if not df_predictive.empty:
            df_predictive = df_predictive.sort_values(by="Skor Probabilitas AI", ascending=False)
            st.subheader("📊 Tabel Analisis Sinyal & Target Ambil Untung Esok Hari")
            st.dataframe(df_predictive, use_container_width=True, hide_index=True)
        else:
            st.info("Gagal menyusun ringkasan data prediksi AI.")

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
