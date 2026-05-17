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
OFFER_PRICE = "0.00"
OFFER_PRICE_CURRENCY = "EUR"
OFFER_AVAILABILITY = "https://schema.org/OutOfStock"
OFFER_ITEM_CONDITION = "https://schema.org/UsedCondition"

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


def product_offer(item_url):
    return {
        "@type": "Offer",
        "url": item_url,
        "price": OFFER_PRICE,
        "priceCurrency": OFFER_PRICE_CURRENCY,
        "availability": OFFER_AVAILABILITY,
        "itemCondition": OFFER_ITEM_CONDITION,
        "name": "Personal collection item (not for sale)",
    }


def build_schema(rows, players, seasons, shirt_types, brands):
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
                "offers": product_offer(item_url),
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Season", "value": clean(row.get("Seizoen"))},
                    {"@type": "PropertyValue", "name": "Shirt type", "value": clean(row.get("Shirt"))},
                    {"@type": "PropertyValue", "name": "Size", "value": clean(row.get("Maat"))},
                ],
            },
        }
        if clean(row.get("Merk")):
            item["item"]["additionalProperty"].append(
                {"@type": "PropertyValue", "name": "Brand", "value": clean(row.get("Merk"))}
            )
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
                *brands,
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
brands = unique_case_insensitive(row.get("Merk", "") for row in rows)

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
        *brands,
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
schema_json = json.dumps(build_schema(rows, players, seasons, shirt_types, brands), ensure_ascii=False, indent=8)
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
            <div class="collection-heading">
              <div class="collection-intro">
                  <span class="panel-kicker">Club Brugge archive</span>
                  <h1 itemprop="name">My personal shirt collection</h1>
                  <p itemprop="description">Here you can find my unique Club Brugge shirts collection.</p>
              </div>
              <div class="view-toggle collection-view-toggle" aria-label="Choose collection layout">
                <span>View</span>
                <button type="button" id="view-list" class="active" aria-pressed="true">List</button>
                <button type="button" id="view-gallery" aria-pressed="false">Gallery</button>
              </div>
            </div>
            <section class="collection-insights" aria-label="Collection statistics and charts">
              <div id="collection-stats" class="collection-stats" aria-live="polite"></div>
              <div class="collection-charts" aria-label="Collection charts">
                <article class="chart-card">
                  <div class="chart-heading">
                    <span class="panel-kicker">By type</span>
                    <strong>Shirt types</strong>
                  </div>
                  <div id="chart-type" class="chart-bars"></div>
                </article>
                <article class="chart-card">
                  <div class="chart-heading">
                    <span class="panel-kicker">By status</span>
                    <strong>Collectibles</strong>
                  </div>
                  <div id="chart-collectible" class="chart-bars"></div>
                </article>
                <article class="chart-card">
                  <div class="chart-heading">
                    <span class="panel-kicker">By brand</span>
                    <strong>Shirt brands</strong>
                  </div>
                  <div id="chart-brand" class="chart-bars"></div>
                </article>
                <article class="chart-card chart-card-wide">
                  <div class="chart-heading">
                    <span class="panel-kicker">Top seasons</span>
                    <strong>Most represented seasons</strong>
                  </div>
                  <div id="chart-season" class="chart-bars chart-bars-compact"></div>
                </article>
              </div>
            </section>

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
            <p id="filter-results" class="filter-results" aria-live="polite"></p>
            <p id="filter-empty" class="filter-empty" hidden>No shirts match these filters yet. Try clearing the filters or selecting fewer options.</p>
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
    shirt_brand = clean(row.get("Merk"))
    shirt_signatures = clean(row["Handtekeningen"])

    image1 = local_image(row["Foto1"])
    image2 = local_image(row["Foto2"])
    image3 = local_image(row["Foto3"])
    images = [image for image in (image1, image2, image3) if image]

    collectible_value = shirt_extra.lower()
    collectible_attr = f' data-collectible="{esc(collectible_value)}"' if collectible_value else ""
    brand_attr = f' data-brand="{esc(shirt_brand.lower())}" data-brand-label="{esc(shirt_brand)}"' if shirt_brand else ""
    player_attr = f' data-player="{esc(shirt_player.lower())}"' if shirt_player else ""
    section_id = f"shirt-{esc(shirt_id)}"
    title = shirt_name(row)
    visible_title = f"{shirt_team} {shirt_season} {shirt_type} - Size: {shirt_size}"
    article_keywords = ", ".join(filter(None, [shirt_team, shirt_season, shirt_type, shirt_brand, shirt_player, shirt_number, shirt_extra]))

    html_content += f"""
        <!-- Shirt {shirt_counter} (ID: {esc(shirt_id)}) -->
        <article id="{section_id}" class="shirt-section"{collectible_attr}{brand_attr}{player_attr} itemscope itemtype="https://schema.org/Product" itemprop="hasPart">
            <meta itemprop="name" content="{esc(title)}">
            <meta itemprop="description" content="{esc(shirt_description(row))}">
            <meta itemprop="category" content="Football shirt">
            <meta itemprop="keywords" content="{esc(article_keywords)}">
            <div itemprop="offers" itemscope itemtype="https://schema.org/Offer">
                <meta itemprop="name" content="Personal collection item (not for sale)">
                <meta itemprop="price" content="{OFFER_PRICE}">
                <meta itemprop="priceCurrency" content="{OFFER_PRICE_CURRENCY}">
                <link itemprop="availability" href="{OFFER_AVAILABILITY}">
                <link itemprop="itemCondition" href="{OFFER_ITEM_CONDITION}">
                <link itemprop="url" href="{esc(f'{COLLECTION_URL}#shirt-{shirt_id}')}">
            </div>
            <h3>{esc(visible_title)}</h3>
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
                <div class="photo" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
                    <img src="{esc(image)}" alt="{esc(alt_text)}" title="{esc(title)} photo {image_index}" loading="lazy" itemprop="contentUrl">
                    <meta itemprop="caption" content="{esc(alt_text)}">
                </div>
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

    if shirt_extra:
        html_content += f"""
            <div class="collectible-info">Status: {esc(shirt_extra)}</div>
        """

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
