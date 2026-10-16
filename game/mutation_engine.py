# =====================================================================
# VALORIYA: MAXLUQOTLAR MUTATSIYASI & ELITALAR MATRITSASI (5,000+ ENCOUNTERS)
# =====================================================================
# 50 ta tayanch maxluq x 20 Mutatsiya modifikatori x 5 Daraja Unvoni = 5,000 ta unikal jang!
# Zindonda yoki dunyoda har bir maxluq dinamik mutatsiya auralari va qo'shimcha mukofotlar bilan yaratiladi.
# =====================================================================

import random
from typing import Dict, Any, List, Optional
from game.bestiary import BESTIARY_DATA

MONSTER_MUTATIONS = {
    "venomous": {
        "name_uz": "Zaharlangan",
        "icon": "🧪",
        "desc": "Hujum qilganda qahramon qoniga halokatli zahar purkaydi (har turda +15 DoT).",
        "bonus_atk": 4,
        "poison_potency": 15
    },
    "armored": {
        "name_uz": "Plitali Sovutli",
        "icon": "🛡",
        "desc": "Qalin tosh va po'lat qoplamasi bilan himoyalangan (barcha olingan zarba -35%).",
        "bonus_def": 18,
        "dmg_reduction": 0.35
    },
    "berserk": {
        "name_uz": "Quturgan",
        "icon": "🩸",
        "desc": "Salomatligi 40% dan kamayganda dahshatli g'azabga minib, zarbasi 2 barobar ortadi.",
        "bonus_atk": 8,
        "enrage_trigger": 0.40
    },
    "shadow": {
        "name_uz": "Soyali",
        "icon": "👤",
        "desc": "Zulmat ichida erib harakatlanadi, zarbalardan 30% ehtimol bilan qochadi.",
        "evasion": 30
    },
    "vampiric": {
        "name_uz": "Vampirik",
        "icon": "🧛",
        "desc": "Qahramonga urgan zarbasining 35% ini o'zining salomatligiga aylantiradi.",
        "lifesteal": 35
    },
    "explosive": {
        "name_uz": "Portlovchi",
        "icon": "💣",
        "desc": "O'lim oldidan qattiq portlab, atrofga 45 yuqori olovli zarar tarqatadi.",
        "death_explosion": 45
    },
    "mana_burner": {
        "name_uz": "Ruh Yemiruvchi",
        "icon": "🔮",
        "desc": "Har bir zarbasida qahramonning ruhiy quvvati (Mana) va irodasini so'rib oladi.",
        "mana_burn": 15
    },
    "lightning_fast": {
        "name_uz": "Chaqmoqdek Tezkor",
        "icon": "⚡️",
        "desc": "Mislsiz chaqqonlikka ega, jang boshida ketma-ket 2 marta zarba beradi.",
        "double_strike": True
    },
    "glacial": {
        "name_uz": "Muzlatuvchi",
        "icon": "❄️",
        "desc": "Dahshatli sovuq taratadi, qahramonning harakat tezligini va zarbasini susaytiradi.",
        "chill_slow": 30
    },
    "flame_aura": {
        "name_uz": "Olovli Aura",
        "icon": "🔥",
        "desc": "Yong'oqdek olov aurasiga ega, har raundda qahramonni 14 alangali zarar bilan kuydiradi.",
        "flame_tick": 14
    },
    "sunderer": {
        "name_uz": "Sovut Yoruvchi",
        "icon": "🔨",
        "desc": "Qahramonning zirhini e'tiborga olmay, sof (True Damage) zarar yetkazadi.",
        "armor_ignore": 45
    },
    "colossus": {
        "name_uz": "Titan Gavdali",
        "icon": "🗿",
        "desc": "Ulkan tog'dek gavdaga ega, maksimal salomatligi 2.2 barobar ko'proq.",
        "hp_mult": 2.2,
        "bonus_def": 10
    },
    "necromantic": {
        "name_uz": "Nekromantik",
        "icon": "☠️",
        "desc": "Bir marta o'lgach, qora sehr kuchi bilan 40% salomatlikda qayta tiriladi.",
        "revive": True
    },
    "invisible": {
        "name_uz": "Ko'rinmas Pinhon",
        "icon": "👁‍🗨",
        "desc": "Jangni ko'rinmas boshlaydi, birinchi zarbasi kafolatlangan kritik (2.5x) bo'ladi.",
        "first_strike_crit": 2.5
    },
    "frenzied": {
        "name_uz": "Shiddatli Hujumchi",
        "icon": "🌪",
        "desc": "Jang cho'zilgan sari har bir navbatda zarba kuchi 12% dan muttasil oshib boradi.",
        "stacking_atk": 0.12
    },
    "dread": {
        "name_uz": "Dahshat Taratuvchi",
        "icon": "😱",
        "desc": "Efirga vahima sochadi, qahramonning hujum kuchini 20% ga pasaytiradi.",
        "atk_debuff": 20
    },
    "hallucinogenic": {
        "name_uz": "Sehrli Adashtiruvchi",
        "icon": "🌀",
        "desc": "Qahramon ko'ziga saroblar ko'rsatib, zarbalarini xato ketishiga sabab bo'ladi.",
        "blind_chance": 25
    },
    "reflective": {
        "name_uz": "Zarba Qaytaruvchi",
        "icon": "🪞",
        "desc": "Yaltiroq po'sti bor, o'ziga urilgan har qanday jismoniy zarbaning 22% ini qaytaradi.",
        "reflect_pct": 22
    },
    "calamitous": {
        "name_uz": "Falokat Manbasi",
        "icon": "🌋",
        "desc": "Har bir tanqidiy zarbasi qahramonda og'ir qon ketish va travma qoldiradi.",
        "wound_inflict": True
    },
    "omnipotent": {
        "name_uz": "Buzilmas Iroda",
        "icon": "👑",
        "desc": "Barcha turdagi sehr, la'nat va salbiy auralarga nisbatan 60% immunitetga ega.",
        "status_resist": 60
    }
}

