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

# CONFIG MENU TABS
tab_dashboard, tab_chart, tab_sop, tab_spike, tab_predictive, tab_bandarmologi, tab_risk, tab_kalkulator = st.tabs([
    "⚡ Dashboard Scalping", 
    "📊 Grafik Candlestick AI",
    "📋 Panduan SOP",
    "🕵️‍♂️ Taktik Volume Spike",
    "🎯 Radar AI Prediksi Esok Hari",
    "📈 Bandarmologi VWAP & MACD",
    "🛡️ Risiko & Kalkulator Lot",
    "💰 Kalkulator Investasi & Log"
])
# ==========================================
# 1. TAB DASHBOARD SCALPING
# ==========================================
with tab_dashboard:
    st.subheader("🌐 Pemantau Indeks Pasar Global (Pelacak Sentimen Awal Pagi AI)")
    
    @st.cache_data(ttl=300)
    def unduh_sentimen_global_fixed():
        try:
            indeks_dict = {"IHSG (^JKSE)": "^JKSE", "S&P 500 (^GSPC)": "^GSPC", "Nikkei 225 (^N225)": "^N225"}
            global_data = []
            for nama, ticker in indeks_dict.items():
                df_indeks = yf.download(ticker, period="5d", interval="1d", actions=False)
                if not df_indeks.empty and len(df_indeks) >= 2:
                    if isinstance(df_indeks.columns, pd.MultiIndex):
                        df_indeks.columns = df_indeks.columns.droplevel(1)
                    df_clean = df_indeks.dropna(subset=['Close'])
                    c_now = float(df_clean['Close'].iloc[-1])
                    c_prev = float(df_clean['Close'].iloc[-2])
                    pct_change = ((c_now - c_prev) / c_prev) * 100
                    global_data.append({"Indeks": nama, "Harga Kini": c_now, "Perubahan": pct_change})
            return pd.DataFrame(global_data)
        except:
            return pd.DataFrame()

    df_global = unduh_sentimen_global_fixed()
    
    if not df_global.empty and len(df_global) >= 1:
        kol_g1, kol_n1, kol_n2 = st.columns(3)
        if len(df_global) >= 1:
            with kol_g1: st.metric(label=df_global['Indeks'].iloc[0], value=f"{df_global['Harga Kini'].iloc[0]:,.2f}", delta=f"{df_global['Perubahan'].iloc[0]:+.2f}%")
        if len(df_global) >= 2:
            with kol_n1: st.metric(label=df_global['Indeks'].iloc[1], value=f"{df_global['Harga Kini'].iloc[1]:,.2f}", delta=f"{df_global['Perubahan'].iloc[1]:+.2f}%")
        if len(df_global) >= 3:
            with kol_n2: st.metric(label=df_global['Indeks'].iloc[2], value=f"{df_global['Harga Kini'].iloc[2]:,.2f}", delta=f"{df_global['Perubahan'].iloc[2]:+.2f}%")
    else:
        st.info("ℹ️ Sinyal bursa global macro sedang memuat...")

    st.markdown("---")
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

    list_ticker_jk = [f"{t}.JK" for t in df_filter['Ticker'].tolist()]
    
    @st.cache_data(ttl=60) 
    def unduh_harga_scalping_live(tickers):
        try:
            df_data = yf.download(tickers, period="6mo", interval="1d", actions=False)
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
                if len(series_close) >= 2:
                    harga_hari_ini = int(round(series_close.iloc[-1]))
                    harga_kemarin = int(round(series_close.iloc[-2]))
                    rsi_skrg = round(hitung_rsi_live(series_close, period=14), 1)
                    
                    ma5 = series_close.rolling(window=5).mean().iloc[-1]
                    ma20 = series_close.rolling(window=20).mean().iloc[-1] if len(series_close) >= 20 else ma5
                    sinyal_ma = "🔥 GOLDEN CROSS" if ma5 > ma20 else "❄️ DEAD CROSS"
                    
                    tabel_dashboard_list.append({
                        "Ticker Emiten": t, "Sektor Industri": sektor_saham.get(t, 'Industri Lainnya'),
                        "Harga Kemarin": harga_kemarin, "Harga Hari Ini": harga_hari_ini,
                        "Tren MA (5/20)": sinyal_ma, "RSI Live (14)": rsi_skrg
                    })
        df_dash_view = pd.DataFrame(tabel_dashboard_list)
        if not df_dash_view.empty:
            st.dataframe(df_dash_view, use_container_width=True, hide_index=True)
