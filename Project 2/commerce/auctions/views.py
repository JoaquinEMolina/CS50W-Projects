from pyexpat.errors import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth.decorators import login_required

from auctions.forms import ListingForm

from .models import Bid, Category, Listing, User, Comment

def is_in_watchlist(user,listing):
    return user in watchlist.all()

def index(request):
    listings = Listing.objects.filter(active=True)
    for listing in listings:
        listing.in_watchlist = listing.watchlist.filter(id=request.user.id).exists()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "page_title": "Active Listings"
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = listing.bids.all()
    highest_bid = listing.highest_bid

    user_has_highest_bid = False
    if highest_bid and highest_bid.user == request.user:
        user_has_highest_bid = True

    return render_listing_with_context(request, listing)


def render_listing_with_context(request, listing, message=None):
    bids = listing.bids.all()
    highest_bid = listing.highest_bid
    user_has_highest_bid = highest_bid and highest_bid.user == request.user
    in_watchlist = request.user in listing.watchlist.all()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_count": bids.count(),
        "user_has_highest_bid": user_has_highest_bid,
        "message": message,
        "in_watchlist": in_watchlist
    })




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
@login_required    
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            return redirect("listing", listing_id=listing.id)
    else:
        form = ListingForm()
    return render(request, "auctions/create_listing.html", {
        "form": form
    })

@login_required
def make_bid(request,listing_id):
    if request.method == "POST":
        amount = request.POST["amount"]
        listing = Listing.objects.get(pk=listing_id)
        

        if not amount:
            return render_listing_with_context(request, listing, "Please enter a bid amount.")
        try:
            amount = Decimal(amount)
        except:
            return render_listing_with_context(request, listing, "Invalid bid amount.")
        
        
        highest_bid = listing.highest_bid
        current_price = highest_bid.amount if highest_bid else listing.initial_price
        
        if listing.created_by.id == request.user.id:
            return render_listing_with_context(request, listing, "You can't bid in your own auction.")
        if amount <= current_price:
            return render_listing_with_context(request, listing, "Your bid must be higher than the current price.")
        else:
            bid = Bid(listing=listing, user=request.user, amount=amount)
            bid.save()
            return redirect("listing", listing_id=listing_id)
    else:
        return redirect("index")
    
@login_required    
def make_comment(request,listing_id):
    if request.method == "POST":
        comment = request.POST["comment"]
        if not comment:
            return redirect("listing", listing_id=listing_id)
        else:
            listing = Listing.objects.get(pk=listing_id)
            comment = Comment(listing=listing, user=request.user, comment=comment)
            comment.save()
            return redirect("listing", listing_id=listing_id)
    else:
        return redirect("index")

@login_required
def watchlist(request):
    user = request.user
    listings_in_watchlist = Listing.objects.filter(watchlist=user)
    if listings_in_watchlist:
        for listing in listings_in_watchlist:
            listing.in_watchlist = listing.watchlist.filter(id=request.user.id).exists()
        return render(request, "auctions/watchlist.html", {
            "listings": listings_in_watchlist
        })
    else:
        return render(request, "auctions/watchlist.html", {
            "listings": listings_in_watchlist,
            "message": "No listings in your watchlist."
        })


@login_required
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    listing.watchlist.remove(request.user)
    next_url = request.GET.get("next", None)
    if next_url:
        return redirect(next_url)
    return redirect("listing", listing_id=listing_id)

@login_required
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    listing.watchlist.add(request.user)
    next_url = request.GET.get("next", None)
    if next_url:
        return redirect(next_url)
    return redirect("listing", listing_id=listing_id)


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })
   


def category(request, category_name):
    listings = Listing.objects.filter(category__name=category_name, active=True)
    if listings:
        return render(request, "auctions/category.html", {
            "listings": listings,
            "category_name": category_name
        })
    else:
        return render(request, "auctions/category.html", {
            "message": "No active listings in this category.",
            "category_name": category_name
        })

def listing_close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    highest_bid = listing.highest_bid
    if highest_bid:
        listing.winner = highest_bid.user
        listing.active = False
        listing.save()
        return render(request, "auctions/listing.html",{
            "listing": listing
        })
    else:
        return render(request, "auctions/listing.html", {
            "message_error_close": "No bids yet, cannot close listing.",
            "listing": listing
        })



