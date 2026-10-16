import random
from game.constants import HIT_ZONES
from game.dark_engine import DarkEngine

class BattleEngine:
    @staticmethod
    def calculate_round(attacker: dict, defender: dict, target_zone: str = "torso", action: str = "strike"):
        """
        12-zonali kinetik zarba hisoblagichi (Dark System bilan integratsiyalashgan).
        action: 'strike' (oddiy zarba), 'heavy_strike' (og'ir zarba), 'defend' (qalqon tutish), 'skill' (maxsus mahorat)
        """
        zone_info = HIT_ZONES.get(target_zone, HIT_ZONES["torso"])
        log = []

        # 0. AQL (SANITY) VA TELBALIK TEKSHIRUVI (Zulmat Tizimi)
        attacker_sanity = attacker.get("sanity", 100)
        is_panicked, panic_log, sanity_dmg_mult = DarkEngine.check_sanity_battle_effect(attacker_sanity)
        if panic_log:
            log.append(panic_log)
        if is_panicked:
            # Raund boy berildi (hujum qila olmadi)
            return 0, log, False
        
        # 1. Chidamlilik (Stamina) sarfi va tekshiruvi
        stamina_cost = 15 if action == "strike" else (30 if action == "heavy_strike" else 20)
        
        # Jarohatlar tufayli qo'shimcha charchoq
        extra_drain = attacker.get("stamina_drain_round", 0)
        if extra_drain > 0:
            stamina_cost += extra_drain
            log.append(f"🩸 Chuqur jarohat tufayli harakat og'irlashdi (+{extra_drain} Stamina ketdi).")

        is_exhausted = attacker.get("stamina", 100) <= 0
        
        if is_exhausted:
            stamina_damage_penalty = 0.5
            log.append("⚠️ Siz hansirab qoldingiz (Stamina 0)! Zarbangiz kuchi 50% ga pasaydi.")
        else:
            stamina_damage_penalty = 1.0
            attacker["stamina"] = max(0, attacker.get("stamina", 100) - stamina_cost)
            
        # 2. Qochish (Evasion/Dodge)
        attacker_runes = attacker.get("runes", []) or attacker.get("equipped_runes", [])
        has_frost_rune = "frost_rune" in attacker_runes
        has_fire_rune = "fire_rune" in attacker_runes
        has_lightning_rune = "lightning_rune" in attacker_runes

        defender_agi = defender.get("agility", 10)
        attacker_agi = attacker.get("agility", 10)
        dodge_chance = max(5, min(40, (defender_agi - attacker_agi) // 2 + 10))
        
        if has_frost_rune:
            dodge_chance = 0
            log.append("❄️ [Muz Runasi]: Dushman muzlab qoldi, zarbadan qochish imkoniyati 0%!")

        if random.randint(1, 100) <= dodge_chance and action != "skill":
            log.append(f"💨 {defender['name']} chaqqonlik bilan chetga sakrab zarbadan qochib qoldi!")
            return 0, log, False
            
        # 3. Zirh va Zarba Hisobi
        base_atk = attacker.get("strength", 15) * 1.5 + attacker.get("weapon_attack", 10)
        
        # Qonli Ahd (Demon Pact) Zulmat bonusi
        has_demon_pact = attacker.get("bloodline_trait") == "demon_pact"
        if has_demon_pact:
            base_atk += 45

        base_def = defender.get("constitution", 15) * 0.8 + defender.get("armor_defense", 8)
        
        skill_multiplier = 1.0
        if action == "heavy_strike":
            skill_multiplier = 1.6
        elif action == "skill":
            skill_multiplier = 2.0
            
        # Kritik zarba
        crit_chance = max(5, int(attacker_agi / 2.5) + zone_info["crit_bonus"])
        is_crit = random.randint(1, 100) <= crit_chance
        crit_multiplier = 1.8 if is_crit else 1.0
        
        # RNG o'zgaruvchanlik (0.9 dan 1.1 gacha)
        rng_factor = random.uniform(0.9, 1.1)
        
        raw_damage = (base_atk * skill_multiplier * zone_info["multiplier"] * stamina_damage_penalty * crit_multiplier * sanity_dmg_mult * rng_factor)
        
        # Qalqon bloklash tekshiruvi
        defender_blocked = False
        if defender.get("is_defending", False):
            if has_lightning_rune:
                log.append(f"⚡️ [Momaqaldiroq Runasi]: Zarb qalqonni 100% teshib o'tdi va dushman staminasini 0 qildi!")
                defender["stamina"] = 0
            else:
                raw_damage *= 0.3  # 70% zarar kamayadi
                defender_blocked = True
                log.append(f"🛡 {defender['name']} qalqonini tutib zarbani 70% ga qaytardi!")
            
        actual_damage = max(1, int(raw_damage - base_def))

        # Olov runasi (Har raund +25 olov zarari)
        if has_fire_rune:
            fire_burn_dmg = 25
            actual_damage += fire_burn_dmg
            log.append(f"🔥 [Olov Runasi]: Qurol alangalanib dushmanga +{fire_burn_dmg} olov zarari yetkazdi!")
        
        # Agar himoyalanuvchi staminasi 0 bo'lsa, 2x zarar oladi
        if defender.get("stamina", 100) <= 0:
            actual_damage = int(actual_damage * 1.8)
            log.append(f"💥 {defender['name']} charchaganligi sababli himoyalana olmadi (+80% zarar)!")
            
        defender["hp"] = max(0, defender["hp"] - actual_damage)
        
        crit_str = " (💥 KRITIK ZARBA!)" if is_crit else ""
        dark_str = " 🌑 [Zulmat Qahr-G'azabi]" if has_demon_pact else ""
        log.append(f"⚔️ {attacker['name']} dushmanning [{zone_info['name']}] qismiga {actual_damage} zarar yetkazdi!{crit_str}{dark_str}")
        
        # Qonli Ahd Lifesteal (Jon so'rish)
        if has_demon_pact and actual_damage > 10:
            leech_hp = int(actual_damage * 0.20)
            attacker["hp"] = min(attacker.get("max_hp", 100), attacker.get("hp", 100) + leech_hp)
            log.append(f"🩸 *QON SO'RISH:* Iblis kuchi dushmandan +{leech_hp} HP ni joningizga qo'shdi!")

        # Qon ketish ehtimoli
        if is_crit and zone_info["wound"] == "arterial_bleed":
            log.append(f"🩸 Dushmanning tomiri kesildi! Qon ketishi (Bleed) boshlandi.")
            defender["is_bleeding"] = True
            
        return actual_damage, log, is_crit
