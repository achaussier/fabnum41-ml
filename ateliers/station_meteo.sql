-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost:3306
-- Généré le : lun. 23 nov. 2026 à 08:52
-- Version du serveur : 8.4.3
-- Version de PHP : 8.4.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `station_meteo`
--

-- --------------------------------------------------------

--
-- Structure de la table `alerte`
--

CREATE TABLE `alerte` (
  `ID_ALERTE` int NOT NULL,
  `VALEUR_DECLENCHANTE` decimal(6,2) NOT NULL,
  `VALEUR_SEUIL_APPLIQUEE` decimal(6,2) NOT NULL,
  `DATE_DECLENCHEMENT` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ETAT_ALERTE` varchar(50) NOT NULL DEFAULT 'DECLENCHEE',
  `DATE_NOTIFICATION` datetime DEFAULT NULL,
  `DATE_ACQUITTEMENT` datetime DEFAULT NULL,
  `DATE_CLOTURE` datetime DEFAULT NULL,
  `ID_SEUIL` int NOT NULL,
  `ID_UTILISATEUR_ACQUITTEMENT` int DEFAULT NULL
) ;

-- --------------------------------------------------------

--
-- Structure de la table `anomalie`
--

CREATE TABLE `anomalie` (
  `ID_ANOMALIE` int NOT NULL,
  `INSTANT_MESURE_ANORMALE` datetime NOT NULL,
  `VALEUR_MESUREE` decimal(9,2) NOT NULL,
  `SCORE_ANOMALIE` decimal(6,2) NOT NULL,
  `DATE_DETECTION` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `CODE_GRANDEUR` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Structure de la table `destinataire`
--

CREATE TABLE `destinataire` (
  `ID_DESTINATAIRE` int NOT NULL,
  `EMAIL_DESTINATAIRE` varchar(255) NOT NULL,
  `RECOIT_EMAIL_QUOTIDIEN` tinyint(1) NOT NULL DEFAULT '1',
  `RECOIT_ALERTES` tinyint(1) NOT NULL DEFAULT '1',
  `DESTINATAIRE_ACTIF` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Structure de la table `grandeur`
--

CREATE TABLE `grandeur` (
  `CODE_GRANDEUR` varchar(30) NOT NULL,
  `LIBELLE_GRANDEUR` varchar(50) NOT NULL,
  `UNITE_GRANDEUR` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Structure de la table `historique_seuil`
--

CREATE TABLE `historique_seuil` (
  `ID_HISTORIQUE` int NOT NULL,
  `ANCIENNE_VALEUR` decimal(6,2) DEFAULT NULL,
  `NOUVELLE_VALEUR` decimal(6,2) NOT NULL,
  `DATE_MODIFICATION_SEUIL` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ID_SEUIL` int NOT NULL,
  `ID_UTILISATEUR` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Structure de la table `resultat_ia`
--

CREATE TABLE `resultat_ia` (
  `ID_RESULTAT` int NOT NULL,
  `TYPE_RESULTAT` varchar(50) NOT NULL,
  `CONTENU_RESUME` text,
  `VALEUR_PREVUE` decimal(9,2) DEFAULT NULL,
  `INCERTITUDE` decimal(9,2) DEFAULT NULL,
  `INSTANT_PREVU` datetime DEFAULT NULL,
  `DATE_GENERATION` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `CODE_GRANDEUR` varchar(30) DEFAULT NULL
) ;

-- --------------------------------------------------------

--
-- Structure de la table `seuil`
--

CREATE TABLE `seuil` (
  `ID_SEUIL` int NOT NULL,
  `TYPE_ALERTE` varchar(50) NOT NULL,
  `OPERATEUR` varchar(10) NOT NULL,
  `VALEUR_SEUIL` decimal(6,2) NOT NULL,
  `SEUIL_ACTIF` tinyint(1) NOT NULL DEFAULT '1',
  `CODE_GRANDEUR` varchar(30) NOT NULL
) ;

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

CREATE TABLE `utilisateur` (
  `ID_UTILISATEUR` int NOT NULL,
  `NOM_UTILISATEUR` varchar(50) NOT NULL,
  `PRENOM_UTILISATEUR` varchar(50) NOT NULL,
  `EMAIL_UTILISATEUR` varchar(255) NOT NULL,
  `MOT_DE_PASSE_HASH` varchar(255) NOT NULL,
  `ROLE` varchar(50) NOT NULL,
  `COMPTE_ACTIF` tinyint(1) NOT NULL DEFAULT '1',
  `TOKEN_RESET_HASH` varchar(64) DEFAULT NULL,
  `TOKEN_RESET_EXPIRATION` datetime DEFAULT NULL,
  `DATE_CREATION_COMPTE` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `alerte`
--
ALTER TABLE `alerte`
  ADD PRIMARY KEY (`ID_ALERTE`),
  ADD KEY `ID_SEUIL` (`ID_SEUIL`),
  ADD KEY `ID_UTILISATEUR_ACQUITTEMENT` (`ID_UTILISATEUR_ACQUITTEMENT`);

--
-- Index pour la table `anomalie`
--
ALTER TABLE `anomalie`
  ADD PRIMARY KEY (`ID_ANOMALIE`),
  ADD UNIQUE KEY `CODE_GRANDEUR` (`CODE_GRANDEUR`,`INSTANT_MESURE_ANORMALE`);

--
-- Index pour la table `destinataire`
--
ALTER TABLE `destinataire`
  ADD PRIMARY KEY (`ID_DESTINATAIRE`),
  ADD UNIQUE KEY `EMAIL_DESTINATAIRE` (`EMAIL_DESTINATAIRE`);

--
-- Index pour la table `grandeur`
--
ALTER TABLE `grandeur`
  ADD PRIMARY KEY (`CODE_GRANDEUR`);

--
-- Index pour la table `historique_seuil`
--
ALTER TABLE `historique_seuil`
  ADD PRIMARY KEY (`ID_HISTORIQUE`),
  ADD KEY `ID_SEUIL` (`ID_SEUIL`),
  ADD KEY `ID_UTILISATEUR` (`ID_UTILISATEUR`);

--
-- Index pour la table `resultat_ia`
--
ALTER TABLE `resultat_ia`
  ADD PRIMARY KEY (`ID_RESULTAT`),
  ADD KEY `CODE_GRANDEUR` (`CODE_GRANDEUR`);

--
-- Index pour la table `seuil`
--
ALTER TABLE `seuil`
  ADD PRIMARY KEY (`ID_SEUIL`),
  ADD UNIQUE KEY `TYPE_ALERTE` (`TYPE_ALERTE`),
  ADD KEY `CODE_GRANDEUR` (`CODE_GRANDEUR`);

--
-- Index pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  ADD PRIMARY KEY (`ID_UTILISATEUR`),
  ADD UNIQUE KEY `EMAIL_UTILISATEUR` (`EMAIL_UTILISATEUR`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `alerte`
--
ALTER TABLE `alerte`
  MODIFY `ID_ALERTE` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `anomalie`
--
ALTER TABLE `anomalie`
  MODIFY `ID_ANOMALIE` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `destinataire`
--
ALTER TABLE `destinataire`
  MODIFY `ID_DESTINATAIRE` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `historique_seuil`
--
ALTER TABLE `historique_seuil`
  MODIFY `ID_HISTORIQUE` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `resultat_ia`
--
ALTER TABLE `resultat_ia`
  MODIFY `ID_RESULTAT` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `seuil`
--
ALTER TABLE `seuil`
  MODIFY `ID_SEUIL` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  MODIFY `ID_UTILISATEUR` int NOT NULL AUTO_INCREMENT;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `alerte`
--
ALTER TABLE `alerte`
  ADD CONSTRAINT `alerte_ibfk_1` FOREIGN KEY (`ID_SEUIL`) REFERENCES `seuil` (`ID_SEUIL`),
  ADD CONSTRAINT `alerte_ibfk_2` FOREIGN KEY (`ID_UTILISATEUR_ACQUITTEMENT`) REFERENCES `utilisateur` (`ID_UTILISATEUR`);

--
-- Contraintes pour la table `anomalie`
--
ALTER TABLE `anomalie`
  ADD CONSTRAINT `anomalie_ibfk_1` FOREIGN KEY (`CODE_GRANDEUR`) REFERENCES `grandeur` (`CODE_GRANDEUR`);

--
-- Contraintes pour la table `historique_seuil`
--
ALTER TABLE `historique_seuil`
  ADD CONSTRAINT `historique_seuil_ibfk_1` FOREIGN KEY (`ID_SEUIL`) REFERENCES `seuil` (`ID_SEUIL`),
  ADD CONSTRAINT `historique_seuil_ibfk_2` FOREIGN KEY (`ID_UTILISATEUR`) REFERENCES `utilisateur` (`ID_UTILISATEUR`);

--
-- Contraintes pour la table `resultat_ia`
--
ALTER TABLE `resultat_ia`
  ADD CONSTRAINT `resultat_ia_ibfk_1` FOREIGN KEY (`CODE_GRANDEUR`) REFERENCES `grandeur` (`CODE_GRANDEUR`);

--
-- Contraintes pour la table `seuil`
--
ALTER TABLE `seuil`
  ADD CONSTRAINT `seuil_ibfk_1` FOREIGN KEY (`CODE_GRANDEUR`) REFERENCES `grandeur` (`CODE_GRANDEUR`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
