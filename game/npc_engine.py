import random
from game.constants import BOT_FIRST_NAMES, BOT_TITLES, BOT_EPITHETS, BOT_PERSONAS, HIT_ZONES

class NPCEngine:
    @staticmethod
    def generate_bot_knight(target_level: int = 1):
        """
        O'yinchining darajasiga mos avtomatik Bot-Ritsar yaratadi.
        """
        level = max(1, target_level + random.choice([-1, 0, 1]))
        title = random.choice(BOT_TITLES)
        name = random.choice(BOT_FIRST_NAMES)
        epithet = random.choice(BOT_EPITHETS)
        full_name = f"{title} {name} {epithet}"
        
        persona = random.choice(BOT_PERSONAS)
        
        # Darajasiga qarab stats
        base_hp = 100 + (level * 20)
        base_atk = 18 + (level * 6)
        base_def = 10 + (level * 5)
        base_agi = 10 + (level * 3)
        
        # O'lja hisobi
        loot_gold = random.randint(35, 75) * level
        loot_xp = 40 * level
        
        return {
            "name": full_name,
            "level": level,
            "hp": base_hp,
            "max_hp": base_hp,
            "stamina": 100,
            "strength": base_atk,
            "constitution": base_def,
            "agility": base_agi,
            "weapon_attack": level * 4,
            "armor_defense": level * 3,
            "persona": persona,
            "is_defending": False,
            "is_bleeding": False,
            "loot_gold": loot_gold,
            "loot_xp": loot_xp
        }

    @staticmethod
    def choose_bot_action(bot: dict, opponent_hp_percent: float):
        """
        AI Bot xarakteriga qarab harakatni tanlaydi.
        """
        hp_percent = (bot["hp"] / bot["max_hp"]) * 100
        persona = bot.get("persona", "berserk")
        
        # 1. Qo'rqoq (Coward)
        if persona == "coward" and hp_percent < 25:
            return "surrender", "stomach", "🏳️ Dushman qo'rquvdan tiz cho'kib, taslim bo'lishini va oltinlarini berishini aytdi!"
            
        # 2. Taktik Himoyachi (Defender)
        if persona == "defender":
            if random.random() < 0.45:
                bot["is_defending"] = True
                return "defend", "torso", f"🛡 {bot['name']} qalqoni ortiga yashirindi."
            return "strike", random.choice(["torso", "r_shoulder", "stomach"]), ""
            
        # 3. Berserk (Tajovuzkor)
        if persona == "berserk":
            target = random.choice(["head", "neck", "torso"])
            if random.random() < 0.5:
                return "heavy_strike", target, f"🩸 {bot['name']} vahshiy qichqiriq bilan og'ir zarba bermoqda!"
            return "strike", target, ""
            
        # 4. Hiylakor (Poisoner)
        target = random.choice(["neck", "groin", "face"])
        return "strike", target, f"🐍 {bot['name']} zaif nuqtani nishonga olmoqda!"