MONSTER_RANKS = {
    "common": {
        "title_uz": "Oddiy",
        "prefix_tag": "",
        "hp_mult": 1.0,
        "atk_mult": 1.0,
        "reward_mult": 1.0,
        "mutation_count": 0
    },
    "elite": {
        "title_uz": "🟣 Elita",
        "prefix_tag": "🟣 Elita",
        "hp_mult": 1.9,
        "atk_mult": 1.35,
        "reward_mult": 2.5,
        "mutation_count": 1
    },
    "champion": {
        "title_uz": "🔴 Chempion",
        "prefix_tag": "🔴 Chempion",
        "hp_mult": 3.2,
        "atk_mult": 1.75,
        "reward_mult": 5.0,
        "mutation_count": 2
    },
    "ancient_guardian": {
        "title_uz": "🟠 Qadimiy Qo'riqchi",
        "prefix_tag": "🟠 Qadimiy Qo'riqchi",
        "hp_mult": 5.5,
        "atk_mult": 2.3,
        "reward_mult": 12.0,
        "mutation_count": 3
    },
    "apocalypse": {
        "title_uz": "💀 Apokalipsis Boshi",
        "prefix_tag": "💀 Dunyo Qiruvchisi",
        "hp_mult": 12.0,
        "atk_mult": 3.8,
        "reward_mult": 30.0,
        "mutation_count": 4
    }
}

