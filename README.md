<p align="center">
  <img src="http://sirdominic.scot/css/sirthisvid.png" alt="Sir's ThisVid Ripper">
  <br><br>
  <img src="http://sirdominic.scot/css/scraperpreview.png" alt="Preview">
  <p align="center">
    <strong>A simple tool to bulk download videos from ThisVid to your computer</strong>
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-how-it-works">How It Works</a> •
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

This is a **Python script** that automatically downloads videos from ThisVid. Instead of clicking and saving each video one by one, this tool does it all for you.

**You don't need to be a programmer to use this** — the script asks you questions and you just type your answers. If you can install an app and follow prompts, you can use this.

### What You'll Need to Install First

| Program | What it is | Where to get it |
|---------|-----------|-----------------|
| **Python** | The programming language this script runs on (like how Word documents need Word to open) | [python.org/downloads](https://www.python.org/downloads/) |
| **yt-dlp** | A video downloading tool that runs in the background | Installed automatically when you run the script |

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

1. Navigate to the folder you extracted:
   ```bash
   cd Desktop/Sir-s-ThisVid-Ripper
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   
   On Mac/Linux, you might need `pip3` instead:
   ```bash
   pip3 install -r requirements.txt
   ```

### Step 4: Run It

**Windows:** Double-click `run.bat`

**Mac/Linux:** 
```bash
./run.sh
```

Or on any system:
```bash
python thisvid_scraper.py
```

---

## 🎯 How It Works

When you run the script, it shows you a menu:

```
══════════════════════════════════════════════════════════════════════
  SIR'S THISVID RIPPER
══════════════════════════════════════════════════════════════════════

  What would you like to scrape?

    [1] Tag
    [2] Profile (user's public videos)
    [3] Category (e.g., gay-newest)
    [4] Resume previous session
    [0] Exit

  Enter choice (0-4):
```

### The Flow

1. **Pick what to scrape** (tag, profile, or category)
2. **Enter the name** (e.g., for a tag, just type the tag name like `feet`)
3. **Enter the last page number** (go to ThisVid, navigate to the last page of results, and enter that number)
4. **Choose where to save** — you can drag and drop a folder from Finder/Explorer directly into the terminal window!
5. **Press Enter** and let it run

### Choosing a Download Folder

When the script asks where to save videos:

```
📁 DOWNLOAD FOLDER
Where should videos be saved?

💡 TIP: You can drag and drop a folder from Finder/Explorer into
   this window to paste its path automatically!

Default: /Users/you/thisvid_downloads

Folder (Enter for default, or drag folder here):
```

- **Press Enter** to use the default folder
- **Or drag a folder** from Finder (Mac) or Explorer (Windows) directly into the terminal — it will paste the path for you

### Resuming Downloads

If you stop the script or it crashes, just run it again and choose **[4] Resume previous session**. It will pick up where it left off.

---

## 📁 Progress Files

The script creates these files in your download folder:

| File | What it does |
|------|--------------|
| `download_status.csv` | List of all videos: pending, completed, or failed |
| `scraped_pages.txt` | Which listing pages have been checked |
| `session.json` | Session data for resuming |

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

**To retry failed videos:** Open `download_status.csv` in Excel or a text editor, find the failed entries, change `failed` to `pending`, save the file, and run the script again with option [4] Resume.
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
