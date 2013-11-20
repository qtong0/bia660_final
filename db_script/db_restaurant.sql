delimiter $$

CREATE TABLE `restaurant_yelp` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(100) DEFAULT NULL,
      `rating` float DEFAULT NULL,
      `review_count` int(11) DEFAULT NULL,
      `phone` varchar(15) DEFAULT NULL,
      `location` varchar(200) DEFAULT NULL,
      PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1$$

delimiter $$

CREATE TABLE `comments` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `id_restaurant` int(11) NOT NULL,
      `comment` text,
      PRIMARY KEY (`id`),
      KEY `fk_comments_1_idx` (`id_restaurant`),
      CONSTRAINT `fk_comments_1` FOREIGN KEY (`id_restaurant`) REFERENCES `restaurant_yelp` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1$$

delimiter $$

CREATE TABLE `id_map` (
      `id_yelp` int(11) NOT NULL,
      `id_allmenu` int(11) NOT NULL,
      PRIMARY KEY (`id_yelp`,`id_allmenu`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$
