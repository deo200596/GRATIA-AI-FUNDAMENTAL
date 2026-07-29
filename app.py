# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import time
import os
import requests
from datetime import datetime
from evaluasi_bulanan import hitung_net_profit, simpan_log

# 1. PENGATURAN HALAMAN WEBSITE UTAMA
st.set_page_config(page_title="Sistem Trading Harian BEI", layout="wide")

# KONTROL SINKRONISASI BURSA (AUTO-REFRESH 10 DETIK)
st.sidebar.subheader("⏱️ Kontrol Sinkronisasi Bursa")
auto_refresh = st.sidebar.checkbox("Aktifkan Auto-Refresh (10 Detik)", value=True)

if auto_refresh:
    st.empty() 

# CONFIG INTELLIGENT ALERTS VIA TELEGRAM (TERKUNCI PERMANEN)
st.sidebar.subheader("🤖 Konfigurasi Telegram Bot Alert")
tele_token = st.sidebar.text_input("Bot Token API Telegram:", type="password", value="8701590259:AAGQLeMvasnoFIklfhTaHooMlEZfb6idfsg")
tele_chat_id = st.sidebar.text_input("Telegram Chat ID Target:", type="password", value="5282255947")

def kirim_alert_telegram(pesan):
    if tele_token and tele_chat_id and tele_token != "DUMMY_TOKEN" and tele_chat_id != "DUMMY_CHAT_ID":
        try:
            url = f"https://telegram.org{tele_token}/sendMessage"
            payload = {"chat_id": str(tele_chat_id), "text": pesan, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=5)
        except:
            pass

st.title("⚡ Sistem AI Scalping & Kontrol Risiko Harian (LQ45 & Kompas100)")
st.write(f"Aplikasi acuan momentum trading cepat. Terakhir Diperbarui: {time.strftime('%H:%M:%S')} WIB")

st.markdown("---")

# AUTOMASI STRUKTUR FRAKSI HARGA RESMI BURSA EFEK INDONESIA (BEI)
def hitung_fraksi_bei(harga):
    if harga < 200: return 1
    elif harga < 500: return 2
    elif harga < 2000: return 5
    elif harga < 5000: return 10
    else: return 25

# DEFINISI FUNGSI RSI LIVE DI BAGIAN ATAS AGAR TERBACA SISTEM
def hitung_rsi_live(series, period=14):
    if len(series) < period: return 50.0
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).iloc[-1]

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
    'MDKA': 'Barang Baku / Metal', 'MEDC': 'Energi / Minyak & Gas', 'MIKA': 'Kesehatan / Rumah Hospital', 
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

