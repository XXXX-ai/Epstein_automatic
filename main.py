#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime

# ────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────

SEARCH_URL = "https://www.justice.gov/epstein"
NAMES_FILE = "Name.txt"
LOG_FILE   = "Log.log"
HEADLESS   = True          # ← Set True when everything works

# ────────────────────────────────────────────────
# LOG
# ────────────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line.strip())
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line)

# ────────────────────────────────────────────────
# SELENIUM
# ────────────────────────────────────────────────

options = webdriver.ChromeOptions()
if HEADLESS:
    options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1200")
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 40)

log("═"*90)
log("EPSTEIN SEARCH START")
log("═"*90)
ascii_art = r"""
 ____  ____  ____  ____  ____  __  __ _        __   _  _  ____  __   _  _   __  ____  __  ___ 
(  __)(  _ \/ ___)(_  _)(  __)(  )(  ( \ ___  / _\ / )( \(_  _)/  \ ( \/ ) / _\(_  _)(  )/ __)
 ) _)  ) __/\___ \  )(   ) _)  )( /    /(___)/    \) \/ (  )( (  O )/ \/ \/    \ )(   )(( (__ 
(____)(__)  (____/ (__) (____)(__)\_)__)     \_/\_/\____/ (__) \__/ \_)(_/\_/\_/(__) (__)\___) 
"""
log(ascii_art.strip())
log("═"*90)

# 1. Load page
driver.get(SEARCH_URL)
time.sleep(5)

# 2. Bypass age gate + cookie banner (JS click = more robust)
for selector in [
    "//*[contains(translate(text(),'YESNO','yesno'),'yes') or contains(text(),'18') or contains(text(),'Continue')]",
    "//button[contains(text(),'Accept') or contains(text(),'Agree') or contains(text(),'OK') or @id='accept']"
]:
    try:
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
        driver.execute_script("arguments[0].click();", btn)
        log(f"→ Blocking element clicked via JS: {selector}")
        time.sleep(3)
        break
    except:
        continue

# 3. Read names
with open(NAMES_FILE, encoding='utf-8') as f:
    names = [line.strip() for line in f if line.strip()]
log(f"{len(names)} names loaded")

# 4. Main loop
for idx, name in enumerate(names, 1):
    log(f"[{idx:2d}/{len(names)}] → '{name}'")

    try:
        # Text field
        search_input = wait.until(EC.presence_of_element_located((By.ID, "searchInput")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
        time.sleep(1.2)
        driver.execute_script("arguments[0].focus();", search_input)

        search_input.clear()
        time.sleep(0.8)
        search_input.send_keys(name)
        time.sleep(1.0)
        search_input.send_keys(Keys.ENTER)
        # ← no log here

        # Search button (extra safety)
        try:
            btn = wait.until(EC.element_to_be_clickable((By.ID, "searchButton")))
            driver.execute_script("arguments[0].click();", btn)
            # ← no log here
        except:
            pass

        time.sleep(6.0)  # time for #results

        # Analyze results
        results_div = driver.find_element(By.ID, "results")
        html_lower = results_div.get_attribute("innerHTML").lower()

        no_result = any(x in html_lower for x in ["no results", "no matches", "nothing found", "0 results"]) 

        # Approximate number of occurrences of the name in the results block
        occurrences = html_lower.count(name.lower())

        # Retrieve link texts (often titles or document names)
        links = results_div.find_elements(By.TAG_NAME, "a")
        doc_names = []
        for link in links:
            txt = link.text.strip()
            if txt and len(txt) > 3:           # filtre éléments trop courts
                doc_names.append(txt)

        if not no_result and len(links) > 0:
            log("  → FOUND ✅")
            log(f"  → Approximate occurrences: {occurrences}")
            if doc_names:
                log("  → Documents / items found:")
                for doc in doc_names:
                    log(f"      • {doc}")
            else:
                log("  → No document titles retrieved")
        else:
            log("  → Not found ❌")

    except TimeoutException:
        log("  → TIMEOUT on the input or results")
        driver.save_screenshot(f"error_timeout_{name}.png")
    except Exception as e:
        log(f"  → Error: {type(e).__name__} → {str(e)}")
        driver.save_screenshot(f"error_{name}.png")

    time.sleep(4 + (idx % 5))  # anti-ban

log("═"*90)
log("SCAN FINISHED — Results in Log.log")
log("═"*90)

driver.quit()