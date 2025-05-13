from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
import re
import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters



load_dotenv()  # Load dari .env ke environment variable

# Ganti dengan token bot Telegram kamu
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Ganti dengan URL Web App Google Apps Script kamu
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    "👋 *Halo! Saya BOT Report BA UT TA Bekasi.*\n\n"
    "📄 *Silakan kirim file PDF laporan instalasi untuk disimpan.*\n\n"
    "🔁 Untuk *memperbarui data* yang sudah ada, gunakan perintah:\n"
    "/update\n\n"
    "🔍 Untuk *melihat data* berdasarkan _No Permintaan_, gunakan:\n"
    "/cekdata <No Permintaan>",
    parse_mode='Markdown'
)


async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    operation = context.user_data.get('operation', 'insert') 
    # Menyimpan file PDF yang dikirimkan
    file = await update.message.document.get_file()
    file_path = f"{file.file_unique_id}.pdf"
    await file.download_to_drive(file_path)

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    # Proses PDF untuk ekstrak data
    data = process_pdf_bytes(pdf_bytes)

    # 🔒 Validasi wajib: No Permintaan harus ada
    if not data["No Permintaan"] or data["No Permintaan"] == "-":
        await update.message.reply_text(
        "❌ Gagal memproses file.\n\n*No Permintaan tidak ditemukan* di dalam file PDF.\n"
        "Pastikan format file sudah benar dan terbaca.",
        parse_mode='Markdown'
        )
        os.remove(file_path)
        context.user_data.pop('operation', None)
        return

    # Periksa keberadaan data jika operasi adalah 'insert'
    if operation == 'insert':
        existing_data = get_nopermintaan(data["No Permintaan"])
        if isinstance(existing_data, str) and "Data No Permintaan" in existing_data:
            await update.message.reply_text(
                f"⚠️ No Permintaan {data['No Permintaan']} sudah ada.\n"
                f"Silakan gunakan perintah /update untuk memperbarui data."
            )
            os.remove(file_path)
            context.user_data.pop('operation', None)
            return

    # Kirim data ke Database
    user_info = update.effective_user
    response = send_to_gsheet(data, user_info, operation)
    
    # Kirim respons ke pengguna Telegram
    if response["status"] == "success":
        await update.message.reply_text("✅ " + response["message"])
    else:
        await update.message.reply_text("❌ " + response["message"])

    # Format dan kirim hasil parsing ke Telegram
    formatted_data = format_output(data)
    await update.message.reply_text(formatted_data)

    # Hapus file PDF sementara
    os.remove(file_path)

    # Hapus operasi dari user_data setelah selesai
    context.user_data.pop('operation', None)

# Fungsi untuk menangani perintah /insert
async def insert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['operation'] = 'insert'
    await update.message.reply_text("Silakan kirim file PDF untuk di-*insert*.",
    parse_mode='Markdown'
    )

# Fungsi untuk menangani perintah /update
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['operation'] = 'update'
    await update.message.reply_text(
        "Silakan kirim file PDF untuk di-*update*.",
        parse_mode='Markdown'
    )

