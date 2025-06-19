from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class CalculationSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    jumlah_umkm = db.Column(db.Integer, nullable=False)
    nama_file_sumber = db.Column(db.String(255), nullable=True)
    
    kriteria_config_json = db.Column(db.Text, nullable=True)
    saw_decision_matrix_json = db.Column(db.Text, nullable=True)
    saw_normalized_matrix_json = db.Column(db.Text, nullable=True)
    saw_umkm_processed_json = db.Column(db.Text, nullable=True)

    results = db.relationship('UMKMResult', backref='session', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<CalculationSession {self.id} - {self.timestamp}>'

class UMKMResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('calculation_session.id'), nullable=False)
    
    umkm_id_asli = db.Column(db.String(50))
    nama_umkm = db.Column(db.String(150), nullable=False)
    
    klasifikasi_aset = db.Column(db.String(50), nullable=True)
    nilai_saw = db.Column(db.Float, nullable=True)
    ranking_saw = db.Column(db.Integer, nullable=True)

    kriteria_values_json = db.Column(db.Text, nullable=False)

    def get_kriteria_values(self):
        try:
            return json.loads(self.kriteria_values_json)
        except json.JSONDecodeError:
            return {}