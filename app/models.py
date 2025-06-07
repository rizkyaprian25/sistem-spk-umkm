from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class CalculationSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    jumlah_umkm = db.Column(db.Integer, nullable=False)
    jumlah_cluster_digunakan = db.Column(db.Integer, nullable=False)
    nama_file_sumber = db.Column(db.String(255), nullable=True)
    kriteria_config_json = db.Column(db.Text, nullable=True) # Menyimpan kriteria & bobot global

    # --- KOLOM BARU UNTUK DETAIL SAW ---
    saw_decision_matrix_json = db.Column(db.Text, nullable=True)    # Matriks keputusan (data awal)
    saw_normalized_matrix_json = db.Column(db.Text, nullable=True) # Matriks normalisasi
    saw_umkm_processed_json = db.Column(db.Text, nullable=True)     # Info UMKM yg diproses SAW (ID, nama)
    # Bobot dan detail kriteria (nama, tipe) sudah tercakup dalam kriteria_config_json
    # atau bisa direkonstruksi dari sana jika diperlukan secara terpisah.
    # --- AKHIR KOLOM BARU ---

    results = db.relationship('UMKMResult', backref='session', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<CalculationSession {self.id} - {self.timestamp}>'

class UMKMResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('calculation_session.id'), nullable=False)
    
    umkm_id_asli = db.Column(db.String(50))
    nama_umkm = db.Column(db.String(150), nullable=False)
    kriteria_values_json = db.Column(db.Text, nullable=False) # Nilai kriteria asli UMKM ini

    cluster_kmeans = db.Column(db.Integer, nullable=True)
    nilai_saw = db.Column(db.Float, nullable=True)
    ranking_saw = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<UMKMResult {self.id} - {self.nama_umkm} for Session {self.session_id}>'

    def get_kriteria_values(self):
        try:
            return json.loads(self.kriteria_values_json)
        except json.JSONDecodeError:
            return {}