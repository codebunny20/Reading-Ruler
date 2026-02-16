# drafty

A lightweight desktop GUI for drafting social posts with a **two-pane layout**:  
- **Left:** editor (your draft)  
- **Right:** **live preview** that renders your post as it would appear on the selected platform

Use it to iterate quickly on copy, spacing, and platform constraints before posting.

## Features

- Two-pane editor + live preview
- Platform-aware preview rules (length, truncation/“see more”, normalization)
- Quick iteration on formatting (line breaks, paragraphs, hashtags)

## Platform rules (preview behavior)

### Twitter / X
- **Effective length:** preview uses an “effective length” model (not strictly raw characters).  
  - This is intended to approximate real-world counting behavior, but may differ from the platform’s current rules.
- The preview will indicate when the draft exceeds the effective limit.

### Instagram
- **Hashtag limit:** Instagram allows up to **30 hashtags** per post.  
- The preview flags drafts that exceed this limit.

### LinkedIn
- **Normalization:** LinkedIn tends to normalize whitespace (e.g., collapsing repeated spaces and/or applying consistent line break behavior).  
- The preview applies LinkedIn-style normalization so what you see is closer to what gets published.

### “See more” cutoffs (truncation preview)
The preview simulates common truncation thresholds where platforms show a **“see more”** break:
- If the draft exceeds the platform cutoff, the preview shows the truncated view and indicates that content continues.
- Note: exact cutoffs can vary by client/app/version; treat these as best-effort approximations.

## How to run

1. Ensure you have **Python 3.10+** installed.
2. From the project folder:

   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   pip install -r requirements.txt
   python -m drafty
   ```

If your entry point differs (e.g., `python app.py`), use the command appropriate for this repo’s current launcher.

## Controls

- **Type in the left pane** to edit your draft.
- **Live preview updates automatically** in the right pane.
- **Select the target platform** (e.g., Twitter/X, Instagram, LinkedIn) to apply that platform’s rules.
- Use the app’s actions (e.g., **Copy**, **Clear**, **Export**) if available in the current UI build.

## Notes / Limitations

- **Previews are approximate.** Real platforms change rules/clients frequently; final rendering may differ.
- **Effective length & truncation** are heuristics for drafting convenience, not authoritative enforcement.
- If you rely on exact compliance (e.g., brand/legal copy), verify in the platform’s native composer before publishing.
