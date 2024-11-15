import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('rolling_averages.csv')
training_data = df.drop(columns=["Date", "Team_home", "Team_away", "Point_diff"])
correlation_matrix = training_data.corr()

# Set up the matplotlib figure
plt.figure(figsize=(12, 8))

# Create a heatmap of the correlation matrix
sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', linewidths=0.5)

# Display the plot
plt.show()
