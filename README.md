# SPK-Penilaian-Senstivitas-Pada-Bahan-Retinoid# SPK — Sistem Pendukung Keputusan (TOPSIS & Profile Matching)

Aplikasi web berbasis Flask untuk membantu perankingan alternatif menggunakan dua metode populer:
- TOPSIS
- Profile Matching (PM)

UI memakai Bootstrap 5 dan visualisasi memakai Plotly (via CDN). Data kriteria, alternatif, serta hasil perhitungan disimpan ke file lokal [spk_data.json](spk_data.json).

## Fitur
- Kelola kriteria: kode, nama, atribut (`benefit`/`cost`), tambah & hapus.
- Kelola alternatif: ubah nama dan nilai per kriteria; tambah & hapus baris.
- Hitung TOPSIS: atur bobot dan atribut per kriteria; hasil ranking + grafik.
- Hitung Profile Matching: atur target dan bobot; hasil ranking + grafik.
- Perbandingan hasil PM vs TOPSIS: tabel, grafik peringkat, dan grafik skor.
- Persistensi otomatis ke [spk_data.json](spk_data.json) + tombol Reset ke data contoh (A1–A5).

## Prasyarat
- Windows dengan Python 3.8 atau lebih baru (disarankan 3.8 sesuai task VS Code).
- Koneksi internet untuk memuat Bootstrap & Plotly dari CDN.

## Instalasi & Menjalankan
Pilih salah satu cara di bawah.

### 1) Cepat (tanpa virtualenv)
```powershell
# Masuk ke folder proyek
cd C:\Users\abner\Documents\SPK

# Install dependensi minimal
py -3.8 -m pip install --upgrade pip
py -3.8 -m pip install -r requirements.txt

# Jalankan aplikasi
py -3.8 app.py
```
Akses: http://localhost:8000

### 2) Virtualenv (disarankan)
```powershell
cd C:\Users\abner\Documents\SPK
py -3.8 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### 3) Conda (alternatif)
```powershell
cd C:\Users\abner\Documents\SPK
# Buat environment lokal di folder .conda (sesuai task yang tersedia)
C:\Users\miniforge3\Scripts\conda.exe create -p .\.conda python=3.8 -y
C:\Users\miniforge3\Scripts\conda.exe run -p .\.conda pip install -r requirements.txt
C:\Users\miniforge3\Scripts\conda.exe run -p .\.conda python app.py
```

### 4) Jalankan via VS Code Task
Di workspace ini sudah tersedia task:
- Run SPK (py 3.8)
- Run SPK (Conda)

Cara menjalankan:
- Buka Command Palette → “Tasks: Run Task” → pilih salah satu task di atas.

## Struktur Proyek
- [app.py](app.py): aplikasi Flask (router, algoritma, dan template in-memory)
- [spk_data.json](spk_data.json): penyimpanan data persisten (dibuat/diupdate otomatis)
- [readme.md](readme.md): dokumentasi proyek ini
- [requirements.txt](requirements.txt): daftar dependensi Python

## Cara Pakai Singkat
1) Buka halaman utama (Menu “Data”): kelola kriteria dan alternatif.
2) Menu “Profile Matching”: isi Target & Bobot lalu klik “Hitung Profile Matching”.
3) Menu “TOPSIS”: isi Bobot & Atribut (benefit/cost) lalu klik “Hitung TOPSIS”.
4) Menu “Perbandingan”: lihat tabel dan grafik perbandingan hasil PM vs TOPSIS.
5) Tombol “Reset Default” mengembalikan data ke contoh A1–A5.

## Endpoint Penting
- `/` → Data Kriteria & Alternatif
- `/ profile-matching` → Perhitungan Profile Matching
- `/topsis` → Perhitungan TOPSIS
- `/comparison` → Perbandingan hasil PM vs TOPSIS
- `/health` → Kesehatan aplikasi (OK)

## Catatan Teknis
- Server berjalan di port 8000. Ubah port pada bagian akhir [app.py](app.py) bila perlu:
  ```python
  app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
  ```
- Jika ingin reset total (termasuk file), Anda dapat menghapus [spk_data.json](spk_data.json) saat aplikasi dalam keadaan mati.
- Plotly & Bootstrap dimuat via CDN; pastikan koneksi internet aktif.

## Dibuat Oleh

- 452321002  Abner Boas P.P Gultom
- 4523210062 Mesak Mychart E. Purba
- 4523210122 Khalissa Raihanah Azhari

