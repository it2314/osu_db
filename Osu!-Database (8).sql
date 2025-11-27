CREATE TABLE `Countries` (
  `code` char(2) PRIMARY KEY,
  `name` varchar(255) NOT NULL,
  `flag_url` varchar(255)
);

CREATE TABLE `Players` (
  `id_player` int PRIMARY KEY,
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `country_code` char(2) NOT NULL,
  `join_date` date NOT NULL
);

CREATE TABLE `GameModes` (
  `id_mode` int PRIMARY KEY,
  `name` ENUM ('taiko', 'standard', 'mania', 'ctb') NOT NULL,
  `description` varchar(255)
);

CREATE TABLE `BeatmapSets` (
  `id_set` int PRIMARY KEY,
  `title` varchar(255) NOT NULL,
  `artist` varchar(255) NOT NULL,
  `creator` varchar(255) NOT NULL,
  `source` varchar(255),
  `tags` varchar(500),
  `status` ENUM ('Ranked', 'Loved', 'Pending', 'Graveyard') NOT NULL,
  `approved_date` date
);

CREATE TABLE `Beatmaps` (
  `id_beatmap` int PRIMARY KEY,
  `id_set` int NOT NULL,
  `id_mode` int NOT NULL,
  `difficulty_name` varchar(255) NOT NULL,
  `difficulty_rating` float NOT NULL,
  `total_length` int NOT NULL,
  `bpm` int NOT NULL,
  `max_combo` int NOT NULL,
  `approach_rate` float NOT NULL,
  `overall_difficulty` float NOT NULL,
  `circle_size` float NOT NULL,
  `health_points` float NOT NULL
);

CREATE TABLE `Mods` (
  `id_mod` int PRIMARY KEY,
  `code` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255)
);

CREATE TABLE `Plays` (
  `id_play` bigint PRIMARY KEY,
  `id_player` int NOT NULL,
  `id_beatmap` int NOT NULL,
  `score` int NOT NULL,
  `max_combo` int NOT NULL,
  `accuracy` float NOT NULL,
  `rank` ENUM ('SS', 'SSH', 'S', 'SH', 'A', 'B', 'C', 'D') NOT NULL,
  `date_played` datetime NOT NULL,
  `perfect` boolean NOT NULL DEFAULT false
);

CREATE TABLE `PlayMods` (
  `id_play` bigint NOT NULL,
  `id_mod` int NOT NULL,
  PRIMARY KEY (`id_play`, `id_mod`)
);

CREATE TABLE `Medals` (
  `id_medal` int PRIMARY KEY,
  `name` varchar(255) NOT NULL,
  `description` varchar(255),
  `icon_url` varchar(255)
);

CREATE TABLE `PlayerMedals` (
  `id_player` int NOT NULL,
  `id_medal` int NOT NULL,
  `achieved_date` date NOT NULL,
  PRIMARY KEY (`id_player`, `id_medal`)
);

CREATE TABLE `PlayerStats` (
  `id_player` int NOT NULL,
  `id_mode` int NOT NULL,
  `global_rank` int,
  `local_rank` int,
  `pp_total` float DEFAULT 0,
  `playcount` int DEFAULT 0,
  `overall_accuracy` float DEFAULT 0,
  PRIMARY KEY (`id_player`, `id_mode`)
);

CREATE INDEX `idx_country_code` ON `Players` (`country_code`);

CREATE UNIQUE INDEX `idx_username` ON `Players` (`username`);

CREATE UNIQUE INDEX `idx_email` ON `Players` (`email`);

CREATE INDEX `idx_join_date` ON `Players` (`join_date`);

CREATE INDEX `idx_title` ON `BeatmapSets` (`title`);

CREATE INDEX `idx_artist` ON `BeatmapSets` (`artist`);

CREATE INDEX `idx_creator` ON `BeatmapSets` (`creator`);

CREATE INDEX `idx_tags` ON `BeatmapSets` (`tags`);

CREATE INDEX `idx_status` ON `BeatmapSets` (`status`);

CREATE INDEX `idx_version` ON `Beatmaps` (`difficulty_name`);

CREATE INDEX `idx_difficulty_rating` ON `Beatmaps` (`difficulty_rating`);

CREATE INDEX `idx_total_length` ON `Beatmaps` (`total_length`);

CREATE INDEX `idx_bpm` ON `Beatmaps` (`bpm`);

CREATE INDEX `idx_max_combo` ON `Beatmaps` (`max_combo`);

CREATE INDEX `idx_approach_rate` ON `Beatmaps` (`approach_rate`);

CREATE INDEX `idx_overall_difficulty` ON `Beatmaps` (`overall_difficulty`);

CREATE INDEX `idx_circle_size` ON `Beatmaps` (`circle_size`);

CREATE INDEX `idx_health_points` ON `Beatmaps` (`health_points`);

CREATE INDEX `idx_score` ON `Plays` (`score`);

CREATE INDEX `idx_max_combo` ON `Plays` (`max_combo`);

CREATE INDEX `idx_accuracy` ON `Plays` (`accuracy`);

CREATE INDEX `idx_rank` ON `Plays` (`rank`);

CREATE INDEX `idx_date_played` ON `Plays` (`date_played`);

CREATE INDEX `idx_perfect` ON `Plays` (`perfect`);

CREATE INDEX `idx_medal_name` ON `Medals` (`name`);

CREATE INDEX `idx_achieved_date` ON `PlayerMedals` (`achieved_date`);

CREATE INDEX `idx_global_rank` ON `PlayerStats` (`global_rank`);

CREATE INDEX `idx_local_rank` ON `PlayerStats` (`local_rank`);

CREATE INDEX `idx_pp_total` ON `PlayerStats` (`pp_total`);

CREATE INDEX `idx_playcount` ON `PlayerStats` (`playcount`);

CREATE INDEX `idx_overall_accuracy` ON `PlayerStats` (`overall_accuracy`);

ALTER TABLE `Players` ADD FOREIGN KEY (`country_code`) REFERENCES `Countries` (`code`);

ALTER TABLE `Beatmaps` ADD FOREIGN KEY (`id_set`) REFERENCES `BeatmapSets` (`id_set`);

ALTER TABLE `Beatmaps` ADD FOREIGN KEY (`id_mode`) REFERENCES `GameModes` (`id_mode`);

ALTER TABLE `Plays` ADD FOREIGN KEY (`id_player`) REFERENCES `Players` (`id_player`);

ALTER TABLE `Plays` ADD FOREIGN KEY (`id_beatmap`) REFERENCES `Beatmaps` (`id_beatmap`);

ALTER TABLE `PlayMods` ADD FOREIGN KEY (`id_play`) REFERENCES `Plays` (`id_play`);

ALTER TABLE `PlayMods` ADD FOREIGN KEY (`id_mod`) REFERENCES `Mods` (`id_mod`);

ALTER TABLE `PlayerMedals` ADD FOREIGN KEY (`id_player`) REFERENCES `Players` (`id_player`);

ALTER TABLE `PlayerMedals` ADD FOREIGN KEY (`id_medal`) REFERENCES `Medals` (`id_medal`);

ALTER TABLE `PlayerStats` ADD FOREIGN KEY (`id_player`) REFERENCES `Players` (`id_player`);

ALTER TABLE `PlayerStats` ADD FOREIGN KEY (`id_mode`) REFERENCES `GameModes` (`id_mode`);
