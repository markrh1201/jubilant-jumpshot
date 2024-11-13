import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

# Load the training and testing data
df_train = pd.read_csv("rolling_averages.csv")
df_test = pd.read_csv("testing.csv")

# Drop rows with missing values in the training dataset (optional: could fill with mean/median values)
df_train = df_train.dropna()

# Separate features and target for training data
X_train = df_train.drop(columns=["Date", "Team_home", "Team_away", "Point_diff"])
y_train = df_train["Point_diff"]

# Use only the features from the testing data
X_test = df_test.drop(columns=["Date", "Team_home", "Team_away"])

# Initialize and train the model
model = GradientBoostingRegressor(random_state=42)
model.fit(X_train, y_train)

# Make predictions on the testing data
y_pred = model.predict(X_test)

# Create a DataFrame to display predicted point differentials for each matchup
predictions_df = pd.DataFrame({
    "Date": df_test["Date"],
    "Team_home": df_test["Team_home"],
    "Team_away": df_test["Team_away"],
    "Predicted_Point_diff": y_pred
})

# Display the predictions
print("\nPredicted Point Differentials for Today's Matchups:")
print(predictions_df)

# Optionally, save predictions to a new CSV file
today = pd.Timestamp("today").strftime("%Y-%m-%d")
predictions_df.to_csv(f"{today}_predictions.csv", index=False)
print(f"Predicted data saved to {today}_predictions.csv.")
