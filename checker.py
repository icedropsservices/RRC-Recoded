import requests
import random
import string
import time
from colorama import Fore, init
from tqdm import tqdm

init(autoreset=True)

# Generate a username
def generate_username(length, use_digits=True):
    chars = string.ascii_letters + (string.digits if use_digits else "")
    return ''.join(random.choices(chars, k=length))

# Check username availability with rate-limit handling
def is_username_available(username, max_retries=5):
    url = f"https://accounts.rec.net/account?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    retries = 0
    while retries <= max_retries:
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 404:
                return True  # Available
            elif response.status_code == 200:
                return False  # Taken
            elif response.status_code == 403:
                wait_time = 2 ** retries
                print(f"{Fore.YELLOW}[403] Rate-limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                print(f"{Fore.YELLOW}[WARN] Unexpected status {response.status_code} for {username}")
                return False
        except Exception as e:
            print(f"{Fore.RED}Error checking {username}: {e}")
            time.sleep(2)
            retries += 1

    print(f"{Fore.RED}Max retries exceeded for {username}. Skipping.")
    return False

def main():
    try:
        length = int(input("Enter desired username length (3–25): "))
        if length < 3 or length > 25:
            print(f"{Fore.RED}Please choose a length between 3 and 25.")
            return

        amount = int(input("How many available usernames to find? "))
        use_digits_input = input("Include digits? (y/n): ").strip().lower()
        use_digits = use_digits_input == 'y'

        output_file = input("Enter output file name (e.g., usernames.txt): ").strip()
        if not output_file.endswith(".txt"):
            output_file += ".txt"
    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter numbers only.")
        return

    print(f"\n{Fore.YELLOW}Finding {amount} available usernames of length {length}...\n")

    found = 0
    attempts = 0
    seen = set()
    valid_usernames = []

    with tqdm(total=amount, desc="Progress", ncols=70, colour='green') as bar:
        while found < amount:
            username = generate_username(length, use_digits)
            if username in seen:
                continue
            seen.add(username)
            attempts += 1

            if is_username_available(username):
                print(f"{Fore.GREEN}[AVAILABLE] {username}")
                valid_usernames.append(username)
                found += 1
                bar.update(1)
            else:
                print(f"{Fore.RED}[TAKEN]     {username}")

            time.sleep(0.8)  # Slight delay to reduce base load

    with open(output_file, "w") as file:
        for name in valid_usernames:
            file.write(name + "\n")

    print(f"\n{Fore.CYAN}Checked {attempts} usernames. Found {found} available.")
    print(f"{Fore.GREEN}Saved to: {output_file}")

if __name__ == "__main__":
    main()
