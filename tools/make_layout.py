"""Writes the G915's key layout into the package manifest's ``keyboard``
section. Run after changing the tables below::

    python tools/make_layout.py logitech.g915/manifest.json

Not part of the package (packages are data only); the manifest carries the
result.

Each key: ``id``, ``label``, position and size in key units (``x``, ``y``,
``w``, ``h``), ``usage`` (HID keyboard usage, for game mode) and ``led``
(per-key lighting zone). Measured on a G915 WIRELESS (US layout, 0x4540
reports layout 1): the main block's LED ids are the HID usage minus 3,
modifiers are usage minus 120, and the special LEDs are brightness 153,
play/pause 155, mute 156, next 157, previous 158, G1-G5 180-184 and the
logo 210. M1-M3, MR and the game-mode key have white LEDs the firmware
drives; they carry neither ``led`` nor ``usage``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def usage_of(name: str) -> int:
    if len(name) == 1 and name in LETTERS:
        return 4 + LETTERS.index(name)
    if len(name) == 1 and name.isdigit():
        return 39 if name == "0" else 29 + int(name)
    return NAMED[name]


NAMED = {
    "Enter": 40, "Esc": 41, "Backspace": 42, "Tab": 43, "Space": 44, "-": 45, "=": 46, "[": 47,
    "]": 48, "\\": 49, ";": 51, "'": 52, "`": 53, ",": 54, ".": 55, "/": 56, "Caps Lock": 57,
    **{f"F{n}": 57 + n for n in range(1, 13)},
    "Print Screen": 70, "Scroll Lock": 71, "Pause": 72, "Insert": 73, "Home": 74, "Page Up": 75,
    "Delete": 76, "End": 77, "Page Down": 78, "Right": 79, "Left": 80, "Down": 81, "Up": 82,
    "Num Lock": 83, "Num /": 84, "Num *": 85, "Num -": 86, "Num +": 87, "Num Enter": 88,
    **{f"Num {n}": 88 + n for n in range(1, 10)}, "Num 0": 98, "Num .": 99, "Menu": 101,
    "Left Ctrl": 224, "Left Shift": 225, "Left Alt": 226, "Left Super": 227,
    "Right Ctrl": 228, "Right Shift": 229, "Right Alt": 230, "Right Super": 231,
}  # fmt: skip

# Short labels drawn on the keys; the full name is the tooltip (label).
SHORT = {
    "Backspace": "⌫", "Caps Lock": "Caps", "Left Shift": "Shift", "Right Shift": "Shift",
    "Left Ctrl": "Ctrl", "Right Ctrl": "Ctrl", "Left Alt": "Alt", "Right Alt": "Alt",
    "Left Super": "Super", "Right Super": "Super", "Print Screen": "PrtSc", "Scroll Lock": "ScrLk", "Insert": "Ins",
    "Delete": "Del", "Page Up": "PgUp", "Page Down": "PgDn", "Num Lock": "Num",
    "Right": "→", "Left": "←", "Down": "↓", "Up": "↑", "Enter": "Enter", "Num Enter": "Enter",
    "Space": "",
}  # fmt: skip

MAIN_X = 1.25  # the G-key column sits left of the main block


SYMBOLS = {"-": "minus", "=": "equal", "[": "lbracket", "]": "rbracket", "\\": "backslash", ";": "semicolon",
           "'": "quote", "`": "grave", ",": "comma", ".": "dot", "/": "slash", "*": "asterisk", "+": "plus"}  # fmt: skip


def slug(name: str) -> str:
    words = [SYMBOLS.get(w, w) for w in name.lower().split()]
    return "_".join("".join(c if c.isalnum() else "_" for c in w).strip("_") for w in words)


def key(name: str, x: float, y: float, w: float = 1, h: float = 1, **extra) -> dict:
    k = {"id": extra.pop("id", None) or slug(name), "label": name, "x": x, "y": y}
    if w != 1:
        k["w"] = w
    if h != 1:
        k["h"] = h
    if (short := SHORT.get(name, name.removeprefix("Num ") if name.startswith("Num ") else None)) is not None:
        k["cap"] = short
    k.update(extra)
    return k


def typing(name: str, x: float, y: float, w: float = 1, h: float = 1) -> dict:
    usage = usage_of(name)
    led = usage - 120 if usage >= 224 else usage - 3
    return key(name, x, y, w, h, usage=usage, led=led)


def row(y: float, x: float, names: list, default_w: float = 1) -> list[dict]:
    out = []
    for item in names:
        name, w = item if isinstance(item, tuple) else (item, default_w)
        if name:
            out.append(typing(name, x, y, w))
        x += w
    return out


def layout() -> list[dict]:
    keys: list[dict] = []
    # Top strip: logo, M-keys, connection, game mode and brightness buttons;
    # media keys on the function row's line, above the keypad.
    keys += [
        key("Logo", 0, 0, h=0.75, id="logo", led=210, cap="G"),  # over the G-key column
        key("M1", 3.25, 0, h=0.75), key("M2", 4.25, 0, h=0.75), key("M3", 5.25, 0, h=0.75), key("MR", 6.25, 0, h=0.75),
        key("LIGHTSPEED", 7.75, 0, h=0.75, id="lightspeed", cap="Wi"),
        key("Bluetooth", 8.75, 0, h=0.75, id="bluetooth", cap="BT"),
        key("Game mode", 9.75, 0, h=0.75, id="game_mode", cap="Game"),
        key("Brightness", 10.75, 0, h=0.75, id="brightness", led=153, cap="☀"),
        key("Previous", 19.75, 1, id="previous", led=158, cap="⏮"),
        key("Play/Pause", 20.75, 1, id="play_pause", led=155, cap="⏯"),
        key("Next", 21.75, 1, id="next", led=157, cap="⏭"),
        key("Mute", 22.75, 1, id="mute", led=156, cap="🔇"),
    ]  # fmt: skip
    # Function row.
    keys += row(1, MAIN_X, ["Esc"])
    for group, x in ((["F1", "F2", "F3", "F4"], 3.25), (["F5", "F6", "F7", "F8"], 7.75), (["F9", "F10", "F11", "F12"], 12.25)):
        keys += row(1, x, group)
    keys += row(1, 16.5, ["Print Screen", "Scroll Lock", "Pause"])
    # G-keys, one per row from the number row down.
    keys += [key(f"G{n}", 0, 1.25 + n, led=179 + n) for n in range(1, 6)]
    y = 2.25
    keys += row(y, MAIN_X, ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", ("Backspace", 2)])
    keys += row(y, 16.5, ["Insert", "Home", "Page Up"])
    keys += row(y, 19.75, ["Num Lock", "Num /", "Num *", "Num -"])
    y += 1
    keys += row(y, MAIN_X, [("Tab", 1.5), *"QWERTYUIOP", "[", "]", ("\\", 1.5)])
    keys += row(y, 16.5, ["Delete", "End", "Page Down"])
    keys += row(y, 19.75, ["Num 7", "Num 8", "Num 9"])
    keys.append(typing("Num +", 22.75, y, h=2))
    y += 1
    keys += row(y, MAIN_X, [("Caps Lock", 1.75), *"ASDFGHJKL", ";", "'", ("Enter", 2.25)])
    keys += row(y, 19.75, ["Num 4", "Num 5", "Num 6"])
    y += 1
    keys += row(y, MAIN_X, [("Left Shift", 2.25), *"ZXCVBNM", ",", ".", "/", ("Right Shift", 2.75)])
    keys += row(y, 17.5, ["Up"])
    keys += row(y, 19.75, ["Num 1", "Num 2", "Num 3"])
    keys.append(typing("Num Enter", 22.75, y, h=2))
    y += 1
    bottom = [("Left Ctrl", 1.25), ("Left Super", 1.25), ("Left Alt", 1.25), ("Space", 6.25), ("Right Alt", 1.25), ("Right Super", 1.25), ("Menu", 1.25), ("Right Ctrl", 1.25)]
    keys += row(y, MAIN_X, bottom)
    keys += row(y, 16.5, ["Left", "Down", "Right"])
    keys += row(y, 19.75, [("Num 0", 2), "Num ."])
    ids = [k["id"] for k in keys]
    assert len(ids) == len(set(ids)), "duplicate key ids"
    leds = [k["led"] for k in keys if "led" in k]
    assert len(leds) == len(set(leds)), "duplicate LED ids"
    return keys


def main() -> None:
    path = Path(sys.argv[1])
    manifest = json.loads(path.read_text())
    manifest["keyboard"] = {"keys": layout()}
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"{path}: {len(manifest['keyboard']['keys'])} keys")


if __name__ == "__main__":
    main()
