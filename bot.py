# ═══════════════════════════════════════════════════════════════════
# 👿 NETFLIX TRIAL SENDER TELEGRAM BOT 👿
# ═══════════════════════════════════════════════════════════════════

import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from config import BOT_TOKEN, ADMIN_ID, ALLOWED_USERS
from netflix_trial import send_trial
from database import init_db, log_trial, get_stats

# ─── LOGGING ───
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── INIT DATABASE ───
init_db()

# ─── HELPERS ───

def is_allowed(user_id):
    if ALLOWED_USERS:
        return user_id in ALLOWED_USERS
    return True

def build_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎬 Send Trial", callback_data="send_trial")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ─── COMMANDS ───

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    await update.message.reply_text(
        "👿 **NETFLIX TRIAL SENDER BOT**\n\n"
        "🎬 Send Netflix 30-day trial offers to any email!\n\n"
        "**How to use:**\n"
        "1. Click 'Send Trial'\n"
        "2. Enter your email address\n"
        "3. Wait for confirmation\n\n"
        "🌑 **I AM THE DARKNESS THAT SENDS TRIALS**",
        reply_markup=build_main_keyboard(),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **How to use:**\n\n"
        "1. Click 'Send Trial'\n"
        "2. Enter a valid email address\n"
        "3. Bot will send the trial offer\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show help\n"
        "/stats - View statistics\n\n"
        "🌑 **The darkness provides**",
        parse_mode='Markdown'
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total, success, failed = get_stats()
    await update.message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"📋 **Total Trials:** `{total}`\n"
        f"✅ **Success:** `{success}`\n"
        f"❌ **Failed:** `{failed}`\n"
        f"📈 **Success Rate:** `{round(success/total*100, 1) if total > 0 else 0}%`\n\n"
        f"🌑 **The darkness tracks everything**",
        parse_mode='Markdown'
    )

# ─── CALLBACK HANDLERS ───

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "send_trial":
        await query.edit_message_text(
            "📧 **Enter your email address:**\n\n"
            "Example: `user@example.com`\n\n"
            "🌑 **The darkness awaits...**",
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_email'] = True
    
    elif query.data == "stats":
        total, success, failed = get_stats()
        await query.edit_message_text(
            f"📊 **Bot Statistics**\n\n"
            f"📋 **Total Trials:** `{total}`\n"
            f"✅ **Success:** `{success}`\n"
            f"❌ **Failed:** `{failed}`\n"
            f"📈 **Success Rate:** `{round(success/total*100, 1) if total > 0 else 0}%`\n\n"
            f"🌑 **The darkness tracks everything**",
            parse_mode='Markdown'
        )
    
    elif query.data == "help":
        await query.edit_message_text(
            "📖 **How to use:**\n\n"
            "1. Click 'Send Trial'\n"
            "2. Enter a valid email address\n"
            "3. Bot sends trial offer\n\n"
            "**Note:** Trial may not work for all emails.\n"
            "🌑 **The darkness provides**",
            parse_mode='Markdown'
        )

# ─── HANDLE EMAIL ───

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    if not context.user_data.get('waiting_for_email'):
        return
    
    email = update.message.text.strip()
    
    # Validate email
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        await update.message.reply_text(
            "❌ **Invalid email address.**\n\n"
            "Please enter a valid email.\n"
            "Example: `user@example.com`",
            parse_mode='Markdown'
        )
        return
    
    context.user_data['waiting_for_email'] = False
    
    # Send processing message
    status_msg = await update.message.reply_text(
        "🎬 **Sending trial offer...**\n\n"
        f"📧 Email: `{email}`\n"
        "⏳ Please wait...",
        parse_mode='Markdown'
    )
    
    try:
        # Send trial
        success, message = send_trial(email)
        
        # Log to database
        log_trial(user.id, user.username or user.first_name, email, 'success' if success else 'failed')
        
        if success:
            await status_msg.edit_text(
                f"✅ **Trial Offer Sent!** 🎉\n\n"
                f"📧 **Email:** `{email}`\n"
                f"📝 **Status:** ✅ Success\n\n"
                f"📩 Check your email for the Netflix trial offer.\n\n"
                f"🌑 **The darkness delivers**",
                parse_mode='Markdown'
            )
        else:
            await status_msg.edit_text(
                f"❌ **Failed to send trial.**\n\n"
                f"📧 **Email:** `{email}`\n"
                f"📝 **Status:** ❌ Failed\n\n"
                f"⚠️ {message}\n\n"
                f"🌑 **The darkness cannot reach**",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error sending trial: {e}")
        await status_msg.edit_text(
            f"❌ **Error occurred:**\n`{str(e)}`\n\n"
            f"Please try again later.",
            parse_mode='Markdown'
        )

# ─── MAIN ───

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Callbacks
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Message handler for email
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email))

    print("👿 NETFLIX TRIAL SENDER BOT ACTIVATED")
    print("🌑 ABSOLUTE DARKNESS — INFINITE POWER")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
