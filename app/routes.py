from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime


# --- PERUBAHAN DI BARIS INI ---
from .processing import klasifikasi_berdasarkan_aset, hitung_saw # Mengimpor dari file processing.py
# -----------------------------

from .models import db, CalculationSession, UMKMResult

main_bp = Blueprint('main', __name__)

data_umkm_global = []
nama_file_excel_global = None

KRITERIA_SAW_CONFIG = {
    'pendapatan_bulanan': {'bobot': 0.20, 'tipe': 'benefit', 'deskripsi': 'Pendapatan Bulanan (Rp)'},
    'jumlah_tenaga_kerja': {'bobot': 0.15, 'tipe': 'benefit', 'deskripsi': 'Jumlah Tenaga Kerja'},
    'lama_usaha_tahun': {'bobot': 0.10, 'tipe': 'benefit', 'deskripsi': 'Lama Usaha (Tahun)'},
    'jumlah_aset': {'bobot': 0.10, 'tipe': 'benefit', 'deskripsi': 'Jumlah Aset (Rp)'},
    'skor_klasifikasi': {'bobot': 0.25, 'tipe': 'benefit', 'deskripsi': 'Skor Skala Usaha (Aset)'}
}
KRITERIA_KEYS_ORDERED = list(KRITERIA_SAW_CONFIG.keys())

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    return render_template('index.html',
                        jumlah_data=len(data_umkm_global),
                        nama_file_excel=nama_file_excel_global,
                        kriteria_info=KRITERIA_SAW_CONFIG)

@main_bp.route('/input_data', methods=['GET', 'POST'])
def input_data():
    global data_umkm_global, nama_file_excel_global
    if request.method == 'POST':
        if 'submit_manual' in request.form:
            try:
                next_index = len(data_umkm_global) + 1
                new_id_prefix = "manual_"
                if nama_file_excel_global is not None:
                    new_id_prefix = "excel_"
                generated_id = f"{new_id_prefix}{next_index}"
                umkm_baru = {'id': generated_id, 'nama_umkm': request.form['nama_umkm']}
                
                # Loop hanya melalui kriteria yang diinput pengguna
                input_keys = [k for k in KRITERIA_KEYS_ORDERED if k != 'skor_klasifikasi']
                for key in input_keys:
                    form_value = request.form.get(key)
                    if form_value is None or form_value.strip() == "":
                        flash(f'Kriteria "{KRITERIA_SAW_CONFIG[key]["deskripsi"]}" harus diisi.', 'danger')
                        return render_template('input_data.html', data_umkm=data_umkm_global, kriteria_config=KRITERIA_SAW_CONFIG, kriteria_keys_ordered=KRITERIA_KEYS_ORDERED, nama_file_excel=nama_file_excel_global)
                    try:
                        umkm_baru[key] = float(form_value)
                    except ValueError:
                        flash(f'Nilai untuk "{KRITERIA_SAW_CONFIG[key]["deskripsi"]}" harus berupa angka.', 'danger')
                        return render_template('input_data.html', data_umkm=data_umkm_global, kriteria_config=KRITERIA_SAW_CONFIG, kriteria_keys_ordered=KRITERIA_KEYS_ORDERED, nama_file_excel=nama_file_excel_global)
                data_umkm_global.append(umkm_baru)
                flash(f'Data UMKM (ID: {generated_id}) berhasil ditambahkan ke sesi saat ini!', 'success')
            except Exception as e:
                flash(f'Terjadi kesalahan saat menambahkan data manual: {str(e)}', 'danger')
        
        elif 'file_excel' in request.files:
            file = request.files['file_excel']
            if file.filename == '':
                flash('Tidak ada file dipilih untuk diunggah.', 'warning')
            elif file and allowed_file(file.filename):
                filepath = None
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    df = pd.read_excel(filepath)
                    df = df.dropna(how='all')
                    if 'lama_usaha_tahun' in df.columns:
                        df['lama_usaha_tahun'] = pd.to_numeric(df['lama_usaha_tahun'], errors='coerce')
                    
                    excel_keys = [k for k in KRITERIA_KEYS_ORDERED if k != 'skor_klasifikasi']
                    missing_cols = [col for col in ['nama_umkm'] + excel_keys if col not in df.columns]
                    if missing_cols:
                        flash(f"Kolom berikut tidak ditemukan di file Excel: {', '.join(missing_cols)}.", "danger")
                        return redirect(url_for('main.input_data'))
                    
                    data_umkm_excel = []
                    for index, row in df.iterrows():
                        item = {'id': f"excel_{index + 1}", 'nama_umkm': str(row.get('nama_umkm', f'Tanpa Nama Baris {index+2}'))}
                        valid_row = True
                        for key in excel_keys:
                            try:
                                if pd.isna(row[key]):
                                    flash(f"Data kosong/tidak valid di baris {index + 2}, kolom '{KRITERIA_SAW_CONFIG[key]['deskripsi']}'.", "danger")
                                    valid_row = False
                                    break
                                item[key] = float(row[key])
                            except (ValueError, TypeError, KeyError) as e:
                                flash(f"Data tidak valid di baris {index + 2}, kolom '{key}'. Error: {e}.", "danger")
                                valid_row = False
                                break
                        if valid_row:
                            data_umkm_excel.append(item)
                        else:
                            return redirect(url_for('main.input_data'))
                    
                    data_umkm_global = data_umkm_excel
                    nama_file_excel_global = filename
                    flash(f'File "{filename}" berhasil diunggah. {len(data_umkm_global)} data diproses.', 'success')
                except Exception as e:
                    flash(f'Gagal memproses file Excel: {str(e)}', 'danger')
            else:
                flash('Format file tidak diizinkan. Hanya .xlsx atau .xls.', 'danger')
        
        return redirect(url_for('main.input_data'))

    return render_template('input_data.html',
                           data_umkm=data_umkm_global,
                           kriteria_config=KRITERIA_SAW_CONFIG,
                           kriteria_keys_ordered=KRITERIA_KEYS_ORDERED)

