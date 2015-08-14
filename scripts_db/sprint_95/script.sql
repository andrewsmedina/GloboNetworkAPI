CREATE TABLE `queue_message` (
    `id_queue_message` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `message` longtext NOT NULL,
    `queue` varchar(250) NOT NULL,
    `sent` bool NOT NULL,
    `method` varchar(250) NOT NULL
)
;