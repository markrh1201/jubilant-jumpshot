import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from datetime import datetime

# Load main data
player_df = pd.read_csv("player_boxscores.csv")
team_df = pd.read_csv("team_advanced_stats.csv")

# Load today's matchups
today_date = datetime.today().strftime('%Y-%m-%d')
matchups_df = pd.read_csv(f"{today_date}_matchups.csv")

# Check if 'Date' column is present in team_df; if not, add it for consistency with player_df
if 'Date' not in team_df.columns:
    team_df['Date'] = today_date  # Assume each row applies to today's date for team stats

# Merge team stats with player data to create training data
player_df = player_df.merge(
    team_df.add_suffix('_team'),
    left_on=['Team', 'Season', 'Date'],
    right_on=['Team_team', 'Season_team', 'Date_team'],
    how='inner'  # Use 'inner' to ensure we only keep matched data
).merge(
    team_df.add_suffix('_opp'),
    left_on=['Opponent', 'Season', 'Date'],
    right_on=['Team_opp', 'Season_opp', 'Date_opp'],
    how='inner'
)

# Select features and target variable for training data
features = player_df[
    ['Minutes', 'FG%', '3P%', 'FT%', 'AST', 'TO', 'REB', 'SPI',
     'OffRtg_team', 'PACE_team', 'eFG%_team', 'DefRtg_opp', 'DREB%_opp']
]
target = player_df['Points']

# Train-test split for evaluation
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Train model
model = GradientBoostingRegressor()
model.fit(X_train, y_train)

# Predict and evaluate on test data
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error on test data: {mae}")

# --- Create Testing Data for Today's Matchups ---

# Filter player and team data to include only rows relevant to today's matchups
today_player_data = player_df[
    (player_df['Date'] == today_date) &
    (player_df['Team'].isin(matchups_df['Team_home']) | player_df['Team'].isin(matchups_df['Team_away']))
]

# Merge today’s player data with team stats for today’s testing set
today_data = today_player_data.merge(
    team_df.add_suffix('_team'),
    left_on=['Team', 'Season', 'Date'],
    right_on=['Team_team', 'Season_team', 'Date_team'],
    how='inner'
).merge(
    team_df.add_suffix('_opp'),
    left_on=['Opponent', 'Season', 'Date'],
    right_on=['Team_opp', 'Season_opp', 'Date_opp'],
    how='inner'
)

# Select features for today's predictions
today_features = today_data[
    ['Minutes', 'FG%', '3P%', 'FT%', 'AST', 'TO', 'REB', 'SPI',
     'OffRtg_team', 'PACE_team', 'eFG%_team', 'DefRtg_opp', 'DREB%_opp']
]

# Predict points for today's matchups
today_predictions = model.predict(today_features)
today_data['Predicted_Points'] = today_predictions

# Save today's predictions to a CSV file
output_file = f"{today_date}_predictions.csv"
today_data[['Player', 'Team', 'Opponent', 'Date', 'Predicted_Points']].to_csv(output_file, index=False)
print(f"Predictions for today's matchups saved to {output_file}")
