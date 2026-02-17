**Projet**

Ce projet automatise des recherches sur la page justice.gov/epstein en utilisant Selenium + ChromeDriver. Il lit des noms depuis `Name.txt`, effectue des recherches sur le site et enregistre les résultats dans un fichier de log.

**Fichiers importants**
- `main.py` : script principal qui pilote Selenium et réalise les recherches.
- `Name.txt` : liste des noms (une ligne par nom) à rechercher.
- `Log.log` : fichier généré contenant les horodatages et le statut de chaque recherche.

**Configuration**
- `DRIVER_PATH` dans `main.py` : chemin vers `chromedriver` (ex. `/usr/bin/chromedriver`).
- Options Selenium : le script utilise par défaut le mode headless. Pour déboguer, commente l'argument `--headless` dans `main.py`.

**Installation (rapide)**
1. Installer Python 3.10+.
2. Installer les dépendances :

```bash
python3 -m pip install -r requirements.txt
# ou au minimum:
python3 -m pip install selenium
```

3. Placer `chromedriver` accessible et autorisé (exécutable). Vérifier `DRIVER_PATH`.

**Utilisation**

```bash
python3 main.py
```

Le script lira `Name.txt`, effectuera les recherches et écrira des lignes horodatées dans `Log.log`.
Le fichier `Name.txt` est déjà rempli de 100 noms de célébrités françaises (modifiez-le à votre guise)

**Dépannage**
- TIMEOUT / résultats non chargés :
  - Lancer sans `--headless` pour voir l'UI et ajuster les sélecteurs.
  - Augmenter les temps d'attente (`WebDriverWait`, `time.sleep`) dans `main.py`.
  - Ajouter capture d'écran ou sauvegarde de `page_source` pour inspection (peut être ajouté au script).
- Erreur `executable_path` : le script utilise `Service` (Selenium 4+). Veillez à avoir une version récente de Selenium.

**Project**

This project automates searches on the justice.gov/epstein page using Selenium + ChromeDriver. It reads names from `Name.txt`, performs searches on the site and logs results to a log file.

**Important files**
- `main.py` : main script that drives Selenium and performs searches.
- `Name.txt` : list of names (one per line) to search for.
- `Log.log` : generated file containing timestamps and status for each search.

**Configuration**
- `DRIVER_PATH` in `main.py` : path to `chromedriver` (e.g. `/usr/bin/chromedriver`).
- Selenium options : the script uses headless mode by default. For debugging, comment out the `--headless` argument in `main.py`.

**Quick installation**
1. Install Python 3.10+.
2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
# or at minimum:
python3 -m pip install selenium
```

3. Place `chromedriver` somewhere accessible and executable. Check `DRIVER_PATH`.

**Usage**

```bash
python3 main.py
```

The script will read `Name.txt`, perform searches and write timestamped lines to `Log.log`.
The `Name.txt` file is already filled with 100 names of French celebrities (modify it at your leisure)

**Troubleshooting**
- TIMEOUT / results not loaded:
  - Run without `--headless` to see the UI and adjust selectors.
  - Increase wait times (`WebDriverWait`, `time.sleep`) in `main.py`.
  - Add screenshots or save `page_source` for inspection (can be added to the script).
- `executable_path` error: the script uses `Service` (Selenium 4+). Ensure you have a recent Selenium version.

**Notes**
- The script includes delays and a user-agent to reduce the risk of being blocked by protections like Akamai.
- Update the search bar selectors in `main.py` if the site's HTML changes.

**License**
- For personal use. Adjust as needed.

````
