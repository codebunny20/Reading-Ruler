# 📘 Reading Ruler — Minimal, Accessible On‑Page Reading Aid

**Reading Ruler** is a lightweight, keyboard‑driven accessibility tool that helps users maintain focus while reading long pages of text.  
It adds a subtle highlight “ruler” that follows the cursor and dims the rest of the page, improving readability without clutter or UI bloat.

This extension is built to be:

- **Minimal** — no popup, no options page, no UI chrome  
- **Fast** — pure content script, no frameworks  
- **Accessible** — adjustable height, dim strength, and brightness  
- **Keyboard‑first** — every feature is controlled by shortcuts  
- **Privacy‑first** — no data collection, no external requests  

---

## ✨ Features

### 🎯 Focus Ruler  
A soft highlight bar follows your cursor, helping you track lines of text while reading.

### 🌙 Adjustable Dim Strength  
Darken or lighten the surrounding page to your preference.

### 📏 Adjustable Ruler Height  
Increase or decrease the reading window for different content types.

### 💡 Brightened Text Under Ruler  
Text inside the ruler is gently brightened for improved clarity.

### ⚡ Instant Keyboard Shortcuts  
No menus. No clicking. Everything is controlled from the keyboard.

---

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| **Toggle Ruler On/Off** | `Ctrl + Shift + R` |
| **Increase Ruler Height** | `Ctrl + Shift + ↑` |
| **Decrease Ruler Height** | `Ctrl + Shift + ↓` |
| **Increase Dim (Darker)** | `Ctrl + Shift + ←` |
| **Decrease Dim (Lighter)** | `Ctrl + Shift + →` |

When the ruler is enabled, a small floating hint appears showing available shortcuts.

---

## 🛠 How It Works

The extension injects a single content script (`content.js`) that:

- Creates a full‑page overlay  
- Cuts a “window” through it using `clip-path`  
- Positions a highlight bar under the cursor  
- Applies a brightness filter inside the ruler  
- Listens for keyboard shortcuts to adjust settings  
- Shows a small fading hint popup for user feedback  

No background scripts.  
No storage.  
No permissions beyond `"activeTab"`.

---

## 📂 Project Structure

```
reading ruler/
├─ manifest.json
├─ content.js
├─ icons/
│  └─ 16.png
└─ Help & Info/
   └─ extension structure.txt
```

---

## 🔒 Privacy

This extension:

- collects **no data**  
- sends **nothing** to external servers  
- stores **no settings**  
- runs **only** on the active tab  

Your reading stays on your device.

---

## 🚀 Why This Exists

I made this extension for Reading long articles, documentation, or dense text online can be visually overwhelming.  
Reading Ruler provides a simple, unobtrusive way to stay focused — especially helpful for:

- ADHD  
- Dyslexia  
- Eye strain  
- Long‑form reading  
- Technical documentation  

It’s intentionally minimal so it works everywhere without getting in your way and im still learning.

---

## 🧩 Installation (Developer Mode)

1. Download or clone this repository  
2. Open `chrome://extensions`  
3. Enable **Developer Mode**  
4. Click **Load unpacked**  
5. Select the `reading ruler/` folder  

---

## 📣 License

MIT — free to use, modify, and build on

---

## 💬 Feedback & Contributions

If you have ideas for small quality‑of‑life improvements or accessibility tweaks, feel free to open an issue or reach out at https://dev.to/codebunny20.