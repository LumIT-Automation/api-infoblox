-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Creato il: Ott 25, 2021 alle 08:14
-- Versione del server: 10.3.31-MariaDB-0+deb10u1-log
-- Versione PHP: 7.3.29-1~deb10u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `api`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `asset`
--

CREATE TABLE `asset` (
  `id` int(11) NOT NULL,
  `address` varchar(64) NOT NULL,
  `fqdn` varchar(255) DEFAULT NULL,
  `baseurl` varchar(255) NOT NULL,
  `tlsverify` tinyint(4) NOT NULL DEFAULT 1,
  `datacenter` varchar(255) DEFAULT NULL,
  `environment` varchar(255) NOT NULL,
  `position` varchar(255) DEFAULT NULL,
  `username` varchar(64) NOT NULL DEFAULT '',
  `password` varchar(64) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `trigger_data`
--

CREATE TABLE `trigger_data` (
  `id` int(11) NOT NULL,
  `trigger_name` varchar(64) NOT NULL,
  `src_asset_id` int(11) DEFAULT NULL,
  `dst_asset_id` int(11) DEFAULT NULL,
  `trigger_condition` varchar(255) NOT NULL,
  `enabled` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `group_role_network`
--

CREATE TABLE `group_role_network` (
  `id` int(255) NOT NULL,
  `id_group` int(11) NOT NULL,
  `id_role` int(11) NOT NULL,
  `id_network` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `identity_group`
--

CREATE TABLE `identity_group` (
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `identity_group_identifier` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `log`
--

CREATE TABLE `log` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `action` varchar(2048) NOT NULL,
  `asset_id` int(11) NOT NULL,
  `object_id` int(11) NOT NULL,
  `status` enum('created','modified','deleted') NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `log_object`
--

CREATE TABLE `log_object` (
  `id` int(11) NOT NULL,
  `type` enum('ipv4','network','') DEFAULT NULL,
  `address` varchar(15) DEFAULT NULL,
  `network` varchar(18) DEFAULT NULL,
  `mask` varchar(15) DEFAULT NULL,
  `gateway` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `log_request`
--

CREATE TABLE `log_request` (
  `id` int(11) NOT NULL,
  `asset_id` int(11) DEFAULT NULL,
  `action` varchar(255) NOT NULL,
  `response_status` int(11) NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp(),
  `username` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `migrations`
--

CREATE TABLE `migrations` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `network`
--

CREATE TABLE `network` (
  `id` int(11) NOT NULL,
  `id_asset` int(11) NOT NULL,
  `network` varchar(64) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `privilege`
--

CREATE TABLE `privilege` (
  `id` int(11) NOT NULL,
  `privilege` varchar(64) NOT NULL,
  `privilege_type` enum('object','asset','global') NOT NULL DEFAULT 'object',
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `role`
--

CREATE TABLE `role` (
  `id` int(11) NOT NULL,
  `role` varchar(64) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `role_privilege`
--

CREATE TABLE `role_privilege` (
  `id_role` int(11) NOT NULL,
  `id_privilege` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `asset`
--
ALTER TABLE `asset`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `address` (`address`);


-- Indici per le tabelle `trigger_data`
--
ALTER TABLE `trigger_data`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `group_role_network`
--
ALTER TABLE `group_role_network`
  ADD PRIMARY KEY (`id_group`,`id_role`,`id_network`),
  ADD KEY `id_role` (`id_role`),
  ADD KEY `grp_network` (`id_network`),
  ADD KEY `id` (`id`);

--
-- Indici per le tabelle `identity_group`
--
ALTER TABLE `identity_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `identity_group_identifier` (`identity_group_identifier`) USING BTREE,
  ADD KEY `name` (`name`);

--
-- Indici per le tabelle `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `username` (`username`),
  ADD KEY `object` (`object_id`);

--
-- Indici per le tabelle `log_object`
--
ALTER TABLE `log_object`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `log_request`
--
ALTER TABLE `log_request`
  ADD PRIMARY KEY (`id`),
  ADD KEY `log_request_asset_id` (`asset_id`);

--
-- Indici per le tabelle `migrations`
--
ALTER TABLE `migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `network`
--
ALTER TABLE `network`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id_asset` (`id_asset`,`network`),
  ADD KEY `p_asset` (`id_asset`);

--
-- Indici per le tabelle `privilege`
--
ALTER TABLE `privilege`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `privilege` (`privilege`);

--
-- Indici per le tabelle `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `role` (`role`);

--
-- Indici per le tabelle `role_privilege`
--
ALTER TABLE `role_privilege`
  ADD PRIMARY KEY (`id_role`,`id_privilege`),
  ADD KEY `rp_privilege` (`id_privilege`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `asset`
--
ALTER TABLE `asset`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `trigger_data`
--
ALTER TABLE `trigger_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `group_role_network`
--
ALTER TABLE `group_role_network`
  MODIFY `id` int(255) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `identity_group`
--
ALTER TABLE `identity_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `log`
--
ALTER TABLE `log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `log_object`
--
ALTER TABLE `log_object`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `log_request`
--
ALTER TABLE `log_request`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `migrations`
--
ALTER TABLE `migrations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `network`
--
ALTER TABLE `network`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `privilege`
--
ALTER TABLE `privilege`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `role`
--
ALTER TABLE `role`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `trigger_data`
--
ALTER TABLE `trigger_data`
  ADD CONSTRAINT `k_src_asset_id` FOREIGN KEY (`src_asset_id`) REFERENCES `asset` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `k_dst_asset_id` FOREIGN KEY (`dst_asset_id`) REFERENCES `asset` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `group_role_network`
--
ALTER TABLE `group_role_network`
  ADD CONSTRAINT `grp_group` FOREIGN KEY (`id_group`) REFERENCES `identity_group` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `grp_network` FOREIGN KEY (`id_network`) REFERENCES `network` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `grp_role` FOREIGN KEY (`id_role`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `log`
--
ALTER TABLE `log`
  ADD CONSTRAINT `object` FOREIGN KEY (`object_id`) REFERENCES `log_object` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `network`
--
ALTER TABLE `network`
  ADD CONSTRAINT `p_asset` FOREIGN KEY (`id_asset`) REFERENCES `asset` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `role_privilege`
--
ALTER TABLE `role_privilege`
  ADD CONSTRAINT `rp_privilege` FOREIGN KEY (`id_privilege`) REFERENCES `privilege` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `rp_role` FOREIGN KEY (`id_role`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

--
-- Limiti per la tabella `log_request`
--
ALTER TABLE `log_request`
  ADD CONSTRAINT `log_request_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;