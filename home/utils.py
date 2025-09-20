import random
import re
from typing import List
from django.db.models import QuerySet
from home.models import Zone

def generate_user_id(first_name: str, last_name: str) -> str:
    """
    Generates a user ID using:
    - First letter of first name (uppercase)
    - First letter of last name (uppercase)
    - A 4-digit random number
    """
    first_initial = first_name[0].upper() if first_name else 'X'
    last_initial = last_name[0].upper() if last_name else 'X'
    random_number = random.randint(1000, 9999)
    return f"{first_initial}{last_initial}{random_number}"

def generate_zone_id(zone_name: str) -> str:
    """
    Generates a unique, human-readable zone ID without numbers by:
    1. Converting to lowercase
    2. Removing special characters and spaces
    3. Using initials for multi-word names
    4. Ensuring uniqueness against existing zones
    """

    existing_zones = Zone.objects.filter(slug__isnull=False).values_list('slug', flat=True)
    # Clean the zone name
    cleaned = zone_name.lower().strip()
    cleaned = re.sub(r'[^a-z\s-]', '', cleaned)
    
    # Try the simplest version first (full lowercase name)
    simple_id = cleaned.replace(' ', '-')
    
    if simple_id not in existing_zones:
        return simple_id
    
    # If simple version exists, try initials
    words = cleaned.split()
    if len(words) > 1:
        initials = ''.join(word[0] for word in words)
        if initials not in existing_zones:
            return initials
    
    # If initials exist, try combinations
    for i in range(1, len(cleaned)):
        candidate = cleaned[:i+1].replace(' ', '-')
        if candidate not in existing_zones:
            return candidate
    
    # As last resort, add a random letter
    while True:
        random_char = random.choice('abcdefghijklmnopqrstuvwxyz')
        candidate = f"{simple_id}-{random_char}"
        if candidate not in existing_zones:
            return candidate