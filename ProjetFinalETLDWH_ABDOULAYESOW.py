'''
L'objectif de ce projet est de créer un ETL pour traiter les données de la population mondiale (1960-2023) en utilisant Apache NiFi pour l’intégration et SQL Server comme entrepôt de données.

Dans un premier temps, nous allons bâtir les processus ETL :

    1. Créer un groupe de processeur nommé INGESTION_POPULATION_MONDIALE dans Apache NiFi.
    2. Récupérer le fichier population_mondiale.csv et nettoyer les données.
    3. Charger les données dans la table population_mondiale_1960_2023 tout en gérant les dédoublonnages via un trigger SQL.
    4. Automatiser le pipeline pour qu'il s'exécute chaque 5 janvier.

Dans un second temps, nous allons construire le Data Warehouse. A partir de la table population_mondiale_1960_2023, alimenter les tables suivantes dans SQL Server :

population_afrique_1960_2023
population_amerique_du_nord_1960_2023
population_amerique_du_sud_1960_2023
population_europe_1960_2023
population_asie_1960_2023
population_oceanie_1960_2023

Ce projet sera réalisé en trois phases :

✅ Phase 1 : Extraction et nettoyage

Analyser le fichier CSV.
Identifier les colonnes inutiles, valeurs manquantes et doublons.
Vérifier l’intégrité des données par continent.

✅ Phase 2 : Implémentation du pipeline ETL

Construire le flow Apache NiFi pour extraire, transformer et charger (ETL).
Configurer la suppression des doublons via un trigger SQL.
Définir l'automatisation du pipeline.

✅ Phase 3 : Création et remplissage du Data Warehouse

Définir les tables et leurs relations.
Créer un processus d'alimentation des tables par continent.

'''
#########

# Analyse du fichier "population_mondiale.csv" en utilisant le processus EDA

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger le fichier CSV avec le bon séparateur
file_path = "C:/Users/lenovo/OneDrive/Desktop/DAMA5/ProjetFinalETLDatawarehouse/ProjetFinalETLDatawarehouse_ABDOULAYESOW/population_mondiale.csv"
df = pd.read_csv(file_path, sep=';')

# 1. Résumé statistique des données numériques
summary_stats = df.describe()
print("\nRésumé statistique des données :")
print(summary_stats)

# 2. Vérification des valeurs manquantes
missing_values = df.isnull().sum()
print("\nValeurs manquantes par colonne :")
print(missing_values[missing_values > 0])

# 3. Distribution de la population en 2023
plt.figure(figsize=(12, 6))
sns.histplot(df['2023'].dropna(), bins=30, kde=True)
plt.xlabel("Population en 2023")
plt.ylabel("Nombre de pays")
plt.title("Distribution de la population par pays en 2023")
plt.show()

# 4. Évolution de la population mondiale
years = [str(year) for year in range(1960, 2024)]
df_population = df[years].sum()  # Somme de la population mondiale par année

plt.figure(figsize=(12, 6))
plt.plot(df_population.index, df_population.values, marker='o', linestyle='-')
plt.xlabel("Année")
plt.ylabel("Population mondiale")
plt.title("Évolution de la population mondiale (1960-2023)")
plt.xticks(rotation=45)
plt.grid()
plt.show()

# 5. Comparaison de la croissance démographique de quelques pays
top_countries = df.nlargest(5, '2023')['country_code']  # 5 pays les plus peuplés en 2023

plt.figure(figsize=(12, 6))
for country in top_countries:
    plt.plot(years, df[df['country_code'] == country][years].values.flatten(), label=country)

plt.xlabel("Année")
plt.ylabel("Population")
plt.title("Évolution de la population des 5 pays les plus peuplés")
plt.legend()
plt.xticks(rotation=45)
plt.grid()
plt.show()

#########

# Implémentation du pipeline ETL avec Apache Nifi

