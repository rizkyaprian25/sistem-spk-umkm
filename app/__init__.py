from flask import Flask
import os
from .models import db 

def create_app():
    app = Flask(__name__)
    # Ganti dengan kunci rahasia unik Anda jika perlu
    app.config['SECRET_KEY'] = 'c9e8f7a1b2d3c4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a1b2c3d4e5f6a7b8c9d0e1'

    # --- MODIFIKASI KONFIGURASI DATABASE DI SINI ---
    # Komentari atau hapus konfigurasi SQLite lama:
    # project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(project_dir, 'site.db')

    # Konfigurasi baru untuk MySQL/MariaDB via XAMPP (menggunakan PyMySQL)
    db_user = "root"  # User default XAMPP MySQL
    db_password = ""  # Password default XAMPP MySQL biasanya kosong. Jika Anda sudah set password, ganti di sini.
    db_host = "localhost" # atau "127.0.0.1"
    db_name = "db_umkm_bantuan_flask" # GANTI DENGAN NAMA DATABASE YANG ANDA BUAT DI LANGKAH 2

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    # --- AKHIR MODIFIKASI KONFIGURASI DATABASE ---

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app) # Inisialisasi SQLAlchemy dengan aplikasi

    # Baris ini akan membuat semua tabel (dari models.py) di database MySQL Anda
    # saat aplikasi pertama kali dijalankan dengan konteks aplikasi yang benar.
    with app.app_context():
        db.create_all() 

    # ... (sisa konfigurasi __init__.py seperti folder uploads, blueprint, filters) ...
    upload_folder_path = os.path.join(os.path.dirname(app.root_path), 'uploads')
    if not os.path.exists(upload_folder_path):
        os.makedirs(upload_folder_path)
    app.config['UPLOAD_FOLDER'] = upload_folder_path

    from .routes import main_bp
    app.register_blueprint(main_bp)

    from . import filters
    filters.init_app(app)

    return app