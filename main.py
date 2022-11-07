# instaling 7a.202208025.82
# /instaling.pl/
# most basic wersja, zacznij od stworzenia bazy danych
# geckodriver pobierz do folderu C:\Drivers\geckodriver-v0.32.0-win64\geckodriver.exe albo dodaj do $PATH
# https://github.com/mozilla/geckodriver/releases

from time import sleep
import glob
from os import path
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import uniform,random
import sqlite3 as sl

###     setup


def db_create_table(con):
    with con:
        try:
            con.execute("""
                CREATE TABLE wyrazenia (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    pol TEXT,
                    ang TEXT,
                    exmpl TEXT
                );
            """)
            
            print("Added 'wyrazenia' table to the database")
        except Exception as Err:
            print(Err)
        try:
            con.execute("""
                CREATE TABLE users (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    login TEXT,
                    password TEXT
                );
            """)
            print("Added 'users' table to the database")
        except Exception as Err:
            print(Err)
            

def db_add_user_acc(con, usr):
    cur = con.cursor()
    cur.execute("""
                    INSERT INTO users 
                            (login, password) 
                    VALUES  (?, ?)
                    """,    (usr[0], usr[1]))
    con.commit()
    cur.close()
    

    
try:
    user = path.expanduser('~')
    firefox_path = f"{user}\AppData\Roaming\Mozilla\Firefox\Profiles\\"
    profile_path = [i if i.endswith(".default-release") else None for i in glob.glob(firefox_path + "*")]
except Exception as Err:
    print(Err)
    

adblockfile = f"{user}\\Downloads\\ublock_origin-1.44.4.xpi"
options=Options()
options.set_preference('profile', profile_path[0])
options.set_preference("extensions.ublock_origin.currentVersion", "1.44.4")
options.set_preference("dom.webdriver.enabled", False)
options.set_preference('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
service = Service('C:\Drivers\geckodriver-v0.32.0-win64\geckodriver.exe')
driver = Firefox(service=service, options=options)
print("Started webdriver")
driver.install_addon(adblockfile, temporary=True)
print("Installed ublock Origin")
print(profile_path)


driver.get("https://instaling.pl/")

WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'/html/body/nav/a[2]/div[1]'))).click()
# sleep(round(uniform(2, 2.769), 4))


fail_chance = 0.05
def Login_on_page(username, password):
    driver.find_element(By.XPATH,'//*[@id="log_email"]').send_keys(username)
    driver.find_element(By.XPATH,'//*[@id="log_password"]').send_keys(password)
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div/div[3]/form/div/div[3]/button'))).click()
    # sleep(round(uniform(2, 2.769), 4))
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[2]/div/p[1]/a'))).click()
    # sleep(round(uniform(2, 2.769), 4))
    try:
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="start_session_button"]'))).click()
        # sleep(round(uniform(2, 2.769), 4))
    except:
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="continue_session_button"]'))).click()
            # sleep(round(uniform(2, 2.769), 4))
        except Exception as E:
            print("Err while starting the session: " + E)


def Find_translation(cur, pol, exmpl):
    try:
        cur.execute("SELECT * FROM wyrazenia WHERE pol=? AND exmpl=?", (pol,exmpl))
        answer = cur.fetchone()
        cur.close()
        return answer
    except:
        print("Couldn't find the translation")



def Input_answer(answer: str):
    try:
        a = answer
        if random() < fail_chance:
            if random() < 0.5:
                method = "method.1"
                a = answer.lower()
                a.replace("e", "r")
                a.replace("a", "q").upper()
                a = a[:1] + "j" + a[1+1:]
            else:
                method = "method.2"
                a = answer.lower()
                a.replace("e", "w")
                a.replace("a", "s").upper()
                a = a[:0] + "n" + a[0+1:]
            print(f"RANDOM 5% FAIL CHANCE, modified word to contain small mistakes with {method}")
        
            
        driver.find_element(By.XPATH,'//*[@id="answer"]').send_keys(a)
        print(f"Entered word {a}")
        # sleep(round(uniform(2, 3.769), 4))
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="check"]'))).click()
        # sleep(round(uniform(2, 2.769), 4))
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="nextword"]'))).click()
    except Exception as Err:
        print(Err)
        print("Err while inputing the answer")
        

def Find_definition(con, cur, pol, exmpl):
    try:
        print(f"{pol}: word not found in the database")
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="check"]'))).click()
        # sleep(round(uniform(2, 2.769), 4))
        ang = driver.find_element(By.XPATH, '//*[@id="word"]').text
        cur.execute("""
                    INSERT INTO wyrazenia 
                            (pol, ang, exmpl) 
                    VALUES  (?, ?, ?)
                    """,    (pol, ang, exmpl))
        con.commit()
        cur.close()
        print("Added new word to the database")
        sleep(10)
        
    except:
        print("Word doesn't have a definition")

def Solve_exercises(con, username, password):
    Login_on_page(username, password)
    while True:
        try: 
            pol = driver.find_element(By.CSS_SELECTOR, 'div[class="translations"]').text
            exmpl = driver.find_element(By.XPATH,'/html/body/div/div[8]/div[1]/div[1]').text
            # sleep(round(uniform(2, 2.769), 4))
            cur = con.cursor()
            result = Find_translation(cur, pol, exmpl)
            if result:
                print(f"'{pol}': word found in the database")
                cur = con.cursor()
                answer = Find_translation(cur, pol, exmpl)
                try:
                    Input_answer(answer[2])
                except:
                    continue
            else:
                cur = con.cursor()
                Find_definition(con, cur, pol, exmpl)
                try:
                    WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="nextword"]'))).click()
                    print("Next word")
                    # sleep(round(uniform(2, 2.769), 4))
                except:
                    print("Couldn't go to the next word")
                    try:
                        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="dont_know_new"]'))).click()
                        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="skip"]'))).click()
                    except:
                        break
        except:
            print("Finished the exercise")
            break
    try:
        # Uncomment to automatically log out
        # # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div/div[2]/img[1]'))).click()
        # # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[2]/div/p[10]/a'))).click()
        # # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div/div[3]/p[4]/a'))).click()
        print("User completed")
    except:
        print("Couldn't log out")
    return 0 
        
        
        
def start_from_db(con):
    cur = con.cursor()
    cur.execute("SELECT login, password FROM users")
    users = cur.fetchall()
    # print(users)
    for i in users:
        Solve_exercises(con, i[0], i[1])
    cur.close()



def main():
    with sl.connect('wyrazenia.db') as con:    
        # db_create_table(con)
        # db_add_user_acc(con, ("login", "password"))
        start_from_db(con)
    
if __name__ == "__main__":
    main()
### todo: add a word counter
