import pandas as pd
import numpy as np

# Load and preprocess data
df = pd.read_csv('regular_season_boxscores_combined_22-24.csv')
df.columns = df.columns.str.strip()  # Clean column names
df['Date'] = pd.to_datetime(df['Date'])  # Convert date to datetime

# Replace invalid entries (like '-') with NaN
df.replace({'-': None}, inplace=True)

# Convert relevant columns to numeric, coerce errors to NaN
numeric_columns = ['Points', 'Minutes', 'FGA', '3PM', '3PA', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'TO', 'STL', 'BLK', 'PF', 'FTM', '+/-', 'SPI']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Handle FG%, 3P%, FT%: strip any whitespace and convert to numeric
percent_columns = ['FG%', '3P%', 'FT%']
df[percent_columns] = df[percent_columns].apply(lambda x: x.str.strip() if x.dtype == "object" else x)
df[percent_columns] = df[percent_columns].apply(pd.to_numeric, errors='coerce')

# Sort by player and date
df = df.sort_values(by=['Player', 'Date'])
# Add binary column to determine if the player's team is home or away
df['is_home'] = np.where(df['Opponent'].str.contains('vs.'), 1, 0)
# Initialize new columns for most recent, L5, L10, and L20 game stats
rolling_windows = [1, 5, 10, 20]  # for last game, L5, L10, L20

# Group by player to calculate stats individually
for player, group in df.groupby('Player'):
    for window in rolling_windows:
        # Create rolling averages for relevant stats
        df.loc[group.index, f'Points_L{window}'] = group['Points'].shift(1).rolling(window).mean()
        df.loc[group.index, f'Minutes_L{window}'] = group['Minutes'].shift(1).rolling(window).mean()
        df.loc[group.index, f'FGA_L{window}'] = group['FGA'].shift(1).rolling(window).mean()
        df.loc[group.index, f'3PM_L{window}'] = group['3PM'].shift(1).rolling(window).mean()
        df.loc[group.index, f'3PA_L{window}'] = group['3PA'].shift(1).rolling(window).mean()
        df.loc[group.index, f'FTA_L{window}'] = group['FTA'].shift(1).rolling(window).mean()
        df.loc[group.index, f'OREB_L{window}'] = group['OREB'].shift(1).rolling(window).mean()
        df.loc[group.index, f'DREB_L{window}'] = group['DREB'].shift(1).rolling(window).mean()
        df.loc[group.index, f'REB_L{window}'] = group['REB'].shift(1).rolling(window).mean()
        df.loc[group.index, f'AST_L{window}'] = group['AST'].shift(1).rolling(window).mean()
        df.loc[group.index, f'TO_L{window}'] = group['TO'].shift(1).rolling(window).mean()
        df.loc[group.index, f'STL_L{window}'] = group['STL'].shift(1).rolling(window).mean()
        df.loc[group.index, f'BLK_L{window}'] = group['BLK'].shift(1).rolling(window).mean()
        df.loc[group.index, f'PF_L{window}'] = group['PF'].shift(1).rolling(window).mean()

        # Additional rolling averages for FG%, 3P%, FTM, FT%, +/-, and SPI
        df.loc[group.index, f'FG%_L{window}'] = group['FG%'].shift(1).rolling(window).mean()
        df.loc[group.index, f'3P%_L{window}'] = group['3P%'].shift(1).rolling(window).mean()
        df.loc[group.index, f'FTM_L{window}'] = group['FTM'].shift(1).rolling(window).mean()
        df.loc[group.index, f'FT%_L{window}'] = group['FT%'].shift(1).rolling(window).mean()
        df.loc[group.index, f'+/-_L{window}'] = group['+/-'].shift(1).rolling(window).mean()
        df.loc[group.index, f'SPI_L{window}'] = group['SPI'].shift(1).rolling(window).mean()


# 2. Fill any remaining NaNs with 0 (e.g., if there's no prior data, use 0 as a neutral value)
df.fillna(0, inplace=True)

# Drop original columns that are now replaced by the rolling stats
df = df.drop(columns=['Minutes', 'FGA', '3PA', 'FTA', 'OREB', 'DREB', 'TO', 'STL', 'BLK', 'PF', 'FTM', '+/-', 'SPI','FGM' ,'FG%'   ,'3P%'   ,'FT%'])

# Save the transformed dataframe to CSV
df.to_csv('Transformed_Boxscores_22-24.csv', index=False)
