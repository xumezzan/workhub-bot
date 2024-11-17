from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler
from flask import Flask, request, jsonify, send_from_directory
import sqlite3

TOKEN = "7758536544:AAHsmNALrPNpxnR4XGDL-ZfaxikmWAoNLs8"

app = Flask(__name__)

# Инициализируем базу данных
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'в процессе'
        )
    """)
    conn.commit()
    conn.close()

# Команда /start
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Открыть WorkHub Mini App", web_app=WebAppInfo(url="http://127.0.0.1:5000/web/index.html"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку ниже, чтобы открыть Mini App:", reply_markup=reply_markup)

# API для получения списка задач
@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, status FROM tasks")
    tasks = [{"id": row[0], "description": row[1], "status": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks)

# API для добавления задачи
@app.route('/addtask', methods=['POST'])
def add_task():
    data = request.json
    description = data.get("description")
    if description:
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

# Обработка статических файлов (index.html)
@app.route('/web/<path:filename>')
def serve_web_app(filename):
    return send_from_directory('web', filename)

# Запуск сервера Flask и Telegram-бота
if __name__ == "__main__":
    init_db()
    # Запускаем Flask-сервер
    app.run(port=5000)
