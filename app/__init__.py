from flask import Flask
import os
from .models import db

def create_app():
    app = Flask(__name__)
    # Baca SECRET_KEY dari environment variable untuk keamanan
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kunci-rahasia-default-untuk-lokal')

    # --- KONFIGURASI DATABASE UNTUK DEPLOYMENT & LOKAL ---
    # Baca URL database dari environment variable 'DATABASE_URI' yang akan kita set di Vercel
    db_uri = os.environ.get('DATABASE_URI')
    
    if not db_uri:
        # JIKA TIDAK DI-DEPLOY (menjalankan di komputer lokal):
        # Gunakan konfigurasi XAMPP/MySQL lokal sebagai fallback.
        print("PERINGATAN: DATABASE_URI tidak ditemukan, aplikasi menggunakan database lokal (XAMPP/MySQL).")
        db_user = "root"
        db_password = ""
        db_host = "localhost"
        db_name = "db_umkm_bantuan_flask" # Pastikan nama ini sesuai dengan DB lokal Anda
        # Ganti PyMySQL dengan psycopg2 jika Anda juga ingin tes Postgres di lokal,
        # tapi untuk XAMPP, PyMySQL masih relevan. Pastikan keduanya terinstal jika perlu.
        # Untuk deployment, kita akan menggunakan Postgres, jadi uri utama harus siap.
        # Untuk sekarang, kita fokus pada XAMPP untuk fallback lokal.
        db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ... sisa kode __init__.py Anda tetap sama ...
    upload_folder_path = os.path.join(os.path.dirname(app.root_path), 'uploads')
    if not os.path.exists(upload_folder_path):
        os.makedirs(upload_folder_path)
    app.config['UPLOAD_FOLDER'] = upload_folder_path

    from .routes import main_bp
    app.register_blueprint(main_bp)

    from . import filters
    filters.init_app(app)

    return app