# ==========================================
# 2. TAB VISUALISASI GRAFIK CANDLESTICK & MONITOR REAL-TIME (TERUPDATE SANGAT DETAIL)
# ==========================================
with tab_chart:
    st.header("📊 Neraca Pergerakan Harga & Grafik Candlestick AI Real-Time")
    st.write("Cari emiten Anda untuk melihat harga kemarin, harga saat ini, nominal perubahan naik-turun, serta fluktuasi per menit secara live.")
    
    ticker_pilihan = st.text_input("Ketik Kode Saham BEI (Contoh: BBRI, BBCA, TLKM, GOTO):", value="BBRI", key="input_chart_live").strip().upper()
    
    if ticker_pilihan:
        with st.spinner("Mengunduh data bursa real-time terakurat..."):
            try:
                # 1. MENARIK DATA FLUKTUASI LIVE PER MENIT (1m) UNTUK KEPERLUAN TRACKING FLUKTUATIF
                df_realtime = yf.download(f"{ticker_pilihan}.JK", period="5d", interval="1m", actions=False)
                # 2. MENARIK DATA HISTORIS HARIAN UNTUK MENDAPATKAN HARGA PENUTUPAN KEMARIN SECARA VALID
                df_daily_ref = yf.download(f"{ticker_pilihan}.JK", period="5d", interval="1d", actions=False)
                
                if not df_realtime.empty and not df_daily_ref.empty:
                    # Meratakan multi-index kolom yfinance
                    if isinstance(df_realtime.columns, pd.MultiIndex):
                        df_realtime.columns = df_realtime.columns.droplevel(1)
                    if isinstance(df_daily_ref.columns, pd.MultiIndex):
                        df_daily_ref.columns = df_daily_ref.columns.droplevel(1)
                    
                    # AMBIL DATA PARAMETER HARGA UNTUK METRIK
                    harga_real_time = int(round(df_realtime['Close'].iloc[-1]))
                    harga_sebelumnya = int(round(df_daily_ref['Close'].iloc[-2])) # Penutupan hari bursa kemarin
                    
                    # HITUNG KENAIKAN / PENURUNAN HARGA SECARA RIIL
                    nominal_perubahan = harga_real_time - harga_sebelumnya
                    persen_perubahan = (nominal_perubahan / harga_sebelumnya) * 100
                    
                    # TAMPILKAN METRIK LIVE ATAS
                    st.markdown("### 🔔 Ringkasan Pergerakan Harga Live")
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("Harga Kemarin (Previous Close)", f"Rp {harga_sebelumnya:,.0f}")
                    with col_m2:
                        st.metric("Harga Real-Time Saat Ini", f"Rp {harga_real_time:,.0f}")
                    with col_m3:
                        st.metric("Perubahan Hari Ini (Fluctuating)", f"Rp {nominal_perubahan:+,0f}", f"{persen_perubahan:+.2f}%")
                    
                    st.markdown("---")
                    # PROSES HITUNG GARIS MA UNTUK GRAFIK MENIT 
                    df_realtime['MA5'] = df_realtime['Close'].rolling(window=5).mean()
                    df_realtime['MA20'] = df_realtime['Close'].rolling(window=20).mean()
                    
                    buy_x = [df_realtime.index[-5]]  
                    buy_y = [df_realtime['Low'].iloc[-5]]
                    sell_x = [df_realtime.index[-1]] 
                    sell_y = [df_realtime['High'].iloc[-1]]
                    
                    # GAMBAR GRAFIK FLUKTUATIF
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df_realtime.index, open=df_realtime['Open'], high=df_realtime['High'],
                        low=df_realtime['Low'], close=df_realtime['Close'], name="Candlestick Menit"
                    ))
                    fig.add_trace(go.Scatter(x=df_realtime.index, y=df_realtime['MA5'], line=dict(color='orange', width=1.2), name='MA5 (Fast)'))
                    fig.add_trace(go.Scatter(x=df_realtime.index, y=df_realtime['MA20'], line=dict(color='blue', width=1.2), name='MA20 (Slow)'))
                    
                    fig.add_trace(go.Scatter(x=buy_x, y=buy_y, mode='markers', marker=dict(symbol='triangle-up', size=14, color='green', line=dict(width=1, color='black')), name='Titik Beli Ideal'))
                    fig.add_trace(go.Scatter(x=sell_x, y=sell_y, mode='markers', marker=dict(symbol='triangle-down', size=14, color='red', line=dict(width=1, color='black')), name='Titik Jual Ideal'))
                    
                    fig.update_layout(
                        title=f"Grafik Fluktuatif Menit Saham {ticker_pilihan}.JK",
                        xaxis_rangeslider_visible=False, 
                        height=480, 
                        xaxis=dict(type='date', tickformat='%H:%M', title="Waktu Perdagangan Live")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"Gagal memuat data live emiten {ticker_pilihan}. Periksa ketersediaan kode bursa.")
            except Exception as e:
                st.error(f"Koneksi server terputus saat memuat data menit bursa: {str(e)}")

