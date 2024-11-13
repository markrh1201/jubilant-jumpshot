import pandas as pd
from datetime import datetime

# Load the historical game stats data
df = pd.read_csv("game_stats.csv", parse_dates=["Date"])

# Sort by date to ensure correct chronological order
df = df.sort_values(by=["Date"])

# Define columns for which you want rolling averages
home_stats_columns = [
    "FGM_home", "FGA_home", "FG%_home", "3PM_home", "3PA_home", "3P%_home",
    "FTM_home", "FTA_home", "FT%_home", "OREB_home", "DREB_home", "REB_home",
    "AST_home", "TO_home", "STL_home", "BLK_home", "PF_home", "Points_home"
]
away_stats_columns = [
    "FGM_away", "FGA_away", "FG%_away", "3PM_away", "3PA_away", "3P%_away",
    "FTM_away", "FTA_away", "FT%_away", "OREB_away", "DREB_away", "REB_away",
    "AST_away", "TO_away", "STL_away", "BLK_away", "PF_away", "Points_away"
]

# Define rolling windows
windows = [1, 5, 10, 20]

# Calculate rolling averages for home team stats
for window in windows:
    for col in home_stats_columns:
        df[f"{col}_avg_{window}"] = (
            df.groupby("Team_home")[col]
            .rolling(window, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

# Calculate rolling averages for away team stats
for window in windows:
    for col in away_stats_columns:
        df[f"{col}_avg_{window}"] = (
            df.groupby("Team_away")[col]
            .rolling(window, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

# Define columns to keep (excluding Point_diff)
columns_to_keep = ['Date', 'Team_home', 'Team_away', 'Point_diff']
for window in windows:
    for col in home_stats_columns + away_stats_columns:
        columns_to_keep.append(f"{col}_avg_{window}")

# Filter out unnecessary columns and save rolling averages to a new CSV
df_rolling_averages = df[columns_to_keep].sort_values(by='Date', ascending=False)
df_rolling_averages.to_csv("rolling_averages.csv", index=False)

print("Saved data to rolling_averages.csv.")

# --- Now, create testing data based on today's matchups ---

# Load today's matchups file
today_str = datetime.now().strftime("%Y-%m-%d")
today_matchups_file = f"{today_str}_matchups.csv"
df_today_matchups = pd.read_csv(today_matchups_file)

# Initialize an empty list to store processed matchup data
today_matchups_data = []

# Loop through each matchup
for _, matchup in df_today_matchups.iterrows():
    home_team = matchup["Team_home"]
    away_team = matchup["Team_away"]
    game_date = matchup["Date"]

    # Extract rolling averages for the home team from the historical data
    home_data = df[(df["Team_home"] == home_team) & (df["Date"] < game_date)].iloc[-1]

    # Extract rolling averages for the away team from the historical data
    away_data = df[(df["Team_away"] == away_team) & (df["Date"] < game_date)].iloc[-1]

    # Combine game information with rolling averages for both teams
    game_data = {
        "Date": game_date,
        "Team_home": home_team,
        "Team_away": away_team,
    }

    # Add home and away team stats for each rolling window
    for window in windows:
        for col in home_stats_columns:
            game_data[f"{col}_avg_{window}"] = home_data[f"{col}_avg_{window}"]
        for col in away_stats_columns:
            game_data[f"{col}_avg_{window}"] = away_data[f"{col}_avg_{window}"]

    # Append game data to the list
    today_matchups_data.append(game_data)

# Convert the list to a DataFrame
df_today_matchups_processed = pd.DataFrame(today_matchups_data)

# Save the processed data to a new CSV
output_file = f"testing.csv"
df_today_matchups_processed.to_csv(output_file, index=False)

print(f"Saved today's matchups with rolling averages to {output_file}.")

