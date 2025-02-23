import pandas as pd
import os

# Lees het Excel-bestand in
df = pd.read_excel(
    r'D:\Hogent\Visual Studio Code\Projecten\SiteGithub\MatteoDeMoor.github.io\excel\Club_Shirts.xlsx'
)

# Filter de DataFrame zodat alleen rijen met een numerieke 'ID' behouden blijven
df = df[pd.to_numeric(df['ID'], errors='coerce').notna()]

# Verwijder de kolom 'Waarde' als deze bestaat
if 'Waarde' in df.columns:
    df.drop('Waarde', axis=1, inplace=True)

# Converteer de kolom 'Nummer':
if 'Nummer' in df.columns:
    # Eerst naar string, daarna verwijderen we een trailing '.0'
    df['Nummer'] = df['Nummer'].astype(str).str.replace(r'\.0$', '', regex=True)
    # Vervang de string "nan" (die ontstaat bij NaN-waarden) door een lege string
    df.loc[df['Nummer'] == 'nan', 'Nummer'] = ''

# Bepaal de output directory en maak deze aan als deze nog niet bestaat
output_dir = r'D:\Hogent\Visual Studio Code\Projecten\SiteGithub\MatteoDeMoor.github.io\csv'
os.makedirs(output_dir, exist_ok=True)

# Stel het volledige pad voor de CSV in
output_path = os.path.join(output_dir, 'Shirts.csv')

# Sla de DataFrame op als CSV
df.to_csv(output_path, index=False)

print("The excel file has been succesfully converted to a CSV file.")
