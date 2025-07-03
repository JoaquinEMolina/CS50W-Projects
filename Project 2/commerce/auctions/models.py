from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    initial_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings_category")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_created")
    watchlist = models.ManyToManyField(User, related_name="watchlist", blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings_won")
    @property
    def highest_bid(self):
        return self.bids.order_by("-amount").first()

    def __str__(self):
        return self.title
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"User: {self.user} - Listing= '{self.listing}' - Amount: ${self.amount}"


class Comment(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    date = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
    def __str__(self):
        return f"{self.listing.title} - {self.user}: {self.comment}"



