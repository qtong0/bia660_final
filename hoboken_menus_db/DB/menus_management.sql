create database if not exists biafinal_db;

GRANT ALL PRIVILEGES ON biafinal_db.* TO 'bia_user'@'localhost' IDENTIFIED BY 'biabiabia';

use biafinal_db;

drop table if exists restaurant_info;

create table if not exists restaurant_info (
    rest_id int primary key auto_increment,
    rest_name varchar(50),
    rest_url varchar(255) unique,
    address varchar(80),
    telephone varchar(50),
    rating decimal(2 , 1 ),
    review_count int
);

drop table if exists category;

create table if not exists category (
    cate_id int primary key auto_increment,
    cate_name varchar(100) unique
);

drop table if exists rest_category;

create table if not exists rest_category (
    rest_id int,
    cate_id int,
    constraint fk_rest_id foreign key (rest_id)
        references restaurant_info (rest_id),
    constraint fk_cate_id foreign key (cate_id)
        references category (cate_id)
);

drop table if exists dish;

create table if not exists dish (
    dish_id int primary key auto_increment,
    cate_id int,
    dish_price decimal(10 , 2 ),
    dish_name varchar(100),
    constraint fk_dish_cate_id foreign key (cate_id)
        references category (cate_id)
);

commit;

alter table dish
	drop foreign key fk_dish_cate_id;
alter table rest_category
	drop foreign key fk_rest_id;
alter table rest_category
	drop foreign key fk_cate_id;
truncate dish;
truncate rest_category;
truncate category;
truncate restaurant_info;
alter table rest_category
	add constraint fk_rest_id foreign key (rest_id)
        references restaurant_info (rest_id);
alter table rest_category
	add constraint fk_cate_id foreign key (cate_id)
        references category (cate_id);
alter table dish
	add constraint fk_dish_cate_id foreign key (cate_id)
		references category (cate_id);

select * from restaurant_info;
select * from category;
select * from dish;
select * from rest_category;

select * from dish where dish_name like '%burger%';
select * from rest_category where cate_id = 41;
select rest_name from restaurant_info where rest_id = 121;

select distinct(rest_name) from restaurant_info, dish, rest_category
where restaurant_info.rest_id = rest_category.rest_id and rest_category.cate_id = dish.cate_id
and dish.dish_name like '%burger%';
