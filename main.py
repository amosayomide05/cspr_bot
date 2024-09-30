from datetime import datetime, timedelta
import os, requests, time, crayons, json, threading
import urllib.parse
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import curlify

# WEE ANJG KALO MO RECODE YA FORK LAH NI REPO
# DAN TETEP CANTUMIN WINSNIPNYA

def is_url_encoded(url):
    decoded_url = urllib.parse.unquote(url)
    reencoded_url = urllib.parse.quote(decoded_url)
    return reencoded_url == url

def url_decode(encoded_url):
    return urllib.parse.unquote(encoded_url)

def print_banner():
    print("csprbot")

def log(message, level="INFO"):
    levels = {
        "INFO": crayons.cyan,
        "ERROR": crayons.red,
        "SUCCESS": crayons.green,
        "WARNING": crayons.yellow
    }
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{crayons.white(current_time)} | {levels.get(level, crayons.cyan)(level)} | {message}")

class Csprbot:
    def __init__(self, token, proxy=None):
        self.session = requests.session()
        self.session.headers.update({
            # 'authority': 'www.binance.info',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'clienttype': 'web',
            'content-type': 'application/json',
            'lang': 'en',
            'origin': 'https://webapp.cspr.community',
            'referer': 'https://webapp.cspr.community/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        })
        
        userAgent = self.get_ua()
        self.session.headers.update({
            'user-agent': userAgent
        })

        if proxy:
            self.session.proxies.update({'http': proxy, 'https': proxy})

        self.token = token
        self.game_response = None
        self.task = None

    def login(self):
        try:
            self.session.headers.update({
            'authorization': f'Bearer {self.token}'
            })
            response = self.session.get('https://api.cspr.community/api/users/me')
            if response.status_code == 200:
                jsonData = response.json()
                user = jsonData["user"]
                userName = user["username"]
                self.point = jsonData["points"]
                log("Logged in successfully!", level="SUCCESS")
                log(f'Username {userName}', level="INFO")
                log(f'Points {self.point}', level="INFO")
                return True
            else:
                log("Failed to login", level="ERROR")
                return False
        except Exception as e:
            log(f"Error during login: {e}", level="ERROR")


    def get_ua(self):
        software = [
            SoftwareName.CHROME.value,
            SoftwareName.EDGE.value,
        ]
        operating = [
            OperatingSystem.ANDROID.value,
            OperatingSystem.WINDOWS.value,
            OperatingSystem.IOS.value,
        ]
        uar = UserAgent(software_names=software, operating_systems=operating, limit=100)
        ua = uar.get_random_user_agent()
        return ua

    def game_data(self):
        try:
            while True:
                responses = requests.post('https://app.winsnip.xyz/play', json=self.game_response).text
                try:
                    response = json.loads(responses)
                except json.JSONDecodeError:
                    continue
                if response['message'] == 'success' and response['game']['log'] >= 100:
                    self.game = response['game']
                    return True
        except Exception as e:
            log(f"Error getting game data: {e}", level="ERROR")

            
    def solve_task(self):
        # try:
            res = self.session.get("https://api.cspr.community/api/users/me/tasks")
            if not res or not res.json():
                log(f"Failed to fetch tasks!", level="ERROR")
                return
            
            tasks_datas = res.json()["tasks"]
            priorityTasks = tasks_datas["priority"]
            dailyTasks = tasks_datas["daily"]

            for priorityTask in priorityTasks:
                self.solve_single_task(task=priorityTask)

            for dailyTask in dailyTasks:
                self.solve_single_task(task=dailyTask)

            today = datetime.now()
            six_am_tomorrow = today.replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=1)
            print(f"Waiting time since 6:00 a.m. is: {six_am_tomorrow - today}")
            sleep((six_am_tomorrow - today).total_seconds())
        # except Exception as e:
        #     log(f"Error completing tasks: {e}", level="ERROR")

    def solve_single_task(self, task):
        if task["claimed_at"] is not None:
            return
        
        seconds_to_allow_claim = task["seconds_to_allow_claim"]
        seconds_to_allow_claim = max(seconds_to_allow_claim, 0)
        # seconds_to_claim_again = task["seconds_to_claim_again"] TODO: tinh sau
        task_name = task["task_name"]
        catetoryType = task["category"]
        title = task["title"]
        rewards_point = 0
        try:
            rewards_point = task["rewards"][0]["value"]
        except:
            log("rewards_point err", level="ERROR")

        date_do_task = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        log(f"Doing task {title}, reward {rewards_point} points, catetory {catetoryType}", level="INFO")

        response = requests.post(
            'https://api.cspr.community/api/users/me/tasks', 
            json={
                    'task_name': task_name, 
                    'action': 0, 
                    'data': {
                        "date": date_do_task
                    }
                },
            )
        
        if response.status_code == 200:
            log("Do task in successfully!", level="SUCCESS")
            log(f"Wait for {seconds_to_allow_claim} to claim!", level="INFO")
            sleep(seconds_to_allow_claim + 1)

            date_do_task = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            response = requests.post(
            'https://api.cspr.community/api/users/me/tasks', 
            json={
                    'task_name': task_name, 
                    'action': 1, 
                    'data': {
                        "date": date_do_task
                    }
                },
            )

            if response.status_code == 200:
                log("Claim successfully!", level="SUCCESS")
            else:
                log(f"Claim failed! {response.status_code}", level="ERROR")

        else:
            log(f"Failed to do task {title} error code {response.status_code}", level="ERROR")

    def set_proxy(self, proxy=None):
        self.ses = requests.Session()
        if proxy is not None:
            self.ses.proxies.update({"http": proxy, "https": proxy})

    def start(self):
        if not self.login():
            log("Login failed.", level="ERROR")
            return
        while True:
            try:
                self.solve_task()
            except Exception as e:
                log(f"zzz: {e}", level="ERROR")
                return
        
def sleep(seconds):
    while seconds > 0:
        time_str = time.strftime('%H:%M:%S', time.gmtime(seconds))
        time.sleep(1)
        seconds -= 1
        print(f'\rWaiting {time_str}', end='', flush=True)
    print()

def run_account(index, token, proxy=None):
    if(is_url_encoded(token)):
        tokens = url_decode(token)
    else:
        tokens = token
    log(f"=== Account {index} ===", level="INFO")
    x = Csprbot(tokens, proxy)
    x.start()
    log(f"=== Account {index} Done ===", level="SUCCESS")
    sleep(10)

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    proxies = [line.strip() for line in open('proxy.txt') if line.strip()]
    tokens = [line.strip() for line in open('data.txt')]

    threads = []
    
    log("==== Starting ===", level="INFO")
    while True:
        for index, token in enumerate(tokens, start=1):
            proxy = proxies[(index - 1) % len(proxies)] if proxies else None
            t = threading.Thread(target=run_account, args=(index, token, proxy))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        log("All accounts have been completed.", level="SUCCESS")
        sleep(2000)