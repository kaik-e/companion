"""Forge Calculator - Full calculation logic"""

from ores import (
    ORES, RARITY_ORDER, RARITY_COLORS,
    WEAPON_ODDS, ARMOR_ODDS,
    WEAPON_BASE_DAMAGE, ARMOR_BASE_DEFENSE,
    MASTERWORK_THRESHOLDS
)


def calculate_forge(detected_ores, craft_type="Weapon"):
    """
    Calculate full forge results from detected ores.
    
    Returns dict with:
    - multiplier: average multiplier
    - total_ores: total ore count
    - rarity: result rarity
    - masterwork_chance: % chance for masterwork
    - item_odds: dict of item type -> probability
    - damage_range / defense_range: (min, max) stats
    - traits: list of traits
    """
    if not detected_ores:
        return None
    
    # Calculate totals
    total_multiplier = 0
    total_count = 0
    rarities = []
    traits = []
    
    for ore_id, ore_data in detected_ores.items():
        count = ore_data["count"]
        multiplier = ore_data["multiplier"]
        rarity = ore_data["rarity"]
        
        total_multiplier += multiplier * count
        total_count += count
        rarities.extend([rarity] * count)
        
        # Check for traits
        ore_info = ORES.get(ore_id, {})
        if "trait" in ore_info:
            trait_type = ore_info.get("trait_type", "All")
            if trait_type == "All" or trait_type == craft_type:
                traits.append({
                    "name": ore_info["trait"],
                    "source": ore_info["name"]
                })
    
    if total_count == 0:
        return None
    
    # Average multiplier
    avg_multiplier = total_multiplier / total_count
    
    # Determine result rarity (highest rarity among ores)
    result_rarity = get_highest_rarity(rarities)
    
    # Masterwork chance based on rarity
    masterwork_chance = MASTERWORK_THRESHOLDS.get(result_rarity, 0)
    
    # Item type odds
    clamped_count = max(3, min(10, total_count))
    
    if craft_type == "Weapon":
        item_odds = WEAPON_ODDS.get(clamped_count, WEAPON_ODDS[10])
        base_stats = WEAPON_BASE_DAMAGE
        stat_name = "damage"
    else:
        item_odds = ARMOR_ODDS.get(clamped_count, ARMOR_ODDS[10])
        base_stats = ARMOR_BASE_DEFENSE
        stat_name = "defense"
    
    # Calculate stat ranges for each possible item
    item_stats = {}
    for item_type, odds in item_odds.items():
        if odds > 0:
            base_min, base_max = base_stats.get(item_type, (10, 15))
            # Apply multiplier to stats
            scaled_min = int(base_min * avg_multiplier)
            scaled_max = int(base_max * avg_multiplier)
            item_stats[item_type] = {
                "odds": odds,
                "min": scaled_min,
                "max": scaled_max
            }
    
    # Overall stat range (weighted by odds)
    overall_min = min(s["min"] for s in item_stats.values())
    overall_max = max(s["max"] for s in item_stats.values())
    
    return {
        "multiplier": round(avg_multiplier, 2),
        "total_ores": total_count,
        "rarity": result_rarity,
        "rarity_color": RARITY_COLORS.get(result_rarity, "#FFFFFF"),
        "masterwork_chance": round(masterwork_chance * 100, 1),
        "item_odds": item_stats,
        "stat_name": stat_name,
        "stat_range": (overall_min, overall_max),
        "traits": traits,
        "craft_type": craft_type
    }


def get_highest_rarity(rarities):
    """Get the highest rarity from a list"""
    if not rarities:
        return "Common"
    
    highest_idx = 0
    for rarity in rarities:
        idx = RARITY_ORDER.index(rarity) if rarity in RARITY_ORDER else 0
        highest_idx = max(highest_idx, idx)
    
    return RARITY_ORDER[highest_idx]


def format_results(result):
    """Format results for display"""
    if not result:
        return "No ores detected"
    
    lines = []
    
    # Header
    lines.append(f"═══ {result['craft_type']} Forge ═══")
    lines.append("")
    
    # Multiplier and rarity
    lines.append(f"Multiplier: {result['multiplier']}x")
    lines.append(f"Rarity: {result['rarity']}")
    lines.append(f"Total Ores: {result['total_ores']}")
    lines.append("")
    
    # Masterwork
    if result['masterwork_chance'] > 0:
        lines.append(f"⭐ Masterwork: {result['masterwork_chance']}%")
        lines.append("")
    
    # Item odds
    lines.append(f"─── Possible {result['craft_type']}s ───")
    for item_type, stats in sorted(result['item_odds'].items(), key=lambda x: -x[1]['odds']):
        pct = int(stats['odds'] * 100)
        stat_range = f"{stats['min']}-{stats['max']} {result['stat_name']}"
        lines.append(f"  {item_type}: {pct}% ({stat_range})")
    lines.append("")
    
    # Traits
    if result['traits']:
        lines.append("─── Traits ───")
        for trait in result['traits']:
            lines.append(f"  ✦ {trait['name']} ({trait['source']})")
    
    return "\n".join(lines)
