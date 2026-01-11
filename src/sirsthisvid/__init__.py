#!/usr/bin/env python3
"""
Sir's ThisVid Ripper v2.1.0
Bulk download videos from ThisVid
"""

__version__ = "2.1.0"

import os
import sys
import csv
import json
import time
import re
import requests
import subprocess
from pathlib import Path
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("📦 Installing beautifulsoup4...")
    subprocess.run([sys.executable, "-m", "pip", "install", "beautifulsoup4", "-q"])
    from bs4 import BeautifulSoup

# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

SCRAPE_DELAY = 0.3
REQUEST_TIMEOUT = 30
AVG_DOWNLOAD_TIME = 10

STATUS_FILE = "download_status.csv"
SESSION_FILE = "session.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
GITHUB_REPO = "sdc88/Sirs-ThisVid-Ripper"

# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def header():
    clear()
    print()
    print("═" * 55)
    print(f"  🎬 SIR'S THISVID RIPPER  v{__version__}")
    print("═" * 55)
    print()

def progress_bar(current, total, prefix=""):
    if total == 0:
        return
    pct = current / total
    filled = int(30 * pct)
    bar = "█" * filled + "░" * (30 - filled)
    print(f"\r  {prefix} [{bar}] {current}/{total} ({pct*100:.0f}%)", end="", flush=True)

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds/60)} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE CHECKER
# ═══════════════════════════════════════════════════════════════════════════════

def check_for_updates():
    """Check GitHub for newer version."""
    header()
    print("  🔄 Checking for updates...\n")
    
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            print("  ℹ️  No releases found yet.")
            print(f"\n  You're on v{__version__}")
            input("\n  Press Enter to go back...")
            return
        
        response.raise_for_status()
        data = response.json()
        latest = data.get("tag_name", "").lstrip("v")
        
        if not latest:
            print("  ⚠️  Couldn't determine latest version")
        elif latest == __version__:
            print(f"  ✅ You're up to date! (v{__version__})")
        else:
            print(f"  🆕 New version available: v{latest}")
            print(f"  📦 You have: v{__version__}")
            print()
            print("  To update, run:")
            print("  pip install --upgrade sirsthisvid")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Couldn't check for updates: {e}")
    
    input("\n  Press Enter to go back...")

# ═══════════════════════════════════════════════════════════════════════════════
# URL BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def build_tag_url(tag, orientation, sort_type, page):
    gender = "males" if orientation == "gay" else "females"
    modifier = f"{sort_type}-{gender}"
    if page == 1:
        return f"https://thisvid.com/tags/{tag}/{modifier}/"
    return f"https://thisvid.com/tags/{tag}/{modifier}/{page}/"

def build_profile_url(member_id, page):
    if page == 1:
        return f"https://thisvid.com/members/{member_id}/public_videos/"
    return f"https://thisvid.com/members/{member_id}/public_videos/{page}/"

def build_all_videos_url(orientation, page):
    base = "gay-newest" if orientation == "gay" else "newest"
    if page == 1:
        return f"https://thisvid.com/{base}/"
    return f"https://thisvid.com/{base}/{page}/"

# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-DETECT LAST PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def find_last_page(first_page_url):
    try:
        response = requests.get(first_page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        pagination = soup.find('div', class_='pagination') or soup.find('ul', class_='pagination')
        
        if pagination:
            page_links = pagination.find_all('a')
            page_nums = []
            for link in page_links:
                text = link.get_text().strip()
                if text.isdigit():
                    page_nums.append(int(text))
            if page_nums:
                return max(page_nums)
        
        last_link = soup.find('a', class_='last') or soup.find('a', string=re.compile(r'last|»', re.I))
        if last_link and last_link.get('href'):
            match = re.search(r'/(\d+)/?$', last_link['href'])
            if match:
                return int(match.group(1))
        
        return 1
    except Exception as e:
        print(f"\n  ⚠️  Couldn't auto-detect pages: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# SCRAPING
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_page(url, session):
    try:
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        video_links = []
        for a in soup.find_all('a', class_='tumbpu'):
            href = a.get('href')
            if href and '/videos/' in href:
                video_links.append(href)
        return video_links
    except:
        return []

def scrape_all_pages(url_builder, last_page):
    print(f"\n  🔍 Scanning {last_page} pages for videos...\n")
    
    all_videos = set()
    session = requests.Session()
    
    for page in range(last_page, 0, -1):
        url = url_builder(page)
        videos = scrape_page(url, session)
        all_videos.update(videos)
        progress_bar(last_page - page + 1, last_page, "Scanning")
        time.sleep(SCRAPE_DELAY)
    
    print()
    return list(all_videos)

# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

def get_status_path(folder):
    return Path(folder) / STATUS_FILE

def get_session_path(folder):
    return Path(folder) / SESSION_FILE

def load_downloaded(folder):
    status_path = get_status_path(folder)
    if not status_path.exists():
        return set()
    
    downloaded = set()
    try:
        with open(status_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[1] == 'completed':
                    downloaded.add(row[0])
    except:
        pass
    return downloaded

def save_status(folder, video_url, status):
    status_path = get_status_path(folder)
    
    if not status_path.exists():
        with open(status_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['video_url', 'status', 'timestamp'])
    
    with open(status_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([video_url, status, datetime.now().isoformat()])

def save_session(folder, session_data):
    with open(get_session_path(folder), 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2)

def load_session(folder):
    path = get_session_path(folder)
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOADING
# ═══════════════════════════════════════════════════════════════════════════════

def check_yt_dlp():
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_yt_dlp():
    print("  📦 Installing yt-dlp...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
    return result.returncode == 0

def download_video(video_url, folder):
    try:
        cmd = [
            'yt-dlp',
            '--format', 'best',
            '--no-warnings',
            '--quiet',
            '--no-overwrites',
            '-o', os.path.join(folder, '%(title)s [%(id)s].%(ext)s'),
            video_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.returncode == 0
    except:
        return False

def download_all(videos, folder):
    print(f"\n  🚀 Downloading {len(videos)} videos...\n")
    
    success = 0
    failed = 0
    
    for i, video_url in enumerate(videos, 1):
        progress_bar(i, len(videos), "Downloading")
        
        if download_video(video_url, folder):
            save_status(folder, video_url, 'completed')
            success += 1
        else:
            save_status(folder, video_url, 'failed')
            failed += 1
    
    print("\n")
    print(f"  ✅ Downloaded: {success}")
    print(f"  ❌ Failed: {failed}")
    return success, failed

# ═══════════════════════════════════════════════════════════════════════════════
# USER INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def ask_choice(prompt, options):
    while True:
        print(prompt)
        for num, label in options:
            print(f"  [{num}] {label}")
        print()
        choice = input("  Choice: ").strip()
        for num, _ in options:
            if choice == str(num):
                return int(choice)
        print("  ⚠️  Invalid choice, try again\n")

def clean_path(path):
    """Clean up paths from terminal drag-and-drop on Mac/Linux/Windows."""
    if not path:
        return path
    
    # Remove surrounding quotes (single or double)
    path = path.strip().strip("'\"")
    
    # Handle various escape sequences from different terminals
    # Mac Terminal and iTerm escape spaces with backslash
    path = path.replace("\\\\ ", " ")  # Double-escaped spaces
    path = path.replace("\\ ", " ")    # Single-escaped spaces
    
    # Remove remaining escape backslashes (but keep Windows path separators)
    # Only remove backslashes that are escaping special chars
    import platform
    if platform.system() != "Windows":
        # On Mac/Linux, backslashes are escape chars, not path separators
        path = path.replace("\\(", "(")
        path = path.replace("\\)", ")")
        path = path.replace("\\&", "&")
        path = path.replace("\\'", "'")
        path = path.replace("\\!", "!")
        # Remove any remaining lone backslashes
        path = path.replace("\\", "")
    
    return path

def ask_folder(suggested_name):
    default = os.path.join(os.path.expanduser("~/Desktop"), suggested_name)
    
    print(f"  📁 Download folder")
    print(f"  Default: {default}")
    print(f"  TIP: Drag a folder here or press Enter for default")
    print()
    
    folder = input("  → ").strip()
    
    # Clean up the path
    folder = clean_path(folder)
    
    if not folder:
        folder = default
    
    folder = os.path.expanduser(folder)
    
    # Verify the path looks valid
    if not folder or folder.isspace():
        print("\n  ⚠️  Invalid path")
        input("\n  Press Enter to go back...")
        return None
    
    try:
        os.makedirs(folder, exist_ok=True)
    except PermissionError:
        print(f"\n  ❌ Permission denied: {folder}")
        print("  Try a different folder, or check permissions.")
        input("\n  Press Enter to go back...")
        return None
    except OSError as e:
        print(f"\n  ❌ Invalid path: {folder}")
        print(f"  Error: {e}")
        input("\n  Press Enter to go back...")
        return None
    except Exception as e:
        print(f"\n  ❌ Couldn't create folder: {e}")
        input("\n  Press Enter to go back...")
        return None
    
    return folder

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FLOWS
# ═══════════════════════════════════════════════════════════════════════════════

def flow_tag():
    header()
    print("  🏷️  TAG\n")
    
    print("  Enter the tag (the word after /tags/ in the URL)")
    print("  Example: thisvid.com/tags/feet → type: feet")
    print()
    tag = input("  → ").strip()
    if not tag:
        return None
    
    print()
    orientation = ask_choice("", [
        (1, "🍆 Gay"),
        (2, "🍑 Straight")
    ])
    orientation = "gay" if orientation == 1 else "straight"
    
    print()
    sort_type = ask_choice("", [
        (1, "🔥 Popular — most viewed"),
        (2, "🆕 Latest — newest uploads")
    ])
    sort_type = "popular" if sort_type == 1 else "latest"
    
    first_url = build_tag_url(tag, orientation, sort_type, 1)
    
    print(f"\n  🔍 Finding last page...")
    last_page = find_last_page(first_url)
    
    if last_page is None:
        last_page = int(input("  Couldn't auto-detect. Enter last page number: ").strip())
    else:
        print(f"  ✓ Found {last_page} pages")
    
    print()
    folder = ask_folder(f"{tag}-{orientation}-{sort_type}")
    
    if not folder:
        return None
    
    return {
        'mode': 'tag',
        'last_page': last_page,
        'folder': folder,
        'url_builder': lambda p: build_tag_url(tag, orientation, sort_type, p),
        'description': f"Tag: {tag} ({orientation}, {sort_type})"
    }

def flow_profile():
    header()
    print("  👤 PROFILE\n")
    
    print("  Enter the member ID (the number at the end of their profile URL)")
    print("  Example: thisvid.com/members/960704 → type: 960704")
    print()
    member_id = input("  → ").strip()
    if not member_id:
        return None
    
    first_url = build_profile_url(member_id, 1)
    
    print(f"\n  🔍 Finding last page...")
    last_page = find_last_page(first_url)
    
    if last_page is None:
        last_page = int(input("  Couldn't auto-detect. Enter last page number: ").strip())
    else:
        print(f"  ✓ Found {last_page} pages")
    
    print()
    folder = ask_folder(f"member-{member_id}")
    
    if not folder:
        return None
    
    return {
        'mode': 'profile',
        'last_page': last_page,
        'folder': folder,
        'url_builder': lambda p: build_profile_url(member_id, p),
        'description': f"Profile: {member_id}"
    }

def flow_all_videos():
    header()
    print("  📺 ALL VIDEOS\n")
    
    orientation = ask_choice("", [
        (1, "🍆 Gay"),
        (2, "🍑 Straight")
    ])
    orientation = "gay" if orientation == 1 else "straight"
    
    first_url = build_all_videos_url(orientation, 1)
    
    print(f"\n  🔍 Finding last page...")
    last_page = find_last_page(first_url)
    
    if last_page is None:
        last_page = int(input("  Couldn't auto-detect. Enter last page number: ").strip())
    else:
        print(f"  ✓ Found {last_page} pages")
    
    print()
    folder = ask_folder(f"{orientation}-newest")
    
    if not folder:
        return None
    
    return {
        'mode': 'all',
        'last_page': last_page,
        'folder': folder,
        'url_builder': lambda p: build_all_videos_url(orientation, p),
        'description': f"All {orientation} videos (newest)"
    }

def flow_resume():
    header()
    print("  ⏩ RESUME\n")
    
    print("  Enter the download folder path:")
    print("  TIP: Drag the folder here")
    print()
    folder = input("  → ").strip()
    
    # Clean up dragged paths
    folder = clean_path(folder)
    folder = os.path.expanduser(folder)
    
    if not folder or not os.path.exists(folder):
        print("\n  ⚠️  Folder doesn't exist")
        input("\n  Press Enter to go back...")
        return None
    
    session = load_session(folder)
    if not session:
        print("\n  ⚠️  No session found in that folder")
        input("\n  Press Enter to go back...")
        return None
    
    # Restore the url_builder based on session data
    session['folder'] = folder
    
    mode = session.get('mode')
    if mode == 'tag':
        # We need to re-parse the description to rebuild the URL
        # Format: "Tag: tagname (orientation, sort_type)"
        desc = session.get('description', '')
        match = re.match(r'Tag: (\S+) \((\w+), (\w+)\)', desc)
        if match:
            tag, orientation, sort_type = match.groups()
            session['url_builder'] = lambda p, t=tag, o=orientation, s=sort_type: build_tag_url(t, o, s, p)
        else:
            print("\n  ⚠️  Couldn't restore session settings")
            input("\n  Press Enter to go back...")
            return None
    elif mode == 'profile':
        desc = session.get('description', '')
        match = re.match(r'Profile: (\S+)', desc)
        if match:
            member_id = match.group(1)
            session['url_builder'] = lambda p, m=member_id: build_profile_url(m, p)
        else:
            print("\n  ⚠️  Couldn't restore session settings")
            input("\n  Press Enter to go back...")
            return None
    elif mode == 'all':
        desc = session.get('description', '')
        if 'gay' in desc.lower():
            orientation = 'gay'
        else:
            orientation = 'straight'
        session['url_builder'] = lambda p, o=orientation: build_all_videos_url(o, p)
    else:
        print("\n  ⚠️  Unknown session type")
        input("\n  Press Enter to go back...")
        return None
    
    print(f"\n  ✓ Found session: {session.get('description', 'Unknown')}")
    return session
    return session

# ═══════════════════════════════════════════════════════════════════════════════
# FIRST RUN WELCOME
# ═══════════════════════════════════════════════════════════════════════════════

def show_welcome():
    """Show welcome message on first run."""
    clear()
    print()
    print("═" * 55)
    print("  🎬 SIR'S THISVID RIPPER")
    print("═" * 55)
    print()
    print("  ✅ Installation complete!")
    print()
    print("  ─────────────────────────────────────────────────────")
    print("  HOW TO USE:")
    print("  ─────────────────────────────────────────────────────")
    print()
    print("  Just type this command anytime:")
    print()
    print("      sirsthisvid")
    print()
    print("  That's it! Follow the prompts to download videos.")
    print()
    print("  ─────────────────────────────────────────────────────")
    print("  UPDATES:")
    print("  ─────────────────────────────────────────────────────")
    print()
    print("      pip install --upgrade sirsthisvid")
    print()
    print("═" * 55)
    print()
    input("  Press Enter to start...")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Check if first run
    config_dir = Path.home() / ".sirsthisvid"
    first_run_file = config_dir / ".installed"
    
    if not first_run_file.exists():
        config_dir.mkdir(exist_ok=True)
        show_welcome()
        first_run_file.touch()
    
    # Check/install yt-dlp
    if not check_yt_dlp():
        header()
        print("  📦 Setting up yt-dlp (video downloader)...\n")
        if install_yt_dlp():
            print("  ✅ Ready!")
            time.sleep(1)
        else:
            print("  ❌ Couldn't install yt-dlp")
            print("  Try manually: pip install yt-dlp")
            sys.exit(1)
    
    while True:
        header()
        
        choice = ask_choice("  What do you want to download?\n", [
            (1, "🏷️  Tag — videos with a specific tag"),
            (2, "👤 Profile — all videos from a user"),
            (3, "📺 All Videos — newest gay or straight"),
            (4, "⏩ Resume — continue where you left off"),
            (5, "🔄 Check for updates"),
            (0, "🚪 Exit")
        ])
        
        if choice == 0:
            print("\n  👋 Bye!\n")
            sys.exit(0)
        
        if choice == 5:
            check_for_updates()
            continue
        
        if choice == 1:
            config = flow_tag()
        elif choice == 2:
            config = flow_profile()
        elif choice == 3:
            config = flow_all_videos()
        elif choice == 4:
            config = flow_resume()
        else:
            continue
        
        if not config:
            continue
        
        save_session(config['folder'], {
            'mode': config['mode'],
            'description': config['description'],
            'last_page': config['last_page'],
            'folder': config['folder']
        })
        
        header()
        all_videos = scrape_all_pages(config['url_builder'], config['last_page'])
        
        already_done = load_downloaded(config['folder'])
        to_download = [v for v in all_videos if v not in already_done]
        
        header()
        print("  📋 READY TO DOWNLOAD\n")
        print(f"  {config['description']}")
        print(f"  Pages: {config['last_page']} → 1")
        print(f"  Folder: {config['folder']}")
        print()
        print(f"  📊 Found: {len(all_videos)} videos")
        print(f"  ✓ Already downloaded: {len(already_done)}")
        print(f"  → To download: {len(to_download)}")
        
        if to_download:
            est_time = len(to_download) * AVG_DOWNLOAD_TIME
            print(f"  ⏱️  Estimated time: {format_time(est_time)}")
        
        print()
        input("  Press Enter to start (Ctrl+C to cancel)...")
        
        if not to_download:
            print("\n  ✅ Nothing new to download!")
            input("\n  Press Enter to continue...")
            continue
        
        download_all(to_download, config['folder'])
        
        print()
        print(f"  📁 Videos saved to: {config['folder']}")
        input("\n  Press Enter to continue...")


def run():
    """Entry point for the command line."""
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  👋 Cancelled\n")
        sys.exit(0)


if __name__ == "__main__":
    run()
