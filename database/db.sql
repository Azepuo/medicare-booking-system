-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : dim. 04 jan. 2026 à 15:08
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `medicare_unified`
--

-- --------------------------------------------------------

--
-- Structure de la table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `admin`
--

INSERT INTO `admin` (`id`, `user_id`, `username`, `photo`, `last_login`) VALUES
(1, 41, 'admin', 'default.png', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `avis`
--

CREATE TABLE `avis` (
  `id` int(11) NOT NULL,
  `patient_id` int(11) DEFAULT NULL,
  `medecin_id` int(11) DEFAULT NULL,
  `rendezvous_id` int(11) DEFAULT NULL,
  `note` int(11) DEFAULT NULL,
  `commentaire` text DEFAULT NULL,
  `date_avis` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `disponibilites`
--

CREATE TABLE `disponibilites` (
  `id` int(11) NOT NULL,
  `medecin_id` int(11) DEFAULT NULL,
  `jour_semaine` varchar(20) DEFAULT NULL,
  `heure_debut` time DEFAULT NULL,
  `heure_fin` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `disponibilites`
--

INSERT INTO `disponibilites` (`id`, `medecin_id`, `jour_semaine`, `heure_debut`, `heure_fin`) VALUES
(2, 1, 'Mercredi', '09:00:00', '17:00:00'),
(3, 10, 'Mercredi', '09:00:00', '17:00:00'),
(4, 10, 'Vendredi', '09:00:00', '17:00:00'),
(5, 11, 'Vendredi', '09:00:00', '17:00:00');

-- --------------------------------------------------------

--
-- Structure de la table `factures`
--

CREATE TABLE `factures` (
  `id` int(11) NOT NULL,
  `rdv_id` int(11) NOT NULL,
  `services` text DEFAULT NULL,
  `date_facture` date NOT NULL DEFAULT curdate(),
  `montant_total` decimal(10,2) DEFAULT 0.00,
  `statut` varchar(20) DEFAULT 'non_payé',
  `moyen_paiement` varchar(50) DEFAULT 'non_defini'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `factures`
--

INSERT INTO `factures` (`id`, `rdv_id`, `services`, `date_facture`, `montant_total`, `statut`, `moyen_paiement`) VALUES
(1, 16, 'Examens de laboratoire:1, Pansement:1', '2025-12-23', 530.00, 'payé', 'especes');

-- --------------------------------------------------------

--
-- Structure de la table `medecins`
--

CREATE TABLE `medecins` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `nom` varchar(150) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `id_specialisation` int(11) DEFAULT NULL,
  `tarif_consultation` decimal(10,2) DEFAULT NULL,
  `statut` enum('Actif','En congé','Inactif') DEFAULT 'Actif',
  `photo_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `clinic` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `medecins`
--

INSERT INTO `medecins` (`id`, `user_id`, `nom`, `email`, `telephone`, `id_specialisation`, `tarif_consultation`, `statut`, `photo_url`, `clinic`) VALUES
(1, 39, 'Dr. Médecin Un', 'medecin1@example.com', '0611111111', 1, 150.00, 'Actif', NULL, NULL),
(2, NULL, 'Dr. Médecin Deux', 'medecin2@example.com', '0611111112', 2, 180.00, 'Actif', NULL, NULL),
(4, NULL, 'Dr Fatima', 'medecin2@clinique.ma', '0622222222', 5, 170.00, 'Actif', NULL, NULL),
(6, NULL, 'yass', 'hhhh@medicare.local', '0612345678', 3, 1677.00, 'Actif', NULL, NULL),
(7, NULL, 'salmani', 'salmani@clinique.ma', '0622222222', 2, 170.00, 'Actif', NULL, NULL),
(10, 38, 'bader', 'yassine@hhh.nn', 'ahmed', 1, NULL, 'Actif', NULL, NULL),
(11, 42, 'hamza', 'hamza@gmail.com', '0622222222', 1, 2000.00, 'Actif', 'zainab_pic.jpeg', 'rahmani');

-- --------------------------------------------------------

--
-- Structure de la table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `titre` varchar(255) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `type` enum('rdv_confirme','rdv_annule','rdv_modifie','rdv_termine','rappel_rdv','demande_avis') DEFAULT NULL,
  `lue` tinyint(1) DEFAULT 0,
  `date_creation` datetime DEFAULT current_timestamp(),
  `date_lecture` datetime DEFAULT NULL,
  `rendezvous_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `notifications`
--

INSERT INTO `notifications` (`id`, `patient_id`, `titre`, `message`, `type`, `lue`, `date_creation`, `date_lecture`, `rendezvous_id`) VALUES
(2, 21, 'Rendez-vous confirmé', 'Votre rendez-vous du 26/12/2025 10:30 est confirmé', 'rdv_confirme', 0, '2025-12-23 21:10:43', NULL, NULL),
(3, 1, 'Rendez-vous confirmé', 'Votre rendez-vous du 26/12/2025 14:00 est confirmé', 'rdv_confirme', 0, '2025-12-23 22:24:39', NULL, 19),
(4, 1, 'Rendez-vous confirmé', 'Votre rendez-vous du 02/01/2026 15:00 est confirmé', 'rdv_confirme', 1, '2025-12-26 19:55:33', '2025-12-26 19:58:32', 20);

-- --------------------------------------------------------

--
-- Structure de la table `patients`
--

CREATE TABLE `patients` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `nom` varchar(150) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `sexe` enum('Homme','Femme') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `patients`
--

INSERT INTO `patients` (`id`, `user_id`, `nom`, `email`, `telephone`, `sexe`) VALUES
(1, 44, 'yassine meskaoui', 'admin@medicare.local', '0612345678', 'Homme'),
(3, NULL, 'Thouriya Rahali', 'thouriyara@gmail.com', '0777889900', 'Femme'),
(4, NULL, 'Sara rr', 'sararr@gmail.com', '0700000000', 'Femme'),
(5, NULL, 'Laila EL Makhlofi', 'lailamakhlofi@gmail.com', '0655443399', 'Femme'),
(6, NULL, 'ikram Ahr', 'ikramahrir@gmail.com', '0666778899', 'Femme'),
(7, NULL, 'Riham User', 'rihamuser@gmail.com', '0600000000', 'Femme'),
(8, NULL, 'user1', 'user1@gmail.com', '0700000000', 'Homme'),
(9, NULL, 'Thouriya Rahali', 'thouriyarah@gmail.com', '0777889900', 'Femme'),
(10, NULL, 'mohamed', 'mehamed@medicare.local', '567890', 'Homme'),
(14, NULL, 'messi', 'messi@gamil.oo', '0612345678', 'Homme'),
(15, NULL, 'tasnim', 'tasnim@bb.com', '67898765', 'Femme'),
(16, NULL, 'tasnimA', 'tasina@gll.nn', '67898765', 'Homme'),
(17, NULL, 'alouli', 'alouli@gkkk.com', '', 'Homme'),
(18, 33, 'kouram', 'kouram@gma.com', '0612345678', 'Homme'),
(19, 39, 'halim', 'yassine@medicare.local', '0600000002', 'Femme'),
(21, 43, 'mohamed', 'mohamde@gg.com', '88888888', 'Femme'),
(22, 45, 'sankohh', 'sankoh@ggg.com', '567890', 'Homme'),
(23, 47, 'hakimi', 'hakimi@hh.co', '88888888', '');

-- --------------------------------------------------------

--
-- Structure de la table `rendezvous`
--

CREATE TABLE `rendezvous` (
  `id` int(11) NOT NULL,
  `date_heure` datetime NOT NULL,
  `patient_id` int(11) NOT NULL,
  `medecin_id` int(11) NOT NULL,
  `statut` enum('En attente','Confirmé','terminé','Annulé') DEFAULT 'En attente',
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `rendezvous`
--

INSERT INTO `rendezvous` (`id`, `date_heure`, `patient_id`, `medecin_id`, `statut`, `notes`) VALUES
(15, '2025-12-23 20:00:00', 18, 10, 'Confirmé', 'koooo'),
(16, '2025-12-23 21:00:00', 19, 11, 'terminé', 'jjjjjjjjjjjjj'),
(18, '2025-12-26 12:30:00', 21, 11, 'Confirmé', 'jjjjjj'),
(19, '2025-12-26 14:00:00', 1, 11, 'Confirmé', 'darni rasii bzaff'),
(20, '2026-01-02 15:00:00', 1, 11, 'Confirmé', 'douleur dans la tete');

--
-- Déclencheurs `rendezvous`
--
DELIMITER $$
CREATE TRIGGER `notification_rdv` AFTER UPDATE ON `rendezvous` FOR EACH ROW BEGIN
  IF NEW.date_heure > NOW() THEN

    IF OLD.statut = 'En attente' AND NEW.statut = 'Confirmé' THEN
      INSERT INTO notifications (patient_id, titre, message, type, rendezvous_id)
      VALUES (
        NEW.patient_id,
        'Rendez-vous confirmé',
        CONCAT('Votre rendez-vous du ',
               DATE_FORMAT(NEW.date_heure,'%d/%m/%Y %H:%i'),
               ' est confirmé'),
        'rdv_confirme',
        NEW.id
      );
    END IF;

    IF NEW.statut = 'Annulé' AND OLD.statut <> 'Annulé' THEN
      INSERT INTO notifications (patient_id, titre, message, type, rendezvous_id)
      VALUES (
        NEW.patient_id,
        'Rendez-vous annulé',
        CONCAT('Votre rendez-vous du ',
               DATE_FORMAT(NEW.date_heure,'%d/%m/%Y %H:%i'),
               ' est annulé'),
        'rdv_annule',
        NEW.id
      );
    END IF;

  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Structure de la table `services`
--

CREATE TABLE `services` (
  `id` int(11) NOT NULL,
  `nom_service` varchar(100) DEFAULT NULL,
  `prix_unitaire` decimal(10,2) DEFAULT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `services`
--

INSERT INTO `services` (`id`, `nom_service`, `prix_unitaire`, `description`) VALUES
(1, 'Consultation', 350.00, 'Consultation médicale générale'),
(2, 'Examens de laboratoire', 450.00, 'Analyses en laboratoire'),
(3, 'Radiologie', 600.00, 'Imagerie médicale'),
(4, 'Échographie', 500.00, 'Ultrasons'),
(5, 'Injection', 120.00, 'Injection'),
(6, 'Pansement', 80.00, 'Soin'),
(7, 'Scanner', 1200.00, 'Scanner médical'),
(8, 'IRM', 1500.00, 'IRM');

-- --------------------------------------------------------

--
-- Structure de la table `specialisations`
--

CREATE TABLE `specialisations` (
  `id` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `specialisations`
--

INSERT INTO `specialisations` (`id`, `nom`, `description`) VALUES
(1, 'Médecine générale', 'Consultation générale et suivi médical'),
(2, 'Cardiologie', 'Maladies du cœur et du système cardiovasculaire'),
(3, 'Dermatologie', 'Maladies de la peau'),
(4, 'Pédiatrie', 'Soins médicaux pour enfants'),
(5, 'Gynécologie', 'Santé reproductive de la femme');

-- --------------------------------------------------------

--
-- Structure de la table `specialites`
--

CREATE TABLE `specialites` (
  `id` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `specialites`
--

INSERT INTO `specialites` (`id`, `nom`, `description`) VALUES
(1, 'Médecine générale', 'Consultation générale et suivi médical'),
(2, 'Cardiologie', 'Maladies du cœur et du système cardiovasculaire'),
(3, 'Dermatologie', 'Maladies de la peau'),
(4, 'Pédiatrie', 'Soins médicaux pour enfants'),
(5, 'Gynécologie', 'Santé reproductive de la femme');

-- --------------------------------------------------------

--
-- Structure de la table `statistiques`
--

CREATE TABLE `statistiques` (
  `id` int(11) NOT NULL,
  `medecin_id` int(11) DEFAULT NULL,
  `total_rdv` int(11) DEFAULT 0,
  `total_patients` int(11) DEFAULT 0,
  `total_avis` int(11) DEFAULT 0,
  `moyenne_notes` float DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `taches`
--

CREATE TABLE `taches` (
  `id` int(11) NOT NULL,
  `titre` varchar(255) DEFAULT NULL,
  `statut` enum('complétée','non_complétée') DEFAULT NULL,
  `date_creation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `taches`
--

INSERT INTO `taches` (`id`, `titre`, `statut`, `date_creation`) VALUES
(1, 'NOODOD', 'complétée', '2025-12-23 23:36:23');

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `nom` varchar(150) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('ADMIN','MEDECIN','PATIENT') NOT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `nom`, `email`, `password`, `role`, `telephone`, `created_at`) VALUES
(33, 'kouramn', 'kouram@gma.com', '$2b$12$cfJgdkflMf80t5fcKTaHq.wEHoMEw9iLbtTH2c5KiUKAJzXq19Qu6', 'PATIENT', '0612345678', '2025-12-20 13:13:36'),
(34, 'halim', 'halim@cc.hh', '$2b$12$lnGGUuY3xYqFhTjfWLAxReLasCIhj6EZZ4zel0EBrKoWNUDfILrX.', 'PATIENT', '0600000002', '2025-12-20 13:44:24'),
(35, 'medcinyasisn', 'medcinyasisn@hhh.cc', '$2b$12$1bnlxAIzFXTJzxCSQQ3myuLtY8KK4SVT6IJJXGowcQ98HMOMw0dUG', 'MEDECIN', '0622222222', '2025-12-20 13:48:42'),
(36, 'anass', 'anssanbbbiba@admin.mm', '$2b$12$ZsoYICSlgbwr.aUP4LOAmecPmxY8e.PmzOadLI6C/WfOBXkySmlbK', 'PATIENT', '567890', '2025-12-20 14:34:14'),
(37, 'hassna', 'hasssna@gal.com', '$2b$12$a6pnxtTxi3tQ1J5ARW4nc./O4WT1fHDh1CeR1TTvV/OJaghkyhX1C', 'ADMIN', '098765456', '2025-12-20 15:26:57'),
(38, 'aboudo', 'yassine@hhh.nn', 'scrypt:32768:8:1$ybik69iYYWRygXZp$ff6cf8514b64809ea0c1e0b20e9440a4225097ad0fb945724010e47e64881b6229cf18c3f47545b1550aac44c2630618683149fefadcca8050d7e2928439dbcf', 'MEDECIN', 'ahmedK', '2025-12-23 10:54:44'),
(39, 'yassine', 'yassine@medicare.local', 'scrypt:32768:8:1$u0DYHKXGIczuWhha$8548e3da440fbcf094c40d1a17a704f1bfc7562c3431b3db9aeb210b16af4c01bc0f144643b80986c5d1a8d1a057ccab67c760f03f23dab6f32dc8bf21e624f1', 'MEDECIN', '678975', '2025-12-23 11:40:28'),
(41, 'mouad', 'mouad@gmail.admin', '$2b$12$g.D/EOqCtNnFblSTDR6puOynD9mXlz5BA/Ox4gQScm6dxmIgJjxAy', 'ADMIN', '66666', '2025-12-23 20:36:57'),
(42, 'hamza', 'hamza@gmail.com', '$2b$12$ee8iLDnuGrsUGukrAcnmUew56ySRaPOWUFXLiWL.7xmIxVnRyg/UO', 'MEDECIN', '062222222', '2025-12-23 20:39:45'),
(43, 'nasima', 'nasima@kk.cc', 'scrypt:32768:8:1$h9H1mqve1lwPyu9f$d850d040047da1032e1d793676ec7d4016e92153394ebc987dd1cc833621853b7d367ea1056112e507e8541829f74429ff02d1e22c7086c75fafec200248cc90', 'PATIENT', '567890', '2025-12-23 21:05:09'),
(44, 'mohamed', 'mohamde@gg.com', '$2b$12$ee8iLDnuGrsUGukrAcnmUew56ySRaPOWUFXLiWL.7xmIxVnRyg/UO', 'PATIENT', '88888888', '2025-12-23 21:55:05'),
(45, 'sankohh', 'sankoh@ggg.com', '$2b$12$5/hVVwmD0oWuUClQ5kuI/eSJvZ3MHMRcXuQhCjMuI431GLrx8rXbO', 'PATIENT', '567890', '2025-12-23 23:24:40'),
(46, 'kamilya', 'hhh@gmail.com', '$2b$12$jGRMCJQtXYtvjSmkFmh0T.1.a6EDrewYr/miihgEFFDJ23jNQCYji', 'PATIENT', '88888888', '2025-12-26 20:16:30'),
(47, 'hakimi', 'hakimi@hh.co', '$2b$12$S2pIGzCtUOh2Cuk4jU7qJuPdkvc4YHzPG7qh2H4aWAF/VzUtV9nne', 'PATIENT', '88888888', '2025-12-26 20:28:57');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Index pour la table `avis`
--
ALTER TABLE `avis`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `medecin_id` (`medecin_id`),
  ADD KEY `rendezvous_id` (`rendezvous_id`);

--
-- Index pour la table `disponibilites`
--
ALTER TABLE `disponibilites`
  ADD PRIMARY KEY (`id`),
  ADD KEY `medecin_id` (`medecin_id`);

--
-- Index pour la table `factures`
--
ALTER TABLE `factures`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_factures_rdv` (`rdv_id`);

--
-- Index pour la table `medecins`
--
ALTER TABLE `medecins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `id_specialisation` (`id_specialisation`);

--
-- Index pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `rendezvous_id` (`rendezvous_id`);

--
-- Index pour la table `patients`
--
ALTER TABLE `patients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Index pour la table `rendezvous`
--
ALTER TABLE `rendezvous`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_medecin_date` (`medecin_id`,`date_heure`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Index pour la table `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `specialisations`
--
ALTER TABLE `specialisations`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nom` (`nom`);

--
-- Index pour la table `specialites`
--
ALTER TABLE `specialites`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nom` (`nom`);

--
-- Index pour la table `statistiques`
--
ALTER TABLE `statistiques`
  ADD PRIMARY KEY (`id`),
  ADD KEY `medecin_id` (`medecin_id`);

--
-- Index pour la table `taches`
--
ALTER TABLE `taches`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `avis`
--
ALTER TABLE `avis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `disponibilites`
--
ALTER TABLE `disponibilites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `factures`
--
ALTER TABLE `factures`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `medecins`
--
ALTER TABLE `medecins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT pour la table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `patients`
--
ALTER TABLE `patients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT pour la table `rendezvous`
--
ALTER TABLE `rendezvous`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT pour la table `services`
--
ALTER TABLE `services`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT pour la table `specialisations`
--
ALTER TABLE `specialisations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `specialites`
--
ALTER TABLE `specialites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `statistiques`
--
ALTER TABLE `statistiques`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `taches`
--
ALTER TABLE `taches`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=48;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `admin`
--
ALTER TABLE `admin`
  ADD CONSTRAINT `fk_admin_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `avis`
--
ALTER TABLE `avis`
  ADD CONSTRAINT `avis_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `avis_ibfk_2` FOREIGN KEY (`medecin_id`) REFERENCES `medecins` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `avis_ibfk_3` FOREIGN KEY (`rendezvous_id`) REFERENCES `rendezvous` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `disponibilites`
--
ALTER TABLE `disponibilites`
  ADD CONSTRAINT `disponibilites_ibfk_1` FOREIGN KEY (`medecin_id`) REFERENCES `medecins` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `factures`
--
ALTER TABLE `factures`
  ADD CONSTRAINT `fk_factures_rdv` FOREIGN KEY (`rdv_id`) REFERENCES `rendezvous` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `medecins`
--
ALTER TABLE `medecins`
  ADD CONSTRAINT `medecins_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `medecins_ibfk_2` FOREIGN KEY (`id_specialisation`) REFERENCES `specialisations` (`id`);

--
-- Contraintes pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`rendezvous_id`) REFERENCES `rendezvous` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `patients`
--
ALTER TABLE `patients`
  ADD CONSTRAINT `patients_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `rendezvous`
--
ALTER TABLE `rendezvous`
  ADD CONSTRAINT `rendezvous_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `rendezvous_ibfk_2` FOREIGN KEY (`medecin_id`) REFERENCES `medecins` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `statistiques`
--
ALTER TABLE `statistiques`
  ADD CONSTRAINT `statistiques_ibfk_1` FOREIGN KEY (`medecin_id`) REFERENCES `medecins` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
