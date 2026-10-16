# =====================================================================
# VALORIYA: MAHORAT SHAJARASI & IXTISOSLASHUV DASTURI (675 TALENTS)
# =====================================================================
# 3 Asosiy Sinf x 3 Sub-klass x 15 Talant x 5 Daraja = 675 ta mahorat birligi!
# Qahramonlar har daraja olganda Skill Point (SP) oladi va o'z sinfini shakllantiradi.
# =====================================================================

from typing import Dict, Any, List, Optional

SKILL_TREES = {
    # -------------------------------------------------------------
    # 1. JANGCHI (WARRIOR) SHAXOBCHASI
    # -------------------------------------------------------------
    "paladin": {
        "class_id": "warrior",
        "title_uz": "✨ Muqaddas Paladin",
        "desc_uz": "Ilohiy nur, himoya qalqonlari va davolovchi muqaddas kuch egasi.",
        "skills": {
            "pal_holy_strike": {
                "name": "Muqaddas Qilich Zarbasi",
                "type": "active",
                "icon": "⚔️",
                "cost_sp": 1,
                "max_rank": 5,
                "desc": "+30 Muqaddas nur zarari beradi va 15 HP salomatlikni tiklaydi.",
                "bonus_atk_per_rank": 12,
                "bonus_heal_per_rank": 8
            },
            "pal_divine_shield": {
                "name": "Ilohiy Qalqon",
                "type": "active",
                "icon": "🛡",
                "cost_sp": 1,
                "max_rank": 5,
                "desc": "2 navbat davomida barcha kiruvchi zarbalarni yutuvchi nur qalqoni.",
                "shield_per_rank": 35
            },
            "pal_righteous_aura": {
                "name": "Adolat Aurasi",
                "type": "passive",
                "icon": "✨",
                "cost_sp": 1,
                "max_rank": 5,
                "desc": "Qahramonning jismoniy va sehrli himoyasini doimiy oshiradi.",
                "def_per_rank": 6
            },
            "pal_lay_on_hands": {
                "name": "Shifo Nuri",
                "type": "active",
                "icon": "💖",
                "cost_sp": 2,
                "max_rank": 5,
                "desc": "Og'ir vaziyatda bir zumda salomatlikning 40% ini qayta tiklaydi.",
                "heal_pct_per_rank": 8
            },
            "pal_undead_bane": {
                "name": "Jonsizlar Qotili",
                "type": "passive",
                "icon": "💀",
                "cost_sp": 1,
                "max_rank": 5,
                "desc": "Skeletlar, zombilar va iblislarga qarshi zarbani oshiradi.",
                "pve_bonus_per_rank": 10
            },
            "pal_conviction": {"name": "Qat'iyat", "type": "passive", "icon": "👑", "cost_sp": 1, "max_rank": 5, "desc": "Tanqidiy zarba ehtimolini oshiradi.", "crit_per_rank": 3},
            "pal_zeal": {"name": "Fidoyilik", "type": "passive", "icon": "🔥", "cost_sp": 1, "max_rank": 5, "desc": "Harakat va hujum tezligini 10% oshiradi.", "speed_per_rank": 4},
            "pal_consecration": {"name": "Muqaddas Yer", "type": "active", "icon": "☀️", "cost_sp": 2, "max_rank": 5, "desc": "Atrofdagi barcha dushmanlarni kuydiruvchi muqaddas hudud.", "aoe_dmg_per_rank": 15},
            "pal_guardian_angel": {"name": "Qo'riqchi Farishta", "type": "passive", "icon": "👼", "cost_sp": 2, "max_rank": 5, "desc": "O'limga yaqinlashganda 20% salomatlik bilan avtomatik qutqarish.", "rescue_hp_per_rank": 5},
            "pal_holy_wrath": {"name": "Muqaddas G'azab", "type": "active", "icon": "⚡️", "cost_sp": 2, "max_rank": 5, "desc": "Dushmanning ko'zini ko'r qiluvchi qudratli chaqmoq zarbasi.", "dmg_per_rank": 20},
            "pal_redemption": {"name": "Mag'firat", "type": "passive", "icon": "🕊", "cost_sp": 1, "max_rank": 5, "desc": "Ruhiy travmalarga chidamlilikni oshiradi.", "sanity_res_per_rank": 6},
            "pal_radiance": {"name": "Jilvalanish", "type": "passive", "icon": "🌟", "cost_sp": 1, "max_rank": 5, "desc": "Zulmat zindonlarida ko'rish maydoni va barqarorlik beradi.", "light_per_rank": 5},
            "pal_blessed_armor": {"name": "Muborak Sovut", "type": "passive", "icon": "🥋", "cost_sp": 1, "max_rank": 5, "desc": "Maksimal HP miqdorini oshiradi.", "hp_per_rank": 25},
            "pal_sacred_duty": {"name": "Muqaddas Burch", "type": "passive", "icon": "📜", "cost_sp": 1, "max_rank": 5, "desc": "Kvestlar va topshiriqlardan ko'proq shon-sharaf olish.", "honor_per_rank": 10},
            "pal_martyr_grace": {"name": "Fidoyi Marhamati", "type": "passive", "icon": "🩸", "cost_sp": 3, "max_rank": 5, "desc": "Zarba qabul qilinganda dushmanga ilohiy qasos qaytarish.", "reflect_per_rank": 5}
        }
    },
    "blood_berserker": {
        "class_id": "warrior",
        "title_uz": "🩸 Qon Berserki",
        "desc_uz": "O'z salomatligi evaziga cheksiz g'azab, zarba tezligi va vampirizmga ega qotil.",
        "skills": {
            "ber_blood_rage": {"name": "Qon G'azabi", "type": "active", "icon": "🩸", "cost_sp": 1, "max_rank": 5, "desc": "Salomatlik evaziga hujum kuchini 35% oshiradi.", "atk_per_rank": 15},
            "ber_whirlwind": {"name": "Qonli Bo'ron", "type": "active", "icon": "🌪", "cost_sp": 2, "max_rank": 5, "desc": "Aylanma qilich bilan barcha dushmanlarga zarba berish.", "aoe_per_rank": 20},
            "ber_lifesteal_fangs": {"name": "Vampirizm Tishlari", "type": "passive", "icon": "🧛", "cost_sp": 1, "max_rank": 5, "desc": "Har bir zarbadan ma'lum qism hayotni tiklab olish.", "lifesteal_per_rank": 3},
            "ber_death_defy": {"name": "O'limga Tik Boqish", "type": "passive", "icon": "💀", "cost_sp": 2, "max_rank": 5, "desc": "Halokatli zarba qabul qilinganda 1 HP bilan tirik qolish.", "chance_per_rank": 6},
            "ber_frenzied_chop": {"name": "Shiddatli Qatliom", "type": "active", "icon": "🪓", "cost_sp": 2, "max_rank": 5, "desc": "Dushmanga ketma-ket 3 marta qattiq bolta urish.", "multihit_dmg_per_rank": 18},
            "ber_endless_thirst": {"name": "Cheksiz Chanqoqlik", "type": "passive", "icon": "🍷", "cost_sp": 1, "max_rank": 5, "desc": "Har bir o'ldirilgan dushmandan +30 HP tiklash.", "kill_heal_per_rank": 10},
            "ber_rampage": {"name": "Quturish", "type": "passive", "icon": "👺", "cost_sp": 1, "max_rank": 5, "desc": "Kam salomatlikda zarba 50% gacha oshadi.", "low_hp_dmg_per_rank": 8},
            "ber_heavy_cleave": {"name": "Sovutni Maydalash", "type": "active", "icon": "🔨", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanning himoyasini 30% sindiruvchi zarba.", "armor_break_per_rank": 6},
            "ber_pain_tolerance": {"name": "Og'riqqa Sabr", "type": "passive", "icon": "⛓", "cost_sp": 1, "max_rank": 5, "desc": "Jarohat va qon ketish oqibatlarini kamaytiradi.", "wound_res_per_rank": 7},
            "ber_bloodied_steel": {"name": "Qonli Po'lat", "type": "passive", "icon": "🗡", "cost_sp": 1, "max_rank": 5, "desc": "Qurolning tanqidiy zarbasi foizini oshiradi.", "crit_per_rank": 3},
            "ber_juggernaut": {"name": "Jaggernaut Kuch-quvvati", "type": "passive", "icon": "🦏", "cost_sp": 1, "max_rank": 5, "desc": "Stamina sarfini kamaytiradi.", "stamina_save_per_rank": 5},
            "ber_slaughterhouse": {"name": "Kushxona", "type": "passive", "icon": "🍖", "cost_sp": 2, "max_rank": 5, "desc": "Elita va Chempion dushmanlarga qarshi +25% zarar.", "elite_dmg_per_rank": 8},
            "ber_war_cry": {"name": "Urush Na'rasi", "type": "active", "icon": "🗣", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanni qo'rqitib, hujum kuchini pasaytiradi.", "fear_debuff_per_rank": 5},
            "ber_crimson_edge": {"name": "Qizil Tig'", "type": "passive", "icon": "🩸", "cost_sp": 1, "max_rank": 5, "desc": "Hujumda doimiy qon ketish effektini chaqiradi.", "bleed_dmg_per_rank": 6},
            "ber_decapitate": {"name": "Boshni Uzish", "type": "active", "icon": "💀", "cost_sp": 3, "max_rank": 5, "desc": "HP < 20% dushmanni bir zumda qatl qiluvchi halokatli tig'.", "execute_threshold_per_rank": 3}
        }
    },
    "colossus_tank": {
        "class_id": "warrior",
        "title_uz": "🛡 Titan Qalqonbardor",
        "desc_uz": "Buzilmas mudofaa, ulkan qalqon va jamoani himoya qiluvchi devor.",
        "skills": {
            "col_shield_slam": {"name": "Qalqon Zarbasi", "type": "active", "icon": "🛡", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanga qattiq urib, uni 1 navbatga karaxt qiladi.", "stun_dmg_per_rank": 10},
            "col_iron_fortress": {"name": "Temir Qo'rg'on", "type": "active", "icon": "🏰", "cost_sp": 2, "max_rank": 5, "desc": "3 navbat davomida barcha zarbalarni 40% ga kamaytiradi.", "reduction_per_rank": 5},
            "col_taunt": {"name": "G'azabli Hayqiriq", "type": "active", "icon": "📣", "cost_sp": 1, "max_rank": 5, "desc": "Dushman e'tiborini tortib, zarbasini 25% pasaytiradi.", "debuff_per_rank": 6},
            "col_thick_hide": {"name": "Tosh Teri", "type": "passive", "icon": "🪨", "cost_sp": 1, "max_rank": 5, "desc": "Jismoniy himoyani muntazam oshirib boradi.", "def_per_rank": 8},
            "col_bastion": {"name": "Buzilmas Devor", "type": "passive", "icon": "🧱", "cost_sp": 2, "max_rank": 5, "desc": "Yiqilish va qopqon zararlariga immunitet beradi.", "resist_per_rank": 10},
            "col_heavy_stance": {"name": "Og'ir Turish", "type": "passive", "icon": "🥋", "cost_sp": 1, "max_rank": 5, "desc": "Maksimal HP ni 40 tadan oshiradi.", "hp_per_rank": 35},
            "col_spiked_shield": {"name": "Tikanli Qalqon", "type": "passive", "icon": "🌵", "cost_sp": 1, "max_rank": 5, "desc": "Qalqonga urgan har bir dushmanga 15 tikan zarari.", "thorn_per_rank": 6},
            "col_unyielding": {"name": "Bo'ysunmas", "type": "passive", "icon": "🗿", "cost_sp": 1, "max_rank": 5, "desc": "Zahar va la'natlarga 40% chidamlilik.", "poison_res_per_rank": 8},
            "col_defenders_will": {"name": "Himoyachi Irodasi", "type": "passive", "icon": "❤️", "cost_sp": 1, "max_rank": 5, "desc": "Har navbatda salomatlik regeneratsiyasi.", "regen_per_rank": 5},
            "col_hold_the_line": {"name": "Chiziqni Saqlash", "type": "active", "icon": "🚩", "cost_sp": 2, "max_rank": 5, "desc": "Ortga chekinmaslik, kritik zarbalarni 0 ga tushirish.", "crit_immune_per_rank": 10},
            "col_mountain_heart": {"name": "Tog' Yuragi", "type": "passive", "icon": "🏔", "cost_sp": 1, "max_rank": 5, "desc": "Sanity (Aql) tushishini sekinlashtiradi.", "sanity_save_per_rank": 6},
            "col_armored_colossus": {"name": "Titan Sovuti", "type": "passive", "icon": "🦾", "cost_sp": 2, "max_rank": 5, "desc": "Og'ir sovutlarning sekinlashtiruvchi ta'sirini yo'qotish.", "mobility_per_rank": 5},
            "col_shield_wall": {"name": "Qalqonlar Devori", "type": "active", "icon": "🛡", "cost_sp": 2, "max_rank": 5, "desc": "Barcha jamoa a'zolariga himoya berish.", "party_def_per_rank": 7},
            "col_fortress_dominance": {"name": "Qo'rg'on Hukmi", "type": "passive", "icon": "👑", "cost_sp": 2, "max_rank": 5, "desc": "Qal'a mudofaasida va qamal janglarida +50% quvvat.", "siege_bonus_per_rank": 12},
            "col_eternal_guard": {"name": "Mangu Qo'riqchi", "type": "passive", "icon": "⚡️", "cost_sp": 3, "max_rank": 5, "desc": "Olingan zarbani energiyaga aylantirib, manani to'ldirish.", "mana_on_hit_per_rank": 4}
        }
    },

    # -------------------------------------------------------------
    # 2. SEHRGAR (MAGE) SHAXOBCHASI
    # -------------------------------------------------------------
    "elementalist": {
        "class_id": "mage",
        "title_uz": "🔥 Elementar Arxisehrgar",
        "desc_uz": "Olovli meteorlar, muzli bo'ronlar va chaqmoqlar hukmdori.",
        "skills": {
            "elm_meteor": {"name": "Osmon Meteori", "type": "active", "icon": "☄️", "cost_sp": 2, "max_rank": 5, "desc": "Dushman ustiga osmondan olovli meteorit tushiradi.", "dmg_per_rank": 25},
            "elm_blizzard": {"name": "Qahraton Bo'roni", "type": "active", "icon": "❄️", "cost_sp": 2, "max_rank": 5, "desc": "Dushmanlarni muzlatib, harakatini to'xtatadi.", "slow_per_rank": 10},
            "elm_chain_lightning": {"name": "Zanjirli Chaqmoq", "type": "active", "icon": "⚡️", "cost_sp": 1, "max_rank": 5, "desc": "Bir necha nishonlar orasida sakrab elektr zarbasi beradi.", "chain_dmg_per_rank": 15},
            "elm_arcane_mind": {"name": "Mistik Tafakkur", "type": "passive", "icon": "🔮", "cost_sp": 1, "max_rank": 5, "desc": "Maksimal Mana zaxirasi va sehr kuchini oshiradi.", "mana_per_rank": 20},
            "elm_pyroblast": {"name": "Magma Shari", "type": "active", "icon": "🔥", "cost_sp": 2, "max_rank": 5, "desc": "Uzoq yonuvchi doimiy olov zarari yetkazadi.", "burn_per_rank": 12},
            "elm_frost_armor": {"name": "Muz Sovuti", "type": "passive", "icon": "🧊", "cost_sp": 1, "max_rank": 5, "desc": "Hujum qilgan dushmanni muzlatib, sekinlashtiradi.", "chill_per_rank": 5},
            "elm_overload": {"name": "Haddan Tashqari Quvvat", "type": "passive", "icon": "💥", "cost_sp": 1, "max_rank": 5, "desc": "Sehrlarning kritik zarbasi ehtimoli va quvvati ortadi.", "spell_crit_per_rank": 4},
            "elm_combustion": {"name": "Portlovchi Alanga", "type": "passive", "icon": "🌋", "cost_sp": 1, "max_rank": 5, "desc": "Yonayotgan dushmanlar portlab ketadi.", "explosion_per_rank": 10},
            "elm_elemental_focus": {"name": "Elementar Diqqat", "type": "passive", "icon": "🎯", "cost_sp": 1, "max_rank": 5, "desc": "Sehr otishda xato ketish ehtimolini 0 ga tushirish.", "accuracy_per_rank": 6},
            "elm_flash_freeze": {"name": "Bir Zumda Muzlatish", "type": "active", "icon": "⛄️", "cost_sp": 2, "max_rank": 5, "desc": "Dushmanni butunlay toshdek muzga aylantiradi.", "freeze_turn_per_rank": 1},
            "elm_thunderstruck": {"name": "Chaqmoq Qahri", "type": "passive", "icon": "🌩", "cost_sp": 1, "max_rank": 5, "desc": "Elektr zarbalari dushmanning sovutini teshib o'tadi.", "armor_pen_per_rank": 8},
            "elm_arcane_surge": {"name": "Sehrli To'lqin", "type": "active", "icon": "🌊", "cost_sp": 2, "max_rank": 5, "desc": "Mana sarflamasdan ketma-ket 2 ta afsun yo'llash.", "free_cast_per_rank": 1},
            "elm_absolute_zero": {"name": "Mutloq Sovuq", "type": "passive", "icon": "🥶", "cost_sp": 2, "max_rank": 5, "desc": "Muz zararlarining kuchi 40% ga ortadi.", "ice_dmg_per_rank": 9},
            "elm_supernova": {"name": "Supernova Portlashi", "type": "active", "icon": "✨", "cost_sp": 3, "max_rank": 5, "desc": "Maydondagi barcha dushmanlarni yo'q qiluvchi yorug'lik portlashi.", "ultimate_dmg_per_rank": 35},
            "elm_archmage_supremacy": {"name": "Oliy Sehrgar Ustunligi", "type": "passive", "icon": "👑", "cost_sp": 3, "max_rank": 5, "desc": "Barcha sehr turlari zararini 50% ga oshiradi.", "all_spell_dmg_per_rank": 10}
        }
    },
    "necromancer": {
        "class_id": "mage",
        "title_uz": "☠️ Zulmat Nekromanti",
        "desc_uz": "O'liklar armiyasini tiriltiruvchi, suyak sovutlari va qarg'ishlar ustasi.",
        "skills": {
            "nec_raise_dead": {"name": "Skelet Askarni Tiriltirish", "type": "active", "icon": "💀", "cost_sp": 2, "max_rank": 5, "desc": "Jangda yordam berish uchun qabrdan skelet chaqiradi.", "skeleton_hp_per_rank": 25},
            "nec_bone_armor": {"name": "Suyak Sovuti", "type": "active", "icon": "🦴", "cost_sp": 1, "max_rank": 5, "desc": "Suyaklardan yasalgan qalqon zarbalarni yutadi.", "bone_shield_per_rank": 20},
            "nec_soul_drain": {"name": "Ruhni So'rib Olish", "type": "active", "icon": "👻", "cost_sp": 1, "max_rank": 5, "desc": "Dushmandan salomatlik va mana o'g'irlaydi.", "drain_per_rank": 12},
            "nec_plague_cloud": {"name": "Vabo Buluti", "type": "active", "icon": "☁️", "cost_sp": 2, "max_rank": 5, "desc": "Zaharli tutun bilan maydonni zaharlaydi.", "plague_dmg_per_rank": 10},
            "nec_dark_pact": {"name": "Zulmat Qasamyodi", "type": "passive", "icon": "📜", "cost_sp": 1, "max_rank": 5, "desc": "Har bir o'lik jasad nekromantni davolaydi.", "corpse_heal_per_rank": 15},
            "nec_corpse_explosion": {"name": "Jasad Portlashi", "type": "active", "icon": "💣", "cost_sp": 2, "max_rank": 5, "desc": "Yiqilgan raqib tanasini portlatib, dushmanlarni maydalash.", "explosion_per_rank": 25},
            "nec_grim_reaper": {"name": "O'lim O'rog'i", "type": "passive", "icon": "⛏", "cost_sp": 1, "max_rank": 5, "desc": "Dushman o'lganda kafolatlangan mana to'ldirish.", "mana_on_kill_per_rank": 8},
            "nec_terror_aura": {"name": "Dahshat Aurasi", "type": "passive", "icon": "😱", "cost_sp": 1, "max_rank": 5, "desc": "Atrofdagi dushmanlarning himoyasini 20% zaiflashtiradi.", "fear_debuff_per_rank": 5},
            "nec_spectral_shroud": {"name": "Arvoh Kafani", "type": "passive", "icon": "👤", "cost_sp": 1, "max_rank": 5, "desc": "Jismoniy zarbalardan qochish ehtimolini beradi.", "evasion_per_rank": 4},
            "nec_shadow_weaving": {"name": "Soya To'qish", "type": "passive", "icon": "🕸", "cost_sp": 1, "max_rank": 5, "desc": "Qorong'ulik sehrlarining zarbasini oshiradi.", "shadow_dmg_per_rank": 7},
            "nec_tomb_call": {"name": "Qabrlar Sadolari", "type": "active", "icon": "🪦", "cost_sp": 2, "max_rank": 5, "desc": "Bir vaqtning o'zida 3 ta zombini jangga chaqirish.", "minion_count_per_rank": 1},
            "nec_undead_mastery": {"name": "Jonsizlar Xojasi", "type": "passive", "icon": "👑", "cost_sp": 2, "max_rank": 5, "desc": "Chaqirilgan maxluqlarning zarbasi va joni 40% ortadi.", "minion_stat_per_rank": 9},
            "nec_soul_siphon": {"name": "Ruhlar Konveyeri", "type": "passive", "icon": "🔮", "cost_sp": 2, "max_rank": 5, "desc": "Dushman jon berayotganda Sanity tiklanadi.", "sanity_restore_per_rank": 6},
            "nec_abyssal_conduit": {"name": "Tubsizlik O'zani", "type": "passive", "icon": "🌌", "cost_sp": 2, "max_rank": 5, "desc": "Qorong'u zararlar raqibning qurolini chirita boshlaydi.", "decay_per_rank": 5},
            "nec_lich_form": {"name": "Lich Qiyofasi", "type": "active", "icon": "💀", "cost_sp": 3, "max_rank": 5, "desc": "O'lmas Lichga aylanadi: +100% sehr quvvati va to'liq jarohat immuniteti.", "lich_power_per_rank": 20}
        }
    },
    "chaos_sorcerer": {
        "class_id": "mage",
        "title_uz": "🌀 Xaos Sehrgari",
        "desc_uz": "Fazoni buzuvchi, qora tuynuklar va kutilmagan kuchlar sehrgari.",
        "skills": {
            "chs_void_rift": {"name": "Bo'shliq Yorig'i", "type": "active", "icon": "🕳", "cost_sp": 2, "max_rank": 5, "desc": "Fazoda yoriq ochib dushmanlarni yutadi.", "void_dmg_per_rank": 20},
            "chs_warp_reality": {"name": "Borliqni Buzish", "type": "active", "icon": "🌀", "cost_sp": 1, "max_rank": 5, "desc": "Tasodifiy kuchli ijobiy yoki halokatli effekt beradi.", "chaos_mult_per_rank": 15},
            "chs_singularity": {"name": "Qora Tuynuk", "type": "active", "icon": "🌌", "cost_sp": 2, "max_rank": 5, "desc": "Ulkan gravitatsiya bilan dushmanlarni maydalash.", "gravity_dmg_per_rank": 22},
            "chs_entangled_fate": {"name": "Chigal Qismat", "type": "passive", "icon": "🧶", "cost_sp": 1, "max_rank": 5, "desc": "Olingan zeerning yarmini dushmanning o'ziga aks ettirish.", "reflect_per_rank": 6},
            "chs_anomaly": {"name": "Sehrli Anomaliya", "type": "passive", "icon": "🔮", "cost_sp": 1, "max_rank": 5, "desc": "20% ehtimol bilan sehrlar 0 mana sarflaydi.", "free_chance_per_rank": 5},
            "chs_nether_beam": {"name": "Do'zax Nuri", "type": "active", "icon": "🔦", "cost_sp": 1, "max_rank": 5, "desc": "To'g'ri chiziq bo'ylab hamma narsani yoqib o'tadi.", "beam_dmg_per_rank": 16},
            "chs_cosmic_decay": {"name": "Kosmik Chirish", "type": "passive", "icon": "🪐", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanning barcha ijobiy auralarini yo'q qilib boradi.", "dispel_per_rank": 8},
            "chs_warp_echoes": {"name": "Fazo Aks-sadosi", "type": "passive", "icon": "🔊", "cost_sp": 1, "max_rank": 5, "desc": "Har bir afsun ortidan ikkinchi kichik aks-sado zarbasi tushadi.", "echo_dmg_per_rank": 7},
            "chs_spatial_tear": {"name": "Fazo Yirtig'i", "type": "active", "icon": "✂️", "cost_sp": 2, "max_rank": 5, "desc": "Dushman jismoniy tanasini bo'laklab tashlaydi.", "tear_dmg_per_rank": 18},
            "chs_chaos_inversion": {"name": "Xaos Teskariligi", "type": "passive", "icon": "🔄", "cost_sp": 1, "max_rank": 5, "desc": "Zarar olinganda ba'zida jon tiklanib ketadi.", "heal_chance_per_rank": 4},
            "chs_quantum_flux": {"name": "Kvant Oqimi", "type": "passive", "icon": "⚡️", "cost_sp": 1, "max_rank": 5, "desc": "Kritik zarba koeffitsientini 2.5x gacha oshirish.", "crit_dmg_per_rank": 10},
            "chs_void_cloak": {"name": "Bo'shliq Choponi", "type": "passive", "icon": "🧥", "cost_sp": 2, "max_rank": 5, "desc": "Zarbalardan fazoning boshqa burchagiga sakrab qochish.", "teleport_dodge_per_rank": 6},
            "chs_cataclysm": {"name": "Kataklizm", "type": "active", "icon": "🌋", "cost_sp": 3, "max_rank": 5, "desc": "Butun jang maydonida yovvoyi portlashlar zanjiri.", "cataclysm_dmg_per_rank": 30},
            "chs_paradox": {"name": "Vaqt Paradoksi", "type": "passive", "icon": "⏳", "cost_sp": 2, "max_rank": 5, "desc": "O'limga duchor bo'lganda vaqtni 1 navbat orqaga qaytarish.", "paradox_hp_per_rank": 8},
            "chs_entropy": {"name": "Mutloq Entropiya", "type": "passive", "icon": "⚛️", "cost_sp": 3, "max_rank": 5, "desc": "Xaos afsunlarining cheksiz kuchi (+60% Damage).", "entropy_per_rank": 12}
        }
    },

    # -------------------------------------------------------------
    # 3. QOCHOQ / MERGAN (ROGUE) SHAXOBCHASI
    # -------------------------------------------------------------
    "assassin": {
        "class_id": "rogue",
        "title_uz": "🗡 Soya Qotili (Assasin)",
        "desc_uz": "Zulmatda pinhon harakatlanuvchi, orqadan zarba va o'ldiruvchi zahar ustasi.",
        "skills": {
            "asn_shadowstep": {"name": "Soya Qadami", "type": "active", "icon": "👤", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanning orqasiga o'tib, keyingi zarbani 100% kritik qiladi.", "crit_bonus_per_rank": 10},
            "asn_backstab": {"name": "Orqadan Pichoq Urish", "type": "active", "icon": "🗡", "cost_sp": 2, "max_rank": 5, "desc": "Orqadan xiyonatkorona 250% yuqori halokatli pichoq zarbasi.", "dmg_mult_per_rank": 20},
            "asn_smoke_bomb": {"name": "Tutun Bomba", "type": "active", "icon": "💨", "cost_sp": 1, "max_rank": 5, "desc": "Ko'zni xira qiluvchi tutun sochib, qochish ehtimolini 70% oshiradi.", "evasion_per_rank": 8},
            "asn_lethal_venom": {"name": "Halokatli Toksin", "type": "passive", "icon": "🧪", "cost_sp": 1, "max_rank": 5, "desc": "Pichoq tig'iga kuchli zahar surtib, dushmanni sekin o'ldirish.", "poison_dmg_per_rank": 6},
            "asn_coup_de_grace": {"name": "So'nggi Hukm", "type": "active", "icon": "☠️", "cost_sp": 3, "max_rank": 5, "desc": "HP < 25% bo'lgan raqibni bir lahzada qatl qilish.", "execute_chance_per_rank": 5},
            "asn_blade_flurry": {"name": "Tig'lar Bo'roni", "type": "active", "icon": "⚔️", "cost_sp": 2, "max_rank": 5, "desc": "Tezkor 4 ta ketma-ket pichoq sanchilishi.", "flurry_hits_per_rank": 1},
            "asn_master_of_shadows": {"name": "Soyalar Xojasi", "type": "passive", "icon": "🌑", "cost_sp": 1, "max_rank": 5, "desc": "Tungi janglarda va qorong'u xonalarda +30% zarba.", "night_dmg_per_rank": 7},
            "asn_precision": {"name": "Zargarona Aniqlik", "type": "passive", "icon": "🎯", "cost_sp": 1, "max_rank": 5, "desc": "Tanqidiy zarba ehtimolini oshiradi.", "crit_per_rank": 4},
            "asn_silent_kill": {"name": "Tovushsiz Qotillik", "type": "passive", "icon": "🤫", "cost_sp": 1, "max_rank": 5, "desc": "Dushman o'lganda boshqa maxluqlar ogohlantirilmaydi.", "stealth_per_rank": 6},
            "asn_poison_affinity": {"name": "Zaharga Moslashuv", "type": "passive", "icon": "🐍", "cost_sp": 1, "max_rank": 5, "desc": "Zahar zararlaridan o'ziga immunitet va kuch olish.", "poison_res_per_rank": 9},
            "asn_shadow_veil": {"name": "Soya Pardasi", "type": "passive", "icon": "🌫", "cost_sp": 2, "max_rank": 5, "desc": "Jangdan so'ng darhol ko'rinmas bo'lib yashirinish.", "drop_aggro_per_rank": 8},
            "asn_bleed_out": {"name": "Qonini Bo'shatish", "type": "passive", "icon": "🩸", "cost_sp": 1, "max_rank": 5, "desc": "Ochiq jarohatlardan qon oqish tezligini oshirish.", "bleed_mult_per_rank": 7},
            "asn_executioner_touch": {"name": "Jallod Tegishi", "type": "passive", "icon": "🖐", "cost_sp": 2, "max_rank": 5, "desc": "Kritik zarbalar dushmanning mudofaasini maydalaydi.", "armor_pierce_per_rank": 8},
            "asn_ghost_walk": {"name": "Arvoh Qadami", "type": "passive", "icon": "👻", "cost_sp": 2, "max_rank": 5, "desc": "Qopqonlar va tuzoqlarga hech qachon tushmaslik.", "trap_avoid_per_rank": 10},
            "asn_phantom_strike": {"name": "Fantom Zarbasi", "type": "active", "icon": "⚡️", "cost_sp": 3, "max_rank": 5, "desc": "Ko'zga ko'rinmas holda dushmanning yuragiga tushuvchi halokatli zarba.", "phantom_dmg_per_rank": 30}
        }
    },
    "sharpshooter": {
        "class_id": "rogue",
        "title_uz": "🏹 Sharpshooter Mergan",
        "desc_uz": "Uzoq masofadan nishonni bexato uruvchi, o'qlar yomg'iri va qush ko'zi ustasi.",
        "skills": {
            "shp_snipe": {"name": "Mergan Zarbasi", "type": "active", "icon": "🎯", "cost_sp": 2, "max_rank": 5, "desc": "Kuchli tortilgan o'q bilan ulkan zarar yetkazadi.", "snipe_dmg_per_rank": 22},
            "shp_rain_of_arrows": {"name": "O'qlar Yomg'iri", "type": "active", "icon": "🌧", "cost_sp": 2, "max_rank": 5, "desc": "Maydonga yuzlab o'qlar yog'dirib, to'dani yakson qiladi.", "rain_dmg_per_rank": 18},
            "shp_piercing_shot": {"name": "Zirh Teshuvchi O'q", "type": "active", "icon": "🏹", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanning qalin po'lat sovutini butunlay teshib o'tadi.", "pierce_per_rank": 12},
            "shp_eagle_eye": {"name": "Burgut Ko'zi", "type": "passive", "icon": "🦅", "cost_sp": 1, "max_rank": 5, "desc": "Hujum aniqligi va tanqidiy zarba ehtimolini oshiradi.", "accuracy_per_rank": 5},
            "shp_concussive_shot": {"name": "Karaxt Qiluvchi O'q", "type": "active", "icon": "💫", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanni orqaga surib, harakatini to'xtatadi.", "slow_per_rank": 8},
            "shp_quick_draw": {"name": "Chaqqon Otish", "type": "passive", "icon": "⚡️", "cost_sp": 1, "max_rank": 5, "desc": "Birinchi zarbani dushmandan oldin berish imkoniyati.", "speed_per_rank": 6},
            "shp_bullseye": {"name": "To'g'ri Yurakka", "type": "passive", "icon": "🎯", "cost_sp": 1, "max_rank": 5, "desc": "Kritik zarbalar dushmanning harakatini 1 navbatga to'xtatadi.", "headshot_per_rank": 4},
            "shp_falconry": {"name": "Ovchi Lochini", "type": "passive", "icon": "🦅", "cost_sp": 2, "max_rank": 5, "desc": "Lochin dushmanning ko'zini cho'qib, sarosimaga soladi.", "falcon_dmg_per_rank": 10},
            "shp_trueshot": {"name": "Haqiqiy O'q", "type": "passive", "icon": "✨", "cost_sp": 1, "max_rank": 5, "desc": "Barcha kamon zarbalariga +20% sof kuch beradi.", "bow_dmg_per_rank": 8},
            "shp_barbed_arrow": {"name": "Tikanli Nayza O'qi", "type": "active", "icon": "🌵", "cost_sp": 1, "max_rank": 5, "desc": "Surganda og'ir jarohat qoldirib, qon oqizadi.", "bleed_per_rank": 9},
            "shp_heavy_draw": {"name": "Og'ir Ip Tortish", "type": "passive", "icon": "💪", "cost_sp": 1, "max_rank": 5, "desc": "Kuch ko'rsatkichi hisobiga kamon zarbasini oshirish.", "str_scale_per_rank": 6},
            "shp_nimble_footing": {"name": "Epchil Oyoqlar", "type": "passive", "icon": "👟", "cost_sp": 1, "max_rank": 5, "desc": "Yaqin masofadagi jangchilardan oson qochib ketish.", "kite_per_rank": 7},
            "shp_vital_spot": {"name": "Zaif Nuqta Qidiruvchisi", "type": "passive", "icon": "🔍", "cost_sp": 2, "max_rank": 5, "desc": "Maxluqlar zaifliklariga tegadigan zarba quvvati 50% oshadi.", "weakness_mult_per_rank": 10},
            "shp_master_marksman": {"name": "Usta Nishonchi", "type": "passive", "icon": "👑", "cost_sp": 2, "max_rank": 5, "desc": "Kamon turganda masofa oshgan sari zarar ko'payadi.", "range_dmg_per_rank": 9},
            "shp_ballistic_catastrophe": {"name": "Ballistik Falokat", "type": "active", "icon": "🚀", "cost_sp": 3, "max_rank": 5, "desc": "Quyoshni to'sadigan ulkan o'qlar selini yog'dirish.", "catastrophe_dmg_per_rank": 35}
        }
    },
    "trapper": {
        "class_id": "rogue",
        "title_uz": "🪤 Qaroqchi-Tuzoqchi",
        "desc_uz": "Minalar, tikanli simlar, portlovchi moddalar va qaroqchilik hiylalari ustasi.",
        "skills": {
            "trp_explosive_mine": {"name": "Portlovchi Mina", "type": "active", "icon": "💣", "cost_sp": 1, "max_rank": 5, "desc": "Dushman qadam bosganda portlab, 60 olovli zarar yetkazadi.", "mine_dmg_per_rank": 15},
            "trp_caltrops": {"name": "Temir Tikanlar", "type": "active", "icon": "🔩", "cost_sp": 1, "max_rank": 5, "desc": "Polga o'tkir tikanlar sochib, dushmanni sekinlashtiradi.", "slow_per_rank": 8},
            "trp_pocket_sand": {"name": "Ko'zga Qum Sochish", "type": "active", "icon": "🏖", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanni 2 navbatga butunlay ko'r qilib qo'yadi.", "blind_per_rank": 1},
            "trp_wire_snare": {"name": "Po'lat Qopqon", "type": "active", "icon": "⛓", "cost_sp": 1, "max_rank": 5, "desc": "Yirtqich maxluq oyog'ini mahkam qisib, qimirlatmaydi.", "snare_dmg_per_rank": 10},
            "trp_vanish": {"name": "Bir Zumda G'oyib Bo'lish", "type": "active", "icon": "💨", "cost_sp": 2, "max_rank": 5, "desc": "Xavfli vaziyatda jang maydonidan sirli tarzda yo'qolish.", "escape_per_rank": 10},
            "trp_sabotage": {"name": "Qo'poruvchilik", "type": "passive", "icon": "🧨", "cost_sp": 1, "max_rank": 5, "desc": "Dushmanning qurolini sindirib, zarbasini 25% pasaytirish.", "sabotage_per_rank": 6},
            "trp_acid_flask": {"name": "Kislotali Shisha", "type": "active", "icon": "🧪", "cost_sp": 1, "max_rank": 5, "desc": "Zirhni erituvchi yashil kislota otish.", "acid_corrode_per_rank": 8},
            "trp_tripwire": {"name": "Pinhona Ip", "type": "passive", "icon": "🧵", "cost_sp": 1, "max_rank": 5, "desc": "Dushman yaqinlashganda avtomatik yiqitish.", "trip_chance_per_rank": 5},
            "trp_ambush_master": {"name": "Pistirma Ustasi", "type": "passive", "icon": "🏕", "cost_sp": 2, "max_rank": 5, "desc": "Pistirmadan berilgan birinchi zarba 3 barobar kuchliroq.", "ambush_mult_per_rank": 12},
            "trp_greed_siphon": {"name": "O'g'ri Qo'llari", "type": "passive", "icon": "💰", "cost_sp": 1, "max_rank": 5, "desc": "Jangda dushman cho'ntagidan qo'shimcha oltin o'g'irlash.", "gold_steal_per_rank": 10},
            "trp_flash_powder": {"name": "Yaltiroq Kukun", "type": "active", "icon": "✨", "cost_sp": 1, "max_rank": 5, "desc": "Kuchli chaqnash bilan dushmanni sarosimaga solish.", "daze_per_rank": 6},
            "trp_shrapnel_trap": {"name": "Parchalanuvchi Qopqon", "type": "passive", "icon": "💥", "cost_sp": 2, "max_rank": 5, "desc": "Qopqonlar portlaganda metall parchalari sochiladi.", "shrapnel_per_rank": 9},
            "trp_master_thief": {"name": "Usta Qaroqchi", "type": "passive", "icon": "🗝", "cost_sp": 2, "max_rank": 5, "desc": "Zindondagi har qanday xazina qulflarini oson buzish.", "lockpick_per_rank": 10},
            "trp_scavengers_eye": {"name": "O'lja Ko'zi", "type": "passive", "icon": "👀", "cost_sp": 1, "max_rank": 5, "desc": "Nodir tushumlar va artefaktlar topish ehtimolini oshirish.", "loot_bonus_per_rank": 8},
            "trp_demolitionist": {"name": "Portlatuvchilar Qiroli", "type": "passive", "icon": "💣", "cost_sp": 3, "max_rank": 5, "desc": "Barcha portlovchi tuzoqlar radiusi va zarari 2x ga ko'payadi.", "bomb_boost_per_rank": 15}
        }
    }
}

def get_skills_matrix_size() -> Dict[str, int]:
    """Mahoratlar shajarasi hajmini hisoblaydi."""
    specs_count = len(SKILL_TREES)
    total_skills = sum(len(s["skills"]) for s in SKILL_TREES.values())
    total_ranks = sum(
        sum(skill["max_rank"] for skill in s["skills"].values())
        for s in SKILL_TREES.values()
    )
    return {
        "specializations": specs_count,
        "total_skill_nodes": total_skills,
        "total_skill_upgrades": total_ranks
    }
