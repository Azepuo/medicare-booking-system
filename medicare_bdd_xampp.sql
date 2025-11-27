CREATE DATABASE IF NOT EXISTS medicare
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE medicare;

-- ================== TABLE admin ==================
DROP TABLE IF EXISTS admin;
CREATE TABLE admin (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom_complet VARCHAR(150) NOT NULL,
  email VARCHAR(100) NOT NULL,
  telephone VARCHAR(30),
  username VARCHAR(50) NOT NULL,
  password VARCHAR(255) NOT NULL,
  date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME,
  photo VARCHAR(255)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO admin VALUES 
(1,'Zainab ERROSSAFI','Zainab@example.com','060088888888888','Zainab IIIII','$2b$12$0gKMrHjtivgEx/RgARNjyecE85Yu4jtOgbLO9vY78AApKr3i.VH86','2025-11-23 20:10:57',NULL,'zainab_pic.jpeg');

-- ================== TABLE medecins ==================
DROP TABLE IF EXISTS medecins;
CREATE TABLE medecins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(150) NOT NULL,
  specialite VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  telephone VARCHAR(20),
  annees_experience INT,
  tarif_consultation DECIMAL(10,2),
  description TEXT,
  statut ENUM('Actif','En congé','Inactif') DEFAULT 'Actif',
  date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO medecins VALUES
(11,'amine','cardio','amine@gmail.com','888888888888',8,600.00,'iiiiiiiiiiiiiiiiiiiii','Actif','2025-11-22 18:04:36'),
(12,'oussama','pediatre','oussama@gmail.com','5555555',3,300.00,'ooooooooooooooooooooo','Actif','2025-11-22 21:33:29'),
(13,'ayoub','generaliste','ayoub@gmail.com','999999',4,400.00,'Generaliste ','Actif','2025-11-25 22:23:53');

-- ================== TABLE patients ==================
DROP TABLE IF EXISTS patients;
CREATE TABLE patients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(150) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  telephone VARCHAR(20),
  cin VARCHAR(20) UNIQUE,
  date_naissance DATE,
  sexe ENUM('Homme','Femme') NOT NULL,
  date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO patients VALUES
(8,'amine','BDSHA@gmail.com','9876','M01789','2002-04-05','Femme','2025-11-22 17:46:48'),
(9,'salma','salma@gmail.com','098765','999','2009-06-08','Homme','2025-11-22 19:13:06'),
(10,'wiwi','wiwi@gmail.com','2222222222222','888','2007-02-21','Femme','2025-11-22 21:38:15');

-- ================== TABLE rendezvous ==================
DROP TABLE IF EXISTS rendezvous;
CREATE TABLE rendezvous (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT,
  medecin_id INT,
  date_rdv DATE NOT NULL,
  heure_rdv TIME NOT NULL,
  statut ENUM('en_attente','terminé','annulé') DEFAULT 'en_attente',
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY(medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO rendezvous VALUES
(1,NULL,NULL,'2025-10-22','10:00:00','terminé',NULL,'2025-11-22 15:06:57'),
(13,8,11,'2025-11-25','10:00:00','terminé','zainab','2025-11-22 19:14:12'),
(16,9,11,'2025-11-25','09:09:00','terminé','uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuugggggg','2025-11-22 21:45:22'),
(17,9,12,'2025-11-24','21:00:00','en_attente','','2025-11-24 18:07:29'),
(18,10,12,'2025-11-24','20:00:00','en_attente','','2025-11-24 18:34:47'),
(19,8,12,'2025-11-26','10:00:00','en_attente','','2025-11-25 22:50:18');

-- ================== TABLE disponibilites_medecin ==================
DROP TABLE IF EXISTS disponibilites_medecin;
CREATE TABLE disponibilites_medecin (
  id INT AUTO_INCREMENT PRIMARY KEY,
  medecin_id INT NOT NULL,
  date_disponible DATE NOT NULL,
  heure_debut TIME,
  heure_fin TIME,
  disponible TINYINT(1) DEFAULT 1,
  FOREIGN KEY(medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO disponibilites_medecin VALUES
(10,11,'2025-11-25','08:00:00','12:00:00',1),
(17,12,'2025-11-26','08:00:00','21:00:00',1),
(18,12,'2025-12-01','09:00:00','22:00:00',1),
(19,12,'2025-12-02','10:00:00','00:00:00',1),
(20,12,'2025-11-24','08:00:00','23:00:00',1),
(21,11,'2025-11-24','08:00:00','00:00:00',1);

-- ================== TABLE factures ==================
DROP TABLE IF EXISTS factures;
CREATE TABLE factures (
  id INT AUTO_INCREMENT PRIMARY KEY,
  rdv_id INT NOT NULL,
  services TEXT,
  date_facture DATE DEFAULT (CURDATE()),
  montant_total DECIMAL(10,2) DEFAULT 0.00,
  statut VARCHAR(20) DEFAULT 'non_payé',
  moyen_paiement VARCHAR(50) DEFAULT 'non_defini',
  FOREIGN KEY(rdv_id) REFERENCES rendezvous(id) ON DELETE CASCADE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO factures VALUES
(15,16,'Consultation:1, Injection:1','2025-11-25',720.00,'non_payé','especes');

-- ================== TABLE services ==================
DROP TABLE IF EXISTS services;
CREATE TABLE services (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom_service VARCHAR(100) NOT NULL,
  prix_unitaire DECIMAL(10,2) NOT NULL,
  description TEXT
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO services VALUES
(1,'Consultation',350.00,'Consultation médicale générale'),
(2,'Examens de laboratoire',450.00,'Analyses et tests en laboratoire'),
(3,'Radiologie',600.00,'Imagerie médicale par rayons X'),
(4,'Échographie',500.00,'Imagerie par ultrasons'),
(5,'Injection',120.00,'Injection médicamenteuse'),
(6,'Pansement',80.00,'Soin et pansement'),
(7,'Scanner',1200.00,'Scanner médical'),
(8,'IRM',1500.00,'Imagerie par résonance magnétique');

-- ================== TABLE specialites ==================
DROP TABLE IF EXISTS specialites;
CREATE TABLE specialites (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(100) NOT NULL UNIQUE,
  description TEXT
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ================== TABLE taches ==================
DROP TABLE IF EXISTS taches;
CREATE TABLE taches (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titre VARCHAR(255) NOT NULL,
  statut ENUM('complétée','non_complétée') DEFAULT 'non_complétée',
  date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO taches VALUES
(1,'Verifier les conges','complétée','2025-11-24 16:42:02'),
(5,'hhhhhh','non_complétée','2025-11-24 19:42:45');
