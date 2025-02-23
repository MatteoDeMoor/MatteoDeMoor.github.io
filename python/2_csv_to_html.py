import csv

csv_file_path = 'D:/Hogent/Visual Studio Code/Projecten/SiteGithub/MatteoDeMoor.github.io/csv/Shirts.csv'

# Open de CSV file
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Verzamel alle rijen in een lijst en draai deze om (van onder naar boven)
    rows = list(reader)
    rows.reverse()

    # Begin de HTML-inhoud
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="css/style.css">
        <link rel="stylesheet" href="css/style2.css">
        <link rel="icon" href="./images/ai2.png" type="image/x-icon">
        <title>Shirt Collection - Matteo De Moor</title>
        <style>
            /* CSS voor een nette presentatie */
            .player-info, .extra-info {
                text-align: center;
                margin-top: 10px;
                font-weight: bold;
            }
            .shirt-section {
                margin-bottom: 40px;
                border-bottom: 1px solid #ccc;
                padding-bottom: 20px;
            }
            .photo-row {
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
            }
            .photo {
                max-width: 300px;
            }
            .shirt-details {
                text-align: center;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Shirt Collection</h1>
        </header>

        <nav>
            <ul>
                <li><a href="index.html">Homepage</a></li>
                <li><a href="shirts.html">Shirts</a></li>
                <li><a href="bike.html">Bike</a></li>
            </ul>
        </nav>

        <main>
            <section>
                <h2>My personal shirt collection</h2>
                <p>Here you can find my unique Club Brugge shirts collection.</p>
    """

    # Teller voor shirts
    shirt_counter = 1

    # Loop door elke rij in de CSV
    for row in rows:
        shirt_team = "Club Brugge"  # hardcoded
        shirt_season = row['Seizoen']
        shirt_type = row['Shirt']
        shirt_size = row['Maat']
        shirt_player = row['Speler']
        shirt_number = row['Nummer']
        shirt_extra = row['Extra']
        shirt_future = row['Toekomst']
        shirt_signatures = row['Handtekeningen']

        # Stel paden samen voor de foto's (indien aanwezig)
        image1 = f"./shirtImages/{row['Foto1']}" if row['Foto1'] else ""
        image2 = f"./shirtImages/{row['Foto2']}" if row['Foto2'] else ""
        image3 = f"./shirtImages/{row['Foto3']}" if row['Foto3'] else ""
        
        # Begin de HTML voor deze shirtsectie
        html_content += f"""
        <!-- Shirt {shirt_counter} (ID: {row['ID']}) -->
        <div class="shirt-section">
            <h3>{shirt_team} {shirt_season} {shirt_type} - Size: {shirt_size}</h3>
            <div class="photo-row">
        """
        
        # Eerste foto
        if image1:
            html_content += f"""
                <div class="photo">
                    <img src="{image1}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
            """

        # Tweede foto
        if image2:
            html_content += f"""
                <div class="photo">
                    <img src="{image2}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
            """

        # Derde foto
        if image3:
            html_content += f"""
                <div class="photo">
                    <img src="{image3}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
            """
        
        html_content += "</div>"  # sluit de photo-row

        # Toon spelerinformatie (indien ingevuld)
        if shirt_player and shirt_number.strip():
            html_content += f"""
            <div class="player-info">Player: {shirt_player} - Number: {shirt_number}</div>
            """

        # Voeg de extra details toe indien beschikbaar
        # html_content += '<div class="shirt-details">'
        # if shirt_value:
        #     html_content += f"<p>Value: {shirt_value}</p>"
        # if shirt_extra:
        #     html_content += f"<p>Extra: {shirt_extra}</p>"
        # if shirt_future:
        #     html_content += f"<p>Future: {shirt_future}</p>"
        # if shirt_signatures:
        #     html_content += f"<p>Signatures: {shirt_signatures}</p>"
        # html_content += "</div>"

        # Sluit de shirtsectie
        html_content += """
        </div>
        """
        
        # Verhoog de teller
        shirt_counter += 1

    # Sluit de HTML-inhoud af
    html_content += """
            </section>
        </main>
    </body>
    </html>
    """
    
    # Schrijf de HTML naar een bestand
    with open('D:/Hogent/Visual Studio Code/Projecten/SiteGithub/MatteoDeMoor.github.io/shirts.html', 'w', encoding='utf-8') as htmlfile:
        htmlfile.write(html_content)

print("HTML file has been generated successfully.")
