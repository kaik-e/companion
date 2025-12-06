"""Forge Calculator - Exact copy of /forger command logic"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data import (
    ORES, RARITY_ORDER, RARITY_COLORS,
    WEAPON_ODDS, ARMOR_ODDS,
    WEAPON_PRICES, WEAPON_BASE_DAMAGE, ARMOR_PRICES,
    calculate_weapon_damage, calculate_masterwork_price, format_price
)

MAX_ODDS_ORE_COUNT = 55


def calculate_transferred_stat(percentage):
    """
    Formula: y = 4.5x - 35, clamped between 0 and 100
    Returns fraction (0-1)
    """
    y = 4.5 * percentage - 35
    if y < 0:
        y = 0
    if y > 100:
        y = 100
    return y / 100


def calculate_forge(detected_ores, craft_type="Weapon"):
    """
    Calculate full forge results - exact copy of /forger command logic.
    
    detected_ores: dict of ore_name -> {name, count, rarity, multiplier}
    """
    if not detected_ores:
        return None
    
    # Convert detected_ores to list format [{name, amount}]
    selected_ores = []
    for ore_id, ore_data in detected_ores.items():
        selected_ores.append({
            "name": ore_data["name"],
            "amount": ore_data["count"]
        })
    
    # Get odds dict
    odds_dict = WEAPON_ODDS if craft_type == "Weapon" else ARMOR_ODDS
    
    # Calculate combined multiplier
    total_multiplier = 0
    total_count = 0
    
    for ore in selected_ores:
        ore_data = ORES.get(ore["name"])
        if not ore_data:
            continue
        total_multiplier += ore_data["multiplier"] * ore["amount"]
        total_count += ore["amount"]
    
    if total_count == 0:
        return None
    
    combined_multiplier = total_multiplier / total_count
    
    # Get odds for ore count (capped at 55)
    odds_key = min(total_count, MAX_ODDS_ORE_COUNT)
    if odds_key < 3:
        odds_key = 3
    odds = odds_dict.get(odds_key, odds_dict[max(odds_dict.keys())])
    
    # Calculate composition percentages
    composition = {}
    for ore in selected_ores:
        composition[ore["name"]] = (ore["amount"] / total_count) * 100
    
    # Calculate traits (need at least 10% of ore for traits to apply)
    traits = []
    for ore_name, pct in composition.items():
        ore_data = ORES.get(ore_name)
        if not ore_data or not ore_data.get("traits"):
            continue
        
        # Check if trait applies to this craft type
        trait_type = ore_data.get("traitType")
        if trait_type and trait_type != "All" and trait_type != craft_type:
            continue
        
        # Need at least 10% for traits
        if pct < 10:
            continue
        
        transferred_fraction = calculate_transferred_stat(pct)
        ore_trait_parts = []
        
        i = 0
        while i < len(ore_data["traits"]):
            t1 = ore_data["traits"][i]
            if "maxStat" not in t1:
                i += 1
                continue
            
            v1 = round(transferred_fraction * t1["maxStat"], 2)
            line = f"{v1}% {t1['description']}"
            
            # Check for merge (sentence-style traits)
            should_merge = (
                t1["description"].strip().lower().endswith(("with", "of", "for", "per", "to", "in"))
                and i + 1 < len(ore_data["traits"])
                and "maxStat" in ore_data["traits"][i + 1]
            )
            
            if should_merge:
                t2 = ore_data["traits"][i + 1]
                v2 = round(transferred_fraction * t2["maxStat"], 2)
                line += f" {v2}% {t2['description']}"
                i += 1
            
            ore_trait_parts.append(line)
            i += 1
        
        if ore_trait_parts:
            traits.append({
                "text": ", ".join(ore_trait_parts),
                "source": ore_name
            })
    
    if not traits:
        traits.append({"text": "No traits transfer", "source": None})
    
    # Determine rarity from highest composition ore
    highest_ore = ""
    highest_pct = 0
    for ore_name, pct in composition.items():
        if pct > highest_pct:
            highest_pct = pct
            highest_ore = ore_name
    
    rarity = ORES.get(highest_ore, {}).get("rarity", "Unknown")
    rarity_color = RARITY_COLORS.get(rarity, "#808080")
    
    # Filter and sort odds (only show > 0)
    sorted_odds = {}
    for item_type, chance in sorted(odds.items(), key=lambda x: -x[1]):
        if chance > 0:
            sorted_odds[item_type] = chance
    
    # Calculate damage/price for each possible item
    item_stats = {}
    prices = WEAPON_PRICES if craft_type == "Weapon" else ARMOR_PRICES
    
    for item_type, chance in sorted_odds.items():
        damage = None
        if craft_type == "Weapon":
            damage = calculate_weapon_damage(item_type, combined_multiplier)
        
        mw_price = calculate_masterwork_price(item_type, combined_multiplier, craft_type)
        
        item_stats[item_type] = {
            "odds": chance,
            "damage": damage,
            "mw_price": mw_price
        }
    
    return {
        "multiplier": round(combined_multiplier, 2),
        "total_ores": total_count,
        "composition": composition,
        "rarity": rarity,
        "rarity_color": rarity_color,
        "odds": sorted_odds,
        "item_stats": item_stats,
        "traits": traits,
        "craft_type": craft_type,
        "warning": "Ore total above 55! Showing stats for 55 ores only." if total_count > 55 else None
    }


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
    
    if result.get("warning"):
        lines.append(f"⚠️ {result['warning']}")
    lines.append("")
    
    # Item odds with damage and price
    lines.append(f"─── Possible {result['craft_type']}s ───")
    for item_type, stats in result['item_stats'].items():
        pct = int(stats['odds'] * 100)
        damage_str = f"{stats['damage']:.1f} dmg" if stats['damage'] else ""
        price_str = f"MW: {format_price(stats['mw_price'])}" if stats['mw_price'] else ""
        lines.append(f"  {item_type}: {pct}% | {damage_str} | {price_str}")
    lines.append("")
    
    # Traits
    lines.append("─── Traits ───")
    for trait in result['traits']:
        if trait['source']:
            lines.append(f"  ✦ {trait['text']} ({trait['source']})")
        else:
            lines.append(f"  {trait['text']}")
    
    return "\n".join(lines)
