import pandas as pd
import os

# Read the Excel file into a DataFrame
df = pd.read_excel(
    r'D:\Hogent\Visual Studio Code\Projecten\SiteGithub\MatteoDeMoor.github.io\excel\Club_Shirts.xlsx'
)

# Keep only rows where 'ID' is numeric
df = df[pd.to_numeric(df['ID'], errors='coerce').notna()]

# Drop the 'Waarde' column if it exists
if 'Waarde' in df.columns:
    df.drop('Waarde', axis=1, inplace=True)

# Convert the 'Nummer' column
if 'Nummer' in df.columns:
    # First convert to string, then remove any trailing '.0'
    df['Nummer'] = df['Nummer'].astype(str).str.replace(r'\.0$', '', regex=True)
    # Replace the literal string "nan" (resulting from NaN) with an empty string
    df.loc[df['Nummer'] == 'nan', 'Nummer'] = ''

# Define the output directory and create it if it doesn't exist
output_dir = r'D:\Hogent\Visual Studio Code\Projecten\SiteGithub\MatteoDeMoor.github.io\csv'
os.makedirs(output_dir, exist_ok=True)

# Define the full path for the CSV file
output_path = os.path.join(output_dir, 'Shirts.csv')

# Save the DataFrame as a CSV (without the index column)
df.to_csv(output_path, index=False)

print("The Excel file has been successfully converted to a CSV file.")
