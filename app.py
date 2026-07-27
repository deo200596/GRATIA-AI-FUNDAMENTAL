import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# 1. PENGATURAN HALAMAN WEBSITE UTAMA
st.set_page_config(page_title="Sistem Trading Harian BEI", layout="wide")

st.title("⚡ Sistem AI Scalping & Kontrol Risiko Harian (LQ45 & Kompas100)")
st.write("Aplikasi acuan momentum trading cepat dan harian menggunakan live price streaming bursa efek.")

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

# STRUKTUR TAB MENU UTAMA WEB
tab_dashboard, tab_sop = st.tabs(["⚡ Dashboard Scalping & Trading Harian", "📋 Panduan SOP Scalping"])
with tab_dashboard:
    # MEMBACA DATA SAHAM DARI BASE CSV LOKAL
    try:
        df_raw = pd.read_csv('data_kompas100.csv')
        df_raw['Sektor_Industri'] = df_raw['Ticker'].map(sektor_saham).fillna('Industri Lainnya')
    except FileNotFoundError:
        st.error("File data_kompas100.csv tidak ditemukan di direktori Anda.")
        st.stop()

    # PILIHAN FILTER INDEKS BURSA
    pilihan_indeks = st.radio("Pilih Indeks Acuan Trading:", options=["Saham Unggulan LQ45", "Saham Likuid Kompas100"], horizontal=True)
    
    if pilihan_indeks == "Saham Unggulan LQ45":
        df_filter = df_raw[df_raw['Ticker'].isin(saham_lq45)].copy()
    else:
        df_filter = df_raw.copy()

    total_saham = len(df_filter)
    st.metric(f"Total Saham Siap Di-scalping ({pilihan_indeks})", f"{total_saham} Emiten Aktif")

    # STREAMING DATA HARGA LIVE
    list_ticker_jk = [f"{t}.JK" for t in df_filter['Ticker'].tolist()]
    
    @st.cache_data(ttl=30) # Segarkan data scalping setiap 30 detik untuk akurasi day trading
    def unduh_harga_scalping_live(tickers):
        try:
            return yf.download(tickers, period="1d", interval="1m", actions=False, multi_level_index=False)
        except:
            return pd.DataFrame()

    data_bursa = unduh_harga_scalping_live(list_ticker_jk)
    
    kamus_harga_live = {}
    kamus_perubahan = {}
    kamus_momentum = {}

    for t in df_filter['Ticker']:
        ticker_full = f"{t}.JK"
        harga_terakhir = None
        
        if not data_bursa.empty and ticker_full in data_bursa.columns:
            series_close = data_bursa[ticker_full].dropna()
            if not series_close.empty:
                harga_terakhir = int(round(series_close.iloc[-1]))

        if harga_terakhir is not None and harga_terakhir > 0:
            harga_basis = int(df_filter[df_filter['Ticker'] == t]['Harga_Sekarang'].values[0])
            selisih = harga_terakhir - harga_basis
            status_mo = "🟢 SCALPING BUY (Bullish)" if selisih > 0 else ("🔴 AVOID (Bearish)" if selisih < 0 else "⚪ WAIT (Sideways)")
        else:
            harga_terakhir = int(df_filter[df_filter['Ticker'] == t]['Harga_Sekarang'].values[0])
            selisih = 0
            status_mo = "⚪ WAIT (Sideways)"

        kamus_harga_live[t] = harga_terakhir
        kamus_perubahan[t] = selisih
        kamus_momentum[t] = status_mo

    df_filter['Harga_Live_Pasar'] = df_filter['Ticker'].map(kamus_harga_live)
    df_filter['Fluktuasi_Harga'] = df_filter['Ticker'].map(kamus_perubahan)

    with st.expander(f"🔍 Papan Monitor Trading & Selisih Harga Terkini - {pilihan_indeks}", expanded=True):
        def beri_warna_fluktuasi(val):
            if val > 0: return 'color: #00cc66; font-weight: bold;'
            elif val < 0: return 'color: #ff3333; font-weight: bold;'
            return 'color: #888888;'
            
        st.dataframe(
            df_filter[['Ticker', 'Nama', 'Sektor_Industri', 'Harga_Live_Pasar', 'Fluktuasi_Harga']].style.map(beri_warna_fluktuasi, subset=['Fluktuasi_Harga']),
            column_config={
                "Ticker": st.column_config.TextColumn("Kode Saham"),
                "Nama": st.column_config.TextColumn("Nama Perusahaan"),
                "Sektor_Industri": st.column_config.TextColumn("Sektor Industri"),
                "Harga_Live_Pasar": st.column_config.NumberColumn("Harga Terkini", format="Rp %d"),
                "Fluktuasi_Harga": st.column_config.NumberColumn("Selisih Transaksi", format="Rp %+d")
            },
            width='stretch', hide_index=True
        )
    st.markdown("---")
    st.subheader("📋 Kalkulator Kontrol Risiko & Rekomendasi Portofolio Trading Harian")

    # MEMBUAT KALKULATOR TRADING KILAT UNTUK SELURUH EMITEN INDEKS
    df_trading = df_filter.copy()
    df_trading['Harga_Beli_Masuk'] = df_trading['Ticker'].map(kamus_harga_live)
    df_trading['Porsi_Modal_Maks'] = "30% Maks"
    df_trading['Harga_Jual_TP_3%'] = (df_trading['Harga_Beli_Masuk'] * 1.03).fillna(0).astype(int)
    df_trading['Harga_Jual_CL_2%'] = (df_trading['Harga_Beli_Masuk'] * 0.98).fillna(0).astype(int)
    df_trading['Status_Momentum_Live'] = df_trading['Ticker'].map(kamus_momentum)

    cari_saham = st.text_input("🔍 Cari Kode Saham Trading (Contoh: BBCA, GOTO, ANTM):").upper().strip()
    if cari_saham:
        df_trading = df_trading[df_trading['Ticker'].str.contains(cari_saham)]

    st.dataframe(
        df_trading[['Ticker', 'Nama', 'Sektor_Industri', 'Harga_Beli_Masuk', 'Porsi_Modal_Maks', 'Harga_Jual_TP_3%', 'Harga_Jual_CL_2%', 'Status_Momentum_Live']],
        column_config={
            "Ticker": st.column_config.TextColumn("Kode"),
            "Nama": st.column_config.TextColumn("Nama Emiten"),
            "Sektor_Industri": st.column_config.TextColumn("Sektor"),
            "Harga_Beli_Masuk": st.column_config.NumberColumn("Harga Beli Sekarang (Rp)", format="Rp %d"),
            "Porsi_Modal_Maks": st.column_config.TextColumn("Porsi Modal"),
            "Harga_Jual_TP_3%": st.column_config.NumberColumn("Target TP (3%)", format="Rp %d"),
            "Harga_Jual_CL_2%": st.column_config.NumberColumn("Cut Loss (2%)", format="Rp %d"),
            "Status_Momentum_Live": st.column_config.TextColumn("Status Momentum")
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
    
    # PERBAIKAN TOTAL: Seluruh emiten di indeks kini masuk ke dalam dropdown menu grafik tanpa terkecuali
    pilihan_saham_grafik = st.selectbox("Pilih Kode Saham Untuk Grafik Teknis:", options=sorted(df_filter['Ticker'].unique()))
    if pilihan_saham_grafik:
        try:
            data_hist = yf.download(f"{pilihan_saham_grafik}.JK", period="3mo", interval="1d", multi_level_index=False)
            if not data_hist.empty:
                df_tek = data_hist[['Open', 'High', 'Low', 'Close']].dropna().copy()
                df_tek['MA5'] = df_tek['Close'].rolling(window=5).mean()
                df_tek['MA20'] = df_tek['Close'].rolling(window=20).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df_tek.index, open=df_tek['Open'], high=df_tek['High'], low=df_tek['Low'], close=df_tek['Close'], name="Candlestick"))
                fig.add_trace(go.Scatter(x=df_tek.index, y=df_tek['MA5'], mode='lines', name='MA5 (Oranye)', line=dict(color='#ff9900', width=1.5)))
                fig.add_trace(go.Scatter(x=df_tek.index, y=df_tek['MA20'], mode='lines', name='MA20 (Biru)', line=dict(color='#00bcff', width=2)))
                fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=450, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, width='stretch')
        except Exception as e:
            st.error(f"Gagal memproses grafik lilin: {e}")

