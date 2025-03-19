# ETL Data Warehouse

## Description
Ce projet vise à extraire, transformer et charger (ETL) des données de population mondiale dans un Data Warehouse afin de permettre des analyses approfondies et des visualisations interactives.

## Structure du projet
- **Scripts Python et SQL**
  - `ProjetFinalETLDWH_ABDOULAYESOW.py` : Script Python principal pour l'ETL.
  - `Script_ETL_Data_Warehouse.sql` : Script SQL pour la structuration de la base de données.
  - `SQLQuery2.sql` : Script SQL supplémentaire.

- **Données**
  - `population_mondiale.csv` : Données brutes de la population mondiale.
  - `population_mondiale_cleaned.csv` : Données nettoyées et préparées pour l'analyse.

- **Visualisations et rapports**
  - `Bar_Chart_Race_Population_1960_2023.html` : Animation de l'évolution de la population.
  - `Dashboard.html` : Tableau de bord interactif.
  - `Figure_1 Distribution de la population par pays en 2023.png`
  - `Figure_2 Evolution de la population mondiale entre 1960 et 2023.png`
  - `Figure_3 Evolution de la population des cinq pays les plus peuplés.png`
  - `idh_comparaison_no_values.html` : Comparaison de l'IDH.
  - `population_par_continent.html` : Visualisation par continent.
  - `population_pie_1960.html` : Diagramme circulaire pour 1960.
  - `population_pie_2023.html` : Diagramme circulaire pour 2023.

- **Autres fichiers**
  - `.gitignore` : Fichier de configuration Git.
  - `Projet Final.pdf` : Document détaillant le projet.

## Installation
1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/LayeBado7/etl-data-warehouse.git
   ```
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt  # Si un fichier requirements.txt est disponible
   ```
3. **Exécuter le script principal** :
   ```bash
   python ProjetFinalETLDWH_ABDOULAYESOW.py
   ```

## Utilisation
- Exécutez le script Python pour nettoyer et transformer les données.
- Utilisez les fichiers SQL pour structurer la base de données et exécuter des requêtes.
- Ouvrez les fichiers HTML pour visualiser les résultats sous forme de graphiques interactifs.

## Contributeurs
- **Abdoulaye Sow**

## Licence
Ce projet est sous licence MIT (ou toute autre licence à préciser).
