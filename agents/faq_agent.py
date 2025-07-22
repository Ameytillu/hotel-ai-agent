import json

with open("data/rag_database.json", "r") as f:
    rag_data = json.load(f)

def search_rag_database(query):
    query_lower = query.lower()

    # Search rooms
    for room in rag_data.get("rooms", []):
        if query_lower in room["type"].lower() or query_lower in room["description"].lower():
            return format_room_response(room)

    # Search amenities
    for amenity in rag_data.get("amenities", []):
        if query_lower in amenity["name"].lower() or query_lower in amenity["description"].lower():
            return format_amenity_response(amenity)

    # Search services
    for service in rag_data.get("services", []):
        if query_lower in service["name"].lower() or query_lower in service["details"].lower():
            return format_service_response(service)

    # Search policies
    for policy in rag_data.get("hotel_policies", []):
        if query_lower in policy["title"].lower() or query_lower in policy["details"].lower():
            return f"{policy['title']}: {policy['details']}"

    return "Sorry, I couldn’t find anything related to your question."

def format_room_response(room):
    return f"""🛏️ Room: {room['type']}
{room['description']}
💵 Price: {room['price']}
📸 Image: {room['image_link']}
🎥 Video: {room['video_link']}
"""

def format_amenity_response(amenity):
    return f"""✨ Amenity: {amenity['name']}
{amenity['description']}
📸 Image: {amenity['image_link']}
"""

def format_service_response(service):
    return f"""🛎️ Service: {service['name']}
{service['details']}
🕒 Hours: {service['hours']}
📸 Image: {service['image_link']}
"""