import os
import time
import subprocess
import random
import urllib.parse
import sys

# --- AUTO-INSTALL 'keyboard' LIBRARY ---
# This library is required to detect key presses when the window is minimized.
try:
    import keyboard
except ImportError:
    print("Installing required library 'keyboard'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard"])
    import keyboard

from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

# Custom Colors
Fore.GRAY = "\033[38;5;240m"
Fore.PRIMARY = "\033[38;5;51m"
Fore.ACCENT = "\033[38;5;198m"
Fore.SUCCESS = "\033[38;5;46m"
Fore.WARNING = "\033[38;5;214m"
Fore.ERROR = "\033[38;5;196m"

# File Paths
ACCOUNTS_FILE = "completedquest.txt"
CLAIMED_FILE = "fully_claimed_accounts.txt"

# Firefox Paths
FIREFOX_PATHS = [
    r"C:\Program Files\Mozilla Firefox\firefox.exe",
    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
]

def find_firefox():
    """Locates the Firefox executable."""
    for p in FIREFOX_PATHS:
        if os.path.exists(p): return p
    # Fallback to user input if not found
    return input(f"{Fore.ERROR}Enter full path to firefox.exe: ").strip().strip('"')

firefox_exe = find_firefox()

def force_close_firefox():
    """
    Uses Windows Taskkill to forcefully close all running Firefox instances.
    This ensures the session is cleared for the next account.
    """
    try:
        # /F = Forcefully terminate
        # /IM = Image Name (firefox.exe)
        # /T = Terminates child processes (tabs/extensions)
        subprocess.run(
            ["taskkill", "/F", "/IM", "firefox.exe", "/T"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"{Fore.WARNING}Error closing Firefox: {e}")

def get_token_from_line(line):
    """Extracts token from format email:pass:token or just token."""
    parts = line.strip().split(':')
    return parts[-1].strip() if len(parts) > 1 else parts[0].strip()

def save_success(line):
    """Saves the completed account to a file."""
    with open(CLAIMED_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# --- MAIN SCRIPT ---

print(f"{Fore.PRIMARY}⟡{'─'*60}⟡{Fore.RESET}")
print(f" {Fore.WHITE}Discord Quest Claimer {Fore.GRAY}(Background Hotkey: ENTER)")
print(f"{Fore.PRIMARY}⟡{'─'*60}⟡{Fore.RESET}")

# Load Accounts
try:
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    print(f"{Fore.ERROR}File '{ACCOUNTS_FILE}' not found!")
    input("Press Enter to exit...")
    exit()

print(f"{Fore.PRIMARY}Loaded {len(lines)} accounts.\n")

for i, line in enumerate(lines, 1):
    token = get_token_from_line(line)
    
    # 1. Ensure a clean slate before starting
    force_close_firefox()
    time.sleep(1) # Brief pause to ensure process is dead

    print(f"\n{Fore.GRAY}=== ACCOUNT {i}/{len(lines)} ===")

    # 2. Encode token and prepare URL
    token_encoded = urllib.parse.quote(token)
    url = f"https://discord.com/app?token={token_encoded}"

    print(f"{Fore.PRIMARY}Opening Firefox Private Window...")
    
    # 3. Open Firefox non-blocking (Popen)
    try:
        subprocess.Popen([firefox_exe, "-private-window", url])
        print(f"{Fore.SUCCESS}Window opened.")
    except Exception as e:
        print(f"{Fore.ERROR}Failed to open Firefox: {e}")
        continue

    print(f"\n{Fore.ACCENT}→ Perform actions (Claim Quest)")
    print(f"{Fore.ACCENT}→ When finished, press ENTER (works in background)")

    # 4. Wait for GLOBAL hotkey (Works even if minimized)
    print(f"{Fore.WHITE}>> Waiting for ENTER key... <<{Fore.RESET}")
    
    # This loop prevents CPU usage while waiting
    keyboard.wait("enter") 
    
    # Small delay to prevent accidental double-triggers
    time.sleep(0.5) 

    # 5. Force Close Firefox
    print(f"{Fore.PRIMARY}ENTER Detected! Closing Firefox...")
    force_close_firefox()
    print(f"{Fore.SUCCESS}Browser closed.")

    # 6. Save and Wait
    save_success(line)
    print(f"{Fore.SUCCESS}Account saved to {CLAIMED_FILE}")

    wait_time = random.uniform(1.5, 3)
    print(f"{Fore.GRAY}Waiting {wait_time:.1f}s...")
    time.sleep(wait_time)

print(f"\n{Fore.SUCCESS}ALL DONE!")
input("Press Enter to exit...")