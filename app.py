import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# 1. PENGATURAN HALAMAN WEBSITE
st.set_page_config(page_title="AI Analisis Saham BEI", layout="wide")

st.title("🤖 Sistem AI Prediksi & Penyaring Saham BEI")
st.write("Aplikasi acuan investasi jangka menengah dan panjang berbasis Kombinasi Fundamental & Teknikal Klasik.")

st.markdown("---")

# DAFTAR KODE SAHAM LQ45 RESMI
saham_lq45 = [
    'ACES', 'ADRO', 'AKRA', 'AMMAN', 'AMRT', 'ANTM', 'ARTO', 'ASII', 'BBCA', 'BBNI', 
    'BBRI', 'BBTN', 'BMRI', 'BRIS', 'BRPT', 'BSDE', 'CPIN', 'CTRA', 'EXCL', 'GOTO', 
    'ICBP', 'INCO', 'INDF', 'INKP', 'INTP', 'ISAT', 'ITMG', 'JSMR', 'KLBF', 'MAPI', 
    'MDKA', 'MEDC', 'MIKA', 'MYOR', 'PGAS', 'PTBA', 'SIDO', 'SMGR', 'SMRA', 'TLKM', 
    'TOWR', 'TPIA', 'UNTR', 'UNVR', 'XL'
]

# 2. FUNGSI UNTUK MEMBACA DATA LAPORAN KEUANGAN
def muat_data_dasar():
    try:
        df_raw = pd.read_csv('data_kompas100.csv')
        df_final = pd.read_csv('keputusan_final_ai_saham.csv')
        return df_raw, df_final
    except FileNotFoundError:
        return None, None

df_raw, df_final = muat_data_dasar()

# Fungsi Mewarnai Teks Fluktuasi
def beri_warna_fluktuasi(val):
    if val > 0: return 'color: #00cc66; font-weight: bold;'
    elif val < 0: return 'color: #ff3333; font-weight: bold;'
    else: return 'color: #888888;'

