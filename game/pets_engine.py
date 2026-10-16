# =====================================================================
# VALORIYA: JANGOVAR HAMROHLAR & MINIKLAR DASTURI (960 PETS & MOUNTS)
# =====================================================================
# 30 ta Hayvon Zoti x 4 Evolutsiya Bosqichi x 8 Element Aspekti = 960 ta unikal hamroh!
# Hamrohlar qahramonga jangda bevosita yordam beradi, zarbalarni yutadi va minik vazifasini bajaradi.
# =====================================================================

import random
from typing import Dict, Any, List, Optional

PET_SPECIES = {
    "wolf_shadow": {"name_uz": "Yerosti Soya Bo'risi", "icon": "🐺", "type": "predator", "base_atk": 25, "base_def": 12, "base_hp": 90, "desc": "Zulmatda ko'zlari qizil yonuvchi, to'da bo'lib ov qiluvchi shafqatsiz bo'ri."},
    "horse_royal": {"name_uz": "Qirollik Oq Tulpori", "icon": "🐎", "type": "mount", "base_atk": 15, "base_def": 20, "base_hp": 130, "desc": "Qirollar gvardiyasining chopqir va chidamlilikda tengsiz mashhur zotli tulpori."},
    "griffin_storm": {"name_uz": "Qanotli Bo'ron Griffoni", "icon": "🦅", "type": "flying", "base_atk": 30, "base_def": 18, "base_hp": 110, "desc": "Burgut boshi va sher gavdasiga ega afsonaviy osmon hukmdori."},
    "panther_night": {"name_uz": "Tungi Qora Pantera", "icon": "🐆", "type": "predator", "base_atk": 28, "base_def": 10, "base_hp": 85, "desc": "Bironta tovush chiqarmasdan daraxt shoxlaridan sakrab ov qiluvchi pantera."},
    "lizard_crypt": {"name_uz": "Kript Suyak Kaltakesagi", "icon": "🦎", "type": "reptile", "base_atk": 22, "base_def": 25, "base_hp": 120, "desc": "Zindon toshlari orasida yashovchi, terisi po'latday qattiq kaltakesak."},
    "dragon_magma": {"name_uz": "Magmali Qizil Ajdarchasi", "icon": "🐉", "type": "dragon", "base_atk": 40, "base_def": 22, "base_hp": 140, "desc": "Vulqon yoriqlaridan chiqqan, og'zidan doimiy tutun va lava otilib turuvchi ajdar."},
    "bear_titan": {"name_uz": "Tog'li Titan Ayig'i", "icon": "🐻", "type": "beast", "base_atk": 32, "base_def": 30, "base_hp": 180, "desc": "Ulkan panjalari bilan otni ham bir zarbada qulata oladigan mahobatli ayiq."},
    "leopard_frost": {"name_uz": "Muz Qoyalari Qor Qoploni", "icon": "❄️", "type": "predator", "base_atk": 29, "base_def": 14, "base_hp": 95, "desc": "Mangu qorli cho'qqilarda yashovchi, sovuqdan zarracha qo'rqmaydigan qoplon."},
    "owl_mystic": {"name_uz": "Mistik Qadimgi Boyqush", "icon": "🦉", "type": "magical", "base_atk": 18, "base_def": 16, "base_hp": 80, "desc": "Egasiga xavfni oldindan sezdiruvchi va sehr energiyasini to'ldiruvchi donishmand qush."},
    "lion_golden": {"name_uz": "Oltin Yolli Cho'l Arsloni", "icon": "🦁", "type": "beast", "base_atk": 35, "base_def": 20, "base_hp": 130, "desc": "Quyosh nurlarida tilladek jilvalanuvchi o'rmonlar va dashtlar qiroli."},
    "raven_doom": {"name_uz": "Zulmat Qarg'asi", "icon": "🐦‍⬛", "type": "magical", "base_atk": 20, "base_def": 10, "base_hp": 70, "desc": "Jonsizlar va o'liklar olami bilan aloqa bog'lovchi mash'um qora qarg'a."},
    "hound_hell": {"name_uz": "Do'zax Qizil Tozisi", "icon": "🐕", "type": "demon", "base_atk": 33, "base_def": 15, "base_hp": 105, "desc": "Ko'zlari alangalanuvchi, qon hidini 5 chaqirimdan seza oladigan do'zax iti."},
    "turtle_iron": {"name_uz": "Plitali Tosh Toshbaqasi", "icon": "🐢", "type": "tank", "base_atk": 12, "base_def": 45, "base_hp": 220, "desc": "Hech qanday o'q va qilich tesha olmaydigan qalin sovutli qadimiy toshbaqa."},
    "falcon_thunder": {"name_uz": "Chaqmoq Lochini", "icon": "⚡️", "type": "flying", "base_atk": 34, "base_def": 12, "base_hp": 85, "desc": "Osmondan chaqmoq tezligida sho'ng'ib raqib ko'zini cho'quvchi lochin."},
    "serpent_venom": {"name_uz": "Zaharli Zumrad Ilon", "icon": "🐍", "type": "reptile", "base_atk": 26, "base_def": 14, "base_hp": 90, "desc": "Bitta tomchi zahari filni qulatishga yetadigan yashil ilon."},
    "fox_spirit": {"name_uz": "O'rmon Mistik Tuluxasi", "icon": "🦊", "type": "magical", "base_atk": 22, "base_def": 15, "base_hp": 90, "desc": "To'qqiz dumi borligi aytiladigan, o'yinchiga epchillik va qochish baxsh etuvchi tulki."},
    "boar_armored": {"name_uz": "Yovvoyi Po'lat Qoboni", "icon": "🐗", "type": "beast", "base_atk": 27, "base_def": 28, "base_hp": 150, "desc": "Qattiq tishlari bilan dushman saflarini yorib o'tuvchi qahrli qobon."},
    "stag_celestial": {"name_uz": "Nurli Osmon Bug'usi", "icon": "🦌", "type": "celestial", "base_atk": 18, "base_def": 22, "base_hp": 140, "desc": "Shoxlaridan shifobaxsh nur taralib turuvchi, qahramonni davolovchi kiyik."},
    "spider_widow": {"name_uz": "Qora Beva O'rgimchagi", "icon": "🕷", "type": "insect", "base_atk": 28, "base_def": 16, "base_hp": 95, "desc": "Dushman oyoqlariga to'r otib harakatdan to'xtatuvchi zaharli maxluq."},
    "hydra_swamp": {"name_uz": "Botqoqlik Uch Boshli Gidrasi", "icon": "🐲", "type": "reptile", "base_atk": 38, "base_def": 24, "base_hp": 160, "desc": "Har bir boshi alohida zahar purkaydigan dahshatli botqoq yirtqichi."},
    "bat_vampire": {"name_uz": "Qonxo'r Qanotli Ko'rshapalak", "icon": "🦇", "type": "flying", "base_atk": 24, "base_def": 12, "base_hp": 80, "desc": "Dushmandan qon so'rib, uning yarmini egasiga o'tkazuvchi vampir yordamchi."},
    "tiger_sabre": {"name_uz": "Qilich Tishli Muz Yo'lbarsi", "icon": "🐅", "type": "predator", "base_atk": 36, "base_def": 18, "base_hp": 125, "desc": "Uzunligi yarim metrli tishlarga ega, ibtidoiy muzlik davri yo'lbarsi."},
    "golem_mini": {"name_uz": "Miniaturyali Runa Golemi", "icon": "🗿", "type": "construct", "base_atk": 20, "base_def": 38, "base_hp": 190, "desc": "Qadimiy runalar bilan jonlantirilgan, buyruqlarga so'zsiz bo'ysunuvchi tosh askar."},
    "phoenix_ember": {"name_uz": "Qayta Tug'iluvchi Feniks", "icon": "🔥", "type": "celestial", "base_atk": 38, "base_def": 20, "base_hp": 115, "desc": "Kuli ichidan qayta tiriluvchi va qahramonni o'limdan qutqaruvchi ilohiy qush."},
    "rhino_obsidian": {"name_uz": "Obsidian Qora Karkadoni", "icon": "🦏", "type": "tank", "base_atk": 30, "base_def": 40, "base_hp": 210, "desc": "Qora obsidian toshdek shoxi bilan qamal devorlarini buzuvchi hayvon."},
    "scorpion_desert": {"name_uz": "Qizil Qumlar Chayoni", "icon": "🦂", "type": "insect", "base_atk": 31, "base_def": 22, "base_hp": 100, "desc": "Zaharli dumli nishi bilan dushmanning mudofaasini maydalovchi chayon."},
    "wisp_astral": {"name_uz": "Yulduzlar Aurali Uchquni", "icon": "✨", "type": "magical", "base_atk": 16, "base_def": 20, "base_hp": 90, "desc": "Havo bo'ylab suzib yuruvchi, egasiga aql (Sanity) va mana beruvchi yorug'lik."},
    "chocobo_runner": {"name_uz": "Tezkor Qush Minik", "icon": "🦤", "type": "mount", "base_atk": 16, "base_def": 16, "base_hp": 110, "desc": "Uzoq shaharlararo karvon safarlarida yo'l vaqtini 50% qisqartiruvchi chopqir qush."},
    "wyvern_cloud": {"name_uz": "Bulutlar Qora Vivernasi", "icon": "🦖", "type": "dragon", "base_atk": 42, "base_def": 25, "base_hp": 150, "desc": "Tog'lar ustidan shamoldek uchib o'tuvchi ulkan viverna."},
    "leviathan_pup": {"name_uz": "Cho'kkan Shahar Kichik Leviatani", "icon": "🐳", "type": "water", "base_atk": 35, "base_def": 26, "base_hp": 170, "desc": "Okeanlar tubidan chiqqan, to'lqinlar bilan dushmanlarni yuvib ketuvchi mavjudot."}
}

