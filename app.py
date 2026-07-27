import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# 1. PENGATURAN HALAMAN WEBSITE
st.set_page_config(page_title="AI Analisis Saham BEI", layout="wide")

st.title("🤖 Sistem AI Prediksi & Penyaring Saham BEI")
st.write("Aplikasi acuan investasi jangka menengah dan panjang berbasis Fundamental Murni.")

st.markdown("---")

# 2. FUNGSI UNTUK MEMBACA DATA LAPORAN KEUANGAN (STATIS)
def muat_data_dasar():
    try:
        df_raw = pd.read_csv('data_kompas100.csv')
        df_screener = pd.read_csv('rekomendasi_saham_ai.csv')
        df_final = pd.read_csv('keputusan_final_ai_saham.csv')
        return df_raw, df_screener, df_final
    except FileNotFoundError:
        return None, None, None

df_raw, df_screener, df_final = muat_data_dasar()

# 3. MEMASTIKAN DATA TERSEDIA SEBELUM DITAMPILKAN
if df_final is not None:
    # Menghitung Ringkasan Angka (Metrik)
    total_saham = len(df_raw)
    saham_lolos = len(df_screener)
    strong_buy = len(df_final[df_final['Rekomendasi_Akhir'].str.contains('STRONG BUY')])
    
    # Menampilkan Kotak Ringkasan Di Atas Website
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Saham Dipantau", f"{total_saham} Emiten")
    col2.metric("Saham Lolos Filter Sehat", f"{saham_lolos} Emiten")
    col3.metric("Rekomendasi STRONG BUY AI", f"{strong_buy} Emiten")
    
    # === FITUR PREMIUM: DAFTAR KOMPAS100 DENGAN HARGA REAL-TIME ===
    with st.expander("🔍 Klik di sini untuk melihat Daftar 100 Saham Kompas100 & Harga Real-Time"):
        st.write("Mengambil harga terkini langsung dari bursa pasar efek (Yahoo Finance)...")
        
        # Ambil daftar kode saham asli untuk ditembak massal ke internet
        list_ticker_jk = [f"{t}.JK" for t in df_raw['Ticker'].tolist()]
        
        try:
            # Tembak massal 100 emiten sekaligus dalam 1 detik (sangat ringan untuk RAM 4GB)
            data_pasar = yf.download(list_ticker_jk, period="1d", interval="1m", group_by='ticker', verbose=False)
            
            # Ekstraksi harga terakhir untuk setiap emiten
            list_harga_live = []
            for t in df_raw['Ticker']:
                try:
                    harga_terakhir = data_pasar[f"{t}.JK"]['Close'].dropna().iloc[-1]
                    list_harga_live.append(round(harga_terakhir))
                except:
                    # Jika gagal ambil harga live menit ini, ambil dari data lokal asli
                    harga_lokal = df_raw[df_raw['Ticker'] == t]['Harga_Sekarang'].values[0]
                    list_harga_live.append(harga_lokal)
            
            # Gabungkan harga live ke tabel tampilan Kompas100
            df_kompas100 = df_raw[['Ticker', 'Nama']].copy()
            df_kompas100['Harga_Live_Pasar'] = list_harga_live
            df_kompas100 = df_kompas100.sort_values(by='Ticker').reset_index(drop=True)
            
            # Tampilkan tabel interaktif baru
            st.dataframe(
                df_kompas100, 
                column_config={
                    "Ticker": st.column_config.TextColumn("Kode Saham"),
                    "Nama": st.column_config.TextColumn("Nama Perusahaan"),
                    "Harga_Live_Pasar": st.column_config.NumberColumn("Harga Terkini (Live)", format="Rp %d")
                },
                use_container_width=True, 
                hide_index=True
            )
        except Exception as e:
            st.warning("Gagal memperbarui harga live karena masalah jaringan. Menampilkan data terakhir:")
            st.dataframe(df_raw[['Ticker', 'Nama', 'Harga_Sekarang']].sort_values(by='Ticker'), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 4. FITUR PENCARIAN & TABEL INTERAKTIF REKOMENDASI AI
    st.subheader("📋 Daftar Portofolio Rekomendasi AI")
    st.write("Daftar di bawah ini otomatis diurutkan berdasarkan potensi diskon (*Margin of Safety*) tertinggi:")
    
    cari_saham = st.text_input("🔍 Cari Kode Saham (Contoh: BBCA, TLKM, ASII):").upper().strip()
    
    df_tampilan = df_final.copy()
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
        hide_index=True,
        use_container_width=True
    )
    
else:
    st.error("Waduh! File basis data tidak ditemukan di folder Anda.")