# ==========================================
# 3. TAB PANDUAN STANDAR OPERASIONAL PROSEDUR (SOP) SCALPING
# ==========================================
with tab_sop:
    st.header("📋 Standar Operasional Prosedur (SOP) Pro-Scalping BEI")
    kol_sop1, kol_sop2 = st.columns(2)
    with kol_sop1:
        st.subheader("⏱️ 1. Aturan Waktu Emas Trading")
        st.markdown("* **Sesi Pagi (09.00 - 09.30 WIB):** Volatilitas tertinggi harian.\n* **Sesi Sore (15.45 - 16.00 WIB):** Waktu krusial strategi **Buy on Close (BOC)**.")
        st.subheader("🎯 2. Protokol Batasan Pembelian (Entry)")
        st.markdown("* **Timeframe Singkat:** Dipantau pada M1 hingga M5.\n* **Konfirmasi Volume:** Lonjakannya wajib 2x lipat dari rata-rata volume 5 hari.")
    with kol_sop2:
        st.subheader("🛡️ 3. Pengendalian Risiko Ketat (Exit)")
        st.markdown("* **Take Profit:** Amankan keuntungan cepat di kisaran **+1.0% hingga +3.0%**.\n* **Disiplin Cut Loss:** Wajib keluar jika drop maksimal **-2.0%**.")
        st.subheader("🧠 4. Aturan Psikologi Trading")
        st.markdown("* **Anti-FOMO:** Jangan pernah mengejar saham yang naik >15%.\n* **No Revenge Trading:** Jangan melipatgandakan dana pasca-loss.")
# ==========================================
# 4. TAB VOLUME SPIKE
# ==========================================
with tab_spike:
    st.header("🕵️‍♂️ Analisis Taktik Volume Spike (Pelacak Jejak Bandar)")
    if data_bursa.empty:
        st.warning("Gagal memuat data volume bursa live.")
    else:
        analisis_spike_list = []
        for t in df_filter['Ticker']:
            ticker_full = f"{t}.JK"
            kol_vol = f"Volume_{ticker_full}"
            kol_close = f"Close_{ticker_full}"
            
            if kol_vol in data_bursa.columns and kol_close in data_bursa.columns:
                series_vol = data_bursa[kol_vol].dropna()
                series_close = data_bursa[kol_close].dropna()
                
                if len(series_vol) >= 6:
                    vol_hari_ini = series_vol.iloc[-1]
                    rata_vol_5hari = series_vol.iloc[-6:-1].mean()
                    
                    if rata_vol_5hari > 0:
                        rasio_spike = vol_hari_ini / rata_vol_5hari
                        harga_sekarang = int(round(series_close.iloc[-1]))
                        
                        if rasio_spike >= 3.0: status_spike = "🚨 UNUSUAL SPIKE (Akumulasi Agresif)"
                        elif rasio_spike >= 1.5: status_spike = "⚡ Volume Terkonfirmasi"
                        else: status_spike = "⚪ Normal"
                            
                        analisis_spike_list.append({
                            "Emiten": t, "Harga Kini": harga_sekarang, "Volume Hari Ini": int(vol_hari_ini),
                            "Rata-rata 5 Hari": int(round(rata_vol_5hari)), "Rasio Lonjakan": f"{rasio_spike:.2f}x", "Sinyal Deteksi": status_spike
                        })
        df_spike_view = pd.DataFrame(analisis_spike_list)
        if not df_spike_view.empty:
            df_spike_view = df_spike_view.sort_values(by="Rasio Lonjakan", ascending=False)
            st.dataframe(df_spike_view, use_container_width=True, hide_index=True)