EVOLUTION_STAGES = {
    1: {"stage_name": "Chaqaloq / Bolaligi (Baby)", "stat_mult": 1.0, "skill_slots": 0, "can_mount": False},
    2: {"stage_name": "O'smir Yirtqich (Juvenile)", "stat_mult": 2.2, "skill_slots": 1, "can_mount": False},
    3: {"stage_name": "Jangovar Vahshiy (Adult Warrior)", "stat_mult": 4.5, "skill_slots": 2, "can_mount": True},
    4: {"stage_name": "Qadimiy Afsona (Ancient Mythic)", "stat_mult": 9.0, "skill_slots": 3, "can_mount": True}
}

ELEMENT_ASPECTS = {
    "fire": {"name_uz": "🔥 Olov Aspekti", "bonus_atk": 15, "burn_dot": 20, "desc": "Hujumlarga olovli yonish effekti qo'shadi."},
    "frost": {"name_uz": "❄️ Muz Aspekti", "bonus_def": 12, "slow_chance": 25, "desc": "Dushmanni sovuq bilan muzlatib, harakatini sekinlashtiradi."},
    "lightning": {"name_uz": "⚡️ Chaqmoq Aspekti", "bonus_crit": 12, "chain_shock": 18, "desc": "Tanqidiy zarba va elektr zanjirli zarar beradi."},
    "venom": {"name_uz": "🧪 Zahar Aspekti", "poison_dot": 22, "bonus_atk": 10, "desc": "Har bir zarbada dushman qonini zahar bilan zaharlaydi."},
    "holy": {"name_uz": "✨ Nur Aspekti", "heal_per_turn": 25, "dark_res": 30, "desc": "Qahramonni har raundda davolab boradi va zulmatdan asraydi."},
    "shadow": {"name_uz": "👤 Soya Aspekti", "evasion": 20, "night_boost": 30, "desc": "Zarbalardan qochish va tunda ikki barobar kuch beradi."},
    "earth": {"name_uz": "🪨 Tosh Aspekti", "bonus_def": 25, "shield_hp": 50, "desc": "Titan mudofaasi va doimiy tosh qalqon beradi."},
    "chaos": {"name_uz": "🌀 Xaos Aspekti", "chaos_crit": 25, "unpredictable": True, "desc": "Kutilmaganda dushmanga 2.5x portlovchi halokat yetkazadi."}
}

