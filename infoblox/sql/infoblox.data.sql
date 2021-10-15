-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Creato il: Ago 23, 2021 alle 14:36
-- Versione del server: 10.3.29-MariaDB-0+deb10u1-log
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

--
-- Dump dei dati per la tabella `privilege`
--

INSERT INTO `privilege` (`id`, `privilege`, `propagate_to_all_asset_networks`, `propagate_to_all_assets`, `description`) VALUES
(1, 'asset_patch', 1, 1, NULL),
(2, 'asset_delete', 1, 1, NULL),
(3, 'assets_get', 1, 1, NULL),
(4, 'assets_post', 1, 1, NULL),
(5, 'network_containers_get', 1, 0, NULL),
(6, 'network_container_get', 1, 0, NULL),
(7, 'network_get', 0, 0, NULL),
(8, 'network_post', 0, 0, NULL),
(9, 'network_delete', 0, 0, NULL),
(10, 'networks_get', 1, 0, NULL),
(11, 'ipv4_get', 0, 0, NULL),
(12, 'ipv4s_post', 0, 0, NULL),
(13, 'ipv4_delete', 0, 0, NULL),
(14, 'ipv4_patch', 0, 0, NULL),
(15, 'permission_identityGroups_get', 1, 1, NULL),
(16, 'permission_identityGroups_post', 1, 1, NULL),
(17, 'permission_roles_get', 1, 1, NULL),
(18, 'permission_identityGroup_patch', 1, 1, NULL),
(19, 'permission_identityGroup_delete', 1, 1, NULL),
(20, 'historyComplete_get', 1, 1, NULL);

--
-- Dump dei dati per la tabella `role`
--

INSERT INTO `role` (`id`, `role`, `description`) VALUES
(1, 'admin', 'admin'),
(2, 'staff', 'read / write, excluding assets'),
(3, 'readonly', 'readonly');

--
-- Dump dei dati per la tabella `role_privilege`
--

INSERT INTO `role_privilege` (`id_role`, `id_privilege`) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 6),
(1, 7),
(1, 8),
(1, 9),
(1, 10),
(1, 11),
(1, 12),
(1, 13),
(1, 14),
(1, 15),
(1, 16),
(1, 17),
(1, 18),
(1, 19),
(1, 20),
(2, 5),
(2, 6),
(2, 7),
(2, 8),
(2, 9),
(2, 10),
(2, 11),
(2, 12),
(2, 13),
(2, 14),
(3, 5),
(3, 6),
(3, 7),
(3, 10),
(3, 11);

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;