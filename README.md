# Kekuatan Militer Indonesia: Siap Menjaga Nusantara

Proyek open-source untuk merender video pendek sinematik 30 detik tentang TNI dalam format vertikal 9:16 (1080x1920, 30 fps). Seluruh visual utama dibuat secara generatif dengan Python/Pillow; audio narasi menggunakan eSpeak NG lokal; musik latar dibuat secara sintetis dengan FFmpeg. Tidak memerlukan API key, akun layanan AI berbayar, atau aset stok berbayar.

## Tujuan
Mengenalkan tiga matra TNI, kesiapsiagaan, modernisasi pertahanan, dan pentingnya menjaga wilayah kepulauan Indonesia melalui video edukasi singkat.

## Tools gratis
- Python 3.11
- Pillow untuk ilustrasi generatif
- FFmpeg/ffprobe untuk rendering, audio, dan pemeriksaan durasi
- eSpeak NG untuk text-to-speech lokal (voice Indonesia bila tersedia)
- GitHub Actions untuk render otomatis
- Font DejaVu Sans dari paket fonts-dejavu-core

## Render di GitHub
1. Buka tab **Actions** repository.
2. Pilih workflow **Render Video Nusantara**.
3. Tekan **Run workflow** pada branch `main`.
4. Tunggu sampai job selesai.
5. Unduh artifact **indonesia-military-video-1080x1920** dari halaman run. File MP4 juga dibuat di folder `output/` selama job berjalan.

Workflow otomatis berjalan saat ada push yang mengubah file proyek dan dapat dijalankan manual melalui workflow_dispatch.

## Render lokal
Pastikan Python 3.11+, FFmpeg, eSpeak NG, dan font DejaVu Sans tersedia. Lalu jalankan:

```bash
python -m pip install -r requirements.txt
python src/render_video.py
ffprobe -v error -show_entries format=duration -of default=nw=1 output/indonesia-military-video.mp4
```

Pada Ubuntu/Debian, dependensi sistem dapat dipasang dengan:
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg espeak-ng fonts-dejavu-core
```

Tidak ada API key yang diminta. Jika voice Indonesia tidak tersedia pada distribusi eSpeak NG tertentu, renderer mencoba voice fallback dan mencatat peringatan.

## Data dan ketepatan fakta
- Global Firepower, *2026 Indonesia Military Strength*: https://www.globalfirepower.com/country-military-strength-detail.php?country_id=indonesia
  - GFP mencantumkan peringkat 13 dari 145, estimasi 404.500 personel aktif, dan 338 total aset angkatan laut.
  - GFP menjelaskan bahwa sebagian angka adalah estimasi. Angka ini bukan statistik resmi TNI.
- UU No. 34 Tahun 2004 tentang TNI, Pasal 4: https://jdih.kemenkeu.go.id/api/download/fulltext/2004/34TAHUN2004UU.htm
  - Menyebut TNI terdiri atas Angkatan Darat, Angkatan Laut, dan Angkatan Udara.

Naskah menghindari klaim "kekuatan maritim terbesar di Asia Tenggara" karena perbandingan tersebut tidak dapat disimpulkan hanya dari angka total aset GFP. Kalimat narasi diganti dengan penyebutan jumlah aset yang diberi atribusi sumber. Visual kapal, pesawat, personel, radar, peta, dan monumen adalah ilustrasi generatif, bukan dokumentasi unit atau operasi nyata.

## Sumber dan lisensi aset
Tidak ada foto atau footage pihak ketiga yang dibundel. Ilustrasi dan musik latar dibuat oleh kode proyek saat render. Font DejaVu Sans berasal dari paket fonts-dejavu-core dan didistribusikan di bawah lisensi Bitstream Vera/DejaVu; lihat https://dejavu-fonts.github.io/License.html. eSpeak NG tersedia di https://github.com/espeak-ng/espeak-ng (GPL-3.0). FFmpeg tersedia di https://ffmpeg.org/ (lisensi bergantung pada build dan konfigurasi).

## Lisensi proyek
Kode proyek: MIT License. Lisensi ini tidak mengubah lisensi perangkat lunak sistem yang dipasang saat workflow berjalan.