'''
Objectif : Construire un pipeline ETL dans Apache NiFi.

Actions à mener :
    Créer un groupe de processeurs nommé INGESTION_POPULATION_MONDIALE.
    Lire et transformer les données depuis le CSV (nettoyage final dans NiFi si nécessaire).
    Charger les données dans une table SQL Server (population_mondiale_1960_2023).
    Créer un trigger SQL pour éviter les doublons lors du chargement.
    Planifier l’exécution automatique chaque 5 janvier.

'''
###
# Exportation du fichier nettoyé en format csv pour ingestion dans Apache Nifi

import pandas as pd

# Charger le fichier CSV avec le bon séparateur (;)
file_path = "C:/Users/lenovo/OneDrive/Desktop/DAMA5/ProjetFinalETLDatawarehouse/ProjetFinalETLDatawarehouse_ABDOULAYESOW/population_mondiale.csv"
df = pd.read_csv(file_path, delimiter=";", encoding="utf-8")

# Remplacer les valeurs manquantes dans 'borders' et 'idh_group'
df['borders'].fillna('No Borders', inplace=True)
df['idh_group'].fillna('Unknown', inplace=True)

# Remplacer les valeurs manquantes dans les colonnes de population par la moyenne du pays
cols_years = [str(year) for year in range(1960, 2024)]  # Colonnes de 1960 à 2023
for col in cols_years:
    df[col].fillna(df[cols_years].mean(axis=1), inplace=True)  # Moyenne par ligne

# Sauvegarde du fichier nettoyé en CSV dans un format compatible avec NiFi
cleaned_file_path = "population_mondiale_cleaned.csv"
df.to_csv(cleaned_file_path, sep=";", index=False, encoding="utf-8")

print(f"Fichier nettoyé exporté : {cleaned_file_path}")

###

# Chargement des Données dans SQL Server

'''
Objectifs :

Créer la connexion à SQL Server.
Créer la table population_mondiale_1960_2023.
Insérer les données nettoyées dans la table.

'''

"Nous allons installer pyodbc, une bibliothèque permettant de connecter Python à SQL Server. (pip install pyodbc)"

'''
Nous allons vérifier si SQL Server est actif avant de nous connecter au server en suivant les procédures :

Vérifier si SQL Server est en cours d’exécution (services.msc > SQL Server (MSSQLSERVER)).

Vérifier si le protocole TCP/IP est activé (SQL Server Configuration Manager > SQL Server Network Configuration > Protocols for MSSQLSERVER > Activer TCP/IP).

Vérifier si le serveur accepte les connexions SQL Server Authentication.
'''

# Connexion à Sql Server

import pandas as pd
import pyodbc

# Charger le fichier nettoyé
file_path = "C:\\Users\\lenovo\\OneDrive\\Desktop\\DAMA5\\ProjetFinalETLDatawarehouse\\ProjetFinalETLDatawarehouse_ABDOULAYESOW\\population_mondiale_cleaned.csv"
df = pd.read_csv(file_path, delimiter=";", encoding="utf-8")