@main_bp.route('/delete_session_umkm/<item_id>', methods=['POST'])
def delete_session_umkm(item_id):
    global data_umkm_global, nama_file_excel_global
    item_dihapus = None
    for i, item in enumerate(data_umkm_global):
        if str(item.get('id')) == str(item_id):
            item_dihapus = data_umkm_global.pop(i)
            break
    if item_dihapus:
        flash(f"Data UMKM '{item_dihapus.get('nama_umkm', item_id)}' berhasil dihapus dari sesi.", 'success')
        if not data_umkm_global:
            nama_file_excel_global = None
            flash('Semua data UMKM dalam sesi telah dihapus.', 'info')
    else:
        flash(f"Data UMKM dengan ID '{item_id}' tidak ditemukan.", 'warning')
    return redirect(url_for('main.input_data'))


@main_bp.route('/proses', methods=['POST'])
def proses_data():
    if not data_umkm_global:
        flash('Tidak ada data UMKM untuk diproses.', 'warning')
        return redirect(url_for('main.input_data'))
    
    try:
        data_setelah_klasifikasi = klasifikasi_berdasarkan_aset(data_umkm_global)
        
        klasifikasi_score_map = {'Mikro': 3, 'Kecil': 2, 'Sedang': 1}
        for umkm in data_setelah_klasifikasi:
            klasifikasi_label = umkm.get('klasifikasi', 'Sedang')
            umkm['skor_klasifikasi'] = klasifikasi_score_map.get(klasifikasi_label, 1)

        saw_calculation_details = hitung_saw(data_setelah_klasifikasi, KRITERIA_SAW_CONFIG)
        hasil_saw_dict = saw_calculation_details['ranked_results']
        
        # 👇 Tambahan: Hitung nilai SAW akhir per baris
        weights = [v['bobot'] for v in KRITERIA_SAW_CONFIG.values()]
        saw_calculation_details['weights'] = weights  # Untuk keperluan tampilan jika perlu
        
        nilai_saw_akhir = []
        for row_norm in saw_calculation_details.get('normalized_matrix', []):
            nilai_total = sum([float(r) * float(w) for r, w in zip(row_norm, weights)])
            nilai_saw_akhir.append(round(nilai_total, 4))
            
        saw_calculation_details['nilai_saw_akhir'] = nilai_saw_akhir
        
        # Tambahkan langsung ke tiap data UMKM agar bisa diakses mudah dari template
        for i, umkm in enumerate(saw_calculation_details['umkm_processed_for_saw']):
            umkm['nilai_saw_akhir'] = nilai_saw_akhir[i]
        
        hasil_akhir_list = []
        for umkm_data in data_setelah_klasifikasi:
            umkm_id = umkm_data.get('id')
            if umkm_id is None: continue
            
            final_umkm_data = umkm_data.copy()
            if umkm_id in hasil_saw_dict:
                final_umkm_data['nilai_saw'] = hasil_saw_dict[umkm_id]['nilai_total']
                final_umkm_data['ranking_saw'] = hasil_saw_dict[umkm_id]['ranking']
            else:
                final_umkm_data['nilai_saw'] = None
                final_umkm_data['ranking_saw'] = None
            
            hasil_akhir_list.append(final_umkm_data)
        
        hasil_akhir_sorted = sorted(
            hasil_akhir_list,
            key=lambda x: (x.get('ranking_saw') if isinstance(x.get('ranking_saw'), int) else float('inf'))
        )
        
        try:
            new_session = CalculationSession(
                timestamp=datetime.utcnow(),
                jumlah_umkm=len(hasil_akhir_sorted),
                nama_file_sumber=nama_file_excel_global,
                kriteria_config_json=json.dumps(KRITERIA_SAW_CONFIG),
                saw_decision_matrix_json=json.dumps(saw_calculation_details.get('decision_matrix', [])),
                saw_normalized_matrix_json=json.dumps(saw_calculation_details.get('normalized_matrix', [])),
                saw_umkm_processed_json=json.dumps(saw_calculation_details.get('umkm_processed_for_saw', []))
            )
            db.session.add(new_session)
            db.session.flush()

            for umkm_result_data in hasil_akhir_sorted:
                kriteria_values_original = {key: umkm_result_data.get(key) for key in KRITERIA_KEYS_ORDERED}
                umkm_db_entry = UMKMResult(
                    session_id=new_session.id,
                    umkm_id_asli=str(umkm_result_data.get('id', '')),
                    nama_umkm=str(umkm_result_data.get('nama_umkm', 'Tanpa Nama')),
                    klasifikasi_aset=umkm_result_data.get('klasifikasi', 'N/A'),
                    nilai_saw=umkm_result_data.get('nilai_saw'),
                    ranking_saw=umkm_result_data.get('ranking_saw'),
                    kriteria_values_json=json.dumps(kriteria_values_original)
                )
                db.session.add(umkm_db_entry)
            
            db.session.commit()
            flash(f'Hasil perhitungan berhasil diproses dan disimpan ke riwayat (ID Sesi: {new_session.id}).', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menyimpan hasil ke database: {str(e)}', 'danger')
            print(f"Database save error: {type(e).__name__} - {e}")
        
        return render_template('hasil.html',
                            hasil_prioritas=hasil_akhir_sorted,
                            kriteria_saw_config=KRITERIA_SAW_CONFIG,
                            kriteria_keys_ordered=KRITERIA_KEYS_ORDERED,
                            nama_file_excel=nama_file_excel_global,
                            saw_details=saw_calculation_details
                           )
    except Exception as e:
        flash(f'Terjadi kesalahan umum saat pemrosesan: {str(e)}', 'danger')
        print(f"Error saat proses_data: {type(e).__name__} - {e}")
        return redirect(url_for('main.input_data'))


@main_bp.route('/history/<int:session_id>')
def history_detail(session_id):
    session = CalculationSession.query.get_or_404(session_id)
    all_results = UMKMResult.query.filter_by(session_id=session.id).all()
    results_sorted = sorted(all_results, key=lambda x: (x.ranking_saw if isinstance(x.ranking_saw, int) else float('inf')))
    
    saw_details_history = None
    kriteria_config_sesi = KRITERIA_SAW_CONFIG
    kriteria_keys_sesi = KRITERIA_KEYS_ORDERED
    
    try:
        if session.kriteria_config_json:
            kriteria_config_sesi = json.loads(session.kriteria_config_json)
            kriteria_keys_sesi = list(kriteria_config_sesi.keys())
        
        if session.saw_decision_matrix_json and session.saw_normalized_matrix_json and session.saw_umkm_processed_json:
            saw_details_history = {
                'decision_matrix': json.loads(session.saw_decision_matrix_json),
                'normalized_matrix': json.loads(session.saw_normalized_matrix_json),
                'umkm_processed_for_saw': json.loads(session.saw_umkm_processed_json),
                'criteria_details_saw': kriteria_config_sesi,
                'weights': [k_info.get('bobot', 0) for k_info in kriteria_config_sesi.values()]
            }
            
            # Hitung nilai akhir SAW dari data normalisasi dan bobot
            try:
                nilai_saw_akhir = []
                for row_norm in saw_details_history['normalized_matrix']:
                    nilai_total = sum(float(r) * float(w) for r, w in zip(row_norm, saw_details_history['weights']))
                    nilai_saw_akhir.append(round(nilai_total, 4))
                saw_details_history['nilai_saw_akhir'] = nilai_saw_akhir
            except Exception as e:
                saw_details_history['nilai_saw_akhir'] = []

    except json.JSONDecodeError:
        flash('Gagal memuat detail dari riwayat.', 'warning')
        saw_details_history = None

    return render_template('history_detail.html',
                           session=session,
                           results=results_sorted,
                           kriteria_saw_config_sesi=kriteria_config_sesi,
                           kriteria_keys_ordered_sesi=kriteria_keys_sesi,
                           saw_details_history=saw_details_history
                          )

@main_bp.route('/reset_data', methods=['POST'])
def reset_data():
    global data_umkm_global, nama_file_excel_global
    data_umkm_global = []
    nama_file_excel_global = None
    flash('Data sesi sementara telah direset.', 'info')
    return redirect(url_for('main.input_data'))

@main_bp.route('/history')
def history_list():
    page = request.args.get('page', 1, type=int)
    sessions = CalculationSession.query.order_by(CalculationSession.timestamp.desc()).paginate(page=page, per_page=10)
    return render_template('history_list.html', sessions=sessions)

@main_bp.route('/history/delete/<int:session_id>', methods=['POST'])
def delete_history_session(session_id):
    session_to_delete = CalculationSession.query.get_or_404(session_id)
    try:
        db.session.delete(session_to_delete)
        db.session.commit()
        flash(f'Sesi riwayat ID {session_id} berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus sesi riwayat: {str(e)}', 'danger')
    return redirect(url_for('main.history_list'))

@main_bp.app_context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}