import csv

csv_file_path = 'D:/Hogent/Visual Studio Code/Projecten/SiteGithub/MatteoDeMoor.github.io/csv/Shirts.csv'

# Open the CSV file
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Collect all rows into a list and reverse them (so newest appear first)
    rows = list(reader)
    rows.reverse()

    # Start the HTML content
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
            /* CSS for a clean presentation */
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
            </ul>
        </nav>

        <main>
            <section>
                <h2>My personal shirt collection</h2>
                <p>Here you can find my unique Club Brugge shirts collection.</p>
    """

    # Counter for shirts
    shirt_counter = 1

    # Loop through each row in the CSV
    for row in rows:
        shirt_team       = "Club Brugge"  # hardcoded
        shirt_season     = row['Seizoen']
        shirt_type       = row['Shirt']
        shirt_size       = row['Maat']
        shirt_player     = row['Speler']
        shirt_number     = row['Nummer']
        shirt_extra      = row['Extra']
        shirt_future     = row['Toekomst']
        shirt_signatures = row['Handtekeningen']

        # Construct paths for the photos (if present)
        image1 = f"./shirtImages/{row['Foto1']}" if row['Foto1'] else ""
        image2 = f"./shirtImages/{row['Foto2']}" if row['Foto2'] else ""
        image3 = f"./shirtImages/{row['Foto3']}" if row['Foto3'] else ""
        
        # Start HTML for this shirt section
        html_content += f"""
        <!-- Shirt {shirt_counter} (ID: {row['ID']}) -->
        <div class="shirt-section">
            <h3>{shirt_team} {shirt_season} {shirt_type} - Size: {shirt_size}</h3>
            <div class="photo-row">
        """
        
        # First photo
        if image1:
            html_content += f"""
                <div class="photo">
                    <img src="{image1}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
            """

        # Second photo
        if image2:
            html_content += f"""
                <div class="photo">
                    <img src="{image2}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
            """

        # Third photo
        if image3:
            html_content += f"""
                <div class="photo">
                    <img src="{image3}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
            """
        
        html_content += "</div>"  # close .photo-row

        # Display player information (if provided)
        if shirt_player and shirt_number.strip():
            extra_text = " - Matchworn" if shirt_extra == "Matchworn" else ""
            html_content += f"""
            <div class="player-info">Player: {shirt_player} - Number: {shirt_number}{extra_text}</div>
            """

        # Close the shirt section
        html_content += """
        </div>
        """
        
        # Increment the counter
        shirt_counter += 1

    # Close the HTML content
    html_content += """
            </section>
        </main>
    </body>
    </html>
    """
    
    # Write the HTML to a file
    with open('D:/Hogent/Visual Studio Code/Projecten/SiteGithub/MatteoDeMoor.github.io/shirts.html', 'w', encoding='utf-8') as htmlfile:
        htmlfile.write(html_content)

print("HTML file has been generated successfully.")