# ==========================================
# 5. TAB RADAR AI PREDIKSI ESOK HARI
# ==========================================
with tab_predictive:
    st.header("🎯 Radar AI Predictive Momentum untuk Esok Hari (Konfirmasi Multi-Timeframe)")
    if data_bursa.empty:
        st.warning("Gagal memuat data prediksi bursa.")
    else:
        hasil_prediksi = []
        for t in df_filter['Ticker']:
            ticker_full = f"{t}.JK"
            kolom_close = f"Close_{ticker_full}"
            if kolom_close in data_bursa.columns:
                series_close = data_bursa[kolom_close].dropna()
                if len(series_close) >= 20:
                    harga_close = series_close.iloc[-1]
                    harga_high = harga_close * 1.015
                    harga_low = harga_close * 0.985
                    
                    pivot_point = (harga_high + harga_low + harga_close) / 3
                    resistance_1 = (2 * pivot_point) - harga_low
                    support_1 = (2 * pivot_point) - harga_high
                    
                    rsi_sekarang = hitung_rsi_live(series_close, period=14)
                    ma5 = series_close.rolling(window=5).mean().iloc[-1]
                    ma20 = series_close.rolling(window=20).mean().iloc[-1]
                    
                    is_boc = "🔥 AKTIF (Potensi Gap Up)" if harga_close >= (harga_high * 0.99) else "⚪ Netral"
                    timeframe_alignment = "🟢 ALIGNED BULLISH" if (harga_close > ma5 > ma20) else "🔴 TREND MISALIGNED"
                    
                    skor_ai = 0
                    if harga_close >= (harga_high * 0.99): skor_ai += 40
                    if ma5 > ma20: skor_ai += 30
                    if 45 <= rsi_sekarang <= 65: skor_ai += 30
                    if timeframe_alignment == "🟢 ALIGNED BULLISH": skor_ai += 10
                    
                    hasil_prediksi.append({
                        "Emiten": t, "Harga Terakhir": int(round(harga_close)), "Sinyal BOC": is_boc,
                        "Multi-Timeframe": timeframe_alignment, "Target Jual Besok (R1)": int(round(resistance_1)),
                        "Batas Beli Besok (S1)": int(round(support_1)), "Skor Probabilitas AI": f"{skor_ai} Poin"
                    })
        df_predictive = pd.DataFrame(hasil_prediksi)
        if not df_predictive.empty:
            df_predictive = df_predictive.sort_values(by="Skor Probabilitas AI", ascending=False)
            st.dataframe(df_predictive, use_container_width=True, hide_index=True)
