import csv
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
csv_file_path = base_dir / 'csv' / 'shirts.csv'

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
        <title>Shirt Collection - Matteo De Moor</title>
        <meta name="description" content="Browse Matteo De Moor’s unique Club Brugge football shirt collection with photos, seasons, sizes, and players." />
        <link rel="stylesheet" href="css/style.css">
        <link rel="stylesheet" href="css/style2.css">
        <link rel="icon" href="./images/ai2.png" type="image/x-icon">
        <script src="js/main.js" defer></script>
        <script src="js/shirts.js" defer></script>
    </head>
    <body>
        <header class="top-bar">
          <nav>
            <a href="index.html">Homepage</a>
            <a href="shirts.html">Shirt Collection</a>
          </nav>
        </header>

        <main>
            <section>
                <h2>My personal shirt collection</h2>
                <p>Here you can find my unique Club Brugge shirts collection.</p>
                <div class="filter-bar" aria-label="Filter shirts">
                  <div class="filter-group">
                    <label for="filter-season">Season</label>
                    <select id="filter-season" multiple size="5" aria-label="Filter by season"></select>
                  </div>
                  <div class="filter-group">
                    <label for="filter-type">Type</label>
                    <select id="filter-type" multiple size="5" aria-label="Filter by type"></select>
                  </div>
                <div class="filter-group">
                    <label for="filter-size">Size</label>
                    <select id="filter-size" multiple size="5" aria-label="Filter by size"></select>
                  </div>
                  <div class="filter-group">
                    <label for="filter-collectible">Collectible</label>
                    <select id="filter-collectible" multiple size="5" aria-label="Filter by collectible status"></select>
                  </div>
                  <div class="filter-group filter-group--player">
                    <label for="filter-player">Player</label>
                    <select id="filter-player" multiple size="5" aria-label="Filter by player"></select>
                  </div>
                  <div class="filter-actions">
                    <button id="filter-clear">Clear</button>
                  </div>
                </div>
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
        collectible_value = (shirt_extra or "").strip().lower()
        collectible_attr = f' data-collectible="{collectible_value}"' if collectible_value else ""

        html_content += f"""
        <!-- Shirt {shirt_counter} (ID: {row['ID']}) -->
        <div class="shirt-section"{collectible_attr}>
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
            html_content += f"""
            <div class="player-info">Player: {shirt_player} - Number: {shirt_number}</div>
            """

        if shirt_extra:
            html_content += f"""
            <div class="collectible-info">Status: {shirt_extra}</div>
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
    output_path = base_dir / 'shirts.html'
    with open(output_path, 'w', encoding='utf-8') as htmlfile:
        htmlfile.write(html_content)

print("HTML file has been generated successfully.")
