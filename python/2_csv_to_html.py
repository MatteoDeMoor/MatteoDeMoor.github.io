import csv
import html
import json
from pathlib import Path

BASE_URL = "https://matteodemoor.github.io"
SITE_NAME = "Matteo De Moor"
COLLECTION_URL = f"{BASE_URL}/shirts.html"
DEFAULT_IMAGE = f"{BASE_URL}/images/Matteo.jpg"
TEAM_NAME = "Club Brugge"
TEAM_SAME_AS = "https://www.clubbrugge.be/"

base_dir = Path(__file__).resolve().parents[1]
csv_file_path = base_dir / "csv" / "shirts.csv"
output_path = base_dir / "shirts.html"


def clean(value):
    return (value or "").strip()


def esc(value):
    return html.escape(clean(value), quote=True)


def absolute_image(filename):
    filename = clean(filename)
    return f"{BASE_URL}/shirtImages/{filename}" if filename else ""


def local_image(filename):
    filename = clean(filename)
    return f"./shirtImages/{filename}" if filename else ""


def unique_case_insensitive(values):
    unique = {}
    for value in values:
        value = clean(value)
        if value:
            unique.setdefault(value.casefold(), value)
    return sorted(unique.values(), key=str.casefold)


def first_image(row):
    for key in ("Foto1", "Foto2", "Foto3"):
        image = absolute_image(row.get(key, ""))
        if image:
            return image
    return DEFAULT_IMAGE


def shirt_name(row):
    season = clean(row.get("Seizoen"))
    shirt_type = clean(row.get("Shirt"))
    player = clean(row.get("Speler"))
    number = clean(row.get("Nummer"))
    base = f"{TEAM_NAME} {season} {shirt_type} shirt"
    if player and number:
        return f"{base} - {player} #{number}"
    if player:
        return f"{base} - {player}"
    if number:
        return f"{base} - #{number}"
    return base


def shirt_description(row):
    parts = [shirt_name(row)]
    size = clean(row.get("Maat"))
    extra = clean(row.get("Extra"))
    signatures = clean(row.get("Handtekeningen"))
    if size:
        parts.append(f"Size {size}")
    if extra:
        parts.append(extra)
    if signatures:
        parts.append(f"signed by {signatures}")
    return ", ".join(parts) + "."


def build_schema(rows, players, seasons, shirt_types):
    item_list = []
    for position, row in enumerate(rows, start=1):
        row_id = clean(row.get("ID"))
        item_url = f"{COLLECTION_URL}#shirt-{row_id}"
        player = clean(row.get("Speler"))
        images = [absolute_image(row.get(key, "")) for key in ("Foto1", "Foto2", "Foto3")]
        images = [image for image in images if image]
        item = {
            "@type": "ListItem",
            "position": position,
            "url": item_url,
            "item": {
                "@type": "Product",
                "@id": item_url,
                "name": shirt_name(row),
                "description": shirt_description(row),
                "category": "Football shirt",
                "brand": {
                    "@type": "SportsTeam",
                    "name": TEAM_NAME,
                    "sameAs": TEAM_SAME_AS,
                },
                "image": images or [DEFAULT_IMAGE],
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Season", "value": clean(row.get("Seizoen"))},
                    {"@type": "PropertyValue", "name": "Shirt type", "value": clean(row.get("Shirt"))},
                    {"@type": "PropertyValue", "name": "Size", "value": clean(row.get("Maat"))},
                ],
            },
        }
        if player:
            item["item"]["about"] = {"@type": "Person", "name": player}
        if clean(row.get("Nummer")):
            item["item"]["additionalProperty"].append(
                {"@type": "PropertyValue", "name": "Squad number", "value": clean(row.get("Nummer"))}
            )
        if clean(row.get("Extra")):
            item["item"]["additionalProperty"].append(
                {"@type": "PropertyValue", "name": "Collectible status", "value": clean(row.get("Extra"))}
            )
        if clean(row.get("Handtekeningen")):
            item["item"]["additionalProperty"].append(
                {"@type": "PropertyValue", "name": "Signatures", "value": clean(row.get("Handtekeningen"))}
            )
        item_list.append(item)

    graph = [
        {
            "@type": "CollectionPage",
            "@id": f"{COLLECTION_URL}#collection",
            "url": COLLECTION_URL,
            "name": "Club Brugge Shirt Collection – Matteo De Moor",
            "headline": "Club Brugge football shirt collection with players, seasons and matchworn shirts",
            "description": "A personal searchable archive of Club Brugge football shirts with photos, seasons, sizes, player names, shirt numbers, matchworn shirts and signed shirts.",
            "isPartOf": {"@id": f"{BASE_URL}/#website"},
            "publisher": {"@id": f"{BASE_URL}/#person"},
            "about": [
                {"@type": "SportsTeam", "name": TEAM_NAME, "sameAs": TEAM_SAME_AS},
                "Club Brugge shirts",
                "Football shirts",
                "Matchworn football shirts",
                "Signed football shirts",
                *players[:25],
            ],
            "keywords": [
                "Club Brugge shirt collection",
                "Club Brugge football shirts",
                "Club Brugge matchworn shirt",
                "Club Brugge signed shirt",
                *players,
                *seasons,
                *shirt_types,
            ],
            "primaryImageOfPage": {"@type": "ImageObject", "url": first_image(rows[0]) if rows else DEFAULT_IMAGE},
            "inLanguage": "en",
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{COLLECTION_URL}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Shirt Collection", "item": COLLECTION_URL},
            ],
        },
        {
            "@type": "ItemList",
            "@id": f"{COLLECTION_URL}#shirt-list",
            "name": "Club Brugge shirts by Matteo De Moor",
            "numberOfItems": len(rows),
            "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "itemListElement": item_list,
        },
    ]
    return {"@context": "https://schema.org", "@graph": graph}


