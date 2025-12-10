#!/usr/bin/env python3
"""
Sir's ThisVid Ripper
═══════════════════════════════════════════════════════════════════════════════
Interactive scraper for downloading videos from ThisVid tags, profiles, or categories.
Scrapes from highest page to page 1, tracks progress, and handles resumption.
"""

import os
import sys
import csv
import json
import time
import requests
import subprocess
import threading
import multiprocessing
import concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

MAX_SCRAPE_WORKERS = 5      # Concurrent page scrapes
MAX_DOWNLOAD_WORKERS = 4    # Concurrent video downloads  
SCRAPE_DELAY = 0.5          # Delay between scrapes (seconds)
REQUEST_TIMEOUT = 30        # HTTP request timeout
BATCH_SIZE = 50             # Process in batches of this many

# File names (created in download folder)
STATUS_FILE = "download_status.csv"
PAGES_FILE = "scraped_pages.txt"
SESSION_FILE = "session.json"

# Locks for thread-safe file access
scrape_lock = threading.Lock()
download_lock = multiprocessing.Lock()

# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Print a decorative header."""
    print("\n" + "═" * 70)
    print(f"  {title}")
    print("═" * 70 + "\n")


def print_section(title):
    """Print a section divider."""
    print("\n" + "─" * 70)
    print(f"  {title}")
    print("─" * 70 + "\n")


def print_success(message):
    """Print a success message."""
    print(f"  ✅ {message}")


def print_error(message):
    """Print an error message."""
    print(f"  ❌ {message}")


def print_info(message):
    """Print an info message."""
    print(f"  ℹ️  {message}")


def print_progress(current, total, prefix=""):
    """Print a progress indicator."""
    percentage = (current / total) * 100 if total > 0 else 0
    bar_length = 40
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r  {prefix} [{bar}] {current}/{total} ({percentage:.1f}%)", end="", flush=True)


# ═══════════════════════════════════════════════════════════════════════════════
# URL BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

class URLBuilder:
    """Builds paginated URLs for different ThisVid content types."""
    
    @staticmethod
    def tag_url(tag_slug, page_num):
        """Build URL for a tag page."""
        # Tags use format: /tags/tagname/page/
        return f"https://thisvid.com/tags/{tag_slug}/{page_num}/"
    
    @staticmethod
    def profile_videos_url(username, page_num):
        """Build URL for a profile's videos page."""
        # Profiles use format: /members/username/videos/page/
        if page_num == 1:
            return f"https://thisvid.com/members/{username}/public_videos/"
        return f"https://thisvid.com/members/{username}/public_videos/{page_num}/"
    
    @staticmethod
    def category_url(category_slug, page_num):
        """Build URL for a category page (like gay-newest)."""
        return f"https://thisvid.com/{category_slug}/{page_num}/"
    
    @staticmethod
    def parse_input_url(url):
        """
        Parse a user-provided URL and determine its type.
        Returns: (type, identifier, base_page) or (None, None, None) if invalid
        """
        url = url.strip().rstrip('/')
        
        # Profile videos: /members/username/public_videos/ or /members/username/public_videos/2/
        if '/members/' in url and '/public_videos' in url:
            parts = url.split('/members/')[1].split('/')
            username = parts[0]
            return ('profile', username, 1)
        
        # Tag: /tags/tagname/ or /tags/tagname/2/
        if '/tags/' in url:
            parts = url.split('/tags/')[1].split('/')
            tag_slug = parts[0]
            return ('tag', tag_slug, 1)
        
        # Category (like gay-newest): /category-name/ or /category-name/2/
        # This catches things like /gay-newest/, /amateur/, etc.
        if url.startswith('https://thisvid.com/'):
            path = url.replace('https://thisvid.com/', '').strip('/')
            parts = path.split('/')
            if parts and parts[0] and not parts[0].isdigit():
                category = parts[0]
                return ('category', category, 1)
        
        return (None, None, None)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def get_session_path(download_folder):
    """Get path to session file."""
    return Path(download_folder) / SESSION_FILE


def load_session(download_folder):
    """Load a previous session if it exists."""
    session_path = get_session_path(download_folder)
    if session_path.exists():
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def save_session(download_folder, session_data):
    """Save session data for resumption."""
    session_path = get_session_path(download_folder)
    with open(session_path, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2)


def clear_session(download_folder):
    """Clear session file after completion."""
    session_path = get_session_path(download_folder)
    if session_path.exists():
        session_path.unlink()


# ═══════════════════════════════════════════════════════════════════════════════
# PROGRESS TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

def get_status_path(download_folder):
    """Get path to status CSV file."""
    return Path(download_folder) / STATUS_FILE


def get_pages_path(download_folder):
    """Get path to scraped pages file."""
    return Path(download_folder) / PAGES_FILE


