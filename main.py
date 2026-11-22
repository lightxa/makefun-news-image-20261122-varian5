#!/usr/bin/env python3
"""Broadsheet front page summing up the world news of Sunday 22 Nov 2026.

Draws a newspaper front page (masthead, lead story, five briefs) with a
hand-built 5x7 bitmap font and encodes a PNG with zlib/struct only.
No network, no randomness, no time: two runs write byte-identical files.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (244, 239, 228)
INK = (26, 26, 26)
RED = (164, 30, 34)
BLUE = (31, 78, 121)
GREEN = (58, 125, 68)
AMBER = (217, 164, 65)
GREY = (96, 92, 84)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font: '#' is a set pixel. Uppercase, lowercase, digits, punct.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "\u2019": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
}


def glyph_rows(ch):
    rows = FONT.get(ch)
    if rows is None:
        rows = FONT["?"]
    return rows[:7]


# ------------------------------------------------------------- canvas -----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(w * h * 3)
        for i in range(0, len(self.pix), 3):
            self.pix[i] = bg[0]
            self.pix[i + 1] = bg[1]
            self.pix[i + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i] = c[0]
            self.pix[i + 1] = c[1]
            self.pix[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            for xx in range(x, x + w):
                self.set(xx, y + k, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            for yy in range(y, y + h):
                self.set(x + k, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d2 - r * r) <= r:
                        self.set(xx, yy, c)

    def ellipse_outline_clipped(self, cx, cy, rx, ry, clip_cx, clip_cy, clip_r, c):
        steps = 720
        for k in range(steps):
            a = 2.0 * math.pi * k / steps
            x = int(round(cx + rx * math.cos(a)))
            y = int(round(cy + ry * math.sin(a)))
            if (x - clip_cx) ** 2 + (y - clip_cy) ** 2 <= (clip_r - 1) ** 2:
                self.set(x, y, c)

    def triangle(self, cx, y_top, half_base, height, c):
        for row in range(height):
            half = int(half_base * row / max(1, height - 1))
            for xx in range(cx - half, cx + half + 1):
                self.set(xx, y_top + row, c)


# -------------------------------------------------------------- text ------
def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(cv, x, y, s, scale, color):
    cx = x
    for ch in s:
        rows = glyph_rows(ch)
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "1":
                    cv.rect(cx + rx * scale, y + ry * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap_text(s, scale, max_w):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, max_w, color, leading=None):
    if leading is None:
        leading = 7 * scale + 4
    yy = y
    for line in wrap_text(s, scale, max_w):
        draw_text(cv, x, yy, line, scale, color)
        yy += leading
    return yy


# -------------------------------------------------------------- icons -----
def icon_ballot(cv, x, y, s):
    # ballot box with a tick
    cv.rect(x + 4, y + 18, 40, 26, INK)
    cv.rect(x + 7, y + 21, 34, 20, PAPER)
    cv.hline(x + 16, y + 26, 16, INK, 3)
    cv.line(x + 8, y + 6, x + 18, y + 16, RED, 4)
    cv.line(x + 18, y + 16, x + 40, y - 2, RED, 4)


def icon_cricket(cv, x, y, s):
    # bat and red ball
    cv.line(x + 10, y + 44, x + 30, y + 8, INK, 7)
    cv.line(x + 30, y + 8, x + 36, y + 2, INK, 5)
    cv.circle(x + 40, y + 12, 9, RED, fill=True)
    cv.circle(x + 40, y + 12, 9, INK)
    cv.hline(x + 6, y + 46, 36, INK, 3)


def icon_cedar(cv, x, y, s):
    cv.triangle(x + 24, y + 2, 20, 14, GREEN)
    cv.triangle(x + 24, y + 12, 16, 14, GREEN)
    cv.triangle(x + 24, y + 22, 12, 14, GREEN)
    cv.rect(x + 21, y + 36, 6, 10, INK)


def icon_boat(cv, x, y, s):
    # hull
    for row in range(12):
        half = 20 - row
        for xx in range(x + 24 - half, x + 24 + half + 1):
            cv.set(xx, y + 22 + row, INK)
    cv.rect(x + 20, y + 6, 4, 16, INK)
    cv.triangle(x + 24, y + 6, 12, 12, RED)
    cv.hline(x + 2, y + 40, 44, BLUE, 3)
    cv.hline(x + 8, y + 45, 32, BLUE, 3)


def icon_ball(cv, x, y, s):
    cx, cy, r = x + 24, y + 24, 21
    cv.circle(cx, cy, r, INK, fill=True)
    cv.circle(cx, cy, r, INK)
    # white panels: small pentagon centre + spokes
    cv.circle(cx, cy, 6, PAPER, fill=True)
    for k in range(5):
        a = 2.0 * math.pi * k / 5 - math.pi / 2
        x1 = int(round(cx + 6 * math.cos(a)))
        y1 = int(round(cy + 6 * math.sin(a)))
        x2 = int(round(cx + 19 * math.cos(a)))
        y2 = int(round(cy + 19 * math.sin(a)))
        cv.line(x1, y1, x2, y2, PAPER, 2)


def draw_globe(cv, cx, cy, r):
    # sun behind, top-right of the globe
    sx, sy, sr = cx + 72, cy - 78, 34
    for k in range(12):
        a = 2.0 * math.pi * k / 12
        x1 = int(round(sx + (sr + 4) * math.cos(a)))
        y1 = int(round(sy + (sr + 4) * math.sin(a)))
        x2 = int(round(sx + (sr + 16) * math.cos(a)))
        y2 = int(round(sy + (sr + 16) * math.sin(a)))
        cv.line(x1, y1, x2, y2, AMBER, 3)
    cv.circle(sx, sy, sr, AMBER, fill=True)
    # globe
    cv.circle(cx, cy, r, BLUE, fill=True)
    cv.circle(cx, cy, r, INK)
    cv.circle(cx, cy, r - 2, WHITE)
    # latitude lines
    for dy in (-60, -30, 0, 30, 60):
        half = int(math.sqrt(max(0, r * r - dy * dy)))
        cv.hline(cx - half, cy + dy, 2 * half, WHITE, 2)
    # longitude ellipses, clipped to the disc
    for rx in (30, 62, 94):
        cv.ellipse_outline_clipped(cx, cy, rx, r, cx, cy, r, WHITE)
    # abstract landmasses
    for (lx, ly, lr) in ((cx - 42, cy - 38, 17), (cx - 22, cy - 30, 13),
                         (cx + 38, cy + 8, 15), (cx + 52, cy + 30, 12),
                         (cx - 30, cy + 42, 11), (cx + 8, cy - 52, 10)):
        cv.circle(lx, ly, lr, GREEN, fill=True)


# -------------------------------------------------------------- page ------
def build():
    cv = Canvas(W, H, PAPER)

    # double border frame
    cv.rect(14, 14, 996, 3, INK)
    cv.rect(14, 1007, 996, 3, INK)
    cv.rect(14, 14, 3, 996, INK)
    cv.rect(1007, 14, 3, 996, INK)
    cv.rect(24, 24, 976, 1, INK)
    cv.rect(24, 999, 976, 1, INK)
    cv.rect(24, 24, 1, 976, INK)
    cv.rect(999, 24, 1, 976, INK)

    # ---- nameplate ----
    draw_text_centered(cv, 512, 36, "THE SUNDAY GLOBE", 7, INK)
    cv.hline(48, 100, 928, INK, 2)

    # ---- masthead date band: the date must be unmistakable ----
    cv.rect(48, 110, 928, 62, INK)
    draw_text_centered(cv, 512, 121, "SUNDAY 22 NOVEMBER 2026", 6, WHITE)

    draw_text_centered(
        cv, 512, 184, "ONE DAY IN THE WORLD  \u2022  SIX STORIES FROM SIX TIME ZONES",
        2, GREY)
    cv.hline(48, 206, 928, INK, 3)

    # ---- lead story: COP31 ----
    draw_text(cv, 48, 222, "CLIMATE  \u2022  ANTALYA, TURKIYE", 3, RED)
    draw_text(cv, 48, 248, "CLIMATE DEAL", 8, INK)
    draw_text(cv, 48, 308, "GOES TO THE VOTE", 8, INK)
    deck = ("After two weeks of talks that ran past their Friday deadline, "
            "the COP31 presidents put a new final package before nearly 200 "
            "nations today. Delegates have until 03:00 GMT to object; the "
            "approval session opens at 06:00 GMT.")
    draw_para(cv, 48, 384, deck, 3, 560, INK)
    draw_globe(cv, 820, 462, 95)
    draw_text_centered(cv, 820, 564, "ANTALYA, TURKIYE", 2, GREY)

    cv.hline(48, 592, 928, INK, 3)
    draw_text(cv, 48, 606, "ALSO TODAY", 3, INK)
    cv.hline(48, 632, 928, INK, 1)

    # ---- briefs: two columns, two rows, then a full-width strip ----
    briefs = [
        ("HONG KONG", "HONG KONG VOTES",
         "856 candidates contest 723 seats; polls close at 6pm.", icon_ballot),
        ("WELLINGTON", "PANT HITS 128",
         "India 629 for 6 in Wellington, a lead of 261.", icon_cricket),
        ("BEIRUT", "LEBANON MARKS 83 YEARS",
         "President Aoun addresses the nation on Independence Day.",
         icon_cedar),
        ("NIGERIA", "SEARCH GOES ON IN BAYELSA",
         "24 rescued after the Love Boat capsized; the search goes on.",
         icon_boat),
    ]
    col_x = (48, 536)
    row_y = (648, 772)
    for i, (kick, head, body, icon) in enumerate(briefs):
        x = col_x[i % 2]
        y = row_y[i // 2]
        icon(cv, x, y + 6, 1)
        tx = x + 64
        draw_text(cv, tx, y, kick, 2, RED)
        hy = y + 20
        for line in wrap_text(head, 3, 440 - 64):
            draw_text(cv, tx, hy, line, 3, INK)
            hy += 25
        draw_para(cv, tx, hy + 2, body, 2, 440 - 64, INK)

    # ---- Anfield strip ----
    y = 898
    cv.hline(48, y - 8, 928, INK, 1)
    icon_ball(cv, 48, y, 1)
    draw_text(cv, 120, y, "ANFIELD", 2, RED)
    draw_text(cv, 120, y + 20, "POCHETTINO\u2019S FIRST TEST AT ANFIELD", 3, INK)
    draw_text(cv, 120, y + 48,
              "New Manchester United boss faces Liverpool at 4.30pm; United sit 18th.",
              2, INK)

    # ---- footer ----
    cv.hline(48, 970, 928, INK, 1)
    draw_text_centered(cv, 512, 976,
                       "THE SUNDAY GLOBE  \u2022  SUNDAY 22 NOVEMBER 2026",
                       2, GREY)
    return cv


# --------------------------------------------------------------- png ------
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.pix[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
