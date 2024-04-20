from pybaseball import statcast_batter_percentile_ranks

# 假設您的 DataFrame 名稱為 'stats_df'
player_name = 'Juan Soto'
stats_df = statcast_batter_percentile_ranks(2024)
player_row = stats_df.loc[stats_df['player_name'] == player_name]
print(player_row)