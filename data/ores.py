# Ore data - exact copy from /forger command

ORES = {
    "Stone Ore": {"rarity": "Common", "multiplier": 0.2, "traitType": None, "traits": []},
    "Sand Stone": {"rarity": "Common", "multiplier": 0.25, "traitType": None, "traits": []},
    "Copper Ore": {"rarity": "Common", "multiplier": 0.3, "traitType": None, "traits": []},
    "Iron Ore": {"rarity": "Common", "multiplier": 0.35, "traitType": None, "traits": []},
    "Cardboardite Ore": {"rarity": "Common", "multiplier": 0.7, "traitType": None, "traits": []},
    
    "Tin Ore": {"rarity": "Uncommon", "multiplier": 0.425, "traitType": None, "traits": []},
    "Silver Ore": {"rarity": "Uncommon", "multiplier": 0.5, "traitType": None, "traits": []},
    "Gold Ore": {"rarity": "Uncommon", "multiplier": 0.65, "traitType": None, "traits": []},
    "Bananite Ore": {"rarity": "Uncommon", "multiplier": 0.85, "traitType": None, "traits": []},
    "Cobalt Ore": {"rarity": "Uncommon", "multiplier": 1.0, "traitType": None, "traits": []},
    "Titanium Ore": {"rarity": "Uncommon", "multiplier": 1.15, "traitType": None, "traits": []},
    "Lapis Lazuli Ore": {"rarity": "Uncommon", "multiplier": 1.3, "traitType": None, "traits": []},
    
    "Mushroomite Ore": {"rarity": "Rare", "multiplier": 0.8, "traitType": None, "traits": []},
    "Platinum Ore": {"rarity": "Rare", "multiplier": 0.8, "traitType": None, "traits": []},
    "Quartz Ore": {"rarity": "Rare", "multiplier": 1.5, "traitType": None, "traits": []},
    "Volcanic Rock": {"rarity": "Rare", "multiplier": 1.55, "traitType": None, "traits": []},
    "Amethyst Ore": {"rarity": "Rare", "multiplier": 1.65, "traitType": None, "traits": []},
    "Topaz Ore": {"rarity": "Rare", "multiplier": 1.75, "traitType": None, "traits": []},
    "Diamond Ore": {"rarity": "Rare", "multiplier": 2.0, "traitType": None, "traits": []},
    "Sapphire Ore": {"rarity": "Rare", "multiplier": 2.25, "traitType": None, "traits": []},
    
    "Aite Ore": {"rarity": "Epic", "multiplier": 1.0, "traitType": None, "traits": []},
    "Poopite Ore": {"rarity": "Epic", "multiplier": 1.2, "traitType": None, "traits": []},
    "Obsidian Ore": {"rarity": "Epic", "multiplier": 2.35, "traitType": "Armor", "traits": [
        {"description": "Vitality", "maxStat": 30}
    ]},
    "Cuprite Ore": {"rarity": "Epic", "multiplier": 2.43, "traitType": None, "traits": []},
    "Emerald Ore": {"rarity": "Epic", "multiplier": 2.55, "traitType": None, "traits": []},
    "Ruby Ore": {"rarity": "Epic", "multiplier": 2.95, "traitType": None, "traits": []},
    "Orange Crystal Ore": {"rarity": "Epic", "multiplier": 3.0, "traitType": None, "traits": []},
    "Magenta Crystal Ore": {"rarity": "Epic", "multiplier": 3.1, "traitType": None, "traits": []},
    "Green Crystal Ore": {"rarity": "Epic", "multiplier": 3.2, "traitType": None, "traits": []},
    "Crimson Crystal Ore": {"rarity": "Epic", "multiplier": 3.3, "traitType": None, "traits": []},
    "Rivalite Ore": {"rarity": "Epic", "multiplier": 3.33, "traitType": "Weapon", "traits": [
        {"description": "Crit Chance on Weapons", "maxStat": 20}
    ]},
    "Blue Crystal Ore": {"rarity": "Epic", "multiplier": 3.4, "traitType": None, "traits": []},
    "Arcane Crystal Ore": {"rarity": "Epic", "multiplier": 7.5, "traitType": None, "traits": []},
    
    "Uranium Ore": {"rarity": "Legendary", "multiplier": 3.0, "traitType": "Armor", "traits": [
        {"description": "max HP AOE Damage on Armor", "maxStat": 5}
    ]},
    "Mythril Ore": {"rarity": "Legendary", "multiplier": 3.5, "traitType": "Armor", "traits": [
        {"description": "Vitality", "maxStat": 15}
    ]},
    "Eye Ore": {"rarity": "Legendary", "multiplier": 4.0, "traitType": "All", "traits": [
        {"description": "Weapon Damage", "maxStat": 15},
        {"description": "Health", "maxStat": -10}
    ]},
    "Fireite Ore": {"rarity": "Legendary", "multiplier": 4.5, "traitType": "Weapon", "traits": [
        {"description": "Burn Damage on Weapons with", "maxStat": 20},
        {"description": "chance", "maxStat": 30}
    ]},
    "Lightite Ore": {"rarity": "Legendary", "multiplier": 4.6, "traitType": "Armor", "traits": [
        {"description": "Bonus Movement Speed", "maxStat": 15}
    ]},
    "Magmaite Ore": {"rarity": "Legendary", "multiplier": 5.0, "traitType": "Weapon", "traits": [
        {"description": "AOE Explosion on Weapons with", "maxStat": 50},
        {"description": "chance", "maxStat": 35}
    ]},
    "Rainbow Crystal Ore": {"rarity": "Legendary", "multiplier": 5.25, "traitType": None, "traits": []},
    
    "Demonite Ore": {"rarity": "Mythical", "multiplier": 5.5, "traitType": "Armor", "traits": [
        {"description": "to Burn Enemy when Damage is Taken.", "maxStat": 25}
    ]},
    "Darkryte Ore": {"rarity": "Mythical", "multiplier": 6.3, "traitType": "Armor", "traits": [
        {"description": "Chance to Dodge Damage (Negate Fully)", "maxStat": 15}
    ]},
    
    "Galaxite Ore": {"rarity": "Divine", "multiplier": 11.5, "traitType": None, "traits": []},
    "Vooite Ore": {"rarity": None, "multiplier": 0.0, "traitType": None, "traits": []},
}

RARITY_ORDER = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythical", "Divine"]

RARITY_COLORS = {
    "Common": "#A8A8A8",
    "Uncommon": "#ABFF8C",
    "Rare": "#8CF0FF",
    "Epic": "#C48CFF",
    "Legendary": "#FFE88C",
    "Mythical": "#FF2E69",
    "Divine": "#FFFFFF"
}
