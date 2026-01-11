<p align="center">
  <img src="http://sirdominic.scot/css/sirthisvid.png" alt="Sir's ThisVid Ripper">
  <br><br>
  <img src="http://sirdominic.scot/css/scraperpreview.png" alt="Preview">
  <p align="center">
    <strong>A simple tool to bulk download videos from ThisVid to your computer</strong>
  </p>
  <p align="center">
    <a href="#-install">Install</a> •
    <a href="#-how-it-works">How It Works</a> •
    <a href="#-troubleshooting">Troubleshooting</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-cc0000.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-cc0000.svg" alt="Platform">
  <img src="https://img.shields.io/github/license/sdc88/Sirs-ThisVid-Ripper?color=cc0000" alt="License">
  <img src="https://img.shields.io/badge/powered%20by-yt--dlp-cc0000.svg" alt="Powered by yt-dlp">
</p>

---

## 🚀 Install

### Step 1: Install Python

Go to [python.org/downloads](https://www.python.org/downloads/) and install Python.

**⚠️ Windows users:** Tick the box that says **"Add Python to PATH"** during installation!

### Step 2: Install Sir's ThisVid Ripper

Open **Terminal** (Mac/Linux) or **Command Prompt** (Windows) and run:

```bash
pip install sirsthisvid
```

That's it. You're done.

---

## 🎬 Run

Open Terminal or Command Prompt and type:

```bash
sirsthisvid
```

---

## 🎯 How It Works

When you run `sirsthisvid`, you'll see:

```
═══════════════════════════════════════════════════════════
  🎬 SIR'S THISVID RIPPER  v2.0.0
═══════════════════════════════════════════════════════════

  What do you want to download?

  [1] 🏷️  Tag — videos with a specific tag
  [2] 👤 Profile — all videos from a user
  [3] 📺 All Videos — newest gay or straight
  [4] ⏩ Resume — continue where you left off
  [5] 🔄 Check for updates
  [0] 🚪 Exit

  Choice:
```

### The Flow

1. **Pick what to download** (tag, profile, or all videos)
2. **Enter the details** (tag name, member ID, etc.)
3. **Pick gay or straight**
4. **Choose where to save** — drag and drop a folder or press Enter for Desktop
5. **Press Enter** and let it run

### Downloading a Tag

1. Pick `[1] Tag`
2. Enter the tag name (e.g. `feet`)
3. Pick `[1] Gay` or `[2] Straight`
4. Pick `[1] Popular` or `[2] Latest`
5. Wait!

### Downloading a Profile

1. Pick `[2] Profile`
2. Go to their profile on ThisVid, look at the URL
3. Copy the number (e.g. `960704` from `thisvid.com/members/960704`)
4. Paste it
5. Wait!

### Resuming Downloads

If you stop the script or it crashes, just run `sirsthisvid` again and choose **[4] Resume**. It'll pick up where it left off.

---

## 🔄 Update

To update to the latest version:

```bash
pip install --upgrade sirsthisvid
```

Or pick `[5] Check for updates` in the menu.

---

## 🔧 Troubleshooting

<details>
<summary><strong>❌ "sirsthisvid: command not found"</strong></summary>

Python isn't in your PATH. Try:
```bash
python -m sirsthisvid
```

Or reinstall Python and tick "Add Python to PATH".
</details>

<details>
<summary><strong>❌ "pip: command not found"</strong></summary>

Install Python from [python.org/downloads](https://www.python.org/downloads/) and make sure to tick **"Add Python to PATH"**.
</details>

<details>
<summary><strong>❌ Some videos fail to download</strong></summary>

Some videos might be private, deleted, or geo-blocked. The script marks these as "failed" and moves on.
</details>

---

## 🗑️ Uninstall

```bash
pip uninstall sirsthisvid
```

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
