# -*- coding: utf-8 -*-
import datetime

def hitung_net_profit(modal, nilai_saat_ini, persen_biaya_jual):
    """Menghitung performa net profit riil setelah dipotong biaya jual."""
    biaya_jual = nilai_saat_ini * (persen_biaya_jual / 100)
    nilai_bersih_riil = nilai_saat_ini - biaya_jual
    net_profit = nilai_bersih_riil - modal
    persen_return = (net_profit / modal) * 100 if modal > 0 else 0
    return nilai_bersih_riil, net_profit, persen_return

def simpan_log(modal, nilai_saat_ini, persen_biaya_jual, nilai_bersih_riil, net_profit, persen_return, jenis_data="RIIL"):
    """Mencatat hasil perhitungan secara otomatis ke riwayat_performa.txt"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "UNTUNG (BULLISH)" if net_profit >= 0 else "RUGI (BEARISH)"
    
    log_entry = (
        f"==================================================\n"
        f"Waktu Transaksi : {timestamp} [{jenis_data}]\n"
        f"Modal Belanja   : Rp {modal:,.2f}\n"
        f"Nilai Aset Kini : Rp {nilai_saat_ini:,.2f}\n"
        f"Biaya Jual (%)  : {persen_biaya_jual}%\n"
        f"Nilai Bersih    : Rp {nilai_bersih_riil:,.2f}\n"
        f"Net Profit Riil : Rp {net_profit:,.2f}\n"
        f"Persen Return   : {persen_return:.2f}%\n"
        f"Status Portofolio: {status}\n"
        f"==================================================\n\n"
    )
    with open("riwayat_performa.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)
