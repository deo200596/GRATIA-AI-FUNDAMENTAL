import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# 1. PENGATURAN HALAMAN WEBSITE
st.set_page_config(page_title="AI Analisis Saham BEI", layout="wide")

st.title("🤖 Sistem AI Prediksi & Penyaring Saham BEI")
st.write("Aplikasi acuan investasi jangka menengah dan panjang berbasis Fundamental Murni.")

st.markdown("---")

# 2. FUNGSI UNTUK MEMBACA DATA LAPORAN KEUANGAN
def muat_data_dasar():
    try:
        df_raw = pd.read_csv('data_kompas100.csv')
        df_screener = pd.read_csv('rekomendasi_saham_ai.csv')
        df_final = pd.read_csv('keputusan_final_ai_saham.csv')
        return df_raw, df_screener, df_final
    except FileNotFoundError:
        return None, None, None

df_raw, df_screener, df_final = muat_data_dasar()

# Fungsi Mewarnai Teks Fluktuasi (Hijau jika positif, Merah jika negatif)
def beri_warna_fluktuasi(val):
    if val > 0:
        return 'color: #00cc66; font-weight: bold;' # Hijau cerah
    elif val < 0:
        return 'color: #ff3333; font-weight: bold;' # Merah cerah
    else:
        return 'color: #888888;' # Abu-abu

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
    
    # === FITUR KOMPAS100 DENGAN PERBAIKAN `.map()` UNTUK PEWARNAAN VISUAL ===
    with st.expander("🔍 Klik di sini untuk melihat Daftar 100 Saham Kompas100 & Harga Real-Time"):
        st.write("Mengambil harga terkini langsung dari bursa pasar efek (Yahoo Finance)...")
        
        # Siapkan daftar ticker massal
        list_ticker_jk = [f"{t}.JK" for t in df_raw['Ticker'].tolist()]
        
        try:
            # Unduh data bursa 1 hari terakhir
            data_pasar = yf.download(list_ticker_jk, period="1d", interval="1m")
            
            list_harga_live = []
            list_perubahan = []
            
            for t in df_raw['Ticker']:
                ticker_full = f"{t}.JK"
                harga_terakhir = None
                
                # Periksa struktur Tuple ('Close', 'BBCA.JK') secara spesifik
                for col in data_pasar.columns:
                    if isinstance(col, tuple) and len(col) == 2:
                        if col[0] == 'Close' and col[1] == ticker_full:
                            series_valid = data_pasar[col].dropna()
                            if not series_valid.empty:
                                harga_terakhir = int(round(series_valid.iloc[-1]))
                                break
                
                # Jika harga live berhasil diekstrak
                if harga_terakhir is not None:
                    harga_basis = int(df_raw[df_raw['Ticker'] == t]['Harga_Sekarang'].values[0])
                    selisih = harga_terakhir - harga_basis
                else:
                    # Jika bursa tutup/jeda, gunakan data model lama
                    harga_terakhir = int(df_raw[df_raw['Ticker'] == t]['Harga_Sekarang'].values[0])
                    selisih = 0
                    
                list_harga_live.append(harga_terakhir)
                list_perubahan.append(selisih)
            
            # Memasukkan hasil ke dalam tabel
            df_kompas100 = df_raw[['Ticker', 'Nama']].copy()
            df_kompas100['Harga_Live_Pasar'] = list_harga_live
            df_kompas100['Fluktuasi_Harga'] = list_perubahan
            df_kompas100 = df_kompas100.sort_values(by='Ticker').reset_index(drop=True)
            
            # PERBAIKAN UTAMA: Menggunakan `.map()` menggantikan `.applymap()` yang telah usang di Pandas terbaru
            df_berwarna = df_kompas100.style.map(beri_warna_fluktuasi, subset=['Fluktuasi_Harga'])
            
            st.dataframe(
                df_berwarna, 
                column_config={
                    "Ticker": st.column_config.TextColumn("Kode Saham"),
                    "Nama": st.column_config.TextColumn("Nama Perusahaan"),
                    "Harga_Live_Pasar": st.column_config.NumberColumn("Harga Terkini (Live)", format="Rp %d"),
                    "Fluktuasi_Harga": st.column_config.NumberColumn("Fluktuasi Real-Time", format="Rp %+d")
                },
                use_container_width=True, 
                hide_index=True
            )
        except Exception as e:
            st.warning(f"Sistem bursa sedang istirahat/pemeliharaan ({e}). Menampilkan data model:")
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
