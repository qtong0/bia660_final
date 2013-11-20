The hobokenmenus data is already extracted from the MySQL dump into a fixture file. The fixture file is automatically
loaded into the database when Django creates the schema after you run `./manage.py syncdb` but otherwise the following steps
are how I loaded the data into Django's schema in the first place.

importing from MySQL dump (which I loaded into database `hobokenmenus_db_import`):

First, create Django's MySQL database (I called it `rest660`) in MySQL, configure it in `settings.py`, and create the blank schema with `./manage.py syncdb`


importing that dump into Django's schema:

    insert into restinfo_restaurant
        (hobokenmenus_id, name, url, address, telephone, rating, review_count)
    select rest_id, rest_name, rest_url, address, telephone, rating, review_count
    from hobokenmenus_db_import.restaurant_info;
    
    insert into restinfo_dishcategory
        (hobokenmenus_id, name)
    select cate_id, cate_name
    from hobokenmenus_db_import.category;
    
    insert into restinfo_dishcategory_restaurants
        (dishcategory_id, restaurant_id)
    select distinct cate_id, rest_id
    from hobokenmenus_db_import.rest_category;
    
    insert into restinfo_dish
        (hobokenmenus_id, category_id, name, price)
    select dish_id, cate_id, dish_name, dish_price
    from hobokenmenus_db_import.dish;

