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
HEADLESS   = False          # ← Mets True quand tout marche bien

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
log("DÉBUT RECHERCHE EPSTEIN – Version finale (test validé)")
log(f"Headless : {HEADLESS}")
log("═"*90)

# 1. Chargement page
driver.get(SEARCH_URL)
time.sleep(5)

# 2. Bypass age gate + cookie banner (JS click = plus robuste)
for selector in [
    "//*[contains(translate(text(),'YESNO','yesno'),'yes') or contains(text(),'18') or contains(text(),'Continue')]",
    "//button[contains(text(),'Accept') or contains(text(),'Agree') or contains(text(),'OK') or @id='accept']"
]:
    try:
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
        driver.execute_script("arguments[0].click();", btn)
        log(f"→ Élément bloquant cliqué via JS : {selector}")
        time.sleep(3)
        break
    except:
        continue

# 3. Lecture des noms
with open(NAMES_FILE, encoding='utf-8') as f:
    names = [line.strip() for line in f if line.strip()]
log(f"{len(names)} noms chargés")

# 4. Boucle principale
for idx, name in enumerate(names, 1):
    log(f"[{idx:2d}/{len(names)}] → '{name}'")

    try:
        # Champ texte
        search_input = wait.until(EC.presence_of_element_located((By.ID, "searchInput")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
        time.sleep(1.2)
        driver.execute_script("arguments[0].focus();", search_input)

        search_input.clear()
        time.sleep(0.8)
        search_input.send_keys(name)
        time.sleep(1.0)
        search_input.send_keys(Keys.ENTER)
        log("  → Recherche envoyée (ENTER)")

        # Bouton Search (sécurité supplémentaire)
        try:
            btn = wait.until(EC.element_to_be_clickable((By.ID, "searchButton")))
            driver.execute_script("arguments[0].click();", btn)
            log("  → Bouton #searchButton cliqué via JS")
        except:
            pass

        time.sleep(6.0)  # temps pour #results

        # Analyse résultats
        results_div = driver.find_element(By.ID, "results")
        html_lower = results_div.get_attribute("innerHTML").lower()

        no_result = any(x in html_lower for x in ["no results", "no matches", "nothing found", "0 results", "aucun résultat"])

        if not no_result and len(results_div.find_elements(By.TAG_NAME, "a")) > 0:
            log("  → TROUVÉ ✅")
        else:
            log("  → Non trouvé ❌")

    except TimeoutException:
        log("  → TIMEOUT sur le champ ou les résultats")
        driver.save_screenshot(f"error_timeout_{name}.png")
    except Exception as e:
        log(f"  → Erreur : {type(e).__name__} → {str(e)}")
        driver.save_screenshot(f"error_{name}.png")

    time.sleep(4 + (idx % 5))  # anti-ban

log("═"*90)
log("FIN DU SCAN – Résultats dans Log.log")
log("═"*90)

driver.quit()