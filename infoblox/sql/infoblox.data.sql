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
-- Dump dei dati per la tabella `configuration`
--

INSERT INTO `configuration` (`id`, `config_type`) VALUES
(1, 'global');

--
-- Dump dei dati per la tabella `privilege`
--

INSERT INTO `privilege` (`id`, `privilege`, `privilege_type`, `description`) VALUES
(1, 'asset_patch', 'asset', NULL),
(2, 'asset_delete', 'asset', NULL),
(3, 'assets_get', 'asset', NULL),
(4, 'assets_post', 'asset', NULL),
(5, 'network_containers_get', 'object', NULL),
(6, 'network_container_get', 'object', NULL),
(7, 'network_get', 'object', NULL),
(8, 'network_post', 'object', NULL),
(9, 'network_delete', 'object', NULL),
(10, 'networks_get', 'object', NULL),
(11, 'ipv4_get', 'object', NULL),
(12, 'ipv4s_post', 'object', NULL),
(13, 'ipv4_delete', 'object', NULL),
(14, 'ipv4_patch', 'object', NULL),
(15, 'permission_identityGroups_get', 'global', NULL),
(16, 'permission_identityGroups_post', 'global', NULL),
(17, 'permission_roles_get', 'global', NULL),
(18, 'permission_identityGroup_patch', 'global', NULL),
(19, 'permission_identityGroup_delete', 'global', NULL),
(20, 'historyComplete_get', 'global', NULL),
(21, 'full_visibility', 'global', NULL),
(22, 'vlans_get', 'asset', NULL),
(23, 'vlan_get', 'asset', NULL),
(24, 'assign_network', 'asset', NULL),
(25, 'configuration_put', 'global', NULL),
(26, 'ranges_get', 'asset', NULL),
(27, 'range_get', 'asset', NULL),
(28, 'triggers_post', 'global', NULL),
(29, 'triggers_get', 'global', NULL),
(30, 'trigger_get', 'global', NULL),
(31, 'trigger_patch', 'global', NULL),
(32, 'trigger_delete', 'global', NULL);

--
-- Dump dei dati per la tabella `role`
--

INSERT INTO `role` (`id`, `role`, `description`) VALUES
(1, 'admin', 'admin'),
(2, 'staff', 'read / write, excluding assets'),
(3, 'readonly', 'readonly'),
(4, 'workflow', 'workflow system user'),
(5, 'powerstaff', 'read / write, excluding assets');

--
-- Dump dei dati per la tabella `role_privilege`
--

INSERT INTO `role_privilege` (`id_role`, `id_privilege`) VALUES
(1, 3),
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
(1, 21),
(1, 22),
(1, 23),
(1, 24),
(1, 25),
(1, 26),
(1, 27),
(2, 3),
(2, 5),
(2, 6),
(2, 7),
(2, 10),
(2, 11),
(2, 12),
(2, 13),
(2, 14),
(2, 22),
(2, 23),
(2, 24),
(2, 25),
(2, 26),
(2, 27),
(3, 3),
(3, 5),
(3, 6),
(3, 7),
(3, 10),
(3, 11),
(3, 22),
(3, 23),
(4, 3),
(4, 5),
(4, 6),
(4, 7),
(4, 8),
(4, 9),
(4, 10),
(4, 11),
(4, 12),
(4, 13),
(4, 14),
(4, 22),
(4, 23),
(4, 24),
(4, 25),
(4, 26),
(4, 27),
(5, 3),
(5, 5),
(5, 6),
(5, 7),
(5, 10),
(5, 11),
(5, 12),
(5, 13),
(5, 14),
(5, 22),
(5, 23),
(5, 24),
(5, 25),
(5, 26),
(5, 27);


-- Dump dei dati per la tabella `identity_group`
-- (Workflow system group)

INSERT INTO `identity_group` (`id`, `name`, `identity_group_identifier`) VALUES
(1, 'workflow.local', 'workflow.local');


COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;