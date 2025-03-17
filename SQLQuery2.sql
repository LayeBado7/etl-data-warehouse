-- 📌 Création des tables par continent dans SQL Server

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
