import subprocess

# Lijst met scripts in de gewenste uitvoer-volgorde
scripts = [
    "1_excel_to_csv.py",
    "2_add_id_to_csv.py",
    "3_csv_to_html.py"
]

for script in scripts:
    subprocess.run(["python", script], check=True)
