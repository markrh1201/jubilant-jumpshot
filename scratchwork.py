import pandas as pd

df = pd.read_csv('predictions_with_players_games.csv')

# Extract the date from the 'Game' column and create a new 'Date' column
df['Date'] = pd.to_datetime(df['Game'].str.extract(r'(\d{4}-\d{2}-\d{2})')[0])

# Sort the predictions DataFrame by 'Date' and then by 'Game'
df.sort_values(by=['Date', 'Game'], inplace=True)

# Reset the index after sorting (optional)
df.reset_index(drop=True, inplace=True)

# Save the sorted predictions to a CSV file
df.to_csv('predictions_sorted_by_date_and_game.csv', index=False)