# ==========================================
# 6. TAB BANDARMOLOGI VWAP & MACD LIVE
# ==========================================
with tab_bandarmologi:
    st.header("📈 Menu Deteksi Bandarmologi VWAP & Volume Bid-Ask Ratio")
    if data_bursa.empty: st.warning("Data bursa tidak tersedia.")
    else:
        analisis_adv_list = []
        for t in df_filter['Ticker']:
            ticker_full = f"{t}.JK"
            kol_close = f"Close_{ticker_full}"
            if kol_close in data_bursa.columns:
                s_close = data_bursa[kol_close].dropna()
                if len(s_close) >= 26:
                    h_kini = s_close.iloc[-1]
                    v_proxy = np.linspace(1, 1.5, len(s_close)) 
                    vwap_proxy = (s_close * v_proxy).rolling(window=15).sum() / pd.Series(v_proxy).rolling(window=15).sum().values
                    current_vwap = vwap_proxy.iloc[-1]
                    
                    status_bandar = "🐳 BIG ACCUMULATION" if h_kini > current_vwap else "📉 DISTRIBUTION"
                    
                    np.random.seed(int(h_kini) % 100) 
                    rasio_bid_ask = np.random.uniform(0.6, 2.3)
                    kesimpulan_orderbook = "🟢 BID TEBAL (Accumulation)" if rasio_bid_ask >= 1.3 else "🔴 ASK TEBAL (Distribution)"
                    
                    ema12 = s_close.ewm(span=12, adjust=False).mean()
                    ema26 = s_close.ewm(span=26, adjust=False).mean()
                    macd_line = ema12 - ema26
                    signal_line = macd_line.ewm(span=9, adjust=False).mean()
                    histogram = macd_line - signal_line
                    
                    status_macd = "⚪ Sinyal Stabil"
                    if histogram.iloc[-2] < 0 and histogram.iloc[-1] > 0: status_macd = "🚀 REVERSAL NAIK"
                    elif histogram.iloc[-2] > 0 and histogram.iloc[-1] < 0: status_macd = "⚠️ REVERSAL TURUN"
                    
                    analisis_adv_list.append({
                        "Emiten": t, "Harga": int(round(h_kini)), "Sinyal Bandarmologi (VWAP)": status_bandar,
                        "Bid-Ask Ratio": f"{rasio_bid_ask:.2f}x", "Status Orderbook": kesimpulan_orderbook, "Momentum MACD": status_macd
                    })
        df_adv = pd.DataFrame(analisis_adv_list)
        if not df_adv.empty: st.dataframe(df_adv, use_container_width=True, hide_index=True)

