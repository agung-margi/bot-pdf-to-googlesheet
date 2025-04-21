# 🤖 PDF Extractor Telegram Bot

This Telegram bot allows you to send PDF files and receive structured extracted data directly through Telegram chat.

It is suitable for reports such as:
- Installation reports
- Customer request documents
- Other PDF forms

---

## 📦 Features

- 📥 Receive PDF files from Telegram
- 🧾 Extract data such as:
  - STO
  - Request Number
  - Customer Name
  - Material
- 🔁 Send back the parsed results in text format
- 🚀 Ready to be extended for integration with Google Sheets, databases, etc.

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