# 3. MEMASTIKAN DATA TERSEDIA SEBELUM DITAMPILKAN
if df_final is not None:
    # FITUR PILIHAN INDEKS UTAMA (LQ45 atau KOMPAS100)
    st.subheader("📊 Pilih Cakupan Indeks Bursa")
    pilihan_indeks = st.radio(
        "Tampilkan data berdasarkan indeks:",
        options=["Saham Unggulan LQ45", "Saham Likuid Kompas100"],
        horizontal=True
    )
    
    # Filter data berdasarkan pilihan radio button
    if pilihan_indeks == "Saham Unggulan LQ45":
        df_filter_indeks_raw = df_raw[df_raw['Ticker'].isin(saham_lq45)].copy()
        df_filter_indeks_final = df_final[df_final['Ticker'].isin(saham_lq45)].copy()
    else:
        df_filter_indeks_raw = df_raw.copy()
        df_filter_indeks_final = df_final.copy()
        
    total_saham = len(df_filter_indeks_raw)
    strong_buy = len(df_filter_indeks_final[df_filter_indeks_final['Rekomendasi_Akhir'].str.contains('STRONG BUY')])
    
    col1, col2 = st.columns(2)
    col1.metric(f"Total Saham Dipantau ({pilihan_indeks})", f"{total_saham} Emiten")
    col2.metric("Rekomendasi STRONG BUY AI", f"{strong_buy} Emiten")
    
    # === TAMPILAN LIVE DATA INDEX ===
    with st.expander(f"🔍 Lihat Daftar Emiten & Harga Live - {pilihan_indeks}"):
        st.write("Mengambil harga terkini langsung dari bursa pasar efek (Yahoo Finance)...")
        list_ticker_jk = [f"{t}.JK" for t in df_filter_indeks_raw['Ticker'].tolist()]
        
        try:
            data_pasar = yf.download(list_ticker_jk, period="1d", interval="1m")
            list_harga_live = []
            list_perubahan = []
            
            for t in df_filter_indeks_raw['Ticker']:
                ticker_full = f"{t}.JK"
                harga_terakhir = None
                
                for col in data_pasar.columns:
                    if isinstance(col, tuple) and len(col) == 2:
                        if col == 'Close' and col == ticker_full:
                            series_valid = data_pasar[col].dropna()
                            if not series_valid.empty:
                                harga_terakhir = int(round(series_valid.iloc[-1]))
                                break
                
                if harga_terakhir is not None:
                    harga_basis = int(df_filter_indeks_raw[df_filter_indeks_raw['Ticker'] == t]['Harga_Sekarang'].values)
                    selisih = harga_terakhir - harga_basis
                else:
                    harga_terakhir = int(df_filter_indeks_raw[df_filter_indeks_raw['Ticker'] == t]['Harga_Sekarang'].values)
                    selisih = 0
                    
                list_harga_live.append(harga_terakhir)
                list_perubahan.append(selisih)
            
            df_tabel_live = df_filter_indeks_raw[['Ticker', 'Nama']].copy()
            df_tabel_live['Harga_Live_Pasar'] = list_harga_live
            df_tabel_live['Fluktuasi_Harga'] = list_perubahan
            df_tabel_live = df_tabel_live.sort_values(by='Ticker').reset_index(drop=True)
            
            st.dataframe(
                df_tabel_live.style.map(beri_warna_fluktuasi, subset=['Fluktuasi_Harga']), 
                column_config={
                    "Ticker": st.column_config.TextColumn("Kode Saham"),
                    "Nama": st.column_config.TextColumn("Nama Perusahaan"),
                    "Harga_Live_Pasar": st.column_config.NumberColumn("Harga Terkini (Live)", format="Rp %d"),
                    "Fluktuasi_Harga": st.column_config.NumberColumn("Fluktuasi Real-Time", format="Rp %+d")
                },
                use_container_width=True, hide_index=True
            )
        except Exception as e:
            st.warning("Menampilkan data dasar model karena bursa sedang libur/tutup.")
            st.dataframe(df_filter_indeks_raw[['Ticker', 'Nama', 'Harga_Sekarang']].sort_values(by='Ticker'), use_container_width=True, hide_index=True)
            
    st.markdown("---")
    
    # INTERAKTIF REKOMENDASI AI
    st.subheader("📋 Daftar Portofolio Rekomendasi AI")
    cari_saham = st.text_input("🔍 Cari Kode Saham (Contoh: BBCA, TLKM, ASII):").upper().strip()
    
    df_tampilan = df_filter_indeks_final.copy()
    if cari_saham:
        df_tampilan = df_tampilan[df_tampilan['Ticker'].str.contains(cari_saham)]
        
    st.dataframe(
        df_tampilan,
        column_config={
            "Ticker": st.column_config.TextColumn("Kode Saham"),
            "Nama": st.column_config.TextColumn("Nama Perusahaan"),
            "Harga_Sekarang": st.column_config.NumberColumn("Harga Pasar Model", format="Rp %d"),
            "Harga_Wajar_Graham": st.column_config.NumberColumn("Harga Wajar Graham", format="Rp %d"),
            "Margin_of_Safety(%)": st.column_config.NumberColumn("Margin of Safety", format="%.1f%%"),
            "Rekomendasi_Akhir": st.column_config.TextColumn("Rekomendasi Keputusan AI")
        },
        hide_index=True, use_container_width=True
    )

    # FITUR UNDUH LAPORAN EXCEL LANGSUNG DARI HP
    st.download_button(
        label="📥 Unduh Daftar Saham Rekomendasi AI (CSV)",
        data=df_tampilan.to_csv(index=False).encode('utf-8'),
        file_name='rekomendasi_saham_ai.csv',
        mime='text/csv',
    )
    
    # === FITUR PREMIUM: GRAFIK CANDLESTICK INTERAKTIF + MA5 + MA20 ===
    st.markdown("---")
    st.subheader("🕯️ Analisis Grafik Candlestick Pro & Garis MA (3 Bulan)")
    
    pilihan_saham_grafik = st.selectbox(
        "Pilih Kode Saham untuk melihat Grafik Candlestick & MA Kontrol:",
        options=sorted(df_filter_indeks_raw['Ticker'].unique())
    )
    
    if pilihan_saham_grafik:
        st.write(f"Memproses data teknikal historis untuk **{pilihan_saham_grafik}**...")
        try:
            data_hist = yf.download(f"{pilihan_saham_grafik}.JK", period="3mo", interval="1d")
            
            if not data_hist.empty:
                if isinstance(data_hist.columns, pd.MultiIndex):
                    data_hist.columns = data_hist.columns.get_level_values(0)
                
                df_teknikal = data_hist[['Open', 'High', 'Low', 'Close']].dropna().copy()
                
                df_teknikal['MA5'] = df_teknikal['Close'].rolling(window=5).mean()
                df_teknikal['MA20'] = df_teknikal['Close'].rolling(window=20).mean()
                
                fig = go.Figure()
                
                fig.add_trace(go.Candlestick(
                    x=df_teknikal.index,
                    open=df_teknikal['Open'], high=df_teknikal['High'],
                    low=df_teknikal['Low'], close=df_teknikal['Close'],
                    name="Candlestick"
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_teknikal.index, y=df_teknikal['MA5'],
                    mode='lines', name='Garis MA5 (Tren Pendek)',
                    line=dict(color='#ff9900', width=1.5)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_teknikal.index, y=df_teknikal['MA20'],
                    mode='lines', name='Garis MA20 (Tren Menengah)',
                    line=dict(color='#00bcff', width=2)
                ))
                
                fig.update_layout(
                    title=f"Tren Pergerakan Harga Candlestick {pilihan_saham_grafik}",
                    xaxis_title="Tanggal Bursa",
                    yaxis_title="Harga Saham (Rp)",
                    xaxis_rangeslider_visible=False,
                    template="plotly_dark",
                    height=500,
                    margin=dict(l=10, r=10, t=40, b=10)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **Tips Membaca Grafik:** Jika batang Candlestick atau garis **MA5 (Oranye)** berhasil menembus ke atas garis **MA20 (Biru)**, itu menandakan sinyal *Golden Cross* (potensi pembalikan arah tren naik/bullish) yang sangat bagus untuk konfirmasi momentum beli.")
            else:
                st.warning("Data pasar historis emiten kosong.")
        except Exception as e:
            st.error(f"Gagal melukis candlestick: {e}")
else:
    st.error("Waduh! File basis data tidak ditemukan di folder Anda.")
