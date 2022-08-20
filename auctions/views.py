from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import User, Listing, Bid, Comment, Category, Watchlist

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'description', 'starting_bid', 'category', 'url')
    
class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

class CreateBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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
def createlisting(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            createlisting = form.save(commit=False)
            createlisting.creator = request.user
            createlisting.save()

            return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/createlisting.html", {
            "form": CreateListingForm()
        })


@login_required
def comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        form = CreateCommentForm(request.POST)
        new_comment = form.save(commit=False)
        new_comment.user = request.user
        new_comment.listing= listing
        new_comment.save()
            
        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))


def make_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bid = float(request.POST["bid"])
    if is_valid(bid, listing):
        listing.current_bid = bid
        
        form = CreateBidForm(request.POST)
        new_bid = form.save(commit=False)
        new_bid.user=request.user
        new_bid.listing = listing
        new_bid.save()
        listing.save()

        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
    else:
        return render(request, "auctions/listing.html", {
            "listing":listing,
            "bid_form": CreateBidForm()
        })

def is_valid(bid, listing):
    if bid > listing.starting_bid and (listing.current_bid == 0 or bid > listing.current_bid):
        return True
    else:
        return False


def listing_view(request, listing_id):
    listing= Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing=listing)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "bid_form": CreateBidForm(),
        "comment_form": CreateCommentForm()
    })


def get_last_pk(obj):
    if(obj.objects.first() is None):
        return 1
    else:
        get_pk = obj.objects.order_by('-pk')[0]
        last_pk = get_pk.pk +1
        return last_pk


def watchlist(request):
    watchlist = Watchlist.objects.get(user = request.user)

    return render(request, "auctions/watchlist.html",{
        "watchlist" : watchlist.listings.all(),
    })


def add_watchlist(request, listing_id):
    if request.user.is_authenticated:
        if Watchlist.objects.filter(user=request.user).exists():
            watchlist = Watchlist.objects.get(user=request.user)
        else:
            watchlist = Watchlist(id = get_last_pk(Watchlist), user = request.user)

        saved_listing = Listing.objects.get(pk=listing_id)
        watchlist.save()
        watchlist.listings.add(saved_listing)
        watchlist.save()
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist.listings.all()
    })

    
def remove_watchlist(request, listing_id):
    if request.user.is_authenticated:
        removed_listing = Listing.objects.get(pk=listing_id)
        watchlist = Watchlist.objects.get(user = request.user).listings.remove(removed_listing)
    
    return HttpResponseRedirect(reverse("watchlist"))


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category_view(request, category_id):
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(category=category_id)
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings
    })

def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.user == listing.creator:
        listing.is_active = False
        listing.buyer = Bid.objects.filter(listing=listing).last().user
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:
        listing.watchers.add(request.user)
    return HttpResponseRedirect(reverse("watchlist"))

