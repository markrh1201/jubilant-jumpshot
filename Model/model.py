import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, r2_score, explained_variance_score

# Load the data
df = pd.read_csv('Transformed_Boxscores_22-24.csv')
df.columns = df.columns.str.strip()

# Define the target columns you want to predict
target_columns = ['Points', 'REB', 'AST', '3PM']

# Exclude specific columns that are not used for prediction
excluded_columns = ['Player', 'Team', 'Opponent', 'Date', 'Result', 'Game'] + target_columns

# Select all feature columns by excluding the ones that are not relevant for prediction
feature_columns = [col for col in df.columns if col not in excluded_columns]

# Create a game identifier if needed
df['Game'] = df['Opponent'] + ' on ' + df['Date']

# Split the data into X (features) and y (target)
X = df[feature_columns]
y = df[target_columns]
players = df['Player']
games = df['Game']

# Split the data into training and testing sets (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=12)
players_train, players_test = train_test_split(players, test_size=0.2, random_state=12)
games_train, games_test = train_test_split(games, test_size=0.2, random_state=12)

# Use RandomForestRegressor as the base estimator
multi_target_model = MultiOutputRegressor(GradientBoostingRegressor(random_state=12), n_jobs=6)

# Train the model on all targets
multi_target_model.fit(X_train, y_train)

# Predict all targets
y_pred = multi_target_model.predict(X_test)

# Evaluate performance on all targets
mse_all = mean_squared_error(y_test, y_pred)
mae_all = mean_absolute_error(y_test, y_pred)
r2_all = r2_score(y_test, y_pred)
explained_variance = explained_variance_score(y_test, y_pred)

# Print the evaluation metrics
print(f'Mean Squared Error for all targets: {mse_all}')
print(f'Mean Absolute Error for all targets: {mae_all}')
print(f'R² Score for all targets: {r2_all}')
print(f'Explained Variance Score for all targets: {explained_variance}')

# Create a DataFrame for predictions
predictions_df = pd.DataFrame(y_pred, columns=target_columns)

# Add player names and game information to the predictions DataFrame
predictions_df['Player'] = players_test.reset_index(drop=True)
predictions_df['Game'] = games_test.reset_index(drop=True)

# Add the corresponding features for better context
predictions_df = pd.concat([X_test.reset_index(drop=True), predictions_df], axis=1)

# Sort the predictions DataFrame by 'Game'
predictions_df.sort_values(by='Player', inplace=True)

# Save the predictions to a CSV file
predictions_df.to_csv('predictions_with_players_games.csv', index=False)
