-- ¡IMPORTANTE!
-- Este script debe correse junto con el docker compose ya solo será reconocido una vez.
-- En caso de activar el docker compose antes de tener el sql-init, este deberá ejecutarse-
-- directamente en la terminal 


-- BASE DE DATOS --
CREATE DATABASE IF NOT EXISTS homicidios_db;
USE homicidios_db;

-- CREACIÓN Y GESTIÓN DE USUARIOS -- 
CREATE USER IF NOT EXISTS 'Rai'@'%' IDENTIFIED BY 'hom123';
GRANT ALL PRIVILEGES ON homicidios_db.* TO 'Rai'@'%';
FLUSH PRIVILEGES;

-- Usuario para Juan Camilo Zuluaga --
CREATE USER IF NOT EXISTS 'analista1'@'%' IDENTIFIED BY 'analista1pass';
GRANT SELECT, INSERT, UPDATE, DELETE ON homicidios_db.* TO 'analista1'@'%';

-- Usuario para Wilfredo Martinez -- 
CREATE USER IF NOT EXISTS 'analista2'@'%' IDENTIFIED BY 'analista2pass';
GRANT SELECT ON homicidios_db.* TO 'analista2'@'%';
FLUSH PRIVILEGES;

-- CREATE DTABASE  (Data Lake)
CREATE TABLE IF NOT EXISTS raw_homicidios (
  id_hecho BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  fecha_hecho DATE NOT NULL,
  cod_depto VARCHAR(6) NOT NULL,
  departamento VARCHAR(200),
  cod_muni VARCHAR(8) NOT NULL,
  municipio VARCHAR(200),
  zona VARCHAR(20),
  sexo VARCHAR(20),
  cantidad INT NOT NULL,
  fuente VARCHAR(200),
  fecha_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_raw_uniq (fecha_hecho, cod_depto, cod_muni, zona, sexo, fuente)
) ENGINE=InnoDB;

-- Tablas DIVIPOLA (estáticas)
CREATE TABLE IF NOT EXISTS dim_departamentos (
  cod_depto VARCHAR(6) PRIMARY KEY,
  nombre_depto VARCHAR(200),
  geom POINT NULL,
  lat DOUBLE NULL,
  lon DOUBLE NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_municipios (
  cod_muni VARCHAR(8) PRIMARY KEY,
  cod_depto VARCHAR(6),
  nombre_muni VARCHAR(200),
  lat DOUBLE NULL,
  lon DOUBLE NULL,
  zona_urbana_rural ENUM('URBANA','RURAL','MIXTA') DEFAULT 'MIXTA',
  FOREIGN KEY (cod_depto) REFERENCES dim_departamentos(cod_depto)
) ENGINE=InnoDB;

-- Tabla de control / metadatos para cargas incrementales
CREATE TABLE IF NOT EXISTS etl_control (
  id INT AUTO_INCREMENT PRIMARY KEY,
  proceso VARCHAR(100) UNIQUE,
  last_loaded_date DATE,
  last_loaded_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  notas TEXT
) ENGINE=InnoDB;