def load_scraped_pages(download_folder):
    """Load set of already-scraped page numbers."""
    pages_path = get_pages_path(download_folder)
    if not pages_path.exists():
        return set()
    try:
        with open(pages_path, 'r') as f:
            return {int(line.strip()) for line in f if line.strip()}
    except (IOError, ValueError) as e:
        print_error(f"Could not read pages file: {e}")
        return set()


def load_video_statuses(download_folder):
    """Load dictionary of video URLs and their download statuses."""
    status_path = get_status_path(download_folder)
    
    if not status_path.exists():
        with open(status_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['video_url', 'status', 'added_date'])
        return {}
    
    video_status_map = {}
    try:
        with open(status_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if row and len(row) >= 2:
                    video_status_map[row[0]] = row[1]
    except (IOError, StopIteration) as e:
        print_error(f"Could not read status file: {e}")
        return {}
    
    return video_status_map


def update_status_in_csv(download_folder, video_url, status, lock):
    """Update a video's status in the CSV file."""
    status_path = get_status_path(download_folder)
    
    with lock:
        rows = []
        with open(status_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        for i, row in enumerate(rows):
            if row and row[0] == video_url:
                rows[i][1] = status
                break
        
        with open(status_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)


# ═══════════════════════════════════════════════════════════════════════════════
# SCRAPING
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_single_page(page_num, url_builder_func, session, download_folder, 
                       scraped_pages_set, video_status_map):
    """
    Scrape a single page for video links.
    Returns the number of new links found.
    """
    if page_num in scraped_pages_set:
        return 0
    
    page_url = url_builder_func(page_num)
    
    try:
        response = session.get(
            page_url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find video links - ThisVid uses 'tumbpu' class for thumbnails
        video_links = [
            a['href'] for a in soup.find_all('a', class_='tumbpu') 
            if a.has_attr('href')
        ]
        
        new_links = 0
        status_path = get_status_path(download_folder)
        pages_path = get_pages_path(download_folder)
        
        with scrape_lock:
            with open(status_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for link in video_links:
                    if link not in video_status_map:
                        video_status_map[link] = 'pending'
                        writer.writerow([link, 'pending', datetime.now().isoformat()])
                        new_links += 1
            
            with open(pages_path, 'a') as f:
                f.write(f"{page_num}\n")
            scraped_pages_set.add(page_num)
        
        time.sleep(SCRAPE_DELAY)
        return new_links
    
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to scrape page {page_num}: {e}")
        return 0


def scrape_all_pages(url_type, identifier, start_page, end_page, download_folder,
                     scraped_pages_set, video_status_map):
    """
    Scrape all pages from start_page down to end_page.
    """
    print_section(f"SCRAPING PAGES {start_page} → {end_page}")
    
    # Build the URL function based on type
    if url_type == 'tag':
        url_builder = lambda p: URLBuilder.tag_url(identifier, p)
    elif url_type == 'profile':
        url_builder = lambda p: URLBuilder.profile_videos_url(identifier, p)
    elif url_type == 'category':
        url_builder = lambda p: URLBuilder.category_url(identifier, p)
    else:
        print_error("Unknown URL type!")
        return 0
    
    # Get pages that still need scraping
    pages_to_scrape = [
        p for p in range(start_page, end_page - 1, -1) 
        if p not in scraped_pages_set
    ]
    
    if not pages_to_scrape:
        print_info("All pages already scraped!")
        return 0
    
    print_info(f"Pages to scrape: {len(pages_to_scrape)}")
    print()
    
    session = requests.Session()
    total_new_links = 0
    completed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_SCRAPE_WORKERS) as executor:
        futures = {
            executor.submit(
                scrape_single_page, page_num, url_builder, session, 
                download_folder, scraped_pages_set, video_status_map
            ): page_num for page_num in pages_to_scrape
        }
        
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            new_links = future.result()
            total_new_links += new_links
            print_progress(completed, len(pages_to_scrape), "Scraping")
    
    print()  # New line after progress bar
    print_success(f"Scraping complete! Found {total_new_links} new video links.")
    return total_new_links


# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOADING
# ═══════════════════════════════════════════════════════════════════════════════

def download_single_video(args):
    """
    Download a single video using yt-dlp.
    Called by the multiprocessing pool.
    """
    video_url, download_folder = args
    
    try:
        command = [
            'yt-dlp', 
            '--format', 'best',
            '--no-warnings',
            '--quiet',
            '-o', os.path.join(download_folder, '%(title)s - [%(id)s].%(ext)s'),
            video_url
        ]
        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            timeout=600  # 10 minute timeout per video
        )
        
        if result.returncode == 0:
            update_status_in_csv(download_folder, video_url, 'completed', download_lock)
            return ('success', video_url)
        else:
            update_status_in_csv(download_folder, video_url, 'failed', download_lock)
            return ('failed', video_url, result.stderr.strip())
    
    except subprocess.TimeoutExpired:
        update_status_in_csv(download_folder, video_url, 'timeout', download_lock)
        return ('timeout', video_url)
    except Exception as e:
        update_status_in_csv(download_folder, video_url, 'error', download_lock)
        return ('error', video_url, str(e))


def download_pending_videos(download_folder, video_status_map):
    """
    Download all videos with 'pending' status in batches.
    """
    print_section("DOWNLOADING VIDEOS")
    
    pending_urls = [url for url, status in video_status_map.items() if status == 'pending']
    
    if not pending_urls:
        print_info("No pending videos to download.")
        return
    
    total_pending = len(pending_urls)
    print_info(f"Videos to download: {total_pending}")
    print_info(f"Processing in batches of {BATCH_SIZE}")
    print()
    
    total_success = 0
    total_fail = 0
    batch_num = 0
    
    # Process in batches
    for i in range(0, total_pending, BATCH_SIZE):
        batch_num += 1
        batch = pending_urls[i:i + BATCH_SIZE]
        batch_end = min(i + BATCH_SIZE, total_pending)
        
        print_section(f"BATCH {batch_num} ({i + 1}-{batch_end} of {total_pending})")
        
        download_args = [(url, download_folder) for url in batch]
        
        batch_success = 0
        batch_fail = 0
        
        with multiprocessing.Pool(processes=MAX_DOWNLOAD_WORKERS) as pool:
            results = pool.imap_unordered(download_single_video, download_args)
            
            for j, result in enumerate(results, 1):
                print_progress(j, len(batch), "Downloading")
                
                if result[0] == 'success':
                    batch_success += 1
                else:
                    batch_fail += 1
        
        print()  # New line after progress bar
        print_success(f"Batch {batch_num} complete: {batch_success} succeeded, {batch_fail} failed")
        
        total_success += batch_success
        total_fail += batch_fail
        
        # If there are more batches, ask to continue
        remaining = total_pending - batch_end
        if remaining > 0:
            print()
            print_info(f"{remaining} videos remaining")
            choice = input("  Continue to next batch? (Y/n): ").strip().lower()
            if choice == 'n':
                print_info("Stopping. Run again to resume.")
                break
    
    print()
    print_success(f"Session totals: {total_success} succeeded, {total_fail} failed")


# ═══════════════════════════════════════════════════════════════════════════════
# USER INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def prompt_content_type():
    """Ask user what type of content to scrape."""
    print_header("SIR'S THISVID RIPPER")
    
    print("  What would you like to scrape?\n")
    print("    [1] Tag")
    print("    [2] Profile (user's public videos)")
    print("    [3] Category (e.g., gay-newest)")
    print("    [4] Resume previous session")
    print("    [0] Exit")
    print()
    
    while True:
        choice = input("  Enter choice (0-4): ").strip()
        if choice in ['0', '1', '2', '3', '4']:
            return int(choice)
        print_error("Invalid choice. Please enter 0, 1, 2, 3, or 4.")


def prompt_identifier(content_type):
    """Ask user for the tag name, username, or category."""
    print()
    
    if content_type == 1:  # Tag
        print("  📌 TAG NAME")
        print("  Enter the tag name (as it appears in the URL).")
        print("  Example: for https://thisvid.com/tags/feet/ → enter: feet")
        print()
        identifier = input("  Tag: ").strip()
        return 'tag', identifier
    
    elif content_type == 2:  # Profile
        print("  📌 USERNAME")
        print("  Enter the username of the profile.")
        print("  Example: for https://thisvid.com/members/johnsmith/public_videos/ → enter: johnsmith")
        print()
        identifier = input("  Username: ").strip()
        return 'profile', identifier
    
    elif content_type == 3:  # Category
        print("  📌 CATEGORY")
        print("  Enter the category slug.")
        print("  Example: for https://thisvid.com/gay-newest/ → enter: gay-newest")
        print()
        identifier = input("  Category: ").strip()
        return 'category', identifier
    
    return None, None


def prompt_page_range():
    """Ask user for the page range to scrape."""
    print()
    print("  📄 PAGE RANGE")
    print("  The scraper works from highest page → page 1.")
    print()
    
    while True:
        try:
            last_page = input("  Enter the LAST page number (highest): ").strip()
            last_page = int(last_page)
            if last_page < 1:
                print_error("Page number must be at least 1.")
                continue
            break
        except ValueError:
            print_error("Please enter a valid number.")
    
    # Optionally ask for start page (if they want to start mid-way)
    print()
    print(f"  Scraping will go from page {last_page} down to page 1.")
    custom = input("  Start from a different page? (Enter page or press Enter for default): ").strip()
    
    if custom:
        try:
            start_page = int(custom)
            if start_page > last_page:
                start_page = last_page
            if start_page < 1:
                start_page = 1
        except ValueError:
            start_page = last_page
    else:
        start_page = last_page
    
    return start_page, 1  # start_page, end_page (always 1)


def prompt_download_folder():
    """Ask user for download folder location."""
    print()
    print("  📁 DOWNLOAD FOLDER")
    print("  Where should videos be saved?")
    print()
    print("  💡 TIP: You can drag and drop a folder from Finder/Explorer into")
    print("     this window to paste its path automatically!")
    print()
    
    default_folder = str(Path.cwd() / "thisvid_downloads")
    print(f"  Default: {default_folder}")
    print()
    folder = input(f"  Folder (Enter for default, or drag folder here): ").strip().strip("'\"").strip()
    
    if not folder:
        folder = default_folder
    
    folder = os.path.expanduser(folder)
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)
        print_success(f"Created folder: {folder}")
    else:
        print_info(f"Using existing folder: {folder}")
    
    return folder


def check_yt_dlp():
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def handle_resume_session():
    """Handle resuming a previous session."""
    print()
    print("  📂 RESUME SESSION")
    print("  Enter the download folder of the session to resume.")
    print()
    
    folder = input("  Folder path: ").strip()
    folder = os.path.expanduser(folder)
    
    if not os.path.exists(folder):
        print_error("Folder does not exist!")
        return None
    
    session = load_session(folder)
    if not session:
        print_error("No session file found in that folder!")
        return None
    
    print_success(f"Found session: {session.get('url_type')} → {session.get('identifier')}")
    print_info(f"Pages: {session.get('start_page')} → {session.get('end_page')}")
    
    return session


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point."""
    clear_screen()
    
    # Check for yt-dlp
    if not check_yt_dlp():
        print_header("SIR'S THISVID RIPPER")
        print_error("yt-dlp is not installed!")
        print()
        print("  Install it with: pip install yt-dlp")
        print("  Or: brew install yt-dlp (macOS)")
        print()
        sys.exit(1)
    
    # Get user choice
    choice = prompt_content_type()
    
    if choice == 0:
        print()
        print_info("Goodbye!")
        sys.exit(0)
    
    # Handle resume or new session
    if choice == 4:
        session = handle_resume_session()
        if not session:
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        url_type = session['url_type']
        identifier = session['identifier']
        start_page = session['start_page']
        end_page = session['end_page']
        download_folder = session['download_folder']
    else:
        # New session
        url_type, identifier = prompt_identifier(choice)
        start_page, end_page = prompt_page_range()
        download_folder = prompt_download_folder()
        
        # Save session for potential resume
        session_data = {
            'url_type': url_type,
            'identifier': identifier,
            'start_page': start_page,
            'end_page': end_page,
            'download_folder': download_folder,
            'started_at': datetime.now().isoformat()
        }
        save_session(download_folder, session_data)
    
    # Load progress
    scraped_pages = load_scraped_pages(download_folder)
    video_statuses = load_video_statuses(download_folder)
    
    # Show summary
    print_section("SESSION SUMMARY")
    print(f"  Type:       {url_type}")
    print(f"  Identifier: {identifier}")
    print(f"  Pages:      {start_page} → {end_page}")
    print(f"  Folder:     {download_folder}")
    print(f"  Already scraped: {len(scraped_pages)} pages")
    print(f"  Videos tracked:  {len(video_statuses)}")
    print()
    
    input("  Press Enter to start...")
    
    # Phase 1: Scrape
    scrape_all_pages(
        url_type, identifier, start_page, end_page,
        download_folder, scraped_pages, video_statuses
    )
    
    # Reload statuses (may have been updated by scraping)
    video_statuses = load_video_statuses(download_folder)
    
    # Phase 2: Download
    download_pending_videos(download_folder, video_statuses)
    
    # Clear session on completion
    clear_session(download_folder)
    
    print_section("COMPLETE")
    
    # Final stats
    final_statuses = load_video_statuses(download_folder)
    completed = sum(1 for s in final_statuses.values() if s == 'completed')
    failed = sum(1 for s in final_statuses.values() if s in ('failed', 'error', 'timeout'))
    pending = sum(1 for s in final_statuses.values() if s == 'pending')
    
    print(f"  ✅ Completed: {completed}")
    print(f"  ❌ Failed:    {failed}")
    print(f"  ⏳ Pending:   {pending}")
    print()
    print_info(f"Videos saved to: {download_folder}")
    print()
    
    input("  Press Enter to exit...")


if __name__ == "__main__":
    main()
