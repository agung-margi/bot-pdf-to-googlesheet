# 🤖 PDF Extractor Telegram Bot

Bot Telegram ini memungkinkan kamu mengirim file PDF dan mendapatkan data terstruktur hasil ekstraksi langsung melalui chat Telegram.

Cocok untuk laporan seperti:
- Laporan instalasi
- Dokumen permintaan pelanggan
- Formulir PDF lainnya

---

## 📦 Fitur

- 📥 Terima file PDF dari Telegram
- 🧾 Ekstrak data seperti:
  - STO
  - No Permintaan
  - Nama Pelanggan
  - Material
- 🔁 Kirim balik hasil parsing dalam format teks
- 🚀 Siap dikembangkan untuk integrasi ke Google Sheets, database, dll

---

## 🛠️ Tech Stack

- Python 3
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- PyMuPDF (`fitz`)
- requests

---

## 📂 Struktur Project

## Deskripsi File

* **bot/** (Directory)
    * **bot.py** (File)
        * The main Python script for the bot.
        * Handles bot logic and Telegram API interaction.
    * **requirements.txt** (File)
        * Lists Python dependencies for the bot.
        * Install with: `pip install -r requirements.txt`
    * **README.md** (File)
        * This file.
        * Provides project overview and file descriptions.
---


## 🚀 Cara Menjalankan


```bash
git clone https://github.com/username/pdf-bot.git](https://github.com/agung-margi/bot-pdf-to-googlesheet.git
cd pdf-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py


```

## ✨ Author

**Agung Margi**  
🌐 Website: [agungmargi.my.id](https://agungmargi.my.id)  
✉️ Email: agung.margyono@gmail.com  
🔗 LinkedIn: [linkedin.com/in/agungmargiyono](https://linkedin.com/in/agungmargiyono)