# Connexion à SQL Server
server = 'DESKTOP-RMUNQ82'  # Modifier avec le nom du serveur SQL
database = 'PopulationDB'  # Modifier avec le nom de la base de données
username = 'sa'  # Modifier avec votre utilisateur SQL
password = 'root'  # Modifier avec votre mot de passe SQL
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connexion réussie à SQL Server !")

    # Création de la table population_mondiale_1960_2023
    create_table_query = '''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='population_mondiale_1960_2023' AND xtype='U')
    CREATE TABLE population_mondiale_1960_2023 (
        country_code VARCHAR(10),
        name_en VARCHAR(255),
        name_fr VARCHAR(255),
        borders NVARCHAR(MAX),
        arab_world BIT,
        central_europe_and_the_baltics BIT,
        east_asia_pacific BIT,
        euro_area BIT,
        europe_central_asia BIT,
        european_union BIT,
        latin_america_caribbean BIT,
        north_america BIT,
        oecd_members BIT,
        sub_saharan_africa BIT,
        upper_middle_income BIT,
        south_america BIT,
        central_america_caraibes BIT,
        cocac BIT,
        continental_europe BIT,
        asia_oceania BIT,
        idh_group VARCHAR(255),
        ue27 BIT,
        g7 BIT,
        g20 BIT,
        ''' + ', '.join([f'[{year}] FLOAT' for year in range(1960, 2024)]) + '''
    );
    '''
    
    cursor.execute(create_table_query)
    cursor.commit()

    # Vérification du nombre de colonnes
    num_columns = len(df.columns)
    num_placeholders = insert_query.count('?')
    
    if num_columns != num_placeholders:
        raise ValueError(f"Problème de colonnes : {num_columns} colonnes dans le fichier, {num_placeholders} placeholders dans SQL")

    # Insérer les données dans SQL Server
    insert_query = f'''
    INSERT INTO population_mondiale_1960_2023 VALUES ({', '.join(['?' for _ in range(num_columns)] )})
    '''

    for index, row in df.iterrows():
        try:
            cursor.execute(insert_query, tuple(row))
        except Exception as e:
            print(f"⚠️ Erreur lors de l'insertion de la ligne {index} : {e}")

    # Commit et fermeture de la connexion
    conn.commit()
    cursor.close()
    conn.close()

    print("Les données ont été insérées avec succès dans SQL Server !")

except pyodbc.Error as e:
    print(f"Erreur de connexion à SQL Server : {e}")

except Exception as e:
    print(f"Erreur inattendue : {e}")

# Importatation du fichier "population_mondiale_cleaned.csv" vers Sql Server

import pandas as pd
import pyodbc
from sqlalchemy import create_engine

# 📌 1. Paramètres de connexion à SQL Server
server = 'DESKTOP-RMUNQ82'  # Modifier avec le nom du serveur SQL
database = 'PopulationDB'  # Modifier avec le nom de la base de données
username = 'sa'  # Modifier avec votre utilisateur SQL
password = 'root'  # Modifier avec votre mot de passe SQL

# 📌 2. Création de l'engine SQLAlchemy pour l'importation des données
connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(connection_string)

# 📌 3. Définition du schéma SQL pour la table
create_table_query = """
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'population_mondiale_1960_2023')
BEGIN
    CREATE TABLE population_mondiale_1960_2023 (
        country_code VARCHAR(10),
        name_en NVARCHAR(255),
        name_fr NVARCHAR(255),
        """ + ",\n        ".join([f"[{year}] FLOAT" for year in range(1960, 2024)]) + """
    );
END
"""

# 📌 4. Exécution de la création de la table
with engine.connect() as conn:
    conn.execute(create_table_query)

# 📌 5. Insértion des données dans la table
df_cleaned.to_sql('population_mondiale_1960_2023', con=engine, if_exists='replace', index=False)

print("✅ Données chargées avec succès dans SQL Server !")

###

# Automatisation avec Apache Nifi

'''
Objectif : Créer le pipeline ETL pour Population Mondiale dans Apache NiFi.
 
Il s'agit d'automatiser l'extraction, la transformation et le chargement (ETL) des données dans SQL Server.

Pipeline NiFi :

    GetFile → Lire le fichier population_mondiale.csv

    ConvertRecord → Convertir les données CSV en format SQL

    PutDatabaseRecord → Insérer les données dans SQL Server

    Automatisation → Planifier l'exécution chaque 5 janvier

'''

# Nous allons générer un fichier JSON de configuration NiFi pour automatiser notre pipeline ETL.