with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)
    rows.reverse()

players = unique_case_insensitive(row.get("Speler", "") for row in rows)
seasons = unique_case_insensitive(row.get("Seizoen", "") for row in rows)
shirt_types = unique_case_insensitive(row.get("Shirt", "") for row in rows)
collectible_statuses = unique_case_insensitive(row.get("Extra", "") for row in rows)

player_keyword_preview = ", ".join(players[:18])
keyword_content = ", ".join(
    [
        "Club Brugge shirts",
        "Club Brugge shirt collection",
        "Club Brugge matchworn shirts",
        "Club Brugge signed shirts",
        "football shirt collection",
        *players,
        *seasons,
        *shirt_types,
        *collectible_statuses,
    ]
)
meta_description = (
    f"Browse Matteo De Moor's searchable Club Brugge football shirt collection: {len(rows)} shirts with photos, "
    f"seasons, sizes, shirt numbers, matchworn and signed shirts, including players such as {player_keyword_preview}."
)
social_description = (
    "A searchable personal archive of Club Brugge football shirts with photos, seasons, shirt numbers, "
    "player names, matchworn shirts and signed shirts."
)
schema_json = json.dumps(build_schema(rows, players, seasons, shirt_types), ensure_ascii=False, indent=8)
page_image = first_image(rows[0]) if rows else DEFAULT_IMAGE

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Club Brugge Shirt Collection, Players & Matchworn Shirts – Matteo De Moor</title>

    <meta name="description" content="{esc(meta_description)}" />
    <meta name="keywords" content="{esc(keyword_content)}" />
    <meta name="author" content="Matteo De Moor" />
    <meta name="robots" content="index, follow, max-image-preview:large" />
    <meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />

    <link rel="canonical" href="{COLLECTION_URL}" />

    <!-- Open Graph -->
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="{SITE_NAME}" />
    <meta property="og:title" content="Club Brugge Shirt Collection, Players & Matchworn Shirts – Matteo De Moor" />
    <meta property="og:description" content="{esc(social_description)}" />
    <meta property="og:image" content="{page_image}" />
    <meta property="og:image:alt" content="Club Brugge football shirt from Matteo De Moor's collection" />
    <meta property="og:url" content="{COLLECTION_URL}" />
    <meta property="og:locale" content="en_US" />

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="Club Brugge Shirt Collection, Players & Matchworn Shirts – Matteo De Moor" />
    <meta name="twitter:description" content="{esc(social_description)}" />
    <meta name="twitter:image" content="{page_image}" />
    <meta name="twitter:image:alt" content="Club Brugge football shirt from Matteo De Moor's collection" />

    <link rel="stylesheet" href="css/style2.css">
    <link rel="stylesheet" href="css/style.css">

    <link rel="icon" href="./images/ai2.png" type="image/x-icon">

    <script src="js/main.js" defer></script>
    <script src="js/shirts.js" defer></script>

    <script type="application/ld+json">
{schema_json}
    </script>
