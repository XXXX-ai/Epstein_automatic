#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Installation requise : pip install selenium rich fake-useragent
from fake_useragent import UserAgent

console = Console()

# ────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────
SEARCH_URL = "https://www.justice.gov/epstein"
NAMES_FILE = "Name.txt"
OUTPUT_CSV = "resultats.csv"
HEADLESS = False  # Mettre à True pour la discrétion
WAIT_TIME = 15    # Secondes max d'attente pour le chargement des éléments

def log(msg, style="white", emoji=""):
    ts = datetime.now().strftime("%H:%M:%S")
    console.print(f"[dim]{ts}[/dim] {emoji} {msg}", style=style)

# ────────────────────────────────────────────────
# SETUP DRIVER
# ────────────────────────────────────────────────
def get_driver():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    return driver

# ────────────────────────────────────────────────
# LOGIQUE PRINCIPALE
# ────────────────────────────────────────────────
def run_scanner():
    driver = get_driver()
    wait = WebDriverWait(driver, WAIT_TIME)
    
    console.rule("[bold cyan]EPSTEIN SCANNER V2[/bold cyan]")

    # 1. Lecture et Nettoyage des noms
    try:
        with open(NAMES_FILE, "r", encoding="utf-8") as f:
            raw_names = [line.strip() for line in f if line.strip()]
        # Suppression des doublons tout en gardant l'ordre 
        names = list(dict.fromkeys(raw_names))
        log(f"{len(names)} noms uniques chargés (Doublons ignorés)", style="green", emoji="📋")
    except Exception as e:
        log(f"Erreur fichier : {e}", style="bold red")
        return

    # 2. Initialisation du CSV
    results_data = []
    
    # 3. Accès au site et passage de l'Age Gate
    log(f"Connexion à {SEARCH_URL}...", style="blue")
    driver.get(SEARCH_URL)
    
    try:
        # Attente d'un bouton de confirmation type "Yes" ou "Continue"
        confirm_xpath = "//*[contains(translate(text(),'YES','yes'),'yes') or contains(text(),'18')]"
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_xpath)))
        btn.click()
        log("Accès autorisé (Age Gate passé)", style="green", emoji="🔓")
    except TimeoutException:
        log("Aucune barrière d'âge détectée, passage à la suite.", style="dim")

    # 4. Boucle de recherche
    for idx, name in enumerate(names, 1):
        log(f"[{idx}/{len(names)}] Recherche : [bold]{name}[/bold]", emoji="🔍")
        
        try:
            # Localisation du champ de recherche
            search_input = wait.until(EC.presence_of_element_located((By.ID, "searchInput")))
            search_input.clear()
            search_input.send_keys(name)
            search_input.send_keys(Keys.ENTER)

            # Attente que les résultats soient mis à jour (vérifie le conteneur)
            time.sleep(3) # Petit délai de sécurité pour le rafraîchissement DOM
            results_container = wait.until(EC.presence_of_element_located((By.ID, "results")))
            
            # Analyse des résultats
            links = results_container.find_elements(By.TAG_NAME, "a")
            found_docs = [link.text.strip() for link in links if link.text.strip()]
            
            status = "OUI" if found_docs else "NON"
            color = "green" if found_docs else "red"
            
            # Affichage console
            panel_content = f"Trouvé : [bold]{status}[/bold]\nDocuments : {len(found_docs)}"
            if found_docs:
                panel_content += f"\n[dim]Détails : {', '.join(found_docs[:3])}...[/dim]"
            
            console.print(Panel(panel_content, title=name, border_style=color, expand=False))

            # Stockage
            results_data.append({
                "Nom": name,
                "Trouvé": status,
                "Nb_Docs": len(found_docs),
                "Détails": "; ".join(found_docs)
            })

        except Exception as e:
            log(f"Erreur technique pour {name} : {str(e)[:50]}...", style="bold red", emoji="⚠️")
            results_data.append({"Nom": name, "Trouvé": "ERREUR", "Nb_Docs": 0, "Détails": str(e)})

        # Pause variable pour éviter le bannissement IP
        time.sleep(2)

    # 5. Export des résultats
    try:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["Nom", "Trouvé", "Nb_Docs", "Détails"], delimiter=";")
            writer.writeheader()
            writer.writerows(results_data)
        log(f"Rapport généré : {OUTPUT_CSV}", style="bold green", emoji="💾")
    except Exception as e:
        log(f"Erreur export CSV : {e}", style="red")

    driver.quit()
    console.rule("[bold cyan]SCAN TERMINÉ[/bold cyan]")

if __name__ == "__main__":
    run_scanner()