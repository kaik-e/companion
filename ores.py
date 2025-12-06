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

RARITY_ORDER = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythical", "Divine"]

# Weapon type odds based on ore count
WEAPON_ODDS = {
    3: {"Dagger": 1.0},
    4: {"Dagger": 0.75, "Straight Sword": 0.25},
    5: {"Dagger": 0.50, "Straight Sword": 0.35, "Gauntlet": 0.15},
    6: {"Dagger": 0.30, "Straight Sword": 0.35, "Gauntlet": 0.20, "Katana": 0.15},
    7: {"Dagger": 0.15, "Straight Sword": 0.30, "Gauntlet": 0.20, "Katana": 0.20, "Great Sword": 0.15},
    8: {"Dagger": 0.05, "Straight Sword": 0.20, "Gauntlet": 0.15, "Katana": 0.25, "Great Sword": 0.20, "Great Axe": 0.15},
    9: {"Straight Sword": 0.10, "Gauntlet": 0.10, "Katana": 0.20, "Great Sword": 0.25, "Great Axe": 0.20, "Colossal Sword": 0.15},
    10: {"Katana": 0.15, "Great Sword": 0.25, "Great Axe": 0.25, "Colossal Sword": 0.35},
}

# Armor type odds based on ore count
ARMOR_ODDS = {
    3: {"Light Helmet": 1.0},
    4: {"Light Helmet": 0.75, "Light Leggings": 0.25},
    5: {"Light Helmet": 0.50, "Light Leggings": 0.35, "Light Chestplate": 0.15},
    6: {"Light Helmet": 0.30, "Light Leggings": 0.25, "Light Chestplate": 0.20, "Medium Helmet": 0.25},
    7: {"Light Leggings": 0.15, "Light Chestplate": 0.20, "Medium Helmet": 0.30, "Medium Leggings": 0.20, "Medium Chestplate": 0.15},
    8: {"Light Chestplate": 0.10, "Medium Helmet": 0.20, "Medium Leggings": 0.25, "Medium Chestplate": 0.25, "Heavy Helmet": 0.20},
    9: {"Medium Helmet": 0.10, "Medium Leggings": 0.15, "Medium Chestplate": 0.20, "Heavy Helmet": 0.25, "Heavy Leggings": 0.30},
    10: {"Medium Chestplate": 0.10, "Heavy Helmet": 0.20, "Heavy Leggings": 0.30, "Heavy Chestplate": 0.40},
}

# Base damage for weapons
WEAPON_BASE_DAMAGE = {
    "Dagger": (8, 12),
    "Straight Sword": (12, 18),
    "Gauntlet": (10, 15),
    "Katana": (14, 21),
    "Great Sword": (18, 27),
    "Great Axe": (20, 30),
    "Colossal Sword": (25, 38),
}

# Base defense for armor
ARMOR_BASE_DEFENSE = {
    "Light Helmet": (3, 5),
    "Light Leggings": (4, 6),
    "Light Chestplate": (5, 8),
    "Medium Helmet": (6, 9),
    "Medium Leggings": (7, 11),
    "Medium Chestplate": (9, 14),
    "Heavy Helmet": (10, 15),
    "Heavy Leggings": (12, 18),
    "Heavy Chestplate": (15, 23),
}

# Masterwork thresholds
MASTERWORK_THRESHOLDS = {
    "Common": 0,
    "Uncommon": 0.05,
    "Rare": 0.10,
    "Epic": 0.15,
    "Legendary": 0.25,
    "Mythical": 0.35,
    "Divine": 0.50,
}

# Build search patterns for OCR
ORE_PATTERNS = {}
for ore_id, data in ORES.items():
    name = data["name"].lower()
    base = name.replace(" ore", "").replace(" crystal", "").strip()
    
    ORE_PATTERNS[base] = ore_id
    ORE_PATTERNS[base.replace(" ", "")] = ore_id
    
    if len(base) >= 5:
        ORE_PATTERNS[base[:5]] = ore_id

# Special OCR patterns
ORE_PATTERNS["eye"] = "eyeore"
ORE_PATTERNS["eye ore"] = "eyeore"
ORE_PATTERNS["mythri"] = "mythril"
ORE_PATTERNS["rival"] = "rivalite"
ORE_PATTERNS["topa"] = "topaz"
