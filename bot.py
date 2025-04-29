import asyncio
import logging
import os
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

import nest_asyncio

# 🔐 Чтение токена из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main_menu_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton('🚀 Airdrops')],
    [KeyboardButton('👥 Referral System')],
    [KeyboardButton('💎 Premium Access')]
], resize_keyboard=True)

airdrops_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('🌀 Solana Spin / up to 5 SOL', callback_data='site1')],
    [InlineKeyboardButton('🐧 $PENGU / 5000 PENGU', callback_data='site2')],
    [InlineKeyboardButton('🔄 Refresh List', callback_data='update_list')]
])

update_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('👥 Invite Friends', callback_data='referral_link')],
    [InlineKeyboardButton('💎 Get Premium', callback_data='premium_link')]
])

premium_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('✅ I Paid', callback_data='confirm_payment')]
])

def format_time_delta(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text('🚀 Welcome aboard!\n\nChoose an option to get started:', reply_markup=main_menu_keyboard)

async def airdrops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("🌐 We currently have 139 airdrop websites listed!\n\n"
            "🎯 Available airdrops for you:")
    if update.message:
        await update.message.reply_text(text, reply_markup=airdrops_keyboard)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=airdrops_keyboard)

async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_link = f"https://t.me/YourBot?start={user_id}"
    text = (f'👥 Invite friends and earn rewards!\n'
            f'🎁 Get 1 free refresh for every 5 friends you invite!\n\n'
            f'🔗 Your referral link: {referral_link}')
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard)

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ('💎 Premium Subscription\n\n'
            'Subscription cost for 1 month: 100$\n\n'
            '🪙 Payment address: 0x633707FcAC03a6459e3fB4478b52FEB52E5b22b7\n'
            'Available coins: ETH, BNB, POL\n\n'
            'By paying for a premium account you will receive:\n'
            '• 🔓 Access to all airdrops\n'
            '• ⏰ Early access to new airdrops (24h earlier)\n'
            '• 💬 Private premium users chat')
    if update.message:
        await update.message.reply_text(text, reply_markup=premium_keyboard)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=premium_keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'site1':
        keyboard = [
            [InlineKeyboardButton('🔗 Claim Now', url='https://summer.sol-hook.org')],
            [InlineKeyboardButton('⬅️ Back', callback_data='back_to_airdrops')]
        ]
        await query.edit_message_text(
            '🌀 Solana Spin / up to 5 SOL\n\n'
            '⭐ Rating: ⭐⭐⭐\n'
            '🎁 Reward: random, from 0 to 5 SOL\n\n'
            '📄 Description:\n'
            'It is indeed a random reward, but our observations are that cash rewards fall out about 40% of the time.',
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'site2':
        keyboard = [
            [InlineKeyboardButton('🔗 Claim Now', url='https://penguin.sol-finance.icu')],
            [InlineKeyboardButton('⬅️ Back', callback_data='back_to_airdrops')]
        ]
        await query.edit_message_text(
            '🐧 $PENGU / 5000 PENGU\n\n'
            '⭐ Rating: ⭐⭐⭐⭐⭐\n'
            '🎁 Reward: fixed, 0.1 SOL + 5000 PENGU\n\n'
            '📄 Description:\n'
            'According to the results of our tests, it became clear that the site accepts only “wallets with history” to avoid the influx of recently created accounts.\n'
            'It is still possible to get rewards for multiple accounts, but it requires a special approach.',
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'update_list':
        now = datetime.now()
        last_update = context.user_data.get('last_update')

        if last_update is None:
            context.user_data['last_update'] = now
            await query.edit_message_text('⏳ Loading your airdrops list... Please wait...')
            await asyncio.sleep(1.5)
            await query.message.edit_text('⏳ You can refresh the list again in 12 hours or:', reply_markup=update_keyboard)
        else:
            time_diff = now - last_update
            if time_diff < timedelta(hours=12):
                remaining = timedelta(hours=12) - time_diff
                time_left = format_time_delta(remaining)
                await query.edit_message_text(f'⏳ You can refresh the list in {time_left} or:', reply_markup=update_keyboard)
            else:
                context.user_data['last_update'] = now
                await query.edit_message_text('✅ List refreshed! New airdrops are available.', reply_markup=airdrops_keyboard)

    elif query.data == 'back_to_airdrops':
        await airdrops(update, context)

    elif query.data == 'referral_link':
        user_id = query.from_user.id
        referral_link = f"https://t.me/YourBot?start={user_id}"
        await query.message.reply_text(f'👥 Your referral link: {referral_link}', reply_markup=main_menu_keyboard)

    elif query.data == 'premium_link':
        await premium(update, context)

    elif query.data == 'confirm_payment':
        await query.message.reply_text(
            '📤 Please send the transaction hash (TxID) of your payment.\n'
            'We will verify it manually and grant access within 24 hours.',
            reply_markup=main_menu_keyboard)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    text = update.message.text.strip().lower()

    if text in ['🚀 airdrops', 'airdrops']:
        await airdrops(update, context)
    elif text in ['👥 referral system', 'referral system']:
        await referrals(update, context)
    elif text in ['💎 premium access', 'premium access']:
        await premium(update, context)
    else:
        await update.message.reply_text('📋 Please choose a valid option from the menu below:', reply_markup=main_menu_keyboard)

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print('✅ Bot is running...')
    await app.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
