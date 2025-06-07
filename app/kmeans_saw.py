import numpy as np
from sklearn.cluster import KMeans as SklearnKMeans
from sklearn.preprocessing import StandardScaler
# import json # Tidak perlu json di sini lagi

# ... (fungsi preprocess_data_for_kmeans dan hitung_kmeans tetap sama persis seperti sebelumnya) ...
def preprocess_data_for_kmeans(data_umkm, kriteria_keys):
    fitur_list = []
    valid_data_indices = [] 
    for idx, item in enumerate(data_umkm):
        try:
            current_features = [float(item[key]) for key in kriteria_keys]
            fitur_list.append(current_features)
            valid_data_indices.append(idx)
        except (KeyError, ValueError, TypeError) as e:
            print(f"Peringatan K-Means (preprocess): Data UMKM ID {item.get('id', 'N/A')} dilewati karena kriteria tidak lengkap/valid: {e}")
            continue
    if not fitur_list:
        return np.array([]), [], list(data_umkm)
    fitur_array = np.array(fitur_list)
    scaler = StandardScaler()
    fitur_scaled = scaler.fit_transform(fitur_array)
    return fitur_scaled, valid_data_indices, list(data_umkm)

def hitung_kmeans(data_umkm, n_clusters, kriteria_keys_ordered):
    if not data_umkm:
        return []
    if n_clusters <= 0:
        raise ValueError("Jumlah cluster harus lebih besar dari 0.")
    original_data_umkm_list = list(data_umkm)
    fitur_scaled, valid_indices, _ = preprocess_data_for_kmeans(original_data_umkm_list, kriteria_keys_ordered)
    data_umkm_clustered_result = [item.copy() for item in original_data_umkm_list]
    if fitur_scaled.shape[0] == 0:
        print("Peringatan K-Means: Tidak ada data valid untuk clustering.")
        for item in data_umkm_clustered_result:
            item['cluster'] = None
        return data_umkm_clustered_result
    labels = None
    if fitur_scaled.shape[0] < n_clusters:
        print(f"Peringatan K-Means: Jumlah data valid ({fitur_scaled.shape[0]}) lebih sedikit dari jumlah cluster ({n_clusters}). Semua data valid akan dimasukkan ke cluster 0.")
        labels = np.zeros(fitur_scaled.shape[0], dtype=int)
    else:
        try:
            kmeans_model = SklearnKMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            kmeans_model.fit(fitur_scaled)
            labels = kmeans_model.labels_
        except Exception as e:
            print(f"Error saat menjalankan K-Means: {e}")
            for original_idx_in_data_umkm in valid_indices:
                 data_umkm_clustered_result[original_idx_in_data_umkm]['cluster'] = None
            for idx, item in enumerate(data_umkm_clustered_result):
                if idx not in valid_indices:
                    item['cluster'] = None
            return data_umkm_clustered_result
    if labels is not None:
        for i_label, original_idx_in_data_umkm in enumerate(valid_indices):
            if i_label < len(labels):
                data_umkm_clustered_result[original_idx_in_data_umkm]['cluster'] = int(labels[i_label])
            else:
                data_umkm_clustered_result[original_idx_in_data_umkm]['cluster'] = None
    for idx, item in enumerate(data_umkm_clustered_result):
        if idx not in valid_indices:
            item['cluster'] = None
    return data_umkm_clustered_result