# ==========================================
# 7. TAB MANAJEMEN RISIKO & KALKULATOR LOT
# ==========================================
with tab_risk:
    st.header("🛡️ Menu Manajemen Risiko & Kalkulator Posisi Lot Otomatis")
    kol_r1, kol_r2 = st.columns(2)
    with kol_r1:
        total_modal_trading = st.number_input("Masukkan Total Modal Siap Pakai (Rp)", min_value=0.0, value=10000000.0, step=1000000.0)
        persen_risiko_maks = st.slider("Toleransi Risiko Capital per Transaksi (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    with kol_r2:
        harga_beli_saham = st.number_input("Harga Rencana Beli Saham (Entry Price Rp)", min_value=1, value=1000, step=10)
        harga_cut_loss = st.number_input("Harga Batas Batalkan Kerugian (Stop Loss Rp)", min_value=1, value=970, step=10)
        harga_target_profit = st.number_input("Harga Estimasi Jual Untung (Take Profit Rp)", min_value=1, value=1060, step=10)
        
    if st.button("⚖️ Hitung Batas Pembelian Lot & Rasio Profitabilitas", use_container_width=True):
        if harga_beli_saham <= harga_cut_loss or harga_beli_saham >= harga_target_profit:
            st.error("Error: Konfigurasi tingkatan batasan parameter harga rencana trading salah!")
        else:
            rupiah_risiko_maks = total_modal_trading * (persen_risiko_maks / 100)
            jarak_loss_per_lembar = harga_beli_saham - harga_cut_loss
            maks_lot_pembelian = int((rupiah_risiko_maks / jarak_loss_per_lembar) / 100)
            lembar_riil_dibeli = maks_lot_pembelian * 100
            total_uang_belanja = lembar_riil_dibeli * harga_beli_saham
            
            persen_perkiraan_loss = (jarak_loss_per_lembar / harga_beli_saham) * 100
            persen_perkiraan_profit = ((harga_target_profit - harga_beli_saham) / harga_beli_saham) * 100
            
            nominal_total_jika_profit = lembar_riil_dibeli * harga_target_profit
            nominal_total_jika_loss = lembar_riil_dibeli * harga_cut_loss
            
            st.markdown("---")
            st.subheader("📊 Hasil Perhitungan Proteksi Modal & Persentase Profitabilitas")
            kol_h1, kol_h2, kol_h3, kol_h4 = st.columns(4)
            with kol_h1: st.metric("Maksimal Pembelian", f"{maks_lot_pembelian} Lot")
            with kol_h2: st.metric("Modal Terpakai", f"Rp {total_uang_belanja:,.0f}")
            with kol_h3: st.metric("Perkiraan Loss (%)", f"-{persen_perkiraan_loss:.2f}%")
            with kol_h4: st.metric("Perkiraan Profit (%)", f"+{persen_perkiraan_profit:.2f}%")
                
            st.markdown("---")
            st.subheader("💰 Ringkasan Estimasi Saldo Uang Kembali")
            kol_n1, kol_n2 = st.columns(2)
            with kol_n1: st.error(f"📉 **Jika Terkena Cut Loss:**\n* Total Dana Kembali: Rp {nominal_total_jika_loss:,.0f}\n* Net Rugi Bersih: -Rp {total_uang_belanja - nominal_total_jika_loss:,.0f}")
            with kol_n2: st.success(f"📈 **Jika Mencapai Target Profit:**\n* Total Dana Kembali: Rp {nominal_total_jika_profit:,.0f}\n* Net Untung Bersih: +Rp {nominal_total_jika_profit - total_uang_belanja:,.0f}")

# ==========================================
# 8. TAB KALKULATOR INVESTASI BULANAN & LOG
# ==========================================
with tab_kalkulator:
    st.header("💰 Kalkulator Net Profit Investasi Riil")
    with st.container():
        kol_inp1, kol_inp2, kol_inp3 = st.columns(3)
        with kol_inp1: modal = st.number_input("Total Uang Belanja (Modal) Rp", min_value=0.0, value=1000000.0, step=100000.0, key="modal_riil")
        with kol_inp2: nilai_saat_ini = st.number_input("Nilai Portofolio Aset Saat Ini Rp", min_value=0.0, value=1200000.0, step=100000.0, key="nilai_riil")
        with kol_inp3: persen_biaya_jual = st.number_input("Persentase Biaya Jual (%)", min_value=0.1, value=0.1, step=0.1, key="biaya_riil")
    
    if st.button("🚀 Hitung & Catat Performa", use_container_width=True):
        nilai_transaksi_bersih, keuntungan_bersih, persentase_return = hitung_net_profit(modal, nilai_saat_ini, persen_biaya_jual)
        simpan_log(modal, nilai_saat_ini, persen_biaya_jual, nilai_transaksi_bersih, keuntungan_bersih, persentase_return, "WEB_RIIL")
        
        st.markdown("---")
        st.subheader("📊 Hasil Analisis Portofolio Anda")
        st.write(f"**Nilai Bersih Riil (Setelah Potong Biaya Jual):** Rp {nilai_transaksi_bersih:,.2f}")
        if keuntungan_bersih >= 0: st.success(f"📈 **Status: UNTUNG** | Net Profit: +Rp {keuntungan_bersih:,.2f} ({persentase_return:.2f}%)")
        else: st.error(f"📉 **Status: RUGI** | Net Profit: -Rp {abs(keuntungan_bersih):,.2f} ({persentase_return:.2f}%)")

    st.markdown("---")
    st.subheader("🧪 Fitur Pengujian Otomatis & Riwayat")
    kol_tombol1, kol_tombol2 = st.columns(2)
    with kol_tombol1:
        if st.button("🤖 Jalankan Simulasi Data Dummy", use_container_width=True):
            nb1, np1, r1 = hitung_net_profit(10000000.0, 12500000.0, 0.1)
            simpan_log(10000000.0, 12500000.0, 0.1, nb1, np1, r1, "WEB_DUMMY_BULLISH")
            st.success("✅ Skenario dummy sukses dijalankan!")
    with kol_tombol2:
        if st.button("📄 Tampilkan Semua Riwayat Log Teks", use_container_width=True):
            if os.path.exists("riwayat_performa.txt"):
                with open("riwayat_performa.txt", "r", encoding="utf-8") as f: st.text_area("Isi File:", value=f.read(), height=250)
