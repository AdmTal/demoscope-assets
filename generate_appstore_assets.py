#!/usr/bin/env python3
"""
DemoScope iOS App Store Custom Product Page Asset Generator
============================================================
Generates localized promotional screenshots for iPhone and iPad.
Custom Product Page focus: Teleprompter feature.

Usage:
    python3 generate_appstore_assets.py

Output:
    AppStoreAssets/
      iPhone/<lang>/  (16 images per language: 4 clips × 4 sizes)
      iPad/<lang>/    (16 images per language: 4 clips × 4 sizes)
"""

import subprocess
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORTRAIT_DIR = os.path.join(BASE_DIR, "Portrait")
OUTPUT_DIR = os.path.join(BASE_DIR, "AppStoreAssets")

CLIPS = ["woman_1", "man_1", "woman_2", "man_2"]


# ─────────────────────────────────────────────
# APP STORE SCREENSHOT SIZES
# ─────────────────────────────────────────────
IPHONE_SIZES = [
    (1242, 2688),   # 6.5" portrait
    (2688, 1242),   # 6.5" landscape
    (1284, 2778),   # 6.7" portrait
    (2778, 1284),   # 6.7" landscape
]

IPAD_SIZES = [
    (2064, 2752),   # 12.9" 6th gen portrait
    (2752, 2064),   # 12.9" 6th gen landscape
    (2048, 2732),   # 12.9" 3rd gen portrait
    (2732, 2048),   # 12.9" 3rd gen landscape
]


# ─────────────────────────────────────────────
# VISUAL DESIGN
# ─────────────────────────────────────────────
# Gradient (top, bottom) per clip — bright, warm, friendly
BG_GRADIENTS = {
    "woman_1": ((255, 107, 107), (255, 160, 137)),   # Coral
    "man_1":   ((46, 196, 182),  (86, 227, 215)),    # Teal
    "woman_2": ((139, 92, 246),  (178, 147, 255)),    # Violet
    "man_2":   ((245, 158, 11),  (252, 196, 55)),     # Amber
}

TEXT_FILL = (255, 255, 255)      # White
TEXT_STROKE = (13, 27, 42)       # Dark navy


# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
LATIN_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
CJK_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

# Auto-detected at startup
CJK_INDICES = {}


