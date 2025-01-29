import csv

# Pad naar het bestaande CSV-bestand
input_file_path = 'D:/Hogent/Visual Studio Code/Projecten/SiteGithub/MatteoDeMoor.github.io/csv/shirts.csv'

# Pad naar het nieuwe CSV-bestand (met ID-kolom)
output_file_path = 'D:/Hogent/Visual Studio Code/Projecten/SiteGithub/MatteoDeMoor.github.io/csv/shirts_updated.csv'

# 1. Lees de inhoud van de CSV in.
with open(input_file_path, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    rows = list(reader)

# 2. Voeg vooraan een kolomtitel 'ID' toe in de header (eerste rij)
rows[0].insert(0, 'ID')

# 3. Vul de ID-waarden in (starten vanaf 1, bijvoorbeeld)
for i, row in enumerate(rows[1:], start=1):
    row.insert(0, str(i))

# 4. Schrijf de gewijzigde data uit naar een nieuw CSV-bestand.
with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(rows)

print(f"CSV met ID-kolom is weggeschreven naar: {output_file_path}")