{
  "flow": {
    "processors": [
      {
        "id": "1",
        "name": "GetFile",
        "type": "org.apache.nifi.processors.standard.GetFile",
        "properties": {
          "Input Directory": "/mnt/data/",
          "File Filter": "population_mondiale.csv",
          "Keep Source File": "false"
        }
      },
      {
        "id": "2",
        "name": "ConvertRecord",
        "type": "org.apache.nifi.processors.standard.ConvertRecord",
        "properties": {
          "Record Reader": "CSVReader",
          "Record Writer": "JsonRecordSetWriter"
        }
      },
      {
        "id": "3",
        "name": "PutDatabaseRecord",
        "type": "org.apache.nifi.processors.standard.PutDatabaseRecord",
        "properties": {
          "Database Connection Pooling Service": "SQLServerPool",
          "Table Name": "population_mondiale_1960_2023",
          "Statement Type": "INSERT"
        }
      },
      {
        "id": "4",
        "name": "PutDatabaseRecord_Afrique",
        "type": "org.apache.nifi.processors.standard.PutDatabaseRecord",
        "properties": {
          "Database Connection Pooling Service": "SQLServerPool",
          "Table Name": "population_afrique_1960_2023",
          "Statement Type": "INSERT",
          "SQL Query": "INSERT INTO population_afrique_1960_2023 SELECT * FROM population_mondiale_1960_2023 WHERE sub_saharan_africa = 'True'"
        }
      },
      {
        "id": "5",
        "name": "PutDatabaseRecord_Asie",
        "type": "org.apache.nifi.processors.standard.PutDatabaseRecord",
        "properties": {
          "Database Connection Pooling Service": "SQLServerPool",
          "Table Name": "population_asie_1960_2023",
          "Statement Type": "INSERT",
          "SQL Query": "INSERT INTO population_asie_1960_2023 SELECT * FROM population_mondiale_1960_2023 WHERE asia_oceania = 'True'"
        }
      }
    ],
    "connections": [
      {"sourceId": "1", "destinationId": "2"},
      {"sourceId": "2", "destinationId": "3"},
      {"sourceId": "3", "destinationId": "4"},
      {"sourceId": "3", "destinationId": "5"}
    ],
    "scheduling": {
      "Run Schedule": "0 0 0 5 1 *"  
    }
  }
}

'''
Instructions pour l'importation :

    Ouvrir NiFi → Aller à "Operate".

    Importer le fichier JSON.

    Configurer la connexion SQL (SQLServerPool).

    Démarrer le pipeline.

'''

### Conception du Data Warehouse

# Nous allons maintenant alimenter les tables par continent (population_afrique, population_asie, etc.) par un script SQL afin de peupler ces tables dans Sql Server.

{
  "flow": {
    "processors": [
      {
        "id": "1",
        "name": "GetFile",
        "type": "org.apache.nifi.processors.standard.GetFile",
        "properties": {
          "Input Directory": "/mnt/data/",
          "File Filter": "population_mondiale.csv",
          "Keep Source File": "false"
        }
      },
      {
        "id": "2",
        "name": "ConvertRecord",
        "type": "org.apache.nifi.processors.standard.ConvertRecord",
        "properties": {
          "Record Reader": "CSVReader",
          "Record Writer": "JsonRecordSetWriter"
        }
      },
      {
        "id": "3",
        "name": "PutDatabaseRecord",
        "type": "org.apache.nifi.processors.standard.PutDatabaseRecord",
        "properties": {
          "Database Connection Pooling Service": "SQLServerPool",
          "Table Name": "population_mondiale_1960_2023",
          "Statement Type": "INSERT"
        }
      },
      {
        "id": "4",
        "name": "PutDatabaseRecord_Afrique",
        "type": "org.apache.nifi.processors.standard.PutDatabaseRecord",
        "properties": {
          "Database Connection Pooling Service": "SQLServerPool",
          "Table Name": "population_afrique_1960_2023",
          "Statement Type": "INSERT",
          "SQL Query": "INSERT INTO population_afrique_1960_2023 SELECT * FROM population_mondiale_1960_2023 WHERE sub_saharan_africa = 'True'"
        }
      },
      {
        "id": "5",
        "name": "PutDatabaseRecord_Asie",
        "type": "org.apache.nifi.processors.standard.PutDatabaseRecord",
        "properties": {
          "Database Connection Pooling Service": "SQLServerPool",
          "Table Name": "population_asie_1960_2023",
          "Statement Type": "INSERT",
          "SQL Query": "INSERT INTO population_asie_1960_2023 SELECT * FROM population_mondiale_1960_2023 WHERE asia_oceania = 'True'"
        }
      }
    ],
    "connections": [
      {"sourceId": "1", "destinationId": "2"},
      {"sourceId": "2", "destinationId": "3"},
      {"sourceId": "3", "destinationId": "4"},
      {"sourceId": "3", "destinationId": "5"}
    ],
    "scheduling": {
      "Run Schedule": "0 0 0 5 1 *"  
    }
  }
}

