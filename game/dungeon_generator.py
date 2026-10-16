# =====================================================================
# VALORIYA: PROTSESSUAL ZINDON XONALARI GENERATORI (1,000+ XONALAR)
# =====================================================================
# 10 ta Mavzu x 10 Xona Arxitipi x 10 Tartib (Layout) = 1,000 ta dinamik xona!
# Har bir xonada interaktiv tanlovlar, xazinalar, qopqonlar va maxsus hodisalar yuz beradi.
# =====================================================================

import random
from typing import Dict, Any, List

DUNGEON_THEMES = {
    "crypt": {
        "name_uz": "Go'rkovlar Kriptasi",
        "icon": "🪦",
        "desc": "Zanglagan tobutlar va rutubatli suyaklar hidi anqib turgan zax yerosti xonalari."
    },
    "catacombs": {
        "name_uz": "Zaharli Suyaklar Katakombasi",
        "icon": "💀",
        "desc": "Minglab qadimiy jangchilar dafn etilgan, yashil gazlar ajralib turuvchi tor yo'laklar."
    },
    "infernal": {
        "name_uz": "Magmali Do'zax Yorig'i",
        "icon": "🌋",
        "desc": "Qizigan lava daryolari oqib turuvchi, havosi jazirama va tutunli g'orlar."
    },
    "frozen_abyss": {
        "name_uz": "Muzlagan Ruhlar Tubi",
        "icon": "❄️",
        "desc": "Mangu sovuq muz stalaktitlari osilib turgan, nafas olganda o'pkani kuydiruvchi qahraton."
    },
    "shadow_temple": {
        "name_uz": "Qora Kultistlar Ibodatxonasi",
        "icon": "🕯",
        "desc": "Qora shamlari yonib turgan, devorlarida qon bilan yozilgan yovuz ramzlar mavjud maskan."
    },
    "blood_halls": {
        "name_uz": "Qonxo'r Titanlar Saroyi",
        "icon": "🩸",
        "desc": "Devorlaridan qizil suyuqlik sizib oquvchi, ulkan tosh taxtli qadimiy saroy qoldiqlari."
    },
    "ancient_vault": {
        "name_uz": "Unutilgan Sivilizatsiya Xazinaxonasi",
        "icon": "🏛",
        "desc": "Oltin naqshli ustunlar va qadimiy mexanik qurilmalar bilan to'ldirilgan arxitektura."
    },
    "ruined_sanctuary": {
        "name_uz": "Vayron Bo'lgan Nur Ma'badi",
        "icon": "✨",
        "desc": "Ilohiy haykallar singan bo'lsa-da, havoda hamon muqaddas zarrachalar charx urmoqda."
    },
    "spider_nest": {
        "name_uz": "Qora Beva O'rgimchak Inlari",
        "icon": "🕸",
        "desc": "Har bir qadamingiz yopishqoq to'rlarga chirmashadigan, shipida yuzlab ko'zlar yiltillagan g'or."
    },
    "abyssal_gate": {
        "name_uz": "Tubsizlik Qora Darvozasi",
        "icon": "🌌",
        "desc": "Koinot qa'ridan kelayotgan sirli g'o'ng'illash eshitiluvchi, gravitatsiya buzilgan hudud."
    }
}