# ─────────────────────────────────────────────
# LOCALIZED MARKETING COPY
# ─────────────────────────────────────────────
# One (tagline, subtitle) per clip, per language.
# Clip order: woman_1, man_1, woman_2, man_2
COPY = {
    "en-US": [
        ("Nail Every Take",
         "Professional teleprompter\nat your fingertips"),
        ("Speak With\nConfidence",
         "Read your script\nnaturally on camera"),
        ("Sound Like a Pro",
         "Professional tools,\nnow in your pocket"),
        ("Effortless\nExecutive Presence",
         "Put your best self\nforward, every time"),
    ],
    "fr": [
        ("Réussissez\nChaque Prise",
         "Téléprompteur pro\nà portée de main"),
        ("Parlez Avec\nAssurance",
         "Lisez votre texte\nnaturellement"),
        ("Parlez\nComme un Pro",
         "Des outils pro\ndans votre poche"),
        ("Un Charisme\nSans Effort",
         "Montrez le meilleur\nde vous-même"),
    ],
    "de": [
        ("Jede Aufnahme\nPerfekt",
         "Profi-Teleprompter\ngriffbereit"),
        ("Selbstbewusst\nSprechen",
         "Ihr Skript natürlich\nvor der Kamera lesen"),
        ("Wie ein Profi\nKlingen",
         "Profi-Werkzeuge\nin Ihrer Tasche"),
        ("Mühelose\nPräsenz",
         "Zeigen Sie Ihre\nbeste Seite"),
    ],
    "ja": [
        ("完璧なテイクを\n毎回実現",
         "プロ仕様テレプロンプター\nをあなたの手に"),
        ("自信を持って\n話そう",
         "カメラの前で\n自然に原稿を読む"),
        ("プロのように\n話す",
         "プロのツールを\nポケットの中に"),
        ("エグゼクティブの\n存在感を楽々と",
         "いつでも最高の\n自分を見せよう"),
    ],
    "ko": [
        ("매 테이크를\n완벽하게",
         "전문 텔레프롬프터\n손끝에서 바로"),
        ("자신감 있게\n말하세요",
         "카메라 앞에서\n자연스럽게 대본 읽기"),
        ("프로처럼\n말하기",
         "전문가 도구를\n주머니 속에"),
        ("손쉬운\n리더십 존재감",
         "매번 최고의 모습을\n보여주세요"),
    ],
    "zh-Hans": [
        ("完美每一条",
         "专业提词器\n触手可及"),
        ("自信开口说",
         "在镜头前\n自然读稿"),
        ("像专业人士\n一样表达",
         "专业工具\n尽在掌中"),
        ("从容展现\n领导力",
         "随时展现\n最好的自己"),
    ],
    "zh-Hant": [
        ("完美每一條",
         "專業提詞器\n觸手可及"),
        ("自信開口說",
         "在鏡頭前\n自然讀稿"),
        ("像專業人士\n一樣表達",
         "專業工具\n盡在掌中"),
        ("從容展現\n領導力",
         "隨時展現\n最好的自己"),
    ],
    "pt-BR": [
        ("Acerte Cada\nTomada",
         "Teleprompter profissional\nna ponta dos dedos"),
        ("Fale Com\nConfiança",
         "Leia seu roteiro\nnaturalmente"),
        ("Fale Como\num Profissional",
         "Ferramentas profissionais\nno seu bolso"),
        ("Presença Executiva\nSem Esforço",
         "Mostre o melhor\nde si, sempre"),
    ],
}

LANGUAGES = list(COPY.keys())


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def detect_cjk_indices():
    """Auto-detect CJK font variant indices in the .ttc file."""
    global CJK_INDICES
    lang_map = {"JP": "ja", "KR": "ko", "SC": "zh-Hans", "TC": "zh-Hant"}
    for i in range(30):
        try:
            font = ImageFont.truetype(CJK_FONT, 20, index=i)
            family = font.getname()[0]
            if "Mono" in family:
                continue
            for code, lang_key in lang_map.items():
                if code in family and lang_key not in CJK_INDICES:
                    CJK_INDICES[lang_key] = i
        except (OSError, IOError):
            break
    print(f"  CJK font indices detected: {CJK_INDICES}")


def extract_first_frame(video_path):
    """Extract the first frame from a video as a PIL Image."""
    tmp = video_path + ".tmp_frame.png"
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vframes", "1", "-q:v", "1", tmp,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-500:]}")
    img = Image.open(tmp).convert("RGB")
    os.remove(tmp)
    return img


def gradient_bg(w, h, color_top, color_bottom):
    """Create a vertical gradient background."""
    col = Image.new("RGB", (1, h))
    px = col.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(a + (b - a) * t) for a, b in zip(color_top, color_bottom))
    return col.resize((w, h), Image.NEAREST)


