import sqlite3
from foudinge.entities import Summary
import networkx as nx
from typing import Tuple
import xml.sax.saxutils as saxutils


def get_entities(db_name) -> list[Tuple[str, str, str, str, str]]:
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT
          reviews.url, title, review, entities, clean
          FROM reviews
          JOIN inferred_entities_openai ON reviews.url = inferred_entities_openai.url""")
        data = cursor.fetchall()
    return data


def normalize_text(text):
    """Normalize text to ensure consistent handling of accented characters"""
    if isinstance(text, str):
        # First decode any unicode escape sequences
        return text.encode("utf-8").decode("utf-8", errors="ignore").strip()
    return str(text).strip()


db_name = "reviews.db"

entities = get_entities(db_name)

# First collect all nodes with consistent encoding
restaurants = set([normalize_text(title) for _, title, _, _, _ in entities])
title_to_url = {normalize_text(title): url for url, title, _, _, _ in entities}

# Parse all entities to collect people and their previous restaurants
all_people = set()
all_restaurants = set(restaurants)  # Start with known restaurants from titles

for _, _, _, entity, clean in entities:
    entity_data = clean if clean else entity
    try:
        obj = Summary.model_validate_json(entity_data)
        for person in obj.people:
            normalized_name = normalize_text(person.name)
            all_people.add(normalized_name)
            for restaurant in person.previous_restaurants:
                normalized_restaurant = normalize_text(restaurant)
                all_restaurants.add(normalized_restaurant)
    except Exception as e:
        print(f"Error parsing entity data: {e}")
        continue

# Create graph with properly typed nodes
g = nx.Graph()

# Add all nodes with appropriate types first
for restaurant in all_restaurants:
    g.add_node(restaurant, type="restaurant")
    # Add URL for restaurants that are in the title column
    if restaurant in title_to_url:
        g.nodes[restaurant]["url"] = f"https://lefooding.com/{title_to_url[restaurant]}"

for person in all_people:
    g.add_node(person, type="person")

# Now add edges
for url, title, review, entity, clean in entities:
    entity_data = clean if clean else entity
    try:
        obj = Summary.model_validate_json(entity_data)
        normalized_title = normalize_text(title)

        for person in obj.people:
            normalized_name = normalize_text(person.name)
            if not g.has_edge(normalized_name, normalized_title):
                g.add_edge(normalized_name, normalized_title)
            for restaurant in person.previous_restaurants:
                normalized_restaurant = normalize_text(restaurant)
                if not g.has_edge(normalized_name, normalized_restaurant):
                    g.add_edge(normalized_name, normalized_restaurant)
    except Exception as e:
        print(f"Error adding edges: {e}")
        continue

# Verify all nodes have a type attribute
for node in g.nodes():
    if "type" not in g.nodes[node]:
        print(f"Warning: Node '{node}' has no type attribute")
        g.nodes[node]["type"] = "restaurant"  # Default to restaurant


# Custom GEXF writer to handle encoding issues
def write_gexf_with_encoding(G, path):
    from networkx.readwrite.gexf import generate_gexf
    import xml.dom.minidom

    gexf_string = "\n".join(generate_gexf(G, encoding="utf-8", prettyprint=True))

    # Parse the GEXF string to a DOM object
    dom = xml.dom.minidom.parseString(gexf_string)

    # Write the DOM object to the file with UTF-8 encoding
    with open(path, "w", encoding="utf-8") as f:
        dom.writexml(f, encoding="utf-8", newl="\n", addindent="  ")


# Use NetworkX's built-in writer with explicit encoding
try:
    nx.write_gexf(
        g,
        "restaurant_personnel_network.gexf",
        encoding="utf-8",
        prettyprint=True,
        version="1.2draft",
    )
except Exception as e:
    print(f"Error using standard GEXF writer: {e}")
    # Fall back to custom writer if needed
    write_gexf_with_encoding(g, "restaurant_personnel_network.gexf")

print(f"Graph written with {len(g.nodes())} nodes and {len(g.edges())} edges")
