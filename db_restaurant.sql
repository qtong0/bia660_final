delimiter $$

CREATE TABLE `restaurant` (
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
  `id_restaurant` int(11) NOT NULL,
  `comment` text,
  PRIMARY KEY (`id`),
  KEY `fk_comments_1_idx` (`id_restaurant`),
  CONSTRAINT `fk_comments_1` FOREIGN KEY (`id_restaurant`) REFERENCES `restaurant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=478 DEFAULT CHARSET=latin1$$


