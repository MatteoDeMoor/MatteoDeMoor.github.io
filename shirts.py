import csv

csv_file_path = 'D:/Hogent/Visual Studio Code/Projecten/SiteGithub/MatteoDeMoor.github.io/csv/shirts.csv'


# Open the CSV file
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Collect all rows in a list
    rows = list(reader)
    
    # Reverse the rows list to go through the CSV from bottom to top
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
            /* Additional CSS to center player info */
            .player-info {
                text-align: center;
                margin-top: 10px;
                font-weight: bold;
            }
            .photo-row {
                display: flex;
                justify-content: center;
                gap: 20px;
            }
            .photo {
                max-width: 300px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Shirt collection</h1>
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
    
    # Dynamische teller voor shirts van 1 tot 70
    shirt_counter = 1
    
    # Loop door elke rij in de omgekeerde lijst
    for row in rows:
        shirt_team = row['Team']
        shirt_season = row['Seizoen']
        shirt_type = row['Type']
        shirt_size = row['Maat']
        shirt_player = row['Speler']
        shirt_number = row['Nummer']

        # Update image paths to reference the 'shirtImages' folder
        image1 = f"./shirtImages/{row['Foto1']}" if row['Foto1'] else ""
        image2 = f"./shirtImages/{row['Foto2']}" if row['Foto2'] else ""
        image3 = f"./shirtImages/{row['Foto3']}" if row['Foto3'] else ""  # Optional image
        
        # HTML structure for the shirt section
        html_content += f"""
        <!-- Shirt {shirt_counter} -->
        <div class="shirt-section">
            <h3>{shirt_team} {shirt_season} {shirt_type} shirt - Size: {shirt_size}</h3>
            <div class="photo-row">
                <div class="photo">
                    <img src="{image1}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
        """
        
        # Only add the second and third images if they exist
        if image2:
            html_content += f"""
                <div class="photo">
                    <img src="{image2}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
            """
        if image3:
            html_content += f"""
                <div class="photo">
                    <img src="{image3}" alt="{shirt_team} {shirt_season} {shirt_type} shirt" loading="lazy">
                </div>
            """
        
        # Add the player's name and number if they exist, centered below the photos
        if shirt_player and shirt_number.strip():
            html_content += f"""
            <div class="player-info">Player: {shirt_player} - Number: {shirt_number}</div>
            """
        
        # Close the shirt section
        html_content += """
        </div>
        </div>
        """
        
        # Verhoog de shirt teller
        shirt_counter += 1

    # Close the main content and body
    html_content += """
            </section>
        </main>
    </body>
    </html>
    """
    
    # Save the generated HTML to a file
    with open('D:/Hogent/Visual Studio Code/Projecten/SiteGithub/MatteoDeMoor.github.io/shirts.html', 'w', encoding='utf-8') as htmlfile:
        htmlfile.write(html_content)

print("HTML file has been generated successfully.")
