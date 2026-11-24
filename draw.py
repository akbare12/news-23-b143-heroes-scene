#!/usr/bin/env python3
"""news-23 b143 heroes-scene: draw THE WORLD TODAY front page (1024x1024).

Layout: masthead + kicker + number strip + region bar + UTC strip +
3 BIG hero scenes + 10 cards + map/pins + ALSO list + DATE CHECK + footer.
Run: python3 draw.py  -> writes entry.png next to this file.
"""
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (248, 244, 233)
INK = (26, 26, 26)
RED = (176, 30, 36)
GOLD = (166, 124, 0)
NAVY = (18, 40, 75)
GREEN = (29, 92, 46)
PURPLE = (122, 44, 140)
TEAL = (0, 110, 110)
GRAY = (110, 108, 100)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap, returns list of lines."""
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, s, path, start, min_size, max_w):
    """Largest font size in [min_size, start] whose text fits max_w."""
    for size in range(start, min_size - 1, -1):
        f = font(path, size)
        if text_w(draw, s, f) <= max_w:
            return f
    return font(path, min_size)


def chip(draw, x_right, y, label, fill):
    """Small REPORTED/CLAIM chip, right edge at x_right, 12px tall."""
    f = font(SANS_B, 8)
    tw = text_w(draw, label, f)
    w = int(tw) + 10
    x0 = x_right - w
    draw.rounded_rectangle([x0, y, x_right, y + 12], radius=2, fill=fill)
    draw.text((x0 + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return x0


def hero_block(draw, x, w, scene_fn, headline, body, source):
    """One hero column: scene y188-318, headline, body, source+chip."""
    scene_fn(draw, x, 188, w, 130)
    # headline: 1 line if it fits at >=12px, else 2 lines at 14px
    f1 = fit_font(draw, headline, SANS_B, 16, 12, w)
    if text_w(draw, headline, f1) <= w:
        draw.text((x, 326), headline, font=f1, fill=INK)
        body_lines = wrap(draw, body, font(SANS, 11), w)
        y = 350
        for ln in body_lines[:2]:
            draw.text((x, y), ln, font=font(SANS, 11), fill=INK)
            y += 15
        src_y = 388
    else:
        lines = wrap(draw, headline, font(SANS_B, 14), w)
        y = 324
        for ln in lines[:2]:
            draw.text((x, y), ln, font=font(SANS_B, 14), fill=INK)
            y += 17
        body_lines = wrap(draw, body, font(SANS, 11), w)
        y = 360
        for ln in body_lines[:1]:
            draw.text((x, y), ln, font=font(SANS, 11), fill=INK)
            y += 15
        src_y = 388
    draw.text((x, src_y), source, font=font(SANS, 9), fill=GRAY)
    chip(draw, x + w, src_y - 2, "REPORTED", NAVY)


def scene_kospi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(14, 42, 78))
    random.seed(1431)
    # skyline: buildings capped below the big-number zone
    bx = x + 8
    while bx < x + w - 30:
        bw = random.randint(26, 44)
        bh = random.randint(34, 62)
        by = y + h - 22 - bh
        draw.rectangle([bx, by, bx + bw, y + h - 22], fill=(8, 28, 56),
                       outline=(40, 70, 110))
        for wy in range(by + 6, y + h - 26, 12):
            for wx in range(bx + 5, bx + bw - 4, 11):
                if random.random() < 0.55:
                    draw.rectangle([wx, wy, wx + 4, wy + 5],
                                   fill=(255, 214, 90))
        bx += bw + 6
    # falling chart line, starts clear of the big number
    pts = [(x + 128, y + 34), (x + 168, y + 52), (x + 205, y + 44),
           (x + 240, y + 66), (x + 272, y + 58), (x + 305, y + 84)]
    draw.line(pts, fill=(255, 140, 40), width=3)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255),
                     outline=(255, 140, 40))
    draw.text((x + 10, y + 6), "-3.3%", font=font(SANS_B, 34), fill=(255, 255, 255))
    draw.rectangle([x, y + h - 22, x + w, y + h], fill=(0, 0, 0))
    draw.text((x + 8, y + h - 19),
              "KOSPI 4,708.54  ·  -161 PTS  ·  SAMSUNG -3.1%  ·  HYNIX -2.5%",
              font=font(SANS_B, 9), fill=(255, 255, 255))


def scene_guterres(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=GREEN)
    draw.text((x + 12, y + 8), "150", font=font(SANS_B, 46), fill=(255, 214, 90))
    gold_lines = ["DELEGATES", "BACK A RISK", "FRAMEWORK"]
    yy = y + 58
    for ln in gold_lines:
        draw.text((x + 12, yy), ln, font=font(SANS_B, 15), fill=(255, 214, 90))
        yy += 19
    # globe, right side, masked circle
    cx, cy, r = x + w - 62, y + 52, 44
    mask = Image.new("L", (2 * r, 2 * r), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, 2 * r, 2 * r], fill=255)
    globe = Image.new("RGB", (2 * r, 2 * r), (214, 232, 214))
    gd = ImageDraw.Draw(globe)
    gd.ellipse([2, 2, 2 * r - 2, 2 * r - 2], outline=(90, 140, 100), width=2)
    gd.ellipse([r // 2, 2, 3 * r // 2, 2 * r - 2], outline=(90, 140, 100))
    for yy2 in (r // 2, r, 3 * r // 2):
        gd.line([4, yy2, 2 * r - 4, yy2], fill=(90, 140, 100))
    img = Image.new("RGB", (W, H))
    # paste globe via mask onto the working image is not possible here;
    # draw globe directly with clipped arcs instead:
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 232, 214),
                 outline=(90, 140, 100), width=2)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r],
                 outline=(90, 140, 100))
    for yy2 in (cy - r // 2, cy, cy + r // 2):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340,
                 fill=(90, 140, 100))
        draw.line([cx - r + 6, yy2, cx + r - 6, yy2], fill=(90, 140, 100))
    draw.rectangle([x, y + h - 22, x + w, y + h], fill=(0, 0, 0))
    draw.text((x + 8, y + h - 19), "BRIDGETOWN SUMMIT, BARBADOS",
              font=font(SANS_B, 9), fill=(255, 255, 255))


def scene_power(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 234, 214))
    draw.text((x + 10, y + 8), "NARROWEST SINCE 2018",
              font=font(SANS_B, 11), fill=INK)
    draw.text((x + w - 66, y + 8), "GAP 5.3", font=font(SANS_B, 11), fill=RED)
    bars = [("78.9", "US", NAVY, 0.92, (255, 255, 255)),
            ("73.6", "CHINA", RED, 0.86, (255, 255, 255)),
            ("40.5", "INDIA", (200, 160, 20), 0.52, INK)]
    yy = y + 34
    for val, name, col, frac, lbl_col in bars:
        draw.text((x + 10, yy + 2), val, font=font(SANS_B, 13), fill=INK)
        bx0, bw = x + 62, int((w - 72) * frac)
        draw.rectangle([bx0, yy, bx0 + bw, yy + 20], fill=col)
        lbl = font(SANS_B, 11)
        tw = text_w(draw, name, lbl)
        draw.text((bx0 + bw - tw - 8, yy + 4), name, font=lbl,
                  fill=lbl_col)
        yy += 28
    draw.rectangle([x, y + h - 22, x + w, y + h], fill=(0, 0, 0))
    draw.text((x + 8, y + h - 19), "ASIA POWER INDEX 2026  ·  LOWY INSTITUTE",
              font=font(SANS_B, 9), fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # masthead
    d.text((10, 6), "THE WORLD TODAY", font=font(SERIF_B, 46), fill=INK)
    date_s = "MONDAY 23 NOVEMBER 2026"
    df = font(SANS_B, 15)
    d.text((W - 10 - text_w(d, date_s, df), 24), date_s, font=df, fill=GOLD)
    d.rectangle([10, 60, W - 10, 62], fill=GOLD)

    # kicker
    d.rectangle([0, 66, W, 86], fill=RED)
    d.text((10, 70),
           "AI rout hits Asia   ·   UN chief urges AI rules   ·   "
           "US lead over China at record low   ·   Anthropic IPO $107.3B",
           font=font(SANS_B, 13), fill=(255, 255, 255))

    # number strip: 2 rows x 5 cols
    nums = [
        [("-3.3%", "KOSPI"), ("5.3", "US-CHINA POWER GAP"),
         ("11,762", "EBOLA CASES, DRC"), ("10T won", "SEOUL STABILISATION FUND"),
         ("2%", "BILLIONAIRE TAX IN PARIS")],
        [("$450M", "SKUBAL DEAL"), ("165", "RUSSIAN MISSILES/WEEK"),
         ("12,000", "CLEARED IN MANCHESTER"), ("264 kg", "EXPLOSIVES SEIZED"),
         ("$107.3B", "ANTHROPIC IPO")],
    ]
    col_w = 202
    for row, items in enumerate(nums):
        vy = 92 + row * 30
        ly = vy + 20
        for i, (val, lab) in enumerate(items):
            cx = 12 + i * col_w
            d.text((cx, vy), val, font=font(SANS_B, 19), fill=INK)
            d.text((cx, ly), lab, font=font(SANS, 9), fill=GRAY)
            if i:
                d.line([cx - 6, vy, cx - 6, ly + 10], fill=(200, 196, 184))

    # region bar: segments sum to 1004, starting x=10
    regions = [("ASIA-PACIFIC 7", NAVY, 226), ("AMERICAS 8", RED, 259),
               ("MIDDLE EAST 6", PURPLE, 194), ("EUROPE 5", TEAL, 162),
               ("AFRICA 3", GREEN, 97), ("WORLD 2", GOLD, 66)]
    rx = 10
    for name, col, rw in regions:
        d.rectangle([rx, 152, rx + rw, 170], fill=col)
        tf = font(SANS_B, 10)
        tw = text_w(d, name, tf)
        d.text((rx + (rw - tw) / 2, 156), name, font=tf, fill=(255, 255, 255))
        rx += rw

    # UTC strip
    d.text((10, 174),
           "THE DAY IN UTC    ~00:00 Kospi dives    ~05:30 Guterres opens    "
           "~09:00 Power Index    ~12:00 Paris 2% tax    ~15:00 Kyiv missiles",
           font=font(SANS, 9), fill=GRAY)
    d.text((W - 66, 174), "~ APPROX", font=font(SANS, 9), fill=GRAY)

    # 3 hero scenes
    hero_block(d, 10, 328, scene_kospi, "AI ROUT HITS ASIA",
               "Kospi closes -3.3% to 4,708.54, sheds 161 pts; intraday "
               "-5.8%. Samsung -3.1%, SK Hynix -2.5%.", "KOREA EXCHANGE")
    hero_block(d, 348, 328, scene_guterres,
               "GUTERRES: REGULATE AI BEFORE IT'S TOO LATE",
               "UN chief urges global AI safety rules at the Bridgetown "
               "summit; 150 back a risk framework.", "UNITED NATIONS")
    hero_block(d, 686, 328, scene_power, "US LEAD OVER CHINA AT RECORD LOW",
               "Asia Power Index 2026: US 78.9, China 73.6 — gap 5.3, "
               "narrowest since 2018. India third at 40.5.", "LOWY INSTITUTE")

    # MORE OF THE DAY bar
    d.rectangle([0, 452, W, 470], fill=(0, 0, 0))
    d.text((10, 456), "MORE OF THE DAY  —  10 STORIES",
           font=font(SANS_B, 12), fill=(255, 255, 255))

    # 10 cards: 2 rows x 5 cols, pitch 202, x start 10
    cards = [
        ("1", "AMERICAS", "BESSENT: NVIDIA ANSWERS", "Treasury wants answers.",
         "WSJ", "REPORTED", NAVY),
        ("2", "AMERICAS", "FBI PROBES NCIC HACK", "NCIC database hacked.",
         "AP", "REPORTED", NAVY),
        ("3", "WHITE HOUSE", "TRUMP: IRAN STRIKES MAY RESUME",
         "May resume in New Year.", "Reuters", "REPORTED", NAVY),
        ("4", "MARKETS", "US FUTURES JUMP 3%", "Holiday rally lifts 3%.",
         "Bloomberg", "REPORTED", NAVY),
        ("5", "SPORT", "SKUBAL'S $450M METS DEAL", "Nine-year, largest ever.",
         "AP", "REPORTED", NAVY),
        ("6", "SPORT", "TOM JACKSON DIES AT 75", "Broncos LB, ESPN voice.",
         "ESPN", "REPORTED", NAVY),
        ("7", "LEGAL", "STATES SUE SPACEX", "Ten states sue over AI.",
         "AP", "REPORTED", NAVY),
        ("8", "TECH", "ANTHROPIC IPO: $107.3B", "Raised $83; closes $97.17.",
         "WSJ", "REPORTED", NAVY),
        ("9", "EUROPE", "POLAND: 3 MISSILES CROSSED", "Kyiv: 3 Kh-101s crossed.",
         "AP", "CLAIM", RED),
        ("10", "SPACE", "RUSSIAN NUCLEAR SATELLITE", "May carry a nuke.",
         "Reuters", "CLAIM", RED),
    ]
    for idx, (num, cat, head, body, src, chip_lab, chip_col) in enumerate(cards):
        col, row = idx % 5, idx // 5
        cx = 10 + col * 202
        cy = 476 + row * 64
        cw = 196
        nf = font(SANS_B, 10)
        d.text((cx, cy), num, font=nf, fill=RED)
        nw = text_w(d, num, nf)
        d.text((cx + nw + 5, cy + 1), cat, font=font(SANS_B, 9), fill=RED)
        hf = fit_font(d, head, SANS_B, 11, 9, cw)
        d.text((cx, cy + 16), head, font=hf, fill=INK)
        d.text((cx, cy + 32), body, font=font(SANS, 9), fill=INK)
        d.text((cx, cy + 46), src, font=font(SANS, 8), fill=GRAY)
        chip(d, cx + cw, cy + 44, chip_lab, chip_col)

    # WHERE IT HAPPENED bar
    d.rectangle([0, 608, W, 626], fill=(0, 0, 0))
    d.text((10, 612), "WHERE IT HAPPENED", font=font(SANS_B, 12),
           fill=(255, 255, 255))

    # map panel: two blobs + 13 pins
    map_x0, map_y0 = 10, 632
    blob_green = (196, 224, 178)
    americas = [(40, 648), (95, 638), (155, 648), (195, 668), (190, 720),
                (160, 762), (110, 776), (58, 762), (28, 722), (24, 682)]
    eurasia = [(232, 650), (305, 640), (385, 646), (448, 662), (460, 702),
               (432, 748), (382, 772), (300, 778), (238, 762), (216, 712)]
    d.polygon(americas, fill=blob_green)
    d.polygon(eurasia, fill=blob_green)
    pins = [(1, 424, 690), (2, 70, 736), (3, 402, 668), (4, 122, 690),
            (5, 152, 672), (6, 300, 668), (7, 270, 700), (8, 260, 674),
            (9, 322, 682), (10, 240, 662), (11, 340, 706), (12, 320, 736),
            (13, 298, 756)]
    pf = font(SANS_B, 9)
    for n, px, py in pins:
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                  outline=(255, 255, 255))
        s = str(n)
        d.text((px - text_w(d, s, pf) / 2, py - 6), s, font=pf,
               fill=(255, 255, 255))
    # legend, 3 short lines inside the map panel
    leg = ["Pins 1–13:  1 Seoul · 2 Bridgetown · 3 Beijing · 4 Washington",
           "5 New York · 6 Kyiv · 7 Paris · 8 London · 9 Warsaw",
           "10 Manchester · 11 Beirut · 12 Gaza · 13 Khartoum"]
    ly = 782
    for ln in leg:
        d.text((10, ly), ln, font=font(SANS, 8), fill=GRAY)
        ly += 11

    # ALSO list (right of map), two columns of 9 so it clears the
    # DATE CHECK box below (single column ran to y~904, over the box).
    ax = 482
    d.text((ax, 632), "ALSO ON MONDAY", font=font(SANS_B, 12), fill=INK)
    also = [
        ("14.", "Paris: 100+ back 2% billionaire tax", None),
        ("15.", "Manchester: 12,000 cleared", None),
        ("16.", "Zelenskyy: 165 missiles in a week", None),
        ("17.", "COP31: the day after Antalya pact rejected", None),
        ("18.", "Israel unity talks resume", None),
        ("19.", "Gaza: two killed in Israeli strike", None),
        ("20.", "West Bank settler attacks", None),
        ("21.", "Iran war: no deal in sight", None),
        ("22.", "Lebanon seizes 264 kg explosives", None),
        ("23.", "Bahrain: strike hits plant, 2 hurt", None),
        ("24.", "Benghazi: UN demands probe", "CLAIM"),
        ("25.", "Sudan: defences down drones", "CLAIM"),
        ("26.", "DRC: fighting traps Ebola teams", None),
        ("27.", "Bangladesh: Hasina jailed if she returns", None),
        ("28.", "Seoul minister quits over AI exam row", None),
        ("29.", "SK Telecom -7.3% as hype cools", None),
        ("30.", "China eases margin rules", None),
        ("31.", "Seoul readies 10T-won fund", None),
    ]
    for col_i, col_items in enumerate((also[:9], also[9:])):
        col_x = ax + col_i * 278
        ay = 652
        for num, txt, claim in col_items:
            d.text((col_x, ay), num, font=font(SANS_B, 10), fill=INK)
            d.text((col_x + 26, ay), txt, font=font(SANS, 10), fill=INK)
            if claim:
                cf = font(SANS_B, 8)
                tw = text_w(d, txt, font(SANS, 10))
                d.text((col_x + 26 + tw + 6, ay + 1), "[" + claim + "]",
                       font=cf, fill=RED)
            ay += 14

    # DATE CHECK red box
    d.rectangle([10, 824, W - 10, 934], outline=RED, width=2)
    d.text((18, 832),
           "DATE CHECK  —  READ 23 NOV 2026, 23:59 UTC  ·  STORIES DATED 23 NOV ONLY",
           font=font(SANS_B, 11), fill=RED)
    d.text((18, 854),
           "LEFT OUT — NOT 23 NOV:  Dems reach 258 (22 Nov)  ·  Sparta II fire (22 Nov)",
           font=font(SANS, 10), fill=INK)
    d.text((18, 872),
           "El Chapo Isidro captured (22 Nov)  ·  EU–Indonesia pact (21 Nov)  ·  "
           "Nigeria boat (21 Nov)  ·  ICJ Myanmar ruling (19 Nov)",
           font=font(SANS, 10), fill=INK)
    d.text((18, 894),
           "NOT YET —  Dymer search continues (14 missing)  ·  4 House races uncalled  ·  "
           "COP32 venue not set  ·  WHO evacuating trapped Ebola staff",
           font=font(SANS, 10), fill=INK)

    # footer
    d.text((10, 944),
           "Sources: Reuters · AP · Bloomberg · AFP · Yonhap · BBC · WSJ · ESPN · "
           "Lowy Institute (Asia Power Index 2026).",
           font=font(SANS, 9), fill=GRAY)
    d.text((10, 960),
           "CHIPS: REPORTED = confirmed by wires · CLAIM = one side's claim, "
           "independently unconfirmed · ONGOING = still developing.",
           font=font(SANS, 9), fill=GRAY)
    d.text((10, 976),
           "All times UTC. Figures as reported 23 Nov 2026. Scenes are drawn "
           "illustrations, not photographs.",
           font=font(SANS, 9), fill=GRAY)
    d.rectangle([10, 994, W - 10, 996], fill=GOLD)
    foot = "THE WORLD TODAY  ·  Monday 23 November 2026  ·  31 stories  ·  6 regions"
    ff = font(SANS_B, 11)
    d.text(((W - text_w(d, foot, ff)) / 2, 1002), foot, font=ff, fill=GOLD)

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
