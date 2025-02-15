import pandas as pd
import os

# Lees het Excel-bestand in
df = pd.read_excel(
    r'D:\Hogent\Visual Studio Code\Projecten\SiteGithub\MatteoDeMoor.github.io\excel\Club_Shirts.xlsx'
)

# Filter de DataFrame zodat alleen rijen met een numerieke 'ID' behouden blijven
df = df[pd.to_numeric(df['ID'], errors='coerce').notna()]

# Bepaal de output directory en maak deze aan als deze nog niet bestaat
output_dir = r'D:\Hogent\Visual Studio Code\Projecten\SiteGithub\MatteoDeMoor.github.io\csv'
os.makedirs(output_dir, exist_ok=True)

# Stel het volledige pad voor de CSV in
output_path = os.path.join(output_dir, 'shirts_from_excel.csv')

# Converteer de data naar een CSV-bestand en sla het op
df.to_csv(output_path, index=False)
