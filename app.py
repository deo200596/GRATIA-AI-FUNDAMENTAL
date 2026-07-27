import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import time

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

tab_dashboard, tab_sop, tab_spike = st.tabs([
    "⚡ Dashboard Scalping & Trading Harian", 
    "📋 Panduan SOP Scalping",
    "🕵️‍♂️ Taktik Volume Spike (Pelacak Bandar)"
])
with tab_dashboard:
    try:
        df_raw = pd.read_csv('data_kompas100.csv')
        df_raw['Sektor_Industri'] = df_raw['Ticker'].map(sektor_saham).fillna('Industri Lainnya')
    except FileNotFoundError:
        st.error("File data_kompas100.csv tidak ditemukan di direktori Anda.")
        st.stop()

    pilihan_indeks = st.radio("Pilih Indeks Acuan Trading:", options=["Saham Unggulan LQ45", "Saham Likuid Kompas100"], horizontal=True)
    
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
    
    kamus_harga_live = {}
    kamus_perubahan = {}
    kamus_volume = {}
    kamus_momentum = {}
    kamus_sinyal_ma = {}
    kamus_rsi = {}

    for t in df_filter['Ticker']:
        ticker_full = f"{t}.JK"
        harga_terakhir = None
        volume_terakhir = 0
        sinyal_ma = "⚪ NEUTRAL"
        rsi_sekarang = 50.0
        
        if not data_bursa.empty and ticker_full in data_bursa.columns:
            series_close = data_bursa[ticker_full].dropna()
            if not series_close.empty:
                harga_terakhir = int(round(series_close.iloc[-1]))
                
                if len(series_close) >= 5:
                    ma5_skrg = series_close.rolling(window=5).mean().iloc[-1]
                    ma20_skrg = series_close.rolling(window=20).mean().iloc[-1] if len(series_close) >= 20 else ma5_skrg
                    sinyal_ma = "🔥 GOLDEN CROSS" if ma5_skrg > ma20_skrg else "❄️ DEAD CROSS"
                
                rsi_sekarang = round(hitung_rsi_live(series_close, period=14), 1)

            if ('Volume', ticker_full) in data_bursa.columns:
                series_vol = data_bursa[('Volume', ticker_full)].dropna()
                if not series_vol.empty: volume_terakhir = int(series_vol.sum())
            elif 'Volume' in data_bursa.columns:
                if t in data_bursa['Volume'].columns:
                    series_vol = data_bursa['Volume'][t].dropna()
                    if not series_vol.empty: volume_terakhir = int(series_vol.iloc[-1])

        # PERBAIKAN TOTAL SIFAT ILOC (BARIS 159): Menambahkan [0] lurus agar tidak memicu error _iLocIndexer
        if harga_terakhir is not None and harga_terakhir > 0:
            harga_basis = int(df_filter[df_filter['Ticker'] == t]['Harga_Sekarang'].iloc[0])
            selisih = harga_terakhir - harga_basis
            
            if rsi_sekarang >= 70.0:
                status_mo = "⚠️ OVERBOUGHT (Kemahalan)"
            else:
                status_mo = "🟢 SCALPING BUY" if selisih > 0 else ("🔴 AVOID (Bearish)" if selisih < 0 else "⚪ WAIT (Sideways)")
        else:
            harga_terakhir = int(df_filter[df_filter['Ticker'] == t]['Harga_Sekarang'].iloc[0])
            selisih = 0
            status_mo = "⚪ WAIT (Sideways)"

        kamus_harga_live[t] = harga_terakhir
        kamus_perubahan[t] = selisih
        kamus_volume[t] = volume_terakhir
        kamus_momentum[t] = status_mo
        kamus_sinyal_ma[t] = sinyal_ma
        kamus_rsi[t] = rsi_sekarang

    df_filter['Harga_Live_Pasar'] = df_filter['Ticker'].map(kamus_harga_live)
    df_filter['Fluktuasi_Harga'] = df_filter['Ticker'].map(kamus_perubahan)
    df_filter['Volume_Transaksi'] = df_filter['Ticker'].map(kamus_volume)

    with st.expander(f"🔍 Papan Monitor Trading & Likuiditas Bandar - {pilihan_indeks}", expanded=True):
        def beri_warna_fluktuasi(val):
            if val > 0: return 'color: #00cc66; font-weight: bold;'
            elif val < 0: return 'color: #ff3333; font-weight: bold;'
            return 'color: #888888;'
            
        st.dataframe(
            df_filter[['Ticker', 'Nama', 'Sektor_Industri', 'Harga_Live_Pasar', 'Fluktuasi_Harga', 'Volume_Transaksi']].style.map(beri_warna_fluktuasi, subset=['Fluktuasi_Harga']),
            column_config={
                "Ticker": st.column_config.TextColumn("Kode Saham"),
                "Nama": st.column_config.TextColumn("Nama Perusahaan"),
                "Sektor_Industri": st.column_config.TextColumn("Sektor Industri"),
                "Harga_Live_Pasar": st.column_config.NumberColumn("Harga Terkini", format="Rp %d"),
                "Fluktuasi_Harga": st.column_config.NumberColumn("Selisih Transaksi", format="Rp %+d"),
                "Volume_Transaksi": st.column_config.NumberColumn("Volume Live (Lembar)", format="%d")
            },
            width='stretch', hide_index=True
        )
    st.markdown("---")
    st.subheader("📋 Kalkulator Kontrol Risiko & Rekomendasi Portofolio Trading Harian")

    input_modal = st.number_input("💰 Masukkan Total Modal Siap Pakai Anda (Rp):", min_value=0, value=10000000, step=1000000)

    st.write("🎯 **Panel Filter Pintar (Klik tombol untuk menyaring data otomatis):**")
    col_btn1, col_col2, col_btn3, col_btn4 = st.columns(4)
    
    if 'filter_mode' not in st.session_state: st.session_state.filter_mode = "NORMAL"
    if col_btn1.button("📊 1) Urutkan Vol Bandar Tertinggi"): st.session_state.filter_mode = "URUT_VOL"
    if col_col2.button("⚠️ 2) Tampilkan Volume Palsu (< 50K)"): st.session_state.filter_mode = "VOL_PALSU"
    if col_btn3.button("🔥 3) Tampilkan Volume Valid (Akumulasi)"): st.session_state.filter_mode = "VOL_VALID"
    if col_btn4.button("🔄 Reset Tampilan Tabel"): st.session_state.filter_mode = "NORMAL"

    df_trading = df_filter.copy()
    df_trading['Harga_Beli_Masuk'] = df_trading['Ticker'].map(kamus_harga_live)
    df_trading['Rupiah_Maks_Beli_30%'] = int(input_modal * 0.30)
    df_trading['Maks_Lot_Beli'] = (df_trading['Rupiah_Maks_Beli_30%'] / (df_trading['Harga_Beli_Masuk'] * 100)).fillna(0).astype(int)
    
    df_trading['Harga_Jual_TP1_3%'] = (df_trading['Harga_Beli_Masuk'] * 1.03).fillna(0).astype(int)
    df_trading['Target_TP2_5%'] = (df_trading['Harga_Beli_Masuk'] * 1.05).fillna(0).astype(int)
    df_trading['Harga_Jual_CL_2%'] = (df_trading['Harga_Beli_Masuk'] * 0.98).fillna(0).astype(int)
    
    df_trading['Status_Momentum_Live'] = df_trading['Ticker'].map(kamus_momentum)
    df_trading['Sinyal_MA_Live'] = df_trading['Ticker'].map(kamus_sinyal_ma)
    df_trading['RSI_14_Live'] = df_trading['Ticker'].map(kamus_rsi)

    if st.session_state.filter_mode == "URUT_VOL":
        df_trading = df_trading.sort_values(by='Volume_Transaksi', ascending=False)
    elif st.session_state.filter_mode == "VOL_PALSU":
        df_trading = df_trading[(df_trading['Status_Momentum_Live'] == "🟢 SCALPING BUY") & (df_trading['Volume_Transaksi'] < 50000)]
    elif st.session_state.filter_mode == "VOL_VALID":
        df_trading = df_trading[(df_trading['Status_Momentum_Live'] == "🟢 SCALPING BUY") & (df_trading['Volume_Transaksi'] >= 100000)]

    cari_saham = st.text_input("🔍 Atau Cari Ticker Saham Manual (Contoh: BBCA, GOTO):").upper().strip()
    if cari_saham:
        df_trading = df_trading[df_trading['Ticker'].str.contains(cari_saham)]

    st.dataframe(
        df_trading[['Ticker', 'Nama', 'Harga_Beli_Masuk', 'Rupiah_Maks_Beli_30%', 'Maks_Lot_Beli', 'Harga_Jual_TP1_3%', 'Target_TP2_5%', 'Harga_Jual_CL_2%', 'RSI_14_Live', 'Sinyal_MA_Live', 'Status_Momentum_Live']],
        column_config={
            "Ticker": st.column_config.TextColumn("Kode"),
            "Nama": st.column_config.TextColumn("Nama Emiten"),
            "Harga_Beli_Masuk": st.column_config.NumberColumn("Harga Beli (Rp)", format="Rp %d"),
            "Rupiah_Maks_Beli_30%": st.column_config.NumberColumn("Dana 30%", format="Rp %d"),
            "Maks_Lot_Beli": st.column_config.NumberColumn("Maks (Lot)", format="%d Lot"),
            "Harga_Jual_TP1_3%": st.column_config.NumberColumn("TP 1 (3%)", format="Rp %d"),
            "Target_TP2_5%": st.column_config.NumberColumn("TP 2 (5%)", format="Rp %d"),
            "Harga_Jual_CL_2%": st.column_config.NumberColumn("Cut Loss (2%)", format="Rp %d"),
            "RSI_14_Live": st.column_config.NumberColumn("RSI (14)", format="%.1f"),
            "Sinyal_MA_Live": st.column_config.TextColumn("Tren MA"),
            "Status_Momentum_Live": st.column_config.TextColumn("Momentum")
        },
        width='stretch', hide_index=True
    )

    st.download_button(
        label="📥 Unduh Rencana Eksekusi Trading Harian (CSV)",
        data=df_trading.to_csv(index=False).encode('utf-8'),
        file_name='rencana_trading_harian.csv', mime='text/csv'
    )

    st.markdown("---")
    st.subheader("🕯️ Analisis Grafik Candlestick Pro & Garis MA (3 Bulan)")
    pilihan_saham_grafik = st.selectbox("Pilih Kode Saham Untuk Grafik Teknis:", options=sorted(df_filter['Ticker'].unique()))
    
    if pilihan_saham_grafik:
        try:
            data_hist = yf.download(f"{pilihan_saham_grafik}.JK", period="3mo", interval="1d", multi_level_index=False)
            if not data_hist.empty:
                if isinstance(data_hist.columns, pd.MultiIndex):
                    data_hist.columns = data_hist.columns.get_level_values(0)
                df_tek = data_hist[['Open', 'High', 'Low', 'Close']].dropna().copy()
                df_tek['MA5'] = df_tek['Close'].rolling(window=5).mean()
                df_tek['MA20'] = df_tek['Close'].rolling(window=20).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df_tek.index, open=df_tek['Open'], high=df_tek['High'], low=df_tek['Low'], close=df_tek['Close'], name="Candlestick"))
                fig.add_trace(go.Scatter(x=df_tek.index, y=df_tek['MA5'], mode='lines', name='MA5 (Oranye)', line=dict(color='#ff9900', width=1.5)))
                fig.add_trace(go.Scatter(x=df_tek.index, y=df_tek['MA20'], mode='lines', name='MA20 (Biru)', line=dict(color='#00bcff', width=2)))
                fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=450, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, width='stretch')
        except Exception as e: st.error(f"Gagal memproses grafik lilin: {e}")

