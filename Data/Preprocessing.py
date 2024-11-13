import pandas as pd

def combine_game_stats(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Extract home and away games and make explicit copies to avoid SettingWithCopyWarning
    home_games = df[~df['Opponent'].str.contains('@')].copy()
    away_games = df[df['Opponent'].str.contains('@')].copy()
    
    # Function to standardize matchup format
    def get_matchup_key(row):
        if '@' in row['Opponent']:
            away_team = row['Team']
            home_team = row['Opponent'].split(' @ ')[1]
        else:
            home_team = row['Team']
            away_team = row['Opponent'].split(' vs. ')[1]
        return f"{home_team}_{away_team}_{row['Date']}"
    
    # Add matchup key using .loc to avoid SettingWithCopyWarning
    home_games.loc[:, 'matchup_key'] = home_games.apply(get_matchup_key, axis=1)
    away_games.loc[:, 'matchup_key'] = away_games.apply(get_matchup_key, axis=1)
    
    # Group by matchup_key and aggregate stats, excluding grouping columns
# Group by matchup_key and aggregate stats
    def aggregate_team_stats(group):
        return pd.Series({
            'Points': group['Points'].sum(),
            'FGA': group['FGA'].sum(),
            'FGM': group['FGM'].sum(),
            '3PA': group['3PA'].sum(),
            '3PM': group['3PM'].sum(),
            'FTA': group['FTA'].sum(),
            'FTM': group['FTM'].sum(),
            'OREB': group['OREB'].sum(),
            'DREB': group['DREB'].sum(),
            'REB': group['REB'].sum(),
            'AST': group['AST'].sum(),
            'TO': group['TO'].sum(),
            'STL': group['STL'].sum(),
            'BLK': group['BLK'].sum(),
            'PF': group['PF'].sum(),
            'Team': group['Team'].iloc[0],
            'Date': group['Date'].iloc[0]
        })

    # Group by 'matchup_key' and apply aggregation, excluding 'matchup_key'
    home_stats = home_games.groupby('matchup_key').apply(lambda group: aggregate_team_stats(group.drop(columns=['matchup_key']))).reset_index()
    away_stats = away_games.groupby('matchup_key').apply(lambda group: aggregate_team_stats(group.drop(columns=['matchup_key']))).reset_index()

    
    # Calculate field goal, 3-point, and free throw percentages
    for stats_df in [home_stats, away_stats]:
        stats_df['FG%'] = (stats_df['FGM'] / stats_df['FGA']).fillna(0)
        stats_df['3P%'] = (stats_df['3PM'] / stats_df['3PA']).fillna(0)
        stats_df['FT%'] = (stats_df['FTM'] / stats_df['FTA']).fillna(0)

    # Merge home and away stats
    combined_stats = pd.merge(
        home_stats,
        away_stats,
        on='matchup_key',
        suffixes=('_home', '_away')
    )
    
    # Calculate Point_diff and drop Points_home and Points_away
    combined_stats['Point_diff'] = combined_stats['Points_home'] - combined_stats['Points_away']
    
    # Clean up and reorganize columns
    final_columns = [
        'Date_home',         # Will be renamed to "Date" below
        'Team_home',
        'FGA_home',
        'FGM_home',
        'FG%_home',
        '3PA_home',
        '3PM_home',
        '3P%_home',
        'FTA_home',
        'FTM_home',
        'FT%_home',
        'OREB_home',
        'DREB_home',
        'REB_home',
        'AST_home',
        'TO_home',
        'STL_home',
        'BLK_home',
        'PF_home',
        'Points_home',

        'Team_away',
        'FGA_away',
        'FGM_away',
        'FG%_away',
        '3PA_away',
        '3PM_away',
        '3P%_away',
        'FTA_away',
        'FTM_away',
        'FT%_away',
        'OREB_away',
        'DREB_away',
        'REB_away',
        'AST_away',
        'TO_away',
        'STL_away',
        'BLK_away',
        'PF_away',
        'Points_away',

        'Point_diff'
    ]

    # Select relevant columns and rename 'Date_home' to 'Date'
    final_df = combined_stats[final_columns]
    final_df = final_df.rename(columns={'Date_home': 'Date'})
    final_df = final_df.sort_values(by=['Date', 'Team_home'], ascending=False)
    
    # Save to the output CSV file
    final_df.to_csv(output_file, index=False)

# Usage example
combine_game_stats('player_boxscores.csv', 'game_stats.csv')
