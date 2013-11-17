delimiter $$

CREATE TABLE `resterant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `review_count` int(11) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `location` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=178 DEFAULT CHARSET=latin1$$

delimiter $$

CREATE TABLE `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_resterant` int(11) NOT NULL,
  `comment` text,
  PRIMARY KEY (`id`),
  KEY `fk_comments_1_idx` (`id_resterant`),
  CONSTRAINT `fk_comments_1` FOREIGN KEY (`id_resterant`) REFERENCES `resterant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=478 DEFAULT CHARSET=latin1$$