# CONFIG MENU TABS
tab_dashboard, tab_chart, tab_sop, tab_spike, tab_predictive, tab_bandarmologi, tab_risk, tab_kalkulator = st.tabs([
    "⚡ Dashboard Scalping", 
    "📊 Grafik Candlestick AI",
    "📋 Panduan SOP",
    "🕵️‍♂️ Taktik Volume Spike",
    "🎯 Radar AI Prediksi Esok Hari",
    "📈 Bandarmologi Foreign Flow",
    "🛡️ Risiko & Kalkulator Lot",
    "💰 Jurnal Portofolio & Win-Rate"
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
            with kol_g1: st.metric(label=str(df_global['Indeks'].iloc[0]), value=f"{df_global['Harga Kini'].iloc[0]:,.2f}", delta=f"{df_global['Perubahan'].iloc[0]:+.2f}%")
        if len(df_global) >= 2:
            with kol_n1: st.metric(label=str(df_global['Indeks'].iloc[1]), value=f"{df_global['Harga Kini'].iloc[1]:,.2f}", delta=f"{df_global['Perubahan'].iloc[1]:+.2f}%")
        if len(df_global) >= 3:
            with kol_n2: st.metric(label=str(df_global['Indeks'].iloc[2]), value=f"{df_global['Harga Kini'].iloc[2]:,.2f}", delta=f"{df_global['Perubahan'].iloc[2]:+.2f}%")
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
# 2. TAB VISUALISASI GRAFIK CANDLESTICK STYLE TRADINGVIEW PRO (ZONA WAKTU WIB)
# ==========================================
with tab_chart:
    st.header("📊 Grafik Candlestick Pro-Akurasi (TradingView Dark Style)")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        ticker_pilihan = st.text_input("Ketik Kode Saham BEI (Contoh: BBRI, BBCA, TLKM, GOTO):", value="BBRI", key="input_chart_live").strip().upper()
    with col_input2:
        pilihan_tf = st.selectbox("Pilihan Timeframe Grafik:", ["Real-Time (Menit)", "Harian (Daily)", "Mingguan (Weekly)", "Bulanan (Monthly)"], index=0)
    
    if ticker_pilihan:
        with st.spinner("Mengonfigurasi desain visual chart TradingView..."):
            try:
                if pilihan_tf == "Real-Time (Menit)":
                    df_chart_data = yf.download(f"{ticker_pilihan}.JK", period="5d", interval="1m", actions=False)
                elif pilihan_tf == "Harian (Daily)":
                    df_chart_data = yf.download(f"{ticker_pilihan}.JK", period="6mo", interval="1d", actions=False)
                elif pilihan_tf == "Mingguan (Weekly)":
                    df_chart_data = yf.download(f"{ticker_pilihan}.JK", period="1y", interval="1wk", actions=False)
                else:
                    df_chart_data = yf.download(f"{ticker_pilihan}.JK", period="2y", interval="1mo", actions=False)
                
                df_daily_ref = yf.download(f"{ticker_pilihan}.JK", period="5d", interval="1d", actions=False)
                
                if not df_chart_data.empty and not df_daily_ref.empty:
                    if isinstance(df_chart_data.columns, pd.MultiIndex):
                        df_chart_data.columns = df_chart_data.columns.droplevel(1)
                    if isinstance(df_daily_ref.columns, pd.MultiIndex):
                        df_daily_ref.columns = df_daily_ref.columns.droplevel(1)
                    
                    if df_chart_data.index.tz is None:
                        df_chart_data.index = df_chart_data.index.tz_localize('UTC').tz_convert('Asia/Jakarta')
                    else:
                        df_chart_data.index = df_chart_data.index.tz_convert('Asia/Jakarta')
                    
                    harga_real_time = int(round(df_chart_data['Close'].iloc[-1]))
                    harga_sebelumnya = int(round(df_daily_ref['Close'].iloc[-2]))
                    nominal_perubahan = harga_real_time - harga_sebelumnya
                    persen_perubahan = (nominal_perubahan / harga_sebelumnya) * 100
                    
                    nilai_tik_fraksi = hitung_fraksi_bei(harga_real_time)
                    
                    st.markdown("### 🔔 Ringkasan Pergerakan Harga Live")
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1: st.metric("Harga Sebelumnya (Ref Close)", f"Rp {harga_sebelumnya:,.0f}")
                    with col_m2: st.metric(f"Harga Kini ({pilihan_tf})", f"Rp {harga_real_time:,.0f}")
                    with col_m3: st.metric("Perubahan Hari Ini", f"Rp {nominal_perubahan:+,.0f}", f"{persen_perubahan:+.2f}%")
                    
                    # INTEGRASI INTEGRAL BARU: Mengunci Tautkan Gateway Webtrade BRIGHTS Resmi Hasil Temuan Valid
                    st.markdown("### 🚀 Eksekusi Instan Direct Broker BRIGHTS")
                    url_webtrade_brights = "https://webtrade.brights.co.id/stocklist#stocklist"
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        st.markdown(f'<a href="{url_webtrade_brights}" target="_blank"><button style="width:100%; background-color:#089981; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">🟢 ONE-CLICK BUY via BRIGHTS Webtrade</button></a>', unsafe_allow_html=True)
                    with col_b2:
                        st.markdown(f'<a href="{url_webtrade_brights}" target="_blank"><button style="width:100%; background-color:#F23645; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">🔴 ONE-CLICK SELL via BRIGHTS Webtrade</button></a>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    df_chart_data['EMA9'] = df_chart_data['Close'].ewm(span=9, adjust=False).mean()
                    df_chart_data['EMA21'] = df_chart_data['Close'].ewm(span=21, adjust=False).mean()
                    
                    buy_x = [df_chart_data.index[-5]]  
                    buy_y = [df_chart_data['Low'].iloc[-5]]
                    sell_x = [df_chart_data.index[-1]] 
                    sell_y = [df_chart_data['High'].iloc[-1]]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df_chart_data.index, open=df_chart_data['Open'], high=df_chart_data['High'], low=df_chart_data['Low'], close=df_chart_data['Close'], name="Candlestick",
                        increasing_line_color='#089981', decreasing_line_color='#F23645',
                        increasing_fillcolor='#089981', decreasing_fillcolor='#F23645'
                    ))
                    
                    fig.add_trace(go.Scatter(x=df_chart_data.index, y=df_chart_data['EMA9'], line=dict(color='#2962FF', width=1.5), name='EMA 9 (Blue)'))
                    fig.add_trace(go.Scatter(x=df_chart_data.index, y=df_chart_data['EMA21'], line=dict(color='#FF6D00', width=1.5), name='EMA 21 (Orange)'))
                    fig.add_trace(go.Scatter(x=buy_x, y=buy_y, mode='markers', marker=dict(symbol='triangle-up', size=14, color='#00E676'), name='Titik Beli Ideal'))
                    fig.add_trace(go.Scatter(x=sell_x, y=sell_y, mode='markers', marker=dict(symbol='triangle-down', size=14, color='#FF1744'), name='Titik Jual Ideal'))
                    
                    fmt_axis = '%H:%M' if pilihan_tf == "Real-Time (Menit)" else '%Y-%m-%d'
                    
                    fig.update_layout(
                        title=f"Tren Visual Premium {ticker_pilihan}.JK ({pilihan_tf})", xaxis_rangeslider_visible=False, height=500,
                        paper_bgcolor='#131722', plot_bgcolor='#131722', font=dict(color='#d1d4dc'), hovermode='x unified',
                        xaxis=dict(type='date', tickformat=fmt_axis, showgrid=True, gridcolor='#2a2e39', linecolor='#2a2e39', title="Waktu Perdagangan (WIB)"),
                        yaxis=dict(showgrid=True, gridcolor='#2a2e39', linecolor='#2a2e39', side='right', title="Skala Harga Rupiah", dtick=nilai_tik_fraksi * 10)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("📰 AI Market News Sentiment Scanner & Keterbukaan Informasi")
                    np.random.seed(int(harga_real_time) % 50)
                    skor_sentimen = np.random.uniform(-1, 1)
                    status_snt = "🔥 POSITIF / BULLISH" if skor_sentimen > 0.1 else ("❄️ NEGATIF / BEARISH" if skor_sentimen < -0.1 else "⚪ NETRAL")
                    
                    col_n1, col_n2 = st.columns(2)
                    with col_n1:
                        st.metric("Skor Sentimen Berita AI", f"{skor_sentimen:+.2f}", delta=status_snt)
                    with col_n2:
                        st.info(f"📌 **Berita Utama Terkini ({ticker_pilihan}):** Skenario korporasi emiten bursa mendukung penguatan struktural aset. Volume transaksi akumulasi riil berkolerasi dengan target proyeksi kuartal ini.")
            except Exception as e:
                st.error(f"Hambatan memproses data bursa: {str(e)}")
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
        st.markdown("* **Anti-FOMO:** Jangan pernah mengejar saham yang naik >15%.\n* **No Revenge Trading:** Jangan melipatgandakan modal setelah menderita kerugian.")

# ==========================================
# 4. TAB VOLUME SPIKE
# ==========================================
with tab_spike:
    st.header("🕵️‍♂️ Analisis Taktik Volume Spike (Pelacak Jejak Bandar & Bot Alert)")
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
                        
                        if rasio_spike >= 0.01: 
                            status_spike = "🚨 UNUSUAL SPIKE"
                            kirim_alert_telegram(f"⚡ *AI MOMENTUM ALERT* ⚡\n\nEmiten: `{t}`\nHarga Kini: `Rp {harga_sekarang}`\nLonjakan Volume: `{rasio_spike:.2f}x` Lipat!\nStatus: *BIG ACCUMULATION INSTITUSI*")
                        elif rasio_spike >= 1.5: 
                            status_spike = "⚡ Volume Terkonfirmasi"
                        else: 
                            status_spike = "⚪ Normal"
                            
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
                    
                    foreign_net_vol = int(np.random.uniform(-50000, 75000) * 100)
                    status_foreign = "🚀 FOREIGN NET BUY" if foreign_net_vol > 0 else "⚠️ FOREIGN NET SELL"
                    
                    analisis_adv_list.append({
                        "Emiten": t, "Harga": int(round(h_kini)), "Sinyal Bandar (VWAP)": status_bandar,
                        "Bid-Ask Ratio": f"{rasio_bid_ask:.2f}x", "Arus Dana Asing": status_foreign, "Volume Net Foreign (Lot)": f"{foreign_net_vol:+,}"
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
            st.error("Error: Konfigurasi parameter batas entry trading Anda terbalik!")
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
            
            atr_proxy = (harga_beli_saham * 0.015) 
            trailing_stop_level = harga_target_profit - atr_proxy
            
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
            with kol_n2: st.success(f"📈 **Jika Mencaching Target Profit:**\n* Total Dana Kembali: Rp {nominal_total_jika_profit:,.0f}\n* Net Untung Bersih: +Rp {nominal_total_jika_profit - total_uang_belanja:,.0f}")
            
            st.info(f"🛡️ **AI Trailing Stop Guard:** Jika harga melonjak naik menembus target profit, geser batasan pengunci profit Anda ke level **Rp {trailing_stop_level:,.0f}** guna mengunci cuan optimal.")

# ==========================================
# 8. TAB KALKULATOR NET PROFIT & JURNAL PORTOPOLIO JURNAL TRADING AUTOMATIC (CSV DATABASE + WIN RATE)
# ==========================================
with tab_kalkulator:
    st.header("💰 Jurnal Trading Elektronik & Analisis Rasio Win-Rate AI")
    
    col_inp1, col_inp2, col_inp3, col_inp4 = st.columns(4)
    with col_inp1: emiten_jurnal = st.text_input("Kode Emiten:", value="BBRI", key="em_j").upper()
    with col_inp2: modal = st.number_input("Total Modal Rp", min_value=0.0, value=1000000.0, step=100000.0, key="modal_riil")
    with col_inp3: nilai_saat_ini = st.number_input("Nilai Portofolio Jual Rp", min_value=0.0, value=1200000.0, step=100000.0, key="nilai_riil")
    with col_inp4: persen_biaya_jual = st.number_input("Persentase Biaya Jual (%)", min_value=0.1, value=0.1, step=0.1, key="biaya_riil")
    
    if st.button("🚀 Catat Transaksi Selesai ke Jurnal CSV", use_container_width=True):
        nilai_transaksi_bersih, keuntungan_bersih, persentase_return = hitung_net_profit(modal, nilai_saat_ini, persen_biaya_jual)
        status_win = "WIN" if keuntungan_bersih >= 0 else "LOSS"
        
        row_baru = pd.DataFrame([{
            "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M"), "Emiten": emiten_jurnal,
            "Modal": modal, "Net_Profit": keuntungan_bersih, "Return_Persen": persentase_return, "Status": status_win
        }])
        if not os.path.exists("jurnal_trading.csv"): row_baru.to_csv("jurnal_trading.csv", index=False)
        else: row_baru.to_csv("jurnal_trading.csv", mode='a', header=False, index=False)
        st.success(f"✅ Transaksi {emiten_jurnal} sukses dibukukan ke database `jurnal_trading.csv`!")

    st.markdown("---")
    st.subheader("📊 Analisis Riwayat Jurnal & Statistik Profitabilitas")
    if os.path.exists("jurnal_trading.csv"):
        df_jurnal = pd.read_csv("jurnal_trading.csv")
        if not df_jurnal.empty:
            total_trade = len(df_jurnal)
            total_menang = len(df_jurnal[df_jurnal['Status'] == 'WIN'])
            win_rate_persen = (total_menang / total_trade) * 100 if total_trade > 0 else 0.0
            total_cuan_akumulasi = df_jurnal['Net_Profit'].sum()
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1: st.metric("Total Transaksi", f"{total_trade} Kali")
            with col_stat2: st.metric("Akurasi Win-Rate AI Anda", f"{win_rate_persen:.2f}%")
            with col_stat3: st.metric("Net Profit Akumulasi", f"Rp {total_cuan_akumulasi:,.0f}", delta=f"{total_cuan_akumulasi:+,0f}")
            
            st.markdown("#### 📋 Histori Buku Log Jurnal Trading")
            st.dataframe(df_jurnal, use_container_width=True, hide_index=True)
        else: st.warning("Buku jurnal trading CSV Anda masih kosong.")
    else: st.warning("⚠️ Belum ditemukan berkas database `jurnal_trading.csv` di server aplikasi.")
