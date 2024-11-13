import pandas as pd
from datetime import datetime

# Mapping of NBA team names to their three-letter abbreviations
team_abbreviations = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
}

def save_todays_matchups():
    """
    Load 2024-25_schedule.csv, convert team names to abbreviations, and save only today's games to a new CSV.
    """
    # Load the schedule CSV
    schedule_df = pd.read_csv("2024-25_schedule.csv")
    
    # Rename columns for consistency
    schedule_df.rename(columns={
        'Game Date': 'Date',
        'Visitor/Neutral': 'Team_away',
        'Home/Neutral': 'Team_home'
    }, inplace=True)
    
    # Parse the 'Date' column to datetime format based on the given format in the file
    schedule_df['Date'] = pd.to_datetime(schedule_df['Date'], format="%a, %b %d, %Y")
    
    # Get today's date
    today = datetime.now().date()
    
    # Filter for games that are happening today
    todays_games = schedule_df[schedule_df['Date'].dt.date == today]
    
    # Map team names to abbreviations
    todays_games['Team_home'] = todays_games['Team_home'].map(team_abbreviations)
    todays_games['Team_away'] = todays_games['Team_away'].map(team_abbreviations)
    
    # Drop rows where mapping is missing (i.e., teams not in the abbreviation dictionary)
    todays_games.dropna(subset=['Team_home', 'Team_away'], inplace=True)
    
    # Select only the necessary columns
    todays_games = todays_games[['Date', 'Team_home', 'Team_away']]
    
    # Save to a new CSV with today's date in the filename
    filename = f"{today}_matchups.csv"
    todays_games.to_csv(filename, index=False)
    print(f"Saved today's matchups to {filename}")

# Run the function
save_todays_matchups()