"""
Voici le script Sql utilisé :

Création des tables par continent dans SQL Server

IF OBJECT_ID('population_afrique_1960_2023', 'U') IS NULL
    SELECT * INTO population_afrique_1960_2023 
    FROM population_mondiale_1960_2023 
    WHERE sub_saharan_africa = 'True';

IF OBJECT_ID('population_asie_1960_2023', 'U') IS NULL
    SELECT * INTO population_asie_1960_2023 
    FROM population_mondiale_1960_2023 
    WHERE asia_oceania = 'True';

IF OBJECT_ID('population_amerique_du_nord_1960_2023', 'U') IS NULL
    SELECT * INTO population_amerique_du_nord_1960_2023 
    FROM population_mondiale_1960_2023 
    WHERE north_america = 'True';

IF OBJECT_ID('population_amerique_du_sud_1960_2023', 'U') IS NULL
    SELECT * INTO population_amerique_du_sud_1960_2023 
    FROM population_mondiale_1960_2023 
    WHERE south_america = 'True';

IF OBJECT_ID('population_europe_1960_2023', 'U') IS NULL
    SELECT * INTO population_europe_1960_2023 
    FROM population_mondiale_1960_2023 
    WHERE europe_central_asia = 'True';

IF OBJECT_ID('population_oceanie_1960_2023', 'U') IS NULL
    SELECT * INTO population_oceanie_1960_2023 
    FROM population_mondiale_1960_2023 
    WHERE asia_oceania = 'True' AND sub_saharan_africa = 'False';

"""

### Reporting et Visualisation des Données via Google Data Studio

