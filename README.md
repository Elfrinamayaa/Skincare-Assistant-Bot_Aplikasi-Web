# Skincare-Assistant-Bot_Aplikasi-Web
SkinTant assistant bot adalah chatbot berbasis rule-based dengan Python dan Flask yang dirancang untuk membantu pengguna memahami perawatan kulit, dalam chatbot ini terdapat informasi seputar jenis kulit, masalah wajah, kandungan skincare, dan rutinitas perawatan melalui pencocokan pertanyaan dan jawaban yang telah disiapkan dalam format JSON.

## Menjalankan
```bash
python -m venv venv
venv\Scripts\activate        # Windows (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Buka http://127.0.0.1:5000 lalu pilih **Skincare Assistant**.

## Perintah lain
| Perintah | Fungsi |
| --- | --- |
| `python cli.py --theme skincare --debug` | Chat lewat terminal |
| `python evaluate.py` | Hitung akurasi bot, hasil di `evaluasi/hasil_evaluasi.csv` |
| `pytest` | Jalankan semua tes |

## Struktur
- `app.py` - aplikasi Flask (halaman + REST API)
- `chatbot/` - mesin bot, riwayat chat (SQLite), pemuat tema
- `themes/` - knowledge bot dalam JSON (tambah file baru untuk tema baru)
- `templates/`, `static/` - tampilan web
- `evaluasi/` - data uji dan hasil evaluasi
- `tests/` - tes otomatis

## Menambah pengetahuan
Edit `themes/skincare.json`: tambahkan kalimat ke `patterns` atau buat intent baru
(`tag`, `patterns`, `responses`). Pertanyaan yang belum dikenali bisa dilihat di
`/admin/skincare`. Threshold kecocokan default 0,45 (ubah lewat variabel `THRESHOLD`).
