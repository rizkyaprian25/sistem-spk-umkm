from babel.dates import format_datetime

def datetimeformat(value, format='medium'):
    if not value: # Handle jika value (misalnya session.timestamp) adalah None
        return "" # Kembalikan string kosong atau teks placeholder
    if format == 'full':
        format="EEEE, d MMMM y 'pukul' HH:mm"
    elif format == 'medium':
        format="EE, dd MMM y HH:mm"
    try:
        return format_datetime(value, format, locale='id_ID')
    except Exception as e: # Tangkap error jika format gagal
        print(f"Error formatting date: {e}, value: {value}")
        return str(value) # Kembalikan nilai asli jika gagal format

# --- FILTER BARU UNTUK FORMAT ANGKA ---
def format_number(value):
    if value is None:
        return "N/A" # Atau string kosong "" sesuai preferensi
    try:
        # Coba konversi ke float dulu untuk menangani angka yang mungkin masih string
        num = float(value)
        # Cek apakah angka tersebut sebenarnya adalah integer (misal 3.0 akan menjadi 3)
        if num == int(num):
            return int(num) # Kembalikan sebagai integer (tanpa .0)
        else:
            # Jika desimal, kembalikan apa adanya (Python float akan menampilkan desimalnya)
            # Contoh: 2.5 akan tetap 2.5; 0.8000 akan menjadi 0.8
            return num
    except (ValueError, TypeError):
        # Jika tidak bisa diubah jadi angka, kembalikan nilai aslinya
        return value
# --- AKHIR FILTER BARU ---

def init_app(app):
    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.filters['format_number'] = format_number # Daftarkan filter baru