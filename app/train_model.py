import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
import sys

# --- KONFIGURASI ---
NAMA_FILE_TRAINING = 'Data_Training_Klasifikasi_Aset.xlsx'
NAMA_FILE_MODEL = 'decision_tree_model.joblib'
# --------------------

print("📊 Memulai proses training model Decision Tree (C4.5-style)...\n")

# 1. Muat Data Training dari File Excel
try:
    print(f"📂 Membaca data dari '{NAMA_FILE_TRAINING}'...")
    df = pd.read_excel(NAMA_FILE_TRAINING)
except FileNotFoundError:
    print(f"❌ ERROR: File '{NAMA_FILE_TRAINING}' tidak ditemukan di folder utama proyek.")
    sys.exit()
except Exception as e:
    print(f"❌ ERROR: Gagal membaca file. Pastikan format Excel valid.\nDetail: {e}")
    sys.exit()

# 2. Validasi Kolom
required_columns = ['jumlah_aset', 'klasifikasi']
if not all(col in df.columns for col in required_columns):
    print(f"❌ ERROR: File harus memiliki kolom: {', '.join(required_columns)}")
    sys.exit()

print("✅ Data berhasil dimuat:")
print(df)

# 3. Siapkan Fitur (X) dan Label Target (y)
X = df[['jumlah_aset']]  # Data numerik (2D)
y = df['klasifikasi']    # Label klasifikasi: mikro/kecil/sedang

# 4. Inisialisasi dan Latih Model
model = DecisionTreeClassifier(criterion='entropy', random_state=42)  # C4.5-style
model.fit(X, y)

# 5. Simpan Model
joblib.dump(model, NAMA_FILE_MODEL)

print(f"\n✅ Model selesai dilatih dan disimpan sebagai: '{NAMA_FILE_MODEL}'")
