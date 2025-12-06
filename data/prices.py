# Prices - exact copy from /forger command

WEAPON_PRICES = {
    "Dagger": 68,
    "Straight Sword": 120,
    "Gauntlet": 205,
    "Katana": 324,
    "Great Sword": 485,
    "Great Axe": 850,
    "Colossal Sword": 1355,
}

WEAPON_BASE_DAMAGE = {
    "Dagger": 4.3,
    "Straight Sword": 7.5,
    "Gauntlet": 7.6,
    "Katana": 8.5,
    "Great Sword": 12,
    "Great Axe": 15.75,
    "Colossal Sword": 20,
}

ARMOR_PRICES = {
    "Light Helmet": 65,
    "Light Leggings": 112.5,
    "Light Chestplate": 225,
    "Medium Helmet": 335,
    "Medium Leggings": 485,
    "Medium Chestplate": 850,
    "Heavy Helmet": 1020,
    "Heavy Leggings": 1200,
    "Heavy Chestplate": 1355,
}


def calculate_weapon_damage(weapon_name, multiplier, quality=100, enhancement_level=0):
    """
    Calculate weapon damage: baseDamage * multiplier * 2 * (quality / 100) * enhancementMultiplier
    Enhancement multiplier: 1 + (enhLevel * 0.05)
    """
    base_damage = WEAPON_BASE_DAMAGE.get(weapon_name)
    if not base_damage:
        return None
    
    base_scaling = multiplier * 2 * (quality / 100)
    enhancement_mult = 1 + (enhancement_level * 0.05)
    damage = base_damage * base_scaling * enhancement_mult
    
    return round(damage, 2)


def calculate_masterwork_price(item_name, multiplier, craft_type):
    """
    Masterwork price: (base price x multiplier) + 10%
    """
    prices = WEAPON_PRICES if craft_type == "Weapon" else ARMOR_PRICES
    base_price = prices.get(item_name)
    
    if not base_price:
        return None
    
    price_with_mult = base_price * multiplier
    final_price = price_with_mult * 1.1  # +10%
    
    return round(final_price)


def format_price(price):
    """Format price with k suffix"""
    if price >= 1000:
        return f"{price / 1000:.1f}k"
    return str(price)
