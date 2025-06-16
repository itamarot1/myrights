# קובץ: bot.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# הגדר את הטוקן שלך פה
import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# זיכרון פשוט למשתמשים (בהמשך נעבור לשמירה בקובץ/DB)
user_data = {}

# התחלה
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": "age"}
    await update.message.reply_text("שלום! בן כמה אתה?")

# ניהול תגובות
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"step": "age"}
        await update.message.reply_text("בוא נתחיל מהתחלה. בן כמה אתה?")
        return

    step = user_data[user_id]["step"]

    if step == "age":
        user_data[user_id]["age"] = text
        user_data[user_id]["step"] = "employment"
        await update.message.reply_text("מה הסטטוס התעסוקתי שלך? (שכיר/עצמאי/מובטל)")
    elif step == "employment":
        user_data[user_id]["employment"] = text
        user_data[user_id]["step"] = "health"
        await update.message.reply_text("האם יש לך נכות רפואית כלשהי? (כן/לא)")
    elif step == "health":
        user_data[user_id]["health"] = text

        from gpt_response import get_rights_response

        profile = {
            "age": user_data[user_id]["age"],
            "employment": user_data[user_id]["employment"],
            "health": user_data[user_id]["health"]
        }

        await update.message.reply_text("בודק זכויות מתאימות...")

        gpt_answer = get_rights_response(profile)
        await update.message.reply_text(gpt_answer)

# הפעלת הבוט
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("הבוט רץ...")
    app.run_polling()

if __name__ == "__main__":
    main()