'''
-- ============================================
--  SCRIPT COMPLET : ETL + Data Warehouse + Automatisation
-- ============================================
-- Ce script SQL effectue :
-- ✅ Création des tables
-- ✅ Importation et transformation des données
-- ✅ Sécurisation et optimisation
-- ✅ Automatisation et reporting
-- ✅ Exécution complète en un seul fichier

-- ============================================
--  CRÉATION DES TABLES (Data Warehouse)
-- ============================================

-- Table des pays (Dimension)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='dim_country' AND xtype='U')
CREATE TABLE dim_country (
    country_code VARCHAR(10) PRIMARY KEY,
    name_en VARCHAR(255),
    name_fr VARCHAR(255),
    borders NVARCHAR(MAX)
);

--  Table des années (Dimension)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='dim_year' AND xtype='U')
CREATE TABLE dim_year (
    year INT PRIMARY KEY
);

-- Table principale (Faits : population par pays et année)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='population_data' AND xtype='U')
CREATE TABLE population_data (
    country_code VARCHAR(10),
    year INT,
    sub_saharan_africa BIT,
    europe_central_asia BIT,
    east_asia_pacific BIT,
    north_america BIT,
    latin_america_caribbean BIT,
    asia_oceania BIT,
    population FLOAT,
    PRIMARY KEY (country_code, year),
    FOREIGN KEY (country_code) REFERENCES dim_country(country_code),
    FOREIGN KEY (year) REFERENCES dim_year(year)
);

-- Vérification et ajout des colonnes manquantes
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'population_data' AND COLUMN_NAME = 'sub_saharan_africa')
ALTER TABLE population_data ADD sub_saharan_africa BIT;
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'population_data' AND COLUMN_NAME = 'europe_central_asia')
ALTER TABLE population_data ADD europe_central_asia BIT;
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'population_data' AND COLUMN_NAME = 'east_asia_pacific')
ALTER TABLE population_data ADD east_asia_pacific BIT;
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'population_data' AND COLUMN_NAME = 'north_america')
ALTER TABLE population_data ADD north_america BIT;
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'population_data' AND COLUMN_NAME = 'latin_america_caribbean')
ALTER TABLE population_data ADD latin_america_caribbean BIT;
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'population_data' AND COLUMN_NAME = 'asia_oceania')
ALTER TABLE population_data ADD asia_oceania BIT;

-- ============================================
--  INSERTION DES DONNÉES
-- ============================================

--  Ajout des années dans la table dim_year
INSERT INTO dim_year (year)
SELECT year FROM (VALUES 
    (1960), (1961), (1962), (1963), (1964), (1965), (1966), (1967), (1968), (1969),
    (1970), (1971), (1972), (1973), (1974), (1975), (1976), (1977), (1978), (1979),
    (1980), (1981), (1982), (1983), (1984), (1985), (1986), (1987), (1988), (1989),
    (1990), (1991), (1992), (1993), (1994), (1995), (1996), (1997), (1998), (1999),
    (2000), (2001), (2002), (2003), (2004), (2005), (2006), (2007), (2008), (2009),
    (2010), (2011), (2012), (2013), (2014), (2015), (2016), (2017), (2018), (2019),
    (2020), (2021), (2022), (2023)
) AS years(year)
WHERE NOT EXISTS (
    SELECT 1 FROM dim_year dy WHERE dy.year = years.year
);

--  BULK INSERT : Importation des données population
BULK INSERT population_data
FROM 'C:\data\population_mondiale_cleaned.csv'
WITH (
    DATAFILETYPE = 'char',
    FIELDTERMINATOR = ';',
    ROWTERMINATOR = '0x0D0A',
    FIRSTROW = 2
    );
-- ============================================
--  OPTIMISATION DES REQUÊTES
-- ============================================

-- Index pour améliorer la rapidité des requêtes
IF NOT EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_population_country_year')
CREATE INDEX idx_population_country_year ON population_data (country_code, year);
IF NOT EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_population_year')
CREATE INDEX idx_population_year ON population_data (year);
GO

-- ============================================
--  SÉCURISATION DES DONNÉES
-- ============================================

-- Création d'un utilisateur en lecture seule
IF NOT EXISTS (SELECT name FROM sys.sql_logins WHERE name = 'etl_reader')
    CREATE LOGIN etl_reader WITH PASSWORD = 'StrongPassword123!';
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'etl_reader')
    CREATE USER etl_reader FOR LOGIN etl_reader;

-- Création d'un rôle avec accès limité
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'Data_Reader')
    CREATE ROLE Data_Reader;
GRANT SELECT ON population_data TO Data_Reader;
GRANT SELECT ON dim_country TO Data_Reader;
GRANT SELECT ON dim_year TO Data_Reader;
ALTER ROLE Data_Reader ADD MEMBER etl_reader;

-- ============================================
--  AUTOMATISATION AVEC SQL SERVER AGENT
-- ============================================

-- Création d'un job pour l'importation annuelle
-- Vérification du fichier avant BULK INSERT
IF OBJECT_ID('tempdb..#TempFileCheck') IS NOT NULL DROP TABLE #TempFileCheck;
CREATE TABLE #TempFileCheck (FileExists INT, IsDirectory INT, ParentDirectoryExists INT);
INSERT INTO #TempFileCheck EXEC xp_fileexist 'C:\data\population_mondiale_2024.csv';
IF EXISTS (SELECT * FROM #TempFileCheck WHERE FileExists = 1)
BEGIN
    -- Vérification avant d'exécuter BULK INSERT
    PRINT 'Importation des données en cours...';
        BULK INSERT population_data
    FROM 'C:\data\population_mondiale_2024.csv'
    WITH (
    FIELDTERMINATOR = ';',
    ROWTERMINATOR = '0x0D0A',
    FIRSTROW = 2
    );
END

-- Mise à jour des statistiques pour optimiser les performances
EXEC sp_updatestats;
ALTER INDEX ALL ON population_data REBUILD;

'''

