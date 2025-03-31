import requests, random, time
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
from colorama import Fore, init
init(autoreset=True)

id = "6349A"
url = f"https://{id}.playfabapi.com/Client/LoginWithCustomID"
file = "proxies.txt"
threads = 50
delay = (0.5, 2)
attempts = 3
cooldown = 15
headers = {"Content-Type": "application/json"}
blocked = set()

def loadproxies():
    try:
        with open(file) as f:
            p = [x.strip() for x in f if x.strip()]
        print(Fore.MAGENTA + f"[PROXY] Loaded {len(p)} proxies.")
        return p
    except FileNotFoundError:
        print(Fore.RED + "[FAILURE] Proxy file not found.")
        return []

def randid():
    return random.randint(100000000, 999999999)

def login(p):
    if p in blocked:
        return
    s = requests.Session()
    s.proxies = {"http": f"http://{p}", "https": f"http://{p}"}
    for _ in range(attempts):
        data = {"CustomId": str(randid()), "CreateAccount": True, "TitleId": id}
        try:
            r = s.post(url, headers=headers, json=data, timeout=3)
            if r.status_code == 200:
                print(Fore.GREEN + f"[SUCCESS] {data['CustomId']} - {p}")
                return
            elif r.status_code == 429:
                print(Fore.YELLOW + f"[RATE LIMIT] {p} blocked. Cooling {cooldown}s.")
                blocked.add(p)
                time.sleep(cooldown) # cooldown can be removed but will cause ratelimits if you dont have enough proxies!!
                blocked.remove(p)
                return
            else:
                print(Fore.RED + f"[FAILURE] {data['CustomId']} - {p} - {r.text}")
                return
        except requests.RequestException as e:
            print(Fore.RED + f"[ERROR] {p} - {e}")
            return
        time.sleep(random.uniform(*delay))

def run():
    proxies = loadproxies()
    if not proxies:
        return
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for p in cycle(proxies):
            ex.submit(login, p)

if __name__ == "__main__":
    run()