def hitung_saw(data_umkm_input, kriteria_saw_config): # Ganti nama argumen agar tidak bentrok
    """
    Menghitung skor SAW dan mengembalikan detail perhitungannya.
    """
    if not data_umkm_input: # Menggunakan nama argumen baru
        return {
            'ranked_results': {},
            'decision_matrix': np.array([]),
            'normalized_matrix': np.array([]),
            'weights': np.array([]),
            'umkm_processed_for_saw': [], # List of dicts {id, nama_umkm}
            'criteria_details_saw': {} # Dict {nama_krt: {bobot, tipe, deskripsi}}
        }

    valid_umkm_for_saw_values = [] # List of lists (nilai kriteria)
    umkm_processed_for_saw = [] # List of dicts {id, nama_umkm} untuk mapping
    kriteria_names_ordered = list(kriteria_saw_config.keys())
    
    # Buat dictionary detail kriteria untuk dikembalikan
    criteria_details_for_return = {}
    for k_name in kriteria_names_ordered:
        criteria_details_for_return[k_name] = {
            'bobot': kriteria_saw_config[k_name]['bobot'],
            'tipe': kriteria_saw_config[k_name]['tipe'],
            'deskripsi': kriteria_saw_config[k_name].get('deskripsi', k_name.replace('_', ' ').title()) # Ambil deskripsi
        }

    for umkm_item in data_umkm_input: # Menggunakan nama argumen baru
        try:
            if not isinstance(umkm_item, dict) or 'id' not in umkm_item:
                print(f"Peringatan SAW: Item data tidak valid atau tidak memiliki ID: {umkm_item}")
                continue
            current_values = [float(umkm_item[k_name]) for k_name in kriteria_names_ordered]
            valid_umkm_for_saw_values.append(current_values)
            umkm_processed_for_saw.append({'id': umkm_item['id'], 'nama_umkm': umkm_item.get('nama_umkm', str(umkm_item['id']))})
        except (KeyError, ValueError, TypeError) as e:
            print(f"Peringatan SAW: Data UMKM ID {umkm_item.get('id', 'N/A')} dilewati karena kriteria tidak lengkap/valid: {e}")
            continue

    if not valid_umkm_for_saw_values:
        print("Peringatan SAW: Tidak ada data valid untuk perhitungan SAW.")
        return {
            'ranked_results': {},
            'decision_matrix': np.array([]),
            'normalized_matrix': np.array([]),
            'weights': np.array([kriteria_saw_config[k_name]['bobot'] for k_name in kriteria_names_ordered]), # Kembalikan bobot meski tidak ada data
            'umkm_processed_for_saw': [],
            'criteria_details_saw': criteria_details_for_return
        }

    matriks_keputusan = np.array(valid_umkm_for_saw_values)
    matriks_normalisasi = np.copy(matriks_keputusan).astype(float)

    for j, k_name in enumerate(kriteria_names_ordered):
        k_info = kriteria_saw_config[k_name]
        kolom = matriks_keputusan[:, j]
        if kolom.size == 0:
            matriks_normalisasi[:, j] = 0
            continue
        if k_info['tipe'] == 'benefit':
            max_val = np.max(kolom)
            if max_val == 0:
                matriks_normalisasi[:, j] = 0
            else:
                matriks_normalisasi[:, j] = kolom / max_val
        elif k_info['tipe'] == 'cost':
            min_val = np.min(kolom)
            for i_row in range(matriks_normalisasi.shape[0]):
                if kolom[i_row] == 0:
                    matriks_normalisasi[i_row, j] = 1.0
                else:
                    if min_val == 0 :
                        matriks_normalisasi[i_row, j] = 0.0
                    else:
                        matriks_normalisasi[i_row, j] = min_val / kolom[i_row]

    bobot_array = np.array([kriteria_saw_config[k_name]['bobot'] for k_name in kriteria_names_ordered])
    if not np.isclose(np.sum(bobot_array), 1.0):
        print(f"Peringatan: Total bobot SAW ({np.sum(bobot_array):.2f}) tidak sama dengan 1.")

    skor_akhir = np.dot(matriks_normalisasi, bobot_array)
    hasil_saw_list = []
    ids_for_ranking = [umkm['id'] for umkm in umkm_processed_for_saw] # Ambil ID dari umkm_processed_for_saw
    
    for i_skor, id_u in enumerate(ids_for_ranking):
        hasil_saw_list.append({'id': id_u, 'nilai_total': skor_akhir[i_skor]})

    sorted_hasil_saw = sorted(hasil_saw_list, key=lambda x: x['nilai_total'], reverse=True)
    ranked_results_final = {}
    for rank, item_ranked in enumerate(sorted_hasil_saw):
        ranked_results_final[item_ranked['id']] = {
            'nilai_total': item_ranked['nilai_total'],
            'ranking': rank + 1
        }
    
    return {
        'ranked_results': ranked_results_final,
        'decision_matrix': matriks_keputusan.tolist(), # Ubah ke list agar mudah di-JSON atau di-pass ke template
        'normalized_matrix': matriks_normalisasi.tolist(), # Ubah ke list
        'weights': bobot_array.tolist(), # Ubah ke list
        'umkm_processed_for_saw': umkm_processed_for_saw, # List of dicts {id, nama_umkm}
        'criteria_details_saw': criteria_details_for_return # Detail kriteria yang digunakan
    }