</head>
<body class="home-page collection-page">
    <header class="top-bar command-nav">
      <nav>
        <a href="index.html">Homepage</a>
        <a href="shirts.html">Shirt Collection</a>
      </nav>
    </header>

    <main>
        <section class="collection-shell" itemscope itemtype="https://schema.org/CollectionPage">
            <div class="collection-intro">
                <span class="panel-kicker">Club Brugge archive</span>
                <h1 itemprop="name">My personal Club Brugge shirt collection</h1>
                <p itemprop="description">Here you can find my unique, searchable Club Brugge shirts collection with player names, shirt numbers, seasons, sizes, matchworn shirts and signed shirts.</p>
                <p class="collection-meta">This archive contains {len(rows)} Club Brugge shirts across {len(seasons)} seasons and {len(players)} named players, including {esc(player_keyword_preview)}.</p>
            </div>
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

shirt_counter = 1

for row in rows:
    shirt_team = TEAM_NAME
    shirt_id = clean(row["ID"])
    shirt_season = clean(row["Seizoen"])
    shirt_type = clean(row["Shirt"])
    shirt_size = clean(row["Maat"])
    shirt_player = clean(row["Speler"])
    shirt_number = clean(row["Nummer"])
    shirt_extra = clean(row["Extra"])
    shirt_signatures = clean(row["Handtekeningen"])

    image1 = local_image(row["Foto1"])
    image2 = local_image(row["Foto2"])
    image3 = local_image(row["Foto3"])
    images = [image for image in (image1, image2, image3) if image]

    collectible_value = shirt_extra.lower()
    collectible_attr = f' data-collectible="{esc(collectible_value)}"' if collectible_value else ""
    player_attr = f' data-player="{esc(shirt_player.lower())}"' if shirt_player else ""
    section_id = f"shirt-{esc(shirt_id)}"
    title = shirt_name(row)
    title_with_size = f"{title} - Size: {shirt_size}" if shirt_size else title
    article_keywords = ", ".join(filter(None, [shirt_team, shirt_season, shirt_type, shirt_player, shirt_number, shirt_extra]))

    html_content += f"""
        <!-- Shirt {shirt_counter} (ID: {esc(shirt_id)}) -->
        <article id="{section_id}" class="shirt-section"{collectible_attr}{player_attr} itemscope itemtype="https://schema.org/Product" itemprop="hasPart">
            <meta itemprop="name" content="{esc(title)}">
            <meta itemprop="description" content="{esc(shirt_description(row))}">
            <meta itemprop="category" content="Football shirt">
            <meta itemprop="keywords" content="{esc(article_keywords)}">
            <h3>{esc(title_with_size)}</h3>
            <div class="photo-row">
    """

    for image_index, image in enumerate(images, start=1):
        alt_parts = [shirt_team, shirt_season, shirt_type, "shirt"]
        if shirt_player:
            alt_parts.append(f"worn by or printed for {shirt_player}")
        if shirt_number:
            alt_parts.append(f"number {shirt_number}")
        if shirt_extra:
            alt_parts.append(shirt_extra)
        alt_text = " ".join(alt_parts)
        html_content += f"""
                <figure class="photo" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
                    <img src="{esc(image)}" alt="{esc(alt_text)}" title="{esc(title)} photo {image_index}" loading="lazy" itemprop="contentUrl">
                    <meta itemprop="caption" content="{esc(alt_text)}">
                </figure>
        """

    html_content += "\n            </div>"

    if shirt_player or shirt_number:
        if shirt_player and shirt_number:
            player_text = f"Player: {shirt_player} - Number: {shirt_number}"
        elif shirt_player:
            player_text = f"Player: {shirt_player}"
        else:
            player_text = f"Number: {shirt_number}"
        html_content += f"""
            <div class="player-info">{esc(player_text)}</div>
        """

    detail_items = [
        ("Season", shirt_season),
        ("Type", shirt_type),
        ("Size", shirt_size),
    ]
    if shirt_player:
        detail_items.append(("Player", shirt_player))
    if shirt_number:
        detail_items.append(("Number", shirt_number))
    if shirt_extra:
        detail_items.append(("Status", shirt_extra))
    if shirt_signatures:
        detail_items.append(("Signatures", shirt_signatures))

    if shirt_extra:
        html_content += f"""
            <div class="collectible-info">Status: {esc(shirt_extra)}</div>
        """

    html_content += "\n            <dl class=\"shirt-metadata\" aria-label=\"Shirt metadata\">"
    for label, value in detail_items:
        html_content += f"<dt>{esc(label)}</dt><dd>{esc(value)}</dd>"
    html_content += "</dl>"

    html_content += """
        </article>
    """
    shirt_counter += 1

html_content += """
        </section>
    </main>
</body>
</html>
"""

html_content = "\n".join(line.rstrip() for line in html_content.splitlines()).lstrip() + "\n"

with open(output_path, "w", encoding="utf-8") as htmlfile:
    htmlfile.write(html_content)

print("HTML file has been generated successfully.")
