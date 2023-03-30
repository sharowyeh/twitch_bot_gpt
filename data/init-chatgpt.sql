/*Initial tables for chatgpt instance*/
following are 2 mariadb tables, given me a CURD functions class in python
/*To switch different topics like ChatGPT website conversations*/
CREATE TABLE IF NOT EXISTS `chatgpt`.`topics` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(64) NOT NULL,
    `messages` int(11) DEFAULT '0',
    `total_tokens` int(11) DEFAULT '0',
    `updatetime` datetime(6) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*May follow completion response from chat API*/
CREATE TABLE IF NOT EXISTS `chatgpt`.`messages` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `topics_id` int(11) DEFAULT '0',
    `content` varchar(4096),
    `role` varchar(32),
    `created` int(11) DEFAULT '0',
    `chat_id` varchar(64) NOT NULL,
    `model` varchar(32) NOT NULL,
    `obj` varchar(32),
    `completion_tokens` int(11) DEFAULT '0',
    `prompt_tokens` int(11) DEFAULT '0',
    `total_tokens` int(11) DEFAULT '0',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
