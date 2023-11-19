import pandas as pd

# Load the dataset
df = pd.read_csv('data.csv')

# Remove duplicate skills
df_no_duplicates = df.drop_duplicates(subset='Skill')

# Save the cleaned dataset to a new CSV file
df_no_duplicates.to_csv('cleaned_dataset.csv', index=False)

print("Duplicate skills removed. Cleaned dataset saved.")
