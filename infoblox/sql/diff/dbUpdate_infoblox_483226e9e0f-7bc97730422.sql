
/*
OLD COMMIT: 483226e9e0f2865a0193c90af0fedba2dd838e9e
NEW COMMIT: 7bc977304226727328840c99d47abcda71fc4e5b
*/


/*
SQL SCHEMA SECTION
*/

## mysqldiff 0.60
## 
## Run on Fri Feb  2 17:31:05 2024


ALTER TABLE asset CHANGE COLUMN baseurl baseurl varchar(255) NOT NULL DEFAULT ''; # was varchar(255) NOT NULL
ALTER TABLE asset CHANGE COLUMN fqdn fqdn varchar(255) NOT NULL; # was varchar(255) DEFAULT NULL
ALTER TABLE asset DROP INDEX address;
ALTER TABLE asset DROP COLUMN address; # was varchar(64) NOT NULL
ALTER TABLE asset ADD COLUMN protocol varchar(16) NOT NULL DEFAULT 'https' AFTER fqdn;
ALTER TABLE asset ADD COLUMN port int(11) NOT NULL DEFAULT 443 AFTER protocol;
ALTER TABLE asset ADD COLUMN path varchar(255) NOT NULL DEFAULT '/' AFTER port;
ALTER TABLE asset MODIFY `tlsverify` tinyint(4) NOT NULL DEFAULT 1 AFTER path;

ALTER TABLE asset ADD UNIQUE fqdn (fqdn,protocol,port);
ALTER TABLE log_object CHANGE COLUMN type type enum('ipv4','network','') DEFAULT NULL; # was enum('ipv4','') DEFAULT NULL
CREATE TABLE configuration (
  id int(11) NOT NULL AUTO_INCREMENT,
  config_type varchar(255) DEFAULT NULL,
  configuration text NOT NULL DEFAULT '[]',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE log_request (
  id int(11) NOT NULL AUTO_INCREMENT,
  asset_id int(11) DEFAULT NULL,
  action varchar(255) NOT NULL,
  response_status int(11) NOT NULL,
  date datetime NOT NULL DEFAULT current_timestamp(),
  username varchar(255) NOT NULL,
  PRIMARY KEY (id),
  KEY log_request_asset_id (asset_id),
  CONSTRAINT log_request_asset_id FOREIGN KEY (asset_id) REFERENCES asset (id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE trigger_data (
  id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(64) NOT NULL,
  dst_asset_id int(11) DEFAULT NULL,
  action varchar(255) NOT NULL,
  enabled tinyint(1) NOT NULL,
  PRIMARY KEY (id),
  KEY k_dst_asset_id (dst_asset_id),
  CONSTRAINT k_dst_asset_id FOREIGN KEY (dst_asset_id) REFERENCES asset (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE trigger_condition (
  id int(11) NOT NULL AUTO_INCREMENT,
  trigger_id int(11) NOT NULL,
  src_asset_id int(11) DEFAULT NULL,
  `condition` varchar(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY `condition` (trigger_id,`condition`,src_asset_id) USING BTREE,
  KEY k_src_asset_id (src_asset_id),
  CONSTRAINT k_src_asset_id FOREIGN KEY (src_asset_id) REFERENCES asset (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT k_trigger_id FOREIGN KEY (trigger_id) REFERENCES trigger_data (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;




/*
DATA SECTION
*/

set foreign_key_checks = 0;

# Set the protocol from the original baseurl.
update asset A1 INNER JOIN asset A2 ON A1.id = A2.id set A1.protocol = SUBSTRING_INDEX(A2.baseurl,':',1);

# select if(p0 REGEXP '.*/$', p0, concat(p0, '/') ) as path from (select REGEXP_REPLACE(A2.baseurl, '[a-zA-Z]+://[0-9a-zA-Z.-]+(:[0-9]+)?(/.*)', '\\2') as p0 from A2) as p1;

# Set the path from the original baseurl.
update asset A1 INNER JOIN asset A2 ON A1.id = A2.id set A1.path = (select if(p0 REGEXP '.*/$', p0, concat(p0, '/') ) from (select REGEXP_REPLACE(A3.baseurl, '[a-zA-Z]+://[0-9a-zA-Z.-]+(:[0-9]+)?(/.*)', '\\2') as p0 from asset A3) as p1);

# Put an "/" at the end of the baseurl if missing.
update asset A1 INNER JOIN asset A2 ON A1.id = A2.id set A1.baseurl = ( select if(b0 REGEXP '.*/$', b0, concat(b0, '/') ) as b from (select A3.baseurl as b0 from asset A3) as a );



truncate table privilege;
truncate table role_privilege;
truncate table role;


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
(24, 'cloud_network_assign_put', 'asset', NULL),
(25, 'configuration_put', 'global', NULL),
(26, 'ranges_get', 'asset', NULL),
(27, 'range_get', 'asset', NULL),
(28, 'triggers_post', 'global', NULL),
(29, 'triggers_get', 'global', NULL),
(30, 'trigger_get', 'global', NULL),
(31, 'trigger_patch', 'global', NULL),
(32, 'trigger_delete', 'global', NULL),
(33, 'cloud_network_modify_put', 'object', NULL),
(34, 'cloud_networks_modify_account_put', 'object', NULL),
(35, 'cloud_network_delete', 'object', NULL),
(36, 'cloud_extattrs_get', 'object', NULL),
(37, 'delete_account_cloud_network_put', 'object', NULL);


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
(1, 28),
(1, 29),
(1, 30),
(1, 31),
(1, 32),
(1, 33),
(1, 34),
(1, 35),
(1, 36),
(1, 37),
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
(2, 25),
(2, 36),
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
(4, 33),
(4, 34),
(4, 35),
(4, 36),
(4, 37),
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
(5, 27),
(5, 33),
(5, 34),
(5, 35),
(5, 36),
(5, 37);

INSERT INTO `role` (`id`, `role`, `description`) VALUES
(1, 'admin', 'admin'),
(2, 'staff', 'read / write, excluding assets'),
(3, 'readonly', 'readonly'),
(4, 'workflow', 'workflow system user'),
(5, 'powerstaff', 'read / write, excluding assets');


set foreign_key_checks = 1;
