import io
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List

def get_font(size: int, bold: bool = False):
    """Windows va Linux shriftlarini xavfsiz yuklash yoki standart shriftga o'tish."""
    font_names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/tahomabd.ttf" if bold else "C:/Windows/Fonts/tahoma.ttf",
        "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    ]
    for path in font_names:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_progress_bar(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int, current: int, max_val: int, fill_color: tuple, bg_color=(35, 39, 42), border_color=(180, 150, 80)):
    draw.rectangle([x, y, x + width, y + height], fill=bg_color, outline=border_color, width=1)
    if max_val > 0:
        ratio = max(0.0, min(1.0, current / max_val))
        fill_width = int(width * ratio)
        if fill_width > 0:
            draw.rectangle([x + 1, y + 1, x + fill_width - 1, y + height - 1], fill=fill_color)

def generate_knight_card(character: Dict[str, Any], equipment: List[Dict[str, Any]] = None, guild_name: str = None) -> io.BytesIO:
    """
    Ritsarning yuqori sifatli 800x520 o'lchamdagi rasmiy qirollik shaxsiy yorlig'ini (kartasini) yaratadi.
    """
    equipment = equipment or []
    width = 800
    height = 530

    # 1. Asosiy fon (Qorong'i ritsarlik plitasi)
    img = Image.new("RGB", (width, height), color=(14, 18, 26))
    draw = ImageDraw.Draw(img)

    # Gradient effekti (yuqoridan pastga)
    for y in range(height):
        alpha = y / height
        r = int(14 + (24 - 14) * alpha)
        g = int(18 + (28 - 18) * alpha)
        b = int(26 + (42 - 26) * alpha)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Oltin qirollik hoshiyasi (Double gold frame)
    gold_outer = (212, 175, 55)
    gold_inner = (138, 110, 30)
    draw.rectangle([10, 10, width - 10, height - 10], outline=gold_outer, width=3)
    draw.rectangle([16, 16, width - 16, height - 16], outline=gold_inner, width=1)

    # Burchak bezaklari
    corner_size = 14
    for cx, cy in [(12, 12), (width - 12 - corner_size, 12), (12, height - 12 - corner_size), (width - 12 - corner_size, height - 12 - corner_size)]:
        draw.rectangle([cx, cy, cx + corner_size, cy + corner_size], fill=gold_outer)

    # Shriftlar
    font_title = get_font(22, bold=True)
    font_name = get_font(26, bold=True)
    font_sub = get_font(15, bold=False)
    font_bold = get_font(15, bold=True)
    font_stat = get_font(14, bold=False)
    font_small = get_font(12, bold=False)

    # 3. Sarlavha (Header)
    header_text = "VALORIYA RITSARLAR QIROLLIGI"
    draw.text((width // 2, 36), header_text, fill=gold_outer, font=font_title, anchor="mm")
    draw.line([(120, 52), (width - 120, 52)], fill=gold_inner, width=1)

    # 4. Ritsar Nomi & Toj
    is_king = bool(character.get("is_king", 0))
    knight_name = character.get("name", "Noma'lum Ritsar")
    if is_king:
        draw.text((40, 85), f"👑 [VALORIYA QIROLI] {knight_name}", fill=(255, 215, 0), font=font_name)
    else:
        draw.text((40, 85), f"⚔️ {knight_name}", fill=(240, 240, 245), font=font_name)

    lvl = character.get("level", 1)
    cls = character.get("class_id", "warrior").capitalize()
    k_id = character.get("kingdom_id", "Qirolliksiz")
    g_txt = f" | 🐺 Gildiya: {guild_name}" if guild_name else ""
    draw.text((42, 122), f"Daraja: {lvl} • Kasb: {cls} • Qirollik: {k_id}{g_txt}", fill=(180, 190, 205), font=font_sub)

    # 5. Jon (HP), Chidamlilik (Stamina) va Aql (Sanity) barlari
    bar_x = 42
    bar_width = 330
    bar_h = 16

    # HP
    hp = character.get("hp", 100)
    max_hp = character.get("max_hp", 100)
    draw.text((bar_x, 158), f"❤️ Jon (HP): {hp}/{max_hp}", fill=(240, 100, 100), font=font_bold)
    draw_progress_bar(draw, bar_x, 180, bar_width, bar_h, hp, max_hp, fill_color=(220, 50, 50))

    # Stamina
    stamina = character.get("stamina", 100)
    max_stamina = character.get("max_stamina", 100)
    draw.text((bar_x, 210), f"⚡️ Stamina: {stamina}/{max_stamina}", fill=(70, 160, 255), font=font_bold)
    draw_progress_bar(draw, bar_x, 232, bar_width, bar_h, stamina, max_stamina, fill_color=(40, 140, 240))

    # Sanity
    sanity = character.get("sanity", 100)
    draw.text((bar_x, 262), f"🧠 Aql-Hush (Sanity): {sanity}%", fill=(190, 120, 250), font=font_bold)
    draw_progress_bar(draw, bar_x, 284, bar_width, bar_h, sanity, 100, fill_color=(150, 80, 230))

    # 6. O'ng ustun: Jangovar atributlar (Stats Box)
    box_x = 410
    box_y = 155
    box_w = 345
    box_h = 150
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(20, 25, 36), outline=(60, 75, 95), width=1)
    draw.text((box_x + 15, box_y + 12), "📊 JANGOVAR STATISTIKA", fill=gold_outer, font=font_bold)

    str_val = character.get("strength", 15)
    agi_val = character.get("agility", 12)
    con_val = character.get("constitution", 15)
    int_val = character.get("intelligence", 10)

    draw.text((box_x + 15, box_y + 40), f"🗡 Kuch (STR): {str_val}", fill=(220, 220, 230), font=font_stat)
    draw.text((box_x + 180, box_y + 40), f"🏹 Chaqqonlik (AGI): {agi_val}", fill=(220, 220, 230), font=font_stat)
    draw.text((box_x + 15, box_y + 68), f"🛡 Bardosh (CON): {con_val}", fill=(220, 220, 230), font=font_stat)
    draw.text((box_x + 180, box_y + 68), f"🔮 Zakovat (INT): {int_val}", fill=(220, 220, 230), font=font_stat)

    wins = character.get("wins", 0)
    losses = character.get("losses", 0)
    total_battles = wins + losses
    winrate = f"{(wins / total_battles * 100):.1f}%" if total_battles > 0 else "0%"
    honor = character.get("honor", 0)
    draw.text((box_x + 15, box_y + 98), f"⚔️ Duel: {wins}G' / {losses}M ({winrate}) | 🎖 Shon: {honor}", fill=(255, 200, 100), font=font_stat)
    gold = character.get("gold", 0)
    gems = character.get("gems", 0)
    draw.text((box_x + 15, box_y + 122), f"💰 Xazina: {gold:,} 🪙 Oltin | {gems} 💎 Javohir", fill=(240, 210, 80), font=font_stat)

    # 7. Pastki Qism: Kiyingan Qurol va Sovutlar
    gear_box_y = 325
    draw.rectangle([40, gear_box_y, width - 40, gear_box_y + 145], fill=(18, 22, 32), outline=(50, 60, 75), width=1)
    draw.text((55, gear_box_y + 12), "🛡 JANGOVAR ANJOMLAR & RUNALAR", fill=gold_outer, font=font_bold)

    # Qurollarni aniqlash
    equipped_items = [eq for eq in equipment if eq.get("is_equipped") == 1]
    weapon = next((eq for eq in equipped_items if eq.get("slot_type") == "weapon"), None)
    armor = next((eq for eq in equipped_items if eq.get("slot_type") == "armor"), None)
    shield = next((eq for eq in equipped_items if eq.get("slot_type") == "shield"), None)

    w_name = weapon["item_name"] if weapon else "Yo'q (Mushtlar)"
    a_name = armor["item_name"] if armor else "Yo'q (Yalang'och)"
    s_name = shield["item_name"] if shield else "Yo'q"
    horse_name = character.get("horse_name", "Boychibor")
    bond = character.get("horse_bond", 10)

    draw.text((55, gear_box_y + 42), f"🗡 Qurol: {w_name}", fill=(240, 240, 250), font=font_stat)
    draw.text((410, gear_box_y + 42), f"🛡 Sovut: {a_name}", fill=(240, 240, 250), font=font_stat)
    draw.text((55, gear_box_y + 72), f"🛡 Qalqon: {s_name}", fill=(240, 240, 250), font=font_stat)
    draw.text((410, gear_box_y + 72), f"🐎 Jangovar Ot: {horse_name} ({bond}% Sadoqat)", fill=(240, 240, 250), font=font_stat)

    trait = character.get("bloodline_trait", "noble_blood")
    trait_name = "🩸 Iblis Qonli Ahdi (Dark System)" if trait == "demon_pact" else "👑 Asilzoda Qoni"
    draw.text((55, gear_box_y + 105), f"🧬 Qon chizig'i: {trait_name}", fill=(200, 180, 220), font=font_stat)

    # 8. Footer yozuvi
    footer_text = "Valoriya Qirolligi Rasmiy Yorlig'i • O'yin: @ValoriyaBot"
    draw.text((width // 2, height - 24), footer_text, fill=(120, 130, 145), font=font_small, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
