import numpy as np
import pandas as pd
import joblib
import os # <-- Impor modul os

# --- PERBAIKAN PADA LOGIKA PEMUATAN MODEL ---

# 1. Tentukan path absolut ke file model
#    __file__ adalah path ke file ini (kmeans_saw.py)
#    os.path.dirname(__file__) adalah folder tempat file ini berada ('app')
#    os.path.dirname(os.path.dirname(__file__)) adalah folder induk dari 'app', yaitu folder utama proyek
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(project_root, 'app/decision_tree_model.joblib')

# 2. Muat model menggunakan path absolut yang sudah kita tentukan
try:
    dt_model = joblib.load(model_path)
    print(f"Model Decision Tree berhasil dimuat dari: {model_path}")
except FileNotFoundError:
    dt_model = None
    print(f"PERINGATAN: File model tidak ditemukan di path yang diharapkan: {model_path}")
    print("Pastikan Anda sudah menjalankan 'train_model.py' di folder utama proyek.")
except Exception as e:
    dt_model = None
    print(f"Terjadi error saat memuat model: {e}")

# --- AKHIR PERBAIKAN ---


# --- FUNGSI UNTUK KLASIFIKASI MENGGUNAKAN MODEL ML ---
def klasifikasi_berdasarkan_aset(data_umkm):
    """
    Melakukan klasifikasi UMKM menggunakan model Decision Tree yang sudah dilatih.
    """
    if not dt_model:
        print("Error: Model Decision Tree tidak tersedia.")
        # Fallback: Kembalikan data tanpa klasifikasi
        data_klasifikasi_error = [dict(item) for item in data_umkm]
        for umkm in data_klasifikasi_error:
            umkm['klasifikasi'] = 'Model Tidak Tersedia'
        return data_klasifikasi_error

    data_klasifikasi = [dict(item) for item in data_umkm]
    
    # Siapkan data untuk diprediksi (hanya kolom 'jumlah_aset')
    aset_values = [item.get('jumlah_aset', 0) for item in data_klasifikasi]
    df_to_predict = pd.DataFrame(aset_values, columns=['jumlah_aset'])
    
    # Lakukan prediksi
    predictions = dt_model.predict(df_to_predict)
    
    # Tambahkan hasil prediksi ke setiap item UMKM
    for i, umkm in enumerate(data_klasifikasi):
        umkm['klasifikasi'] = predictions[i]
            
    return data_klasifikasi

# --- FUNGSI SAW (tetap sama seperti sebelumnya) ---
def hitung_saw(data_umkm_input, kriteria_saw_config):
    """ Menghitung skor SAW dan mengembalikan detail perhitungannya. """
    # (Isi fungsi hitung_saw tidak berubah dari versi terakhir, pastikan lengkap)
    if not data_umkm_input: return {'ranked_results': {}, 'decision_matrix': [], 'normalized_matrix': [], 'weights': [], 'umkm_processed_for_saw': [], 'criteria_details_saw': {}}
    valid_umkm_for_saw_values = []; umkm_processed_for_saw = []; kriteria_names_ordered = list(kriteria_saw_config.keys()); criteria_details_for_return = {}
    for k_name in kriteria_names_ordered: criteria_details_for_return[k_name] = {'bobot': kriteria_saw_config[k_name]['bobot'], 'tipe': kriteria_saw_config[k_name]['tipe'], 'deskripsi': kriteria_saw_config[k_name].get('deskripsi', k_name.replace('_', ' ').title())}
    for umkm_item in data_umkm_input:
        try:
            if not isinstance(umkm_item, dict) or 'id' not in umkm_item: continue
            current_values = [float(umkm_item[k_name]) for k_name in kriteria_names_ordered]
            valid_umkm_for_saw_values.append(current_values)
            umkm_processed_for_saw.append({'id': umkm_item['id'], 'nama_umkm': umkm_item.get('nama_umkm', str(umkm_item['id']))})
        except (KeyError, ValueError, TypeError) as e: print(f"Peringatan SAW: Data UMKM ID {umkm_item.get('id', 'N/A')} dilewati: {e}"); continue
    if not valid_umkm_for_saw_values: return {'ranked_results': {}, 'decision_matrix': [], 'normalized_matrix': [], 'weights': [kriteria_saw_config[k_name]['bobot'] for k_name in kriteria_names_ordered], 'umkm_processed_for_saw': [], 'criteria_details_saw': criteria_details_for_return}
    matriks_keputusan = np.array(valid_umkm_for_saw_values); matriks_normalisasi = np.copy(matriks_keputusan).astype(float)
    for j, k_name in enumerate(kriteria_names_ordered):
        k_info = kriteria_saw_config[k_name]; kolom = matriks_keputusan[:, j]
        if kolom.size == 0: matriks_normalisasi[:, j] = 0; continue
        if k_info['tipe'] == 'benefit': max_val = np.max(kolom); matriks_normalisasi[:, j] = kolom / max_val if max_val != 0 else 0
        elif k_info['tipe'] == 'cost':
            min_val = np.min(kolom)
            for i_row in range(matriks_normalisasi.shape[0]):
                if kolom[i_row] == 0: matriks_normalisasi[i_row, j] = 1.0
                else: matriks_normalisasi[i_row, j] = 0.0 if min_val == 0 else min_val / kolom[i_row]
    bobot_array = np.array([kriteria_saw_config[k_name]['bobot'] for k_name in kriteria_names_ordered])
    if not np.isclose(np.sum(bobot_array), 1.0): print(f"Peringatan: Total bobot SAW ({np.sum(bobot_array):.2f}) tidak sama dengan 1.")
    skor_akhir = np.dot(matriks_normalisasi, bobot_array); hasil_saw_list = []; ids_for_ranking = [umkm['id'] for umkm in umkm_processed_for_saw]
    for i_skor, id_u in enumerate(ids_for_ranking): hasil_saw_list.append({'id': id_u, 'nilai_total': skor_akhir[i_skor]})
    sorted_hasil_saw = sorted(hasil_saw_list, key=lambda x: x['nilai_total'], reverse=True); ranked_results_final = {}
    for rank, item_ranked in enumerate(sorted_hasil_saw): ranked_results_final[item_ranked['id']] = {'nilai_total': item_ranked['nilai_total'], 'ranking': rank + 1}
    return {'ranked_results': ranked_results_final, 'decision_matrix': matriks_keputusan.tolist(), 'normalized_matrix': matriks_normalisasi.tolist(), 'weights': bobot_array.tolist(), 'umkm_processed_for_saw': umkm_processed_for_saw, 'criteria_details_saw': criteria_details_for_return}