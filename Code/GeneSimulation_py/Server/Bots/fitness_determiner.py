import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load data
df = pd.read_csv('fitness.csv')

# Normalize 'Average' and 'Max' to [0, 1] range
scaler = MinMaxScaler()
df[['Average_scaled', 'Max_scaled']] = scaler.fit_transform(df[['Average', 'Max']])

# Combine both metrics with equal weight (or tweak if you want)
df['Score'] = df['Average_scaled'] + df['Max_scaled']

# Get the generation with the highest combined score
best_row = df.loc[df['Score'].idxmax()]
print("This was the best row ", best_row)