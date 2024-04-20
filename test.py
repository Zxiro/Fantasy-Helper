# from pybaseball import playerid_lookup, statcast_pitcher


# # only return the ids of chipper jones (returns one row)
# player_data = playerid_lookup('strider','spencer')
# print(player_data)

# data = statcast_pitcher('2022-12-31', '2023-12-31', player_id = player_data.key_mlbam[0])
# print(data)

from pybaseball import statcast_batter_percentile_ranks

# get data for all qualified pitchers in 2019
data = statcast_batter_percentile_ranks(2024)

print(data)