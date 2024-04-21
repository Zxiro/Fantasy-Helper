import io
import logging
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from config import tg_token
from telegram import Update
from telegram.ext import MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler
from pybaseball import statcast_batter_percentile_ranks, statcast_pitcher_percentile_ranks

matplotlib.use('Agg')  # 需要這一行來在非交互式環境中使用matplotlib

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


PLAYERNAME = range(1)

def get_player_data(player_name, player_type):
    if (player_type == 'batter'): stats_df = statcast_batter_percentile_ranks(2024)
    else: stats_df = statcast_pitcher_percentile_ranks(2024)
    player_row = stats_df.loc[stats_df['player_name'] == player_name]

    # 將行轉換為字典
    try:
        player_data = player_row.to_dict('records')[0]
    except IndexError:
        return "Wrong Command, Type Again"
    
    # 提取數值
    stats = []
    pr_values = []
    for stat, value in player_data.items():
        if stat == 'player_name' or stat == 'player_id' or stat == 'year': continue
        if value is not None:
            stats.append(stat)
            pr_values.append(value)
    pr_values = np.array(pr_values)

    sorted_indices = np.argsort(pr_values)[::1]
    stats = np.array(stats)[sorted_indices]
    pr_values = pr_values[sorted_indices]

    # 創建條形圖
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_containers = ax.barh(stats, pr_values)
    
    # 在每個條形上顯示數值
    for bar in bar_containers:
        bar_value = bar.get_width()
        ax.annotate(
            f"{bar_value}",
            xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontweight="bold",
        )
    ax.barh(stats, pr_values)
    ax.set_xlabel('Percentile Rank')
    ax.set_ylabel('Stats')
    ax.set_title(f'{player_name} {player_data["year"]}  Player Data')
    
    # 保存圖片到內存
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    img_bytes = buffer.getvalue()
    plt.close(fig)
    img_file = io.BytesIO(img_bytes)
    img_file.name = 'player_stats.png' 
    return img_file

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"Username: {user.username}, ID: {user.id}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Thanks for adding Fantasy Helper!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def get_batter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('get_pitcher func')
    player_name = update.message.text
    user = update.effective_user
    print(f"Username: {user.username}, ID: {user.id}, Search: {player_name}")
    batter_data = get_player_data(player_name, 'batter')
    if isinstance(batter_data, str):
        # 如果 get_player_data 返回一個字符串,表示輸入錯誤
        await context.bot.send_message(chat_id=update.effective_chat.id, text=batter_data)
        return PLAYERNAME
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=batter_data)
        return ConversationHandler.END

async def get_pitcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('get_pitcher func')
    player_name = update.message.text
    user = update.effective_user
    print(f"Username: {user.username}, ID: {user.id}, Search: {player_name}")
    pitcher_data = get_player_data(player_name, 'pitcher')
    if isinstance(pitcher_data, str):
        # 如果 get_player_data 返回一個字符串,表示輸入錯誤
        await context.bot.send_message(chat_id=update.effective_chat.id, text=pitcher_data)
        return PLAYERNAME
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=pitcher_data)
        return ConversationHandler.END

async def get_player_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the player name")
    return PLAYERNAME

batter_conv_handler = ConversationHandler(
    entry_points = [CommandHandler('get_batter', get_player_name)],
    states = {
        PLAYERNAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_batter)]
    },
    fallbacks=[]
)

pitcher_conv_handler = ConversationHandler(
    # Enter the conversation from this two command
    entry_points = [CommandHandler('get_pitcher', get_player_name)],
    states = {
        PLAYERNAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_pitcher)]
    },
    fallbacks=[]
)


if __name__ == '__main__':
    application = ApplicationBuilder().token(tg_token).build()

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    start_handler = CommandHandler('start', start)
    batter_handler = CommandHandler('get_batter', get_batter)
    pitcher_handler = CommandHandler('get_pitcher', get_pitcher)

    application.add_handler(batter_conv_handler)
    application.add_handler(pitcher_conv_handler)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(batter_handler)
    application.add_handler(pitcher_handler)
    
    application.run_polling()