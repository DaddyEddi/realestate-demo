LISTINGS = [
    {
        "id": 1,
        "address": "123 Oak Street, Austin, TX",
        "price": 450000,
        "bedrooms": 3,
        "bathrooms": 2,
        "sqft": 1850,
        "description": "Charming single-family home in quiet neighborhood. Updated kitchen, hardwood floors, large backyard. Close to top-rated schools."
    },
    {
        "id": 2,
        "address": "456 Maple Ave, Austin, TX",
        "price": 625000,
        "bedrooms": 4,
        "bathrooms": 3,
        "sqft": 2400,
        "description": "Modern home with open floor plan. Chef's kitchen, master suite with walk-in closet, 2-car garage. Great for families."
    },
    {
        "id": 3,
        "address": "789 Pine Road, Austin, TX",
        "price": 320000,
        "bedrooms": 2,
        "bathrooms": 1,
        "sqft": 1200,
        "description": "Cozy starter home. Recently renovated bathroom, new roof 2023, energy-efficient windows. Walking distance to parks."
    },
    {
        "id": 4,
        "address": "321 Elm Boulevard, Austin, TX",
        "price": 890000,
        "bedrooms": 5,
        "bathrooms": 4,
        "sqft": 3600,
        "description": "Luxury property in premium location. Pool, home office, gourmet kitchen, smart home system. Top school district."
    },
    {
        "id": 5,
        "address": "654 Cedar Lane, Austin, TX",
        "price": 510000,
        "bedrooms": 3,
        "bathrooms": 2,
        "sqft": 2100,
        "description": "Stunning renovated home. New kitchen with quartz countertops, spa-like master bath, covered patio. Move-in ready."
    }
]

def get_listings_context():
    context = "Available properties:\n\n"
    for l in LISTINGS:
        context += f"""Property #{l['id']}
Address: {l['address']}
Price: ${l['price']:,}
Bedrooms: {l['bedrooms']} | Bathrooms: {l['bathrooms']} | Size: {l['sqft']} sqft
Description: {l['description']}

"""
    return context