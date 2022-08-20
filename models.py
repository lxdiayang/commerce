from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=30, default='')

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=30, default='')
    description = models.CharField(max_length=300, default='')
    starting_bid = models.FloatField(default=0)
    current_bid = models.FloatField(blank=True, null=True, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="similar_listings")
    url = models.CharField(max_length=1000000, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="creator_listings", default='')
    is_active = models.BooleanField(default=True)
    buyer = models.ForeignKey(User, null=True, on_delete=models.PROTECT, default='')
    error = models.CharField(max_length=1000, default="Sorry, you must enter a valid amount over the starting bid or current bid.")

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    bid = models.FloatField(default=0)

    def __str__(self):
        return f"{self.bid}"
        

class Comment(models.Model):
    comment = models.CharField(max_length=100, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments", default='')

    def __str__(self):
        return f"{self.listing}: {self.user} - {self.comment}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user")
    listings = models.ManyToManyField(Listing, related_name="listings", blank=True)

    def __str__(self):
        return f"{self.user}'s watchlist"