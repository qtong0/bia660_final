from django.db import models


class Restaurant(models.Model):
    hobokenmenus_id = models.PositiveIntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=100)
    address = models.CharField(max_length=80)
    telephone = models.CharField(max_length=50)
    rating = models.FloatField()
    review_count = models.IntegerField()
    
    def __unicode__(self):
        return self.name


class DishCategory(models.Model):
    hobokenmenus_id = models.PositiveIntegerField(primary_key=True, editable=False)
    restaurants = models.ManyToManyField(Restaurant, related_name='dish_categories')
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        parent = self.restaurants.first().name
        return '{0} > {1}'.format(parent, self.name)


class Dish(models.Model):
    hobokenmenus_id = models.PositiveIntegerField(primary_key=True, editable=False)
    category = models.ForeignKey(DishCategory, related_name='dishes')
    name = models.CharField(max_length=50)
    price = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    
    def __unicode__(self):
        return self.name
