import streamlit as st
import pandas as pd
import numpy as np

# 1. PENGATURAN HALAMAN WEBSITE
st.set_page_config(page_title="AI Analisis Saham BEI", layout="wide")

st.title("🤖 Sistem AI Prediksi & Penyaring Saham BEI")
st.write("Aplikasi acuan investasi jangka menengah dan panjang berbasis Fundamental Murni.")

st.markdown("---")

# 2. FUNGSI UNTUK MEMBACA DATA
def muat_data():
    try:
        df_raw = pd.read_csv('data_kompas100.csv')
        df_screener = pd.read_csv('rekomendasi_saham_ai.csv')
        df_final = pd.read_csv('keputusan_final_ai_saham.csv')
        return df_raw, df_screener, df_final
    except FileNotFoundError:
        return None, None, None

df_raw, df_screener, df_final = muat_data()

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
    
    # === FITUR BARU: TOMBOL KLIK UNTUK MELIHAT DAFTAR KOMPAS100 ===
    with st.expander("🔍 Klik di sini untuk melihat Daftar 100 Saham Kompas100 yang Dipantau"):
        st.write("Berikut adalah kode emiten dan nama perusahaan yang dianalisis oleh AI:")
        # Tampilkan hanya kolom Ticker dan Nama dari data mentah asli, urut berdasarkan Ticker
        df_kompas100 = df_raw[['Ticker', 'Nama']].sort_values(by='Ticker').reset_index(drop=True)
        st.dataframe(df_kompas100, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 4. FITUR PENCARIAN & TABEL INTERAKTIF
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
            "Harga_Sekarang": st.column_config.NumberColumn("Harga Pasar", format="Rp %d"),
            "Harga_Wajar_Graham": st.column_config.NumberColumn("Harga Wajar Graham", format="Rp %d"),
            "Margin_of_Safety(%)": st.column_config.NumberColumn("Margin of Safety", format="%.1f%%"),
            "Rekomendasi_Akhir": st.column_config.TextColumn("Rekomendasi Keputusan AI")
        },
        hide_index=True,
        use_container_width=True
    )
    
else:
    st.error("Waduh! File basis data tidak ditemukan di folder Anda.")