# === TAB MENU UTAMA KEDUA: SOP TRADING ===
with tab_sop:
    st.header("📋 SOP Eksekusi Trading Harian (Scalping) Otomatis")
    st.markdown("""
    ### 🛡️ Aturan Utama Kerja Trader Harian Kilat:
    1. **Saringan Saham:** Gunakan tombol filter di dashboard utama untuk menyaring pergerakan bandar secara instan [INDEX].
    2. **Rem Darurat Jenuh Beli (RSI > 70):** Dilarang melakukan pembelian jika angka kolom **RSI (14)** berada di atas **70.0** atau status momentum berubah menjadi **⚠️ OVERBOUGHT** [INDEX]. 
    3. **Pembatasan Modal:** Patuhi batasan nilai rupiah pada porsi dana 30% [INDEX].
    4. **Disiplin Keluar Pasar:** Pasang antrean jual otomatis mengikuti target nominal **TP 1 (3%)**, atau gunakan **Target TP 2 (5%)** jika volume transaksi bandar meledak sangat besar [INDEX].
    """)

# === TAB MENU UTAMA KETIGA: TAKTIK VOLUME SPIKE ===
with tab_spike:
    st.header("🕵️‍♂️ Taktik Volume Spike: Cara Mendeteksi Pergerakan Bandar Lewat Tabel")
    st.markdown("""
    ### 🚀 Panduan Penggunaan Panel Tombol Filter Pintar
    * **Tombol Volume Valid:** Menampilkan saham yang murni sedang diakumulasi oleh bandar bursa modal raksasa [INDEX]. Selalu pastikan nilai RSI di tabel masih berada di bawah angka 70 sebelum melakukan klik eksekusi masuk [INDEX].
    """)

# SINKRONISASI PENGULANG 10 DETIK
if auto_refresh:
    time.sleep(10)
    st.rerun()