def round_corners(img, radius):
    """Add rounded corners, returning an RGBA image."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), (img.width - 1, img.height - 1)], radius=radius, fill=255
    )
    img.putalpha(mask)
    return img


def composite_with_shadow(canvas, img, pos, offset=10, blur=20, opacity=70):
    """Paste img onto canvas with a soft drop shadow."""
    canvas = canvas.convert("RGBA")

    # Build shadow in a tight buffer (faster than full-canvas blur)
    pad = blur * 3
    sbuf = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    sfill = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    if img.mode == "RGBA":
        sfill.putalpha(img.split()[3])
    sbuf.paste(sfill, (pad, pad))
    sbuf = sbuf.filter(ImageFilter.GaussianBlur(blur))

    # Composite shadow then image
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sx, sy = pos[0] + offset - pad, pos[1] + offset - pad
    shadow_layer.paste(sbuf, (sx, sy))
    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.paste(img, pos, img)
    return canvas


def get_font(lang, size):
    """Return the correct bold font for a language."""
    if lang in CJK_INDICES:
        return ImageFont.truetype(CJK_FONT, size, index=CJK_INDICES[lang])
    return ImageFont.truetype(LATIN_FONT, size)


# ─────────────────────────────────────────────
# CARD GENERATORS
# ─────────────────────────────────────────────

def make_portrait_card(frame, cw, ch, clip, lang, clip_idx):
    """
    Portrait layout:
      - Top ~20%: tagline + subtitle (centered)
      - Bottom ~80%: screenshot with rounded corners & shadow
    """
    c1, c2 = BG_GRADIENTS[clip]
    tagline, subtitle = COPY[lang][clip_idx]

    canvas = gradient_bg(cw, ch, c1, c2)

    # --- Screenshot placement (lower 4/5) ---
    pad_x = int(cw * 0.05)
    pad_bot = int(ch * 0.015)
    min_top_gap = int(ch * 0.20)

    avail_w = cw - 2 * pad_x
    avail_h = ch - min_top_gap - pad_bot

    scale = min(avail_w / frame.width, avail_h / frame.height)
    fw = int(frame.width * scale)
    fh = int(frame.height * scale)

    scaled = frame.resize((fw, fh), Image.LANCZOS)
    rounded = round_corners(scaled, int(min(fw, fh) * 0.03))

    img_x = (cw - fw) // 2
    img_y = ch - fh - pad_bot

    shadow_off = max(int(cw * 0.006), 5)
    shadow_blur = max(int(cw * 0.014), 10)
    canvas = composite_with_shadow(canvas, rounded, (img_x, img_y),
                                   offset=shadow_off, blur=shadow_blur)

    # --- Text ---
    draw = ImageDraw.Draw(canvas)

    tag_size = int(ch * 0.034)
    sub_size = int(ch * 0.019)
    tag_stroke = max(int(tag_size * 0.14), 3)
    sub_stroke = max(int(sub_size * 0.12), 2)

    tag_font = get_font(lang, tag_size)
    sub_font = get_font(lang, sub_size)

    # Center text vertically in the gap above the screenshot
    text_cx = cw // 2
    text_cy = int(img_y * 0.38)

    draw.text(
        (text_cx, text_cy), tagline, font=tag_font,
        fill=TEXT_FILL, stroke_width=tag_stroke, stroke_fill=TEXT_STROKE,
        anchor="mm", align="center",
    )

    tag_bbox = draw.textbbox((text_cx, text_cy), tagline,
                             font=tag_font, anchor="mm")
    sub_y = tag_bbox[3] + int(ch * 0.012)

    draw.text(
        (text_cx, sub_y), subtitle, font=sub_font,
        fill=TEXT_FILL, stroke_width=sub_stroke, stroke_fill=TEXT_STROKE,
        anchor="ma", align="center",
    )

    return canvas.convert("RGB")


def make_landscape_card(frame, cw, ch, clip, lang, clip_idx):
    """
    Landscape layout:
      - Left ~42%: tagline + subtitle (centered)
      - Right ~58%: portrait screenshot (centered, with shadow)
    """
    c1, c2 = BG_GRADIENTS[clip]
    tagline, subtitle = COPY[lang][clip_idx]

    canvas = gradient_bg(cw, ch, c1, c2)

    # --- Screenshot on the right ---
    text_zone_w = int(cw * 0.42)
    pad = int(ch * 0.06)

    avail_w = cw - text_zone_w - 2 * pad
    avail_h = ch - 2 * pad

    scale = min(avail_w / frame.width, avail_h / frame.height)
    fw = int(frame.width * scale)
    fh = int(frame.height * scale)

    scaled = frame.resize((fw, fh), Image.LANCZOS)
    rounded = round_corners(scaled, int(min(fw, fh) * 0.03))

    img_x = text_zone_w + (cw - text_zone_w - fw) // 2
    img_y = (ch - fh) // 2

    shadow_off = max(int(ch * 0.005), 4)
    shadow_blur = max(int(ch * 0.012), 8)
    canvas = composite_with_shadow(canvas, rounded, (img_x, img_y),
                                   offset=shadow_off, blur=shadow_blur)

    # --- Text on the left ---
    draw = ImageDraw.Draw(canvas)

    tag_size = int(ch * 0.07)
    sub_size = int(ch * 0.038)
    tag_stroke = max(int(tag_size * 0.14), 3)
    sub_stroke = max(int(sub_size * 0.12), 2)

    tag_font = get_font(lang, tag_size)
    sub_font = get_font(lang, sub_size)

    text_cx = text_zone_w // 2
    text_cy = ch // 2 - int(ch * 0.07)

    draw.text(
        (text_cx, text_cy), tagline, font=tag_font,
        fill=TEXT_FILL, stroke_width=tag_stroke, stroke_fill=TEXT_STROKE,
        anchor="mm", align="center",
    )

    tag_bbox = draw.textbbox((text_cx, text_cy), tagline,
                             font=tag_font, anchor="mm")
    sub_y = tag_bbox[3] + int(ch * 0.03)

    draw.text(
        (text_cx, sub_y), subtitle, font=sub_font,
        fill=TEXT_FILL, stroke_width=sub_stroke, stroke_fill=TEXT_STROKE,
        anchor="ma", align="center",
    )

    return canvas.convert("RGB")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("DemoScope App Store Asset Generator")
    print("=" * 50)

    detect_cjk_indices()

    # --- Extract first frames ---
    print("\n[1/3] Extracting first frames from portrait videos...")
    frames = {}
    for clip in CLIPS:
        path = os.path.join(PORTRAIT_DIR, f"{clip}.mp4")
        if not os.path.exists(path):
            print(f"  SKIP: {path} not found")
            continue
        frames[clip] = extract_first_frame(path)
        print(f"  OK  {clip}: {frames[clip].size}")

    if not frames:
        sys.exit("ERROR: No frames extracted. Check Portrait/ directory.")

    # --- Generate all assets ---
    total = len(frames) * len(LANGUAGES) * (len(IPHONE_SIZES) + len(IPAD_SIZES))
    count = 0

    print(f"\n[2/3] Generating {total} images...")

    for device, sizes in [("iPhone", IPHONE_SIZES), ("iPad", IPAD_SIZES)]:
        for lang in LANGUAGES:
            out_dir = os.path.join(OUTPUT_DIR, device, lang)
            os.makedirs(out_dir, exist_ok=True)

            for clip_idx, clip_name in enumerate(CLIPS):
                if clip_name not in frames:
                    continue

                frame = frames[clip_name]

                for w, h in sizes:
                    is_portrait = h > w

                    if is_portrait:
                        card = make_portrait_card(frame, w, h, clip_name, lang, clip_idx)
                    else:
                        card = make_landscape_card(frame, w, h, clip_name, lang, clip_idx)

                    fname = f"{clip_name}_{w}x{h}.png"
                    card.save(os.path.join(out_dir, fname), "PNG", optimize=True)

                    count += 1
                    if count % 32 == 0 or count == total:
                        print(f"  Progress: {count}/{total}")

    # --- Summary ---
    print(f"\n[3/3] Done! Generated {count} images.")
    print(f"Output: {OUTPUT_DIR}/")

    for device in ["iPhone", "iPad"]:
        device_dir = os.path.join(OUTPUT_DIR, device)
        if os.path.isdir(device_dir):
            print(f"\n  {device}/")
            for lang in sorted(os.listdir(device_dir)):
                lang_dir = os.path.join(device_dir, lang)
                n = len(os.listdir(lang_dir))
                print(f"    {lang}/ ({n} images)")


if __name__ == "__main__":
    main()
