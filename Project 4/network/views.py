import json
import time
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404

from .models import User, Post


def index(request):
    context = {
        "timestamp": int(time.time()),
    }
    return render(request, "network/index.html", context)


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def postbox(request, postbox):
    if postbox == 'all':
        posts = Post.objects.all()
    elif postbox == 'following':
        posts = Post.objects.filter(
            user__in=request.user.following.all()
        )
    else:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(username=postbox)
            posts = Post.objects.filter(user=user)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
    # Return posts in reverse chronologial order 
    posts = posts.order_by("-timestamp")
        
    # Pagination
    page_number = request.GET.get("page",1)
    paginator = Paginator(posts, 10)
    page = paginator.get_page(page_number)
    return JsonResponse({
        "posts": [post.serialize(user=request.user) for post in page],
        "has_previous": page.has_previous(),
        "has_next": page.has_next(),
        "previous_page_number": page.previous_page_number() if page.has_previous() else None,
        "next_page_number": page.next_page_number() if page.has_next() else None,
        "num_pages": paginator.num_pages,
        "current_page": page.number
    })



@csrf_exempt
@login_required
def create_post(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST method required."}, status = 400)
    try:
        data = json.loads(request.body)
        body =  data.get("body","").strip()

        if not body:
            return JsonResponse({"error": "Post content cannot be empty."}, status=400)
        post = Post(user=request.user, body=body)
        post.save()
        return JsonResponse(post.serialize(), status=201)
    
    except Exception as e:
        return JsonResponse({"Error: str(e)"}, status=500)
    
@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def update_post(request, post_id):
    try:
        post = get_object_or_404(Post, pk=post_id)

        if post.user != request.user:
            return JsonResponse({"error": "You don't have permission to edit this post."}, status=403)
        
        data = json.loads(request.body)
        new_body = data.get("body","").strip()

        if not new_body:
            return JsonResponse({"error": "Post content cannot be empty."}, status=400 )
        
        post.body = new_body
        post.save()
        return JsonResponse(post.serialize(), status=200)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def user_profile(request, username):
    user = get_object_or_404(User, username=username)

    followers_count = user.followers.count()
    following_count = user.following.count()


    is_following = request.user.is_authenticated and user.followers.filter(pk=request.user.pk).exists()

    return JsonResponse({
        "username": user.username,
        "followers": followers_count,
        "following": following_count,
        "is_following": is_following
    })

@login_required
def follow_unfollow(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)

        if request.user == target_user:
            return HttpResponseBadRequest("You can't follow yourself.")
        
        if request.user.following.filter(id=target_user.id).exists():
            request.user.following.remove(target_user)
            action = "unfollowed"
        else:
            request.user.following.add(target_user)
            action = "followed"

        return JsonResponse({
            "status": "ok",
            "action": action,
            "followers_count": target_user.followers.count(),
            "following_count": target_user.following.count(),
            "is_following": request.user.following.filter(id=target_user.id).exists()
        })
    return HttpResponseBadRequest("Only POST allowed.")

@login_required
def like_unlike(request, post_id):
    if request.method =='POST':
        post = get_object_or_404(Post, id=post_id)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            action= "unliked"
        else:
            post.likes.add(request.user)
            action = "liked"

        return JsonResponse({
            "status": "ok",
            "action": action,
            "likes_count": post.likes.count()
        })
        
