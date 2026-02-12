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

**Dépannage**
- TIMEOUT / résultats non chargés :
  - Lancer sans `--headless` pour voir l'UI et ajuster les sélecteurs.
  - Augmenter les temps d'attente (`WebDriverWait`, `time.sleep`) dans `main.py`.
  - Ajouter capture d'écran ou sauvegarde de `page_source` pour inspection (peut être ajouté au script).
- Erreur `executable_path` : le script utilise `Service` (Selenium 4+). Veillez à avoir une version récente de Selenium.

**Notes**
- Le script inclut des temporisations et un user-agent pour réduire les risques de blocage par des protections comme Akamai.
- Modifier les sélecteurs de la barre de recherche dans `main.py` si le site change son HTML.

**Licence**
- Usage personnel. Ajuster selon tes besoins.