ROOM_TYPES = {
    "combat": {
        "type": "combat",
        "name_uz": "⚔️ Qonli To'qnashuv Maydoni",
        "desc_uz": "Zulmat ichidan bir to'da qahrli maxluqlar qurollarini shaylab chiqib keldi!",
        "action": "Jangga kirish yoki orqaga chekinish"
    },
    "blood_altar": {
        "type": "altar",
        "name_uz": "🩸 Qadimiy Qon Mehrobi",
        "desc_uz": "Qizil toshdan yo'nilgan mehrobda qon qurbonligi talab qilinmoqda. (HP evaziga ulkan zarba kuchi).",
        "action": "Qon to'kib qurbonlik qilish yoki befarq o'tish"
    },
    "ancient_library": {
        "type": "lore",
        "name_uz": "📜 Qadimiy Solnoma Kutubxonasi",
        "desc_uz": "Chirigan javonlarda ming yillik sirlar bitilgan unutilgan pergamentlar saqlanmoqda.",
        "action": "Solnomalarni o'rganish va relikviya qidirish"
    },
    "trap_room": {
        "type": "trap",
        "name_uz": "🪤 Halokatli Qopqonlar Zali",
        "desc_uz": "Pol ostidan zaharli nayzalar va devorlardan yonuvchi o'qlar otilish xavfi yuqori!",
        "action": "Chaqqonlik bilan qopqonlarni aylanib o'tish"
    },
    "healing_spring": {
        "type": "rest",
        "name_uz": "⛲️ Tiriklik Mistik Bulog'i",
        "desc_uz": "Yer ostidan ko'k jilvali tiniq shifobaxsh suv otilib turibdi. Ruh va tanni davolaydi.",
        "action": "Suvdan ichib salomatlikni to'liq tiklash"
    },
    "black_market": {
        "type": "merchant",
        "name_uz": "🧳 Qora Bozor Ko'chmanchisi",
        "desc_uz": "Kapushon kiygan ko'r savdogar nodir eliksirlar va taqiqlangan afsunlarni taklif qilmoqda.",
        "action": "Savdo rastasini ko'rish"
    },
    "treasure_vault": {
        "type": "treasure",
        "name_uz": "💎 Qulflangan Sirli Xazina Sandig'i",
        "desc_uz": "Zanjirband etilgan og'ir temir sandiq. Ichida afsonaviy tushumlar bo'lishi mumkin.",
        "action": "Qulfni buzish yoki ochqichni qo'llash"
    },
    "spirit_graveyard": {
        "type": "event",
        "name_uz": "👻 Halok Bo'lgan Ritsar Ruhi",
        "desc_uz": "O'tmishda bu yerda yiqilgan botir ritsarning arvohi sizga maxfiy yo'lni ko'rsatmoqchi.",
        "action": "Ruh bilan suhbatlashish va vasiyatini tinglash"
    },
    "rune_puzzle": {
        "type": "puzzle",
        "name_uz": "🔮 Runa Muhrli Sehrli Eshik",
        "desc_uz": "Eshikda to'rtta elementar runa charx urmoqda. To'g'ri ketma-ketlik kashf etilishi lozim.",
        "action": "Runa jumboqlarini yechish"
    },
    "boss_gate": {
        "type": "boss",
        "name_uz": "🚪 Qavat Hukmdori Darvozasi",
        "desc_uz": "Ulkan suyak darvoza ortidan dahshatli nafas va gursillagan qadam tovushlari kelmoqda...",
        "action": "Qavat bossi bilan hal qiluvchi jangga kirish"
    }
}

ROOM_LAYOUTS = {
    "corridor": "tor tosh yo'lak bo'ylab",
    "grand_hall": "baland gumbazli ulkan zal markazida",
    "flooded_chamber": "tizzagacha qora suv bosgan xonada",
    "spiral_staircase": "tubi ko'rinmas aylanma zina chetida",
    "collapsed_bridge": "lava ustidagi yarim qulagan tosh ko'prikda",
    "pillar_arena": "o'nlab qadimiy marmar ustunlar orasida",
    "crystal_cavern": "miltillab turgan binafsha kristallar qurshovida",
    "dungeon_jail": "zanglagan temir qamoqxona panjaralari yonida",
    "ritual_chamber": "qurbonlik doirasi chizilgan qora plitalar ustida",
    "secret_passageway": "suriluvchi sirli devor ortidagi yashirin yo'lda"
}

def generate_procedural_room(floor: int = 1, room_number: int = 1) -> Dict[str, Any]:
    """
    1,000 xil kombinatsiyada zindon xonasini yaratadi.
    """
    theme_key = random.choice(list(DUNGEON_THEMES.keys()))
    room_type_key = random.choice(list(ROOM_TYPES.keys()))
    layout_key = random.choice(list(ROOM_LAYOUTS.keys()))
    
    theme = DUNGEON_THEMES[theme_key]
    room_type = ROOM_TYPES[room_type_key]
    layout_desc = ROOM_LAYOUTS[layout_key]
    
    room_title = f"{theme['icon']} {theme['name_uz']} — {room_type['name_uz']}"
    room_desc = f"{theme['desc']} Siz {layout_desc} harakatlanmoqdasiz. {room_type['desc_uz']}"
    
    return {
        "id": f"room_f{floor}_r{room_number}_{theme_key}_{room_type_key}_{layout_key}",
        "floor": floor,
        "room_number": room_number,
        "theme": theme_key,
        "theme_name": theme["name_uz"],
        "room_type": room_type_key,
        "title": room_title,
        "description": room_desc,
        "action_prompt": room_type["action"],
        "gold_reward": random.randint(20, 60) * floor if room_type_key in ["treasure", "combat"] else 0,
        "xp_reward": 30 * floor if room_type_key == "combat" else 15 * floor
    }

def get_dungeon_matrix_size() -> Dict[str, int]:
    """Zindon xonalari kombinatsiyasi hajmi."""
    themes = len(DUNGEON_THEMES)
    types = len(ROOM_TYPES)
    layouts = len(ROOM_LAYOUTS)
    return {
        "themes": themes,
        "room_types": types,
        "layouts": layouts,
        "total_rooms": themes * types * layouts
    }
