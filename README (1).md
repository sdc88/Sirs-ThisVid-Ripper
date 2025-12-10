<p align="center">
  <img src="http://sirdominic.scot/css/sirthisvid.png" alt="Sir's ThisVid Ripper">
  <p align="center">
    <strong>A simple tool to bulk download videos from ThisVid to your computer</strong>
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-features">Features</a> •
    <a href="#-configuration">Configuration</a> •
    <a href="#-troubleshooting">Troubleshooting</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-cc0000.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-cc0000.svg" alt="Platform">
  <img src="https://img.shields.io/github/license/sdc88/Sir-s-ThisVid-Ripper?color=cc0000" alt="License">
  <img src="https://img.shields.io/badge/powered%20by-yt--dlp-cc0000.svg" alt="Powered by yt-dlp">
</p>

---

## 🤔 What Is This?

This is a **Python script** that automatically downloads videos from ThisVid listing pages. Instead of clicking and saving each video one by one, this tool does it all for you.

**You don't need to be a programmer to use this** — just follow the steps below. If you can install an app and double-click a file, you can use this.

### What You'll Need to Install First

| Program | What it is | Where to get it |
|---------|-----------|-----------------|
| **Python** | The programming language this script runs on (like how Word documents need Word to open) | [python.org/downloads](https://www.python.org/downloads/) |
| **yt-dlp** | A video downloading tool that runs in the background | Installed automatically when you follow the steps below |

---

## ✨ Features

- 📥 **Bulk downloading** — Downloads entire pages of videos automatically
- 💾 **Progress tracking** — Stop anytime and pick up where you left off
- 🔄 **Handles failures** — If a video fails, it's logged so you can retry later
- 🖥️ **Works everywhere** — Windows, Mac, and Linux

---

## 🚀 Quick Start

### Step 1: Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow **Download Python** button
3. Run the installer
4. **⚠️ IMPORTANT (Windows only):** Tick the box that says **"Add Python to PATH"** before clicking Install

### Step 2: Download This Tool

**Option A — Easy way:**
1. Click the green **Code** button at the top of this page
2. Click **Download ZIP**
3. Extract the ZIP file somewhere (like your Desktop or Downloads folder)

**Option B — If you know Git:**
```bash
git clone https://github.com/sdc88/Sir-s-ThisVid-Ripper.git
```

### Step 3: Install the Dependencies

Open **Terminal** (Mac/Linux) or **Command Prompt** (Windows), then:

1. Navigate to the folder you extracted. For example:
   ```bash
   cd Desktop/Sir-s-ThisVid-Ripper
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   
   On Mac/Linux, you might need to use `pip3` instead:
   ```bash
   pip3 install -r requirements.txt
   ```

### Step 4: Run It

**Windows:** Just double-click `run.bat`

**Mac/Linux:** 
```bash
./run.sh
```

Or on any system:
```bash
python scraper.py
```

Videos will download to a folder called `thisvid_downloads`.

---

## ⚙️ Configuration

Before running, you can change which pages to download. Open `scraper.py` in any text editor (Notepad, TextEdit, VS Code) and look for these lines near the top:

```python
START_PAGE = 37068  # Start from this page (works backwards)
END_PAGE = 37060    # Stop at this page (set to 1 for everything)

BASE_URL = "https://thisvid.com/gay-newest/{}/"  # Change category here
```

**How to find page numbers:** Go to ThisVid, navigate to a listing page, and look at the URL. For example, `thisvid.com/gay-newest/500/` means page 500.

---

## 📁 Progress Files

The script creates two files to remember what it's done:

| File | What it does |
|------|--------------|
| `download_status.csv` | List of all videos: pending, completed, or failed |
| `scraped_pages.txt` | Which listing pages have been checked |

**Don't delete these** unless you want to start completely fresh!

---

## 🔧 Troubleshooting

<details>
<summary><strong>❌ "python is not recognized" or "pip is not recognized"</strong></summary>

This means Python wasn't added to your system PATH during installation.

**Fix:** Reinstall Python from [python.org/downloads](https://www.python.org/downloads/) and make sure to tick **"Add Python to PATH"** at the start of the installer.
</details>

<details>
<summary><strong>❌ "yt-dlp is not recognized"</strong></summary>

Try running: `python -m pip install yt-dlp`
</details>

<details>
<summary><strong>❌ Some videos fail to download</strong></summary>

Some videos might be private, deleted, or geo-blocked. The script marks these as "failed" and moves on.

**To retry failed videos:** Open `download_status.csv` in Excel or a text editor, find the failed entries, change `failed` to `pending`, save the file, and run the script again.
</details>

---

## 📜 License

[CC0 1.0 Universal](LICENSE) — Do whatever you want with this.

---

<p align="center">
  <strong>More from Sir:</strong><br><br>
  <a href="https://thevault.locker">🔒 The Vault+</a> · 
  <a href="https://cultofsir.com">👁️ The Cult of Sir</a> · 
  <a href="https://sirdominic.store">🛒 Sir Store</a>
</p>

<p align="center">
  Made with ☕ by <a href="https://sirdominic.scot">Sir</a>
</p>
