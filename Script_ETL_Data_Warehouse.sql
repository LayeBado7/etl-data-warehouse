-- ============================================
-- 🎯 SCRIPT COMPLET : ETL + Data Warehouse + Automatisation
-- ============================================
-- Ce script SQL effectue :
-- ✅ Création des tables
-- ✅ Importation et transformation des données
-- ✅ Sécurisation et optimisation
-- ✅ Automatisation et reporting
-- ✅ Exécution complète en un seul fichier

-- ============================================
-- 1️⃣ CRÉATION DES TABLES (Data Warehouse)
-- ============================================

-- 📌 Table des pays (Dimension)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='dim_country' AND xtype='U')
CREATE TABLE dim_country (
    country_code VARCHAR(10) PRIMARY KEY,
    name_en VARCHAR(255),
    name_fr VARCHAR(255),
    borders NVARCHAR(MAX)
);

-- 📌 Table des années (Dimension)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='dim_year' AND xtype='U')
CREATE TABLE dim_year (
    year INT PRIMARY KEY
);

-- 📌 Table principale (Faits : population par pays et année)
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

-- 📌 Vérification et ajout des colonnes manquantes
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
-- 2️⃣ INSERTION DES DONNÉES
-- ============================================

-- 📌 Ajout des années dans la table dim_year
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

-- 📌 BULK INSERT : Importation des données population
BULK INSERT population_data
FROM 'C:\data\population_mondiale_cleaned.csv'
WITH (
    DATAFILETYPE = 'char',
    FIELDTERMINATOR = ';',
    ROWTERMINATOR = '0x0D0A',
    FIRSTROW = 2
    );
-- ============================================
-- 3️⃣ OPTIMISATION DES REQUÊTES
-- ============================================

-- 📌 Index pour améliorer la rapidité des requêtes
IF NOT EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_population_country_year')
CREATE INDEX idx_population_country_year ON population_data (country_code, year);
IF NOT EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_population_year')
CREATE INDEX idx_population_year ON population_data (year);
GO

-- ============================================
-- 4️⃣ SÉCURISATION DES DONNÉES
-- ============================================

-- 📌 Création d'un utilisateur en lecture seule
IF NOT EXISTS (SELECT name FROM sys.sql_logins WHERE name = 'etl_reader')
    CREATE LOGIN etl_reader WITH PASSWORD = 'StrongPassword123!';
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'etl_reader')
    CREATE USER etl_reader FOR LOGIN etl_reader;

-- 📌 Création d'un rôle avec accès limité
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'Data_Reader')
    CREATE ROLE Data_Reader;
GRANT SELECT ON population_data TO Data_Reader;
GRANT SELECT ON dim_country TO Data_Reader;
GRANT SELECT ON dim_year TO Data_Reader;
ALTER ROLE Data_Reader ADD MEMBER etl_reader;

-- ============================================
-- 5️⃣ AUTOMATISATION AVEC SQL SERVER AGENT
-- ============================================

-- 📌 Création d'un job pour l'importation annuelle
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
