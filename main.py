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
# RICH – affichage console amélioré
# ────────────────────────────────────────────────
from rich.console import Console
from rich.panel import Panel

console = Console()

def log(msg, style="white", emoji=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[dim]{ts}[/dim] {emoji} {msg}", style=style)

# ────────────────────────────────────────────────
# ASCII ART
# ────────────────────────────────────────────────
ascii_art = r"""
 ____  ____  ____  ____  ____  __  __ _        __   _  _  ____  __   _  _   __  ____  __  ___ 
(  __)(  _ \/ ___)(_  _)(  __)(  )(  ( \ ___  / _\ / )( \(_  _)/  \ ( \/ ) / _\(_  _)(  )/ __)
 ) _)  ) __/\___ \  )(   ) _)  )( /    /(___)/    \) \/ (  )( (  O )/ \/ \/    \ )(   )(( (__ 
(____)(__)  (____/ (__) (____)(__)\_)__)     \_/\_/\____/ (__) \__/ \_)(_/\_/\_/(__) (__)\___) 
"""

# ────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────

SEARCH_URL = "https://www.justice.gov/epstein"
NAMES_FILE = "Name.txt"
HEADLESS   = False          # ← Mets True quand tout marche bien
PANEL_WIDTH = 90            # ← Largeur maximale fixe des panneaux (ajuste si besoin : 80, 100...)

# ────────────────────────────────────────────────
# SELENIUM SETUP
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

# Début – affichage stylé
console.rule("RECHERCHE EPSTEIN – DOJ", style="bold cyan")
log("DÉBUT DU SCAN", style="bold cyan", emoji="🚀")

# Affichage propre de l'ASCII art
console.print(ascii_art, style="dim cyan", markup=False)

log(f"Fichier noms : {NAMES_FILE}", style="dim")
console.rule(style="cyan")

# 1. Chargement page
log(f"Ouverture {SEARCH_URL}...", style="blue")
driver.get(SEARCH_URL)
time.sleep(5)

# 2. Bypass age gate + cookie banner
for selector in [
    "//*[contains(translate(text(),'YESNO','yesno'),'yes') or contains(text(),'18') or contains(text(),'Continue')]",
    "//button[contains(text(),'Accept') or contains(text(),'Agree') or contains(text(),'OK') or @id='accept']"
]:
    try:
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
        driver.execute_script("arguments[0].click();", btn)
        log(f"Élément bloquant cliqué via JS", style="green", emoji="✅")
        time.sleep(3)
        break
    except:
        continue

# 3. Lecture des noms
try:
    with open(NAMES_FILE, encoding='utf-8') as f:
        names = [line.strip() for line in f if line.strip()]
    log(f"{len(names)} noms chargés", style="bold green", emoji="📋")
except Exception as e:
    log(f"Erreur lecture {NAMES_FILE} : {e}", style="bold red", emoji="❌")
    driver.quit()
    exit(1)

console.rule(style="cyan")

# 4. Boucle principale (sans barre de progression pour éviter les bugs d'affichage)
for idx, name in enumerate(names, 1):
    log(f"[{idx:2d}/{len(names)}] → '{name}'", style="bold white", emoji="🔍")

    try:
        search_input = wait.until(EC.presence_of_element_located((By.ID, "searchInput")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
        time.sleep(1.2)
        driver.execute_script("arguments[0].focus();", search_input)

        search_input.clear()
        time.sleep(0.8)
        search_input.send_keys(name)
        time.sleep(1.0)
        search_input.send_keys(Keys.ENTER)

        try:
            btn = wait.until(EC.element_to_be_clickable((By.ID, "searchButton")))
            driver.execute_script("arguments[0].click();", btn)
        except:
            pass

        time.sleep(6.0)

        # Analyse résultats
        results_div = driver.find_element(By.ID, "results")
        html_lower = results_div.get_attribute("innerHTML").lower()

        no_result = any(x in html_lower for x in ["no results", "no matches", "nothing found", "0 results", "aucun résultat"])

        occurrences = html_lower.count(name.lower())

        links = results_div.find_elements(By.TAG_NAME, "a")
        doc_names = [link.text.strip() for link in links if link.text.strip() and len(link.text.strip()) > 3]

        if not no_result and len(links) > 0:
            lines = [
                "[bold green]TROUVÉ ✅[/]",
                f"Occurrences approximatives : [cyan]{occurrences}[/cyan]",
                ""
            ]

            if doc_names:
                lines.append("[bold]Documents / éléments trouvés :[/]")
                for doc in doc_names:
                    display_doc = (doc[:65] + "...") if len(doc) > 65 else doc
                    lines.append(f"  • {display_doc}")
            else:
                lines.append("Aucun titre de document récupéré")

            console.print(Panel(
                "\n".join(lines),
                title=f" {name} ",
                border_style="green",
                expand=False,
                padding=(1, 3),
                width=PANEL_WIDTH
            ))

        else:
            console.print(Panel(
                "[bold red]Non trouvé ❌[/]",
                title=f" {name} ",
                border_style="red",
                expand=False,
                padding=(1, 3),
                width=PANEL_WIDTH
            ))

    except TimeoutException:
        log(f"TIMEOUT sur le champ ou les résultats pour '{name}'", style="bold red", emoji="⚠️")
        driver.save_screenshot(f"error_timeout_{name}.png")
    except Exception as e:
        log(f"Erreur pour '{name}' : {type(e).__name__} → {str(e)}", style="bold red", emoji="❌")
        driver.save_screenshot(f"error_{name}.png")

    time.sleep(4 + (idx % 5))

# Fin
console.rule(style="cyan")
log("FIN DU SCAN", style="bold cyan", emoji="🏁")
console.rule(style="cyan")

driver.quit()