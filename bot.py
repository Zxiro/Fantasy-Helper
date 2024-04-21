import logging
from config import tg_token
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, filters, InlineQueryHandler
from pybaseball import statcast_batter_percentile_ranks, statcast_pitcher_percentile_ranks

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
def get_player_data(player_name, player_type):
    print('Start Get {player_name} Player Data:')
    if (player_type == 'batter'): stats_df = statcast_batter_percentile_ranks(2024)
    else: stats_df = statcast_pitcher_percentile_ranks(2024)
    player_row = stats_df.loc[stats_df['player_name'] == player_name]
    print(player_row)
    return player_row.to_json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Thanks for adding Fantasy Helper!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def get_batter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_name = ' '.join(context.args)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=get_player_data(player_name, 'batter'))

async def get_pitcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_name = ' '.join(context.args)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=get_player_data(player_name, 'pitcher'))


if __name__ == '__main__':
    application = ApplicationBuilder().token(tg_token).build()

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    start_handler = CommandHandler('start', start)
    batter_handler = CommandHandler('get_batter', get_batter)
    pitcher_handler = CommandHandler('get_pitcher', get_pitcher)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(batter_handler)
    application.add_handler(pitcher_handler)
    
    application.run_polling()