# Fungsi untuk memproses data PDF
def process_pdf_bytes(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    # Ekstrak No Permintaan secara multiline
    no_permintaan_match = re.search(r'No Permintaan\s*:\s*((?:.*\n)+?)No Telepon', full_text)
    no_permintaan = no_permintaan_match.group(1).replace("\n", "").strip() if no_permintaan_match else "-"

    # Ekstrak data utama
    data = {
        "STO": re.search(r'STO\s*:\s*([^\n]+)', full_text),
        "No Permintaan": no_permintaan,
        "No Telepon": re.search(r'No Telepon\s*:\s*([^\n]+)', full_text),
        "No Inet": re.search(r'No Inet\s*:\s*([^\n]+)', full_text),
        "Tanggal WO": re.search(r'Tanggal WO\s*:\s*([^\n]+)', full_text),
        "Tanggal Transaksi": re.search(r'Tanggal Transaksi\s*:\s*([^\n]+)', full_text),
        "Nama Pelanggan": re.search(r'Nama Pelanggan\s*:\s*([^\n]+)', full_text),
        "No Kontak": re.search(r'No Kontak\s*:\s*([^\n]+)', full_text),
        "RK/MSAN/ODC": re.search(r'RK/MSAN/ODC\s*:\s*([^\n]+)', full_text),
        "DP/ODP": re.search(r'DP/ODP\s*:\s*([^\n]+)', full_text),
        "SN ONT": re.search(r'SN ONT\s*:\s*([^\n]+)', full_text),
        "SN PLC": re.search(r'SN PLC\s*:\s*([^\n]+)', full_text),
        "SN WIFI EXT": re.search(r'SN WIFI EXT\s*:\s*([^\n]+)', full_text),
        "STB ID": re.search(r'STB ID\s*:\s*([^\n]+)', full_text),
        "Nama/Notel Teknisi": re.search(r'Nama\s*/\s*Notel\s*Teknisi\s*:\s*([^\n]+)', full_text),
        "Nama Mitra": re.search(r'Nama Mitra\s*:\s*([^\n]+)', full_text),
    }

    # Bersihkan hasil regex
    for key in data.keys():
        if data[key] is not None and key != "No Permintaan":
            data[key] = data[key].group(1).strip()
        elif key != "No Permintaan":
            data[key] = "-"

    # Regex untuk material dengan semua satuan umum
    material_pattern = re.findall(r'([A-Za-z0-9\-\./]+)\s*:\s*(\d+)\s*(Pcs|Meter|Batang|Unit|Roll|Buah)', full_text, re.IGNORECASE)
    materials = []
    for name, qty, unit in material_pattern:
        clean_name = name.replace("\n", " ").strip()
        materials.append({
            "Nama Material": clean_name,
            "Jumlah": qty,
            "Satuan": unit
        })

    # Koreksi nama material jika typo
    corrections = {
        "LAMP-HOOK": "CLAMP-HOOK",
        # Tambah entri lain jika perlu
    }

    for material in materials:
        name = material["Nama Material"]
        material["Nama Material"] = corrections.get(name.upper(), name)

    data["Materials"] = materials

    # Ambil layanan aktif (dengan checkbox ☑)
    layanan_pattern = re.findall(r'☑\s*(.*)', full_text)
    data["Layanan"] = ", ".join(layanan_pattern) if layanan_pattern else "-"
    
    layanan_parts = [part.strip() for part in data["Layanan"].split(",")]
    if len(layanan_parts) == 2:
        data["Layanan"] = layanan_parts[0]
        data["Speed"] = layanan_parts[1]
    else:
        data["Speed"] = "-"

    # Format layanan dengan “+” untuk jadi bentuk terstruktur
    data["Layanan"] = " / ".join([
        f"{seg.split()[0]} [{ ' '.join(seg.split()[1:]) }]" if "+" in seg else seg
        for seg in data["Layanan"].split(" / ")
    ])

    return data


# Fungsi untuk mengirimkan data ke Database
def send_to_gsheet(data, user, operation):
    payload = {
        **data,
        "telegram_id": user.id,
        "username": user.username,
        "fullname": user.full_name,
        "operation": operation
    }

    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print(f"✅ {result.get('message')}")
                return {"status": "success", "message": result.get("message")}
            else:
                print(f"❌ {result.get('message')}")
                return {"status": "error", "message": result.get("message")}
        else:
            print("❌ Gagal kirim ke Sheets:", response.text)
            return {"status": "error", "message": "Gagal mengirim data ke database."}
    except Exception as e:
        print("❌ Error:", e)
        return {"status": "error", "message": f"Terjadi kesalahan: {e}"}

# Fungsi untuk memformat output data
def format_output(data):
    result = ["*Data berhasil diterima :*"]
    keys_order = [
        "STO", "No Permintaan", "No Telepon", "No Inet", "Tanggal WO", "Tanggal Transaksi",
        "Nama Pelanggan", "No Kontak", "RK/MSAN/ODC", "DP/ODP", "SN ONT", "SN PLC",
        "SN WIFI EXT", "STB ID", "Nama/Notel Teknisi", "Nama Mitra", "Layanan", "Speed"
    ]

    for key in keys_order:
        result.append(f"{key}: {data.get(key, '-')}")

    result.append("\nMaterial:")
    for m in data.get("Materials", []):
        result.append(f"{m['Nama Material']} : {m['Jumlah']}")

    return "\n".join(result)

# cek nopermintaan
def get_nopermintaan(no_permintaan):
    url = GOOGLE_SCRIPT_URL
    response = requests.get(url, params={'noPermintaan': no_permintaan})
    if response.status_code == 200:
        try:
            data = response.json()
        except Exception as e:
            return f"❌ Gagal decode JSON: {e}\n\nRespon dari server:\n{response.text}"
        
        if isinstance(data, dict):
            return (f"Data No Permintaan {no_permintaan}\n\n"
            )
        else:
            return "⚠️ Data tidak ditemukan."
    else:
        return f"❌ Gagal akses database (status {response.status_code})"


# Fungsi untuk mengambil data dari Database
def get_data_from_gsheet(no_permintaan):
    url = GOOGLE_SCRIPT_URL
    response = requests.get(url, params={'noPermintaan': no_permintaan})
    
    print("Status Code:", response.status_code)
    print("Raw Response Text:", response.text)

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception as e:
            return f"❌ Gagal decode JSON: {e}\n\nRespon dari server:\n{response.text}"
        
        if isinstance(data, dict):
            return (f"Data No Permintaan {no_permintaan}\n\n"
                    f"Nama Pelanggan: {data['Nama Pelanggan']}\n"
                    f"No Telepon: {data['No Telepon']}\n"
                    f"No Inet: {data['No Inet']}\n"
                    f"No Kontak: {data['No Kontak']}\n"
                    f"Tanggal WO: {data['Tanggal WO']}\n"
                    f"Tanggal Transaksi: {data['Tanggal Transaksi']}\n"
                    f"RK/MSAN/ODC: {data['RK/MSAN/ODC']}\n"
                    f"DP/ODP: {data['DP/ODP']}\n"
                    f"SN ONT: {data['SN ONT']}\n"
                    f"SN PLC: {data['SN PLC']}\n"
                    f"SN WIFI EXT: {data['SN WIFI EXT']}\n"
                    f"STB ID: {data['STB ID']}\n"
                    f"Nama/Notel Teknisi: {data['Nama/Notel Teknisi']}\n"
                    f"Nama Mitra: {data['Nama Mitra']}\n"
                    f"Layanan: {data['Layanan']}\n"
                    f"Speed: {data['Speed']}")
        else:
            return "⚠️ Data tidak ditemukan."
    else:
        return f"❌ Gagal akses database (status {response.status_code})"
# Fungsi handler untuk /getdata
async def handle_get_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    no_permintaan = context.args[0]
    result = get_data_from_gsheet(no_permintaan)

    await update.message.reply_text(result)


# Handler untuk command yang tidak dikenali
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ *Maaf, perintah tidak dikenali.*\n\n"
        "📄 *Silakan kirim file PDF laporan instalasi untuk disimpan.*\n\n"
        "🔁 Untuk *memperbarui data* yang sudah ada, gunakan perintah:\n"
        "`/update`\n\n"
        "🔍 Untuk *melihat data* berdasarkan _No Permintaan_, gunakan:\n"
        "`/cekdata <No Permintaan>`",
        parse_mode='Markdown'
    )

# Handler untuk pesan non-PDF
async def handle_non_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ Maaf, saya hanya menerima file PDF.\n"
        "Silakan kirim *file berita acara dalam format PDF* untuk diproses.",
        parse_mode='Markdown'
    )


if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(CommandHandler("cekdata", handle_get_data))
    # app.add_handler(CommandHandler("update_sto", handle_update_sto))
    app.add_handler(CommandHandler("insert", insert_command))
    app.add_handler(CommandHandler("update", update_command))

      # Tambahkan handler untuk command yang tidak dikenali
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    # Handler untuk semua pesan non-PDF
    app.add_handler(MessageHandler(~filters.Document.PDF, handle_non_pdf))


    print("Bot is running...")
    app.run_polling()