def generate_companion(species_id: Optional[str] = None, stage: int = 1, aspect_key: Optional[str] = None) -> Dict[str, Any]:
    """
    30 Hayvon x 4 Bosqich x 8 Aspekt = 960 xil kombinatsiyada hamroh yaratadi.
    """
    if not species_id or species_id not in PET_SPECIES:
        species_id = random.choice(list(PET_SPECIES.keys()))
        
    if not aspect_key or aspect_key not in ELEMENT_ASPECTS:
        aspect_key = random.choice(list(ELEMENT_ASPECTS.keys()))
        
    species = PET_SPECIES[species_id]
    stage_info = EVOLUTION_STAGES.get(stage, EVOLUTION_STAGES[1])
    aspect = ELEMENT_ASPECTS[aspect_key]
    
    mult = stage_info["stat_mult"]
    final_atk = int((species["base_atk"] + aspect.get("bonus_atk", 0)) * mult)
    final_def = int((species["base_def"] + aspect.get("bonus_def", 0)) * mult)
    final_hp = int(species["base_hp"] * mult)
    
    full_name = f"{species['icon']} {aspect['name_uz']} — {species['name_uz']} [{stage_info['stage_name']}]"
    
    return {
        "id": f"pet_{species_id}_{stage}_{aspect_key}_{random.randint(1000, 9999)}",
        "species_id": species_id,
        "name": full_name,
        "stage": stage,
        "stage_title": stage_info["stage_name"],
        "aspect": aspect_key,
        "aspect_title": aspect["name_uz"],
        "atk": final_atk,
        "def": final_def,
        "hp": final_hp,
        "max_hp": final_hp,
        "hunger": 100,
        "can_mount": stage_info["can_mount"],
        "skill_slots": stage_info["skill_slots"],
        "aspect_desc": aspect["desc"],
        "desc": f"{species['desc']} {aspect['desc']}"
    }

def get_pet_matrix_size() -> Dict[str, int]:
    """Hamrohlar matritsasi hajmini hisoblaydi."""
    species_cnt = len(PET_SPECIES)
    stages_cnt = len(EVOLUTION_STAGES)
    aspects_cnt = len(ELEMENT_ASPECTS)
    return {
        "species": species_cnt,
        "evolution_stages": stages_cnt,
        "aspects": aspects_cnt,
        "total_companion_variants": species_cnt * stages_cnt * aspects_cnt
    }
