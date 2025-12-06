# Ore data for Forger Companion

ORES = {
    # Common
    "stone": {"name": "Stone Ore", "rarity": "Common", "multiplier": 0.2},
    "sandstone": {"name": "Sand Stone", "rarity": "Common", "multiplier": 0.25},
    "copper": {"name": "Copper Ore", "rarity": "Common", "multiplier": 0.3},
    "iron": {"name": "Iron Ore", "rarity": "Common", "multiplier": 0.35},
    "cardboardite": {"name": "Cardboardite Ore", "rarity": "Common", "multiplier": 0.7},
    
    # Uncommon
    "tin": {"name": "Tin Ore", "rarity": "Uncommon", "multiplier": 0.425},
    "silver": {"name": "Silver Ore", "rarity": "Uncommon", "multiplier": 0.5},
    "gold": {"name": "Gold Ore", "rarity": "Uncommon", "multiplier": 0.65},
    "bananite": {"name": "Bananite Ore", "rarity": "Uncommon", "multiplier": 0.85},
    "cobalt": {"name": "Cobalt Ore", "rarity": "Uncommon", "multiplier": 1.0},
    "titanium": {"name": "Titanium Ore", "rarity": "Uncommon", "multiplier": 1.15},
    "lapislazuli": {"name": "Lapis Lazuli Ore", "rarity": "Uncommon", "multiplier": 1.3},
    
    # Rare
    "mushroomite": {"name": "Mushroomite Ore", "rarity": "Rare", "multiplier": 0.8},
    "platinum": {"name": "Platinum Ore", "rarity": "Rare", "multiplier": 0.8},
    "quartz": {"name": "Quartz Ore", "rarity": "Rare", "multiplier": 1.5},
    "volcanicrock": {"name": "Volcanic Rock", "rarity": "Rare", "multiplier": 1.55},
    "amethyst": {"name": "Amethyst Ore", "rarity": "Rare", "multiplier": 1.65},
    "topaz": {"name": "Topaz Ore", "rarity": "Rare", "multiplier": 1.75},
    "diamond": {"name": "Diamond Ore", "rarity": "Rare", "multiplier": 2.0},
    "sapphire": {"name": "Sapphire Ore", "rarity": "Rare", "multiplier": 2.25},
    
    # Epic
    "aite": {"name": "Aite Ore", "rarity": "Epic", "multiplier": 1.0},
    "poopite": {"name": "Poopite Ore", "rarity": "Epic", "multiplier": 1.2},
    "obsidian": {"name": "Obsidian Ore", "rarity": "Epic", "multiplier": 2.35, "trait": "Vitality", "trait_type": "Armor"},
    "cuprite": {"name": "Cuprite Ore", "rarity": "Epic", "multiplier": 2.43},
    "emerald": {"name": "Emerald Ore", "rarity": "Epic", "multiplier": 2.55},
    "ruby": {"name": "Ruby Ore", "rarity": "Epic", "multiplier": 2.95},
    "orangecrystal": {"name": "Orange Crystal Ore", "rarity": "Epic", "multiplier": 3.0},
    "magentacrystal": {"name": "Magenta Crystal Ore", "rarity": "Epic", "multiplier": 3.1},
    "greencrystal": {"name": "Green Crystal Ore", "rarity": "Epic", "multiplier": 3.2},
    "crimsoncrystal": {"name": "Crimson Crystal Ore", "rarity": "Epic", "multiplier": 3.3},
    "rivalite": {"name": "Rivalite Ore", "rarity": "Epic", "multiplier": 3.33, "trait": "Crit Chance", "trait_type": "Weapon"},
    "bluecrystal": {"name": "Blue Crystal Ore", "rarity": "Epic", "multiplier": 3.4},
    "arcanecrystal": {"name": "Arcane Crystal Ore", "rarity": "Epic", "multiplier": 7.5},
    
    # Legendary
    "uranium": {"name": "Uranium Ore", "rarity": "Legendary", "multiplier": 3.0, "trait": "Max HP AOE Damage", "trait_type": "Armor"},
    "mythril": {"name": "Mythril Ore", "rarity": "Legendary", "multiplier": 3.5, "trait": "Vitality", "trait_type": "Armor"},
    "eyeore": {"name": "Eye Ore", "rarity": "Legendary", "multiplier": 4.0, "trait": "Weapon Damage", "trait_type": "All"},
    "fireite": {"name": "Fireite Ore", "rarity": "Legendary", "multiplier": 4.5, "trait": "Burn Damage", "trait_type": "Weapon"},
    "lightite": {"name": "Lightite Ore", "rarity": "Legendary", "multiplier": 4.6, "trait": "Movement Speed", "trait_type": "Armor"},
    "magmaite": {"name": "Magmaite Ore", "rarity": "Legendary", "multiplier": 5.0, "trait": "AOE Explosion", "trait_type": "Weapon"},
    "rainbowcrystal": {"name": "Rainbow Crystal Ore", "rarity": "Legendary", "multiplier": 5.25},
    
    # Mythical
    "demonite": {"name": "Demonite Ore", "rarity": "Mythical", "multiplier": 5.5, "trait": "Burn on Hit", "trait_type": "Armor"},
    "darkryte": {"name": "Darkryte Ore", "rarity": "Mythical", "multiplier": 6.3, "trait": "Dodge Chance", "trait_type": "Armor"},
    
    # Divine
    "galaxite": {"name": "Galaxite Ore", "rarity": "Divine", "multiplier": 11.5},
}

RARITY_COLORS = {
    "Common": "#A8A8A8",
    "Uncommon": "#ABFF8C",
    "Rare": "#8CF0FF",
    "Epic": "#C48CFF",
    "Legendary": "#FFE88C",
    "Mythical": "#FF2E69",
    "Divine": "#FFFFFF"
}

# Build search patterns - ore name variations for OCR matching
ORE_PATTERNS = {}
for ore_id, data in ORES.items():
    name = data["name"].lower()
    base = name.replace(" ore", "").replace(" crystal", "").replace(" ", "")
    
    # Add various patterns that might match
    patterns = [
        name,                    # full name
        base,                    # without ore/crystal
        base[:5] if len(base) >= 5 else base,  # first 5 chars (truncated names)
    ]
    
    for pattern in patterns:
        if pattern and len(pattern) >= 3:
            ORE_PATTERNS[pattern] = ore_id
