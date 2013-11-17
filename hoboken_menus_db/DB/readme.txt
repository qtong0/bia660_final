to restore the Database:
go to the directory of the db backup file,
$$> mysql -u root -p biafinal_db < menus_db_bk.sql

to get restaurant information:
get all restaurants names which serves burgers:
select distinct(rest_name) from restaurant_info, dish, rest_category
where restaurant_info.rest_id = rest_category.rest_id and rest_category.cate_id = dish.cate_id
and dish.dish_name like '%burger%’;