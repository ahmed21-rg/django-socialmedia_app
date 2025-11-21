from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout
from django.http import JsonResponse 
from .models import *

# Create your views here.

def home(request):  
    following_post = Follwer.objects.filter(follower=request.user).values_list('following', flat=True) # get list of users being followed 
    post = Post.objects.filter(author__in=following_post).order_by('-created_at')
    profilee = profile.objects.all() # get all profiles
    
    for pos in post:
        pos.existing_like = Like.objects.filter(user=request.user, post=pos).exists() # Check if the user has liked the post

    return render(request, 'main.html' , {'post': post, 'profilee': profilee})

def signup(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = User.objects.create_user(username, email, password)
            user.save()
            new_profile = profile.objects.create(user=user)

            return redirect('login')
    except Exception as e:
        print(e)
        return render(request, 'signup.html', {'error': 'user already exists or invalid data'})
    return render(request, 'signup.html', {'error': ''})

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html', {'error': ''})

@login_required
def logoutt(request):
    logout(request)
    return redirect('login')

@login_required
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        caption = request.POST.get('caption')
        image = request.FILES.get('image_upload')
        
        if image:
            new_post = Post.objects.create(author=request.user, caption=caption, image=image)

        else:
            return render(request, 'main.html', {'error': 'Please upload an image.'})
        
        return redirect('home')

def post_details(request, id):

    post = get_object_or_404(Post, id=id)

    return render(request, 'post_details.html', {'post':post})


@login_required
def like(request, id):
    post = get_object_or_404(Post, id=id)


    existing_like = Like.objects.filter(user=request.user, post=post)
    if existing_like.exists():

        existing_like.delete()
        post.no_of_likes -= 1
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        post.no_of_likes += 1
        liked = True

    post.no_of_likes = Like.objects.filter(post=post).count()
    post.save()
    return JsonResponse({
        'no_of_likes': post.no_of_likes,
        'liked': liked
    })


def explore(request):
    post = Post.objects.all().order_by('-created_at')
    profilee = profile.objects.all() # get all profiles
    return render(request, 'explore.html' , {'post': post, 'profilee': profilee})


@login_required
def profile_view(request, username):
    user_obj = User.objects.get(username=username)  # gets the user object

    profile_obj = profile.objects.get(user=user_obj) # gets the profile object

    user_posts = Post.objects.filter(author=user_obj).order_by('-created_at')  # gets posts by the user

    post_count = user_posts.count()  # counts the number of posts

    followers_count = Follwer.objects.filter(following=user_obj).count()
    following_count = Follwer.objects.filter(follower=user_obj).count()

    is_following = Follwer.objects.filter(follower=request.user, following=user_obj).exists()

    context = {
        'user_obj': user_obj,
        'profile_obj': profile_obj,
        'user_posts': user_posts,
        'post_count': post_count,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
    }
    

    return render(request, 'profile.html', context)
@login_required
def edit_profile(request, username):
    user_obj = User.objects.get(username=username)
    profile_obj = profile.objects.get(user=user_obj)

    if request.user != user_obj:
        return redirect('profile', username=user_obj.username)


    if request.method == 'POST':    
        bio = request.POST.get('bio')
        location = request.POST.get('location') 
        profile_picture = request.FILES.get('profile_picture')
        remove_picture = request.POST.get('remove_picture')


        profile_obj.bio = bio
        profile_obj.location = location 

        if remove_picture:
            profile_obj.profile_picture = '/profile_pics/default.jpg'
        elif profile_picture:
            profile_obj.profile_picture = profile_picture
        
        profile_obj.save()
       
        return redirect('profile', username=user_obj.username)
    context = {
        'user_obj': user_obj,
        'profile_obj': profile_obj  
    }
    return render(request, 'edit_profile.html', context)  

def delete_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user == post.author:
        post.delete()
    return redirect('profile', username=request.user.username)



def follower(request, username):
    current_user = get_object_or_404(User, username=username)  # target user to follow/unfollow

    
    if request.user == current_user:
        return redirect('profile', username=username)
    
    # Check if the follow relationship already exists
    existing_follow = Follwer.objects.filter(follower=request.user, following=current_user).first()
    if existing_follow:
        existing_follow.delete()
    else:
        Follwer.objects.create(follower=request.user, following=current_user)

    return redirect('profile', username=current_user.username)


def search_results(request):
    try:
        query= request.GET.get('q', '').strip()
        user = User.objects.filter(username__icontains=query)
        post = Post.objects.filter(caption__icontains=query)
        context = {
            'query': query,
            'user': user,
            'post': post
        }
    except Exception as e:
        print(e)
        
    return render(request, 'search_results.html', context)

def comments(request, id):
    posts = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        content = request.POST.get('content')
        comment = Comment.objects.create(user=request.user, post=posts, content=content)
        return JsonResponse({
            'user' : comment.user.username,
            'content':comment.content,
            'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    comments = Comment.objects.filter(post=posts).order_by('-created_at')

    return render(request, 'comments.html', {'posts': posts, 'comments': comments})