def mutate_monster(base_mob_id: Optional[str] = None, dungeon_floor: int = 1, force_rank: Optional[str] = None) -> Dict[str, Any]:
    """
    50 ta tayanch maxluqdan 5,000+ kombinatsiyali elita maxluq va chempionlarni generatsiya qiladi.
    """
    if not base_mob_id or base_mob_id not in BESTIARY_DATA:
        base_mob_id = random.choice(list(BESTIARY_DATA.keys()))
        
    base_mob = BESTIARY_DATA[base_mob_id]
    
    # Darajani aniqlash (Qavat qancha yuqori bo'lsa, elitalar shuncha ko'p)
    if force_rank:
        rank_key = force_rank
    else:
        weights = [
            max(20, 75 - (dungeon_floor * 5)),   # common
            min(40, 15 + (dungeon_floor * 3)),   # elite
            min(25, 5 + (dungeon_floor * 2)),    # champion
            min(15, 2 + dungeon_floor),          # ancient_guardian
            min(8, 1 + (dungeon_floor // 3))     # apocalypse
        ]
        rank_key = random.choices(list(MONSTER_RANKS.keys()), weights=weights)[0]
        
    rank = MONSTER_RANKS[rank_key]
    
    # Mutatsiyalarni tanlash
    selected_mutations = []
    if rank["mutation_count"] > 0:
        mutation_keys = random.sample(list(MONSTER_MUTATIONS.keys()), k=min(rank["mutation_count"], len(MONSTER_MUTATIONS)))
        for mk in mutation_keys:
            selected_mutations.append(MONSTER_MUTATIONS[mk])
            
    # Ko'rsatkichlarni hisoblash
    mut_hp_mult = 1.0
    mut_bonus_atk = 0
    mut_bonus_def = 0
    
    for m in selected_mutations:
        mut_hp_mult *= m.get("hp_mult", 1.0)
        mut_bonus_atk += m.get("bonus_atk", 0)
        mut_bonus_def += m.get("bonus_def", 0)
        
    final_hp = int(base_mob.get("hp", 100) * rank["hp_mult"] * mut_hp_mult)
    final_atk = int((base_mob.get("atk", 15) * rank["atk_mult"]) + mut_bonus_atk)
    final_def = int(base_mob.get("def", 5) + mut_bonus_def)
    
    # Nomini yig'ish
    mutation_prefixes = " ".join([m["name_uz"] for m in selected_mutations])
    clean_base_name = base_mob["name"]
    
    if rank["prefix_tag"]:
        if mutation_prefixes:
            display_name = f"{rank['prefix_tag']} {mutation_prefixes} {clean_base_name}"
        else:
            display_name = f"{rank['prefix_tag']} {clean_base_name}"
    else:
        display_name = clean_base_name
        
    # Oltin va tajriba mukofotlari
    gold_min = int(15 * rank["reward_mult"] * (1 + (dungeon_floor * 0.3)))
    gold_max = int(35 * rank["reward_mult"] * (1 + (dungeon_floor * 0.3)))
    xp_reward = int(25 * rank["reward_mult"] * (1 + (dungeon_floor * 0.25)))
    
    mut_descriptions = [f"{m['icon']} {m['name_uz']}: {m['desc']}" for m in selected_mutations]
    
    return {
        "id": f"mut_{base_mob_id}_{rank_key}_{random.randint(1000, 9999)}",
        "base_id": base_mob_id,
        "name": display_name,
        "rank": rank_key,
        "rank_title": rank["title_uz"],
        "hp": final_hp,
        "max_hp": final_hp,
        "atk": final_atk,
        "def": final_def,
        "weakness": base_mob.get("weakness", "Yo'q"),
        "mutations": selected_mutations,
        "mutation_descs": mut_descriptions,
        "gold_drop": (gold_min, gold_max),
        "xp_drop": xp_reward,
        "loot_note": f"{rank['reward_mult']}x Oltin va Tajriba, Nodir tushumlar koeffitsienti yuqori."
    }

def get_mutation_matrix_size() -> Dict[str, int]:
    """Maxluqlar matritsasi hajmini hisoblaydi."""
    mob_count = len(BESTIARY_DATA)
    mut_count = len(MONSTER_MUTATIONS)
    rank_count = len(MONSTER_RANKS)
    total_encounters = mob_count * mut_count * rank_count
    return {
        "base_monsters": mob_count,
        "mutations": mut_count,
        "ranks": rank_count,
        "total_unique_encounters": total_encounters
    }
