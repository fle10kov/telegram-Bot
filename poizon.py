from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

INPUT_AMOUNT = 1

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 Poizon", url="https://www.poizon.com/")],
        [InlineKeyboardButton("Сделать заказ 🧾", callback_data='order')],
        [InlineKeyboardButton("Конвертер 💰 CNY→RUB", callback_data='convert')],
        [InlineKeyboardButton("Avito 🛍️",url="https://www.avito.ru/user/f9d2bee70d63a9fe3eec7e93041d7693/profile?src=sharing")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=main_keyboard()
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Напиши / чтобы выбрать нужную команду. 📌 В конверторе ты сможешь рассчитать стоимость заказа. 📌 Оформление заказа происходит через отправление в tg нашему сотруднику рассчёта заказа из бота.")

async def site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Открыть сайт Poizon: https://www.poizon.com/")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tg: @fingerdaddy (любые вопросы) 💹 Курс: 12.5 RUB")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'order':
        await query.edit_message_text("Tg: @fingerdaddy (Пересылай расчёт, оформим заказ😃)", reply_markup=main_keyboard())
    elif data == 'convert':
        await query.edit_message_text("Введите сумму в юанях (от 0 до 1 000 000 000):")
        return INPUT_AMOUNT

async def convert_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace(',', '.').strip()
    try:
        amount_cny = float(text)
        if not (0 <= amount_cny <= 1_000_000_000):
            await update.message.reply_text("Введите число в диапазоне от 0 до 1 000 000 000:")
            return INPUT_AMOUNT
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число:")
        return INPUT_AMOUNT

    exchange_rate = 12.5
    result_rub = amount_cny * exchange_rate + 1000

    await update.message.reply_text(
        f"Результат: {amount_cny} CNY = {result_rub:.2f} RUB (с учётом комиссии 3% и доставки)",
        reply_markup=main_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.", reply_markup=main_keyboard())
    return ConversationHandler.END

def main():
    TOKEN = "#"

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^convert$')],
        states={
            INPUT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_currency)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=True
    )

    order_handler = CallbackQueryHandler(button_handler, pattern='^order$')

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("site", site))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(conv_handler)
    application.add_handler(order_handler)
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()