# === TAB MENU UTAMA KEDUA: SOP TRADING HARIAN / SCALPING ===
with tab_sop:
    st.header("⚡ SOP Eksekusi Trading Harian (Scalping) Otomatis")
    
    st.components.v1.html("""
    <div style="background-color: #0e1117; padding: 20px; border-radius: 10px; font-family: sans-serif; color: white;">
        <div style="display: flex; flex-direction: column; align-items: center;">
            <div style="border: 2px solid #00cc66; padding: 10px; border-radius: 5px; background-color: #1a231a; text-align: center; width: 250px;"><b>1. PANTAU MOMENTUM SCALPING</b><br>Cari Saham Berstatus "🟢 SCALPING BUY"</div>
            <div style="font-size: 20px; margin: 5px;">⬇️</div>
            <div style="border: 2px solid #ffaa00; padding: 10px; border-radius: 5px; background-color: #1a1c23; text-align: center; width: 250px;"><b>2. CEK TEKNIKAL GRAFIK</b><br>Candlestick di Atas MA5 & MA20</div>
            <div style="font-size: 20px; margin: 5px;">⬇️</div>
            <div style="border: 2px solid #00ccff; padding: 10px; border-radius: 5px; background-color: #1a1c23; text-align: center; width: 250px;"><b>3. MASUK POSISI (MAKS 30%)</b><br>Eksekusi Cepat di Harga Live Pasar</div>
            <div style="font-size: 20px; margin: 5px;">⬇️</div>
            <div style="display: flex; justify-content: space-around; width: 100%; margin-top: 10px;">
                <div style="border: 2px solid #00cc66; padding: 10px; border-radius: 5px; background-color: #1a231a; text-align: center; width: 200px;"><b>TAKE PROFIT (TP)</b><br>Jual Kilat saat Profit Naik ≥ 3%</div>
                <div style="border: 2px solid #ff3333; padding: 10px; border-radius: 5px; background-color: #231a1a; text-align: center; width: 200px;"><b>CUT LOSS (CL)</b><br>Disiplin Keluar saat Rugi Meleset ≤ 2%</div>
            </div>
        </div>
    </div>
    """, height=300)

    st.markdown("""
    ### 🛡️ Aturan Utama Kerja Trader Harian Kilat:
    1. **Saringan Saham:** Hanya eksekusi emiten yang memiliki status **🟢 SCALPING BUY (Bullish)** pada tabel kalkulator kontrol risiko.
    2. **Pembatasan Modal:** Maksimal dana satu saham adalah **30% dari total modal siap pakai** untuk mencegah risiko penurunan mendadak (*floating loss* besar).
    3. **Disiplin Ambil Keuntungan:** Pasang *Sell Order* secara otomatis pada harga yang tertera di kolom **Target TP (3%)**. Begitu tersentuh, segera amankan keuntungan tunai Anda.
    4. **Disiplin Batasi Kerugian:** Jika pergerakan pasar berbalik arah menentang posisi Anda, wajib pasang *Stop Loss* otomatis di nominal kolom **Cut Loss (2%)** demi menyelamatkan modal trading Anda dari kejatuhan yang dalam.
    """)
