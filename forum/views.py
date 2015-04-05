import os
from os.path import join as pjoin
from PIL import Image

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings


from .models import Forum, Thread, Post, UserProfile
from .forms import PostForm, ThreadForm, ForumForm, UserProfileForm
# Create your views here.


def index(request):
    forums = Forum.objects.order_by('-created')
    forums = make_paginator(request, forums, 20)

    context_dict = {'forums': forums}
    return render(request, 'forum/index.html', context_dict)


def forum(request, pk):
    """
    Listing all threads in a forum with pk=pk.
    """
    forum = get_object_or_404(Forum, pk=pk)
    threads = Thread.objects.filter(forum=pk).order_by('-created')
    threads = make_paginator(request, threads, 20)
    context_dict = {'threads': threads, 'forum': forum}
    return render(request, 'forum/forum.html', context_dict)


def thread(request, pk):
    """
    List posts in this thread.
    """
    # get_object_or_404 ?? get_list_or_404?? Or just no error handling at all here???
    try:
        posts = Post.objects.filter(thread=pk).order_by('created')
    except:
        raise Http404

    posts = make_paginator(request, posts, 15)
    thread = get_object_or_404(Thread, pk=pk)
    context_dict = {'posts': posts, 'thread': thread}
    return render(request, 'forum/thread.html', context_dict)


def make_paginator(request, items, number):
    '''
    Make a paginator of number items of type 'item'
    '''
    paginator = Paginator(items, number)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        items = paginator.page(page)
    except(InvalidPage, EmptyPage):
        items = paginator.page(paginator.num_pages)

    return items


@login_required
def add_thread(request, pk):
    forum = get_object_or_404(Forum, pk=pk)
    if request.method == 'POST':
        thread = Thread(forum=forum)
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.creator = request.user
            thread.save()
            return redirect('forum:forum', pk=pk)
        else:
            print(form.errors)
    else:
        form = ThreadForm()
        context_dict = {'form': form, 'forum': forum}
    return render(request, 'forum/add_thread.html', context_dict)


@login_required
def add_post(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    if request.method == 'POST':
        post = Post(thread=thread)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()

            profile = UserProfile.objects.get(user=post.creator)
            profile.posts += 1
            profile.save()
            return redirect('forum:thread', pk=pk)
        else:
            print(form.errors)
    else:
        form = PostForm()
        context_dict = {'form': form, 'thread': thread}
    return render(request, 'forum/add_post.html', context_dict)


@login_required
def create_forum(request):
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            forum = form.save(commit=False)
            forum.creator = request.user
            forum.save()
            return redirect('forum:index')
        else:
            print(form.errors)
    else:
        form = ForumForm()
    return render(request, 'forum/create_forum.html', {'form': form})


@login_required
def edit_profile(request, pk):
    try:
        profile = UserProfile.objects.get(user=User.objects.get(pk=pk))
    except:
        profile = None

    if request.method == 'POST':
        if profile:
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                if 'avatar' in request.FILES:
                    avatar = request.FILES['avatar']
                    profile.avatar = avatar
                    profile.save()
                    profile.thumbnail1 = makethumbnail(profile.avatar.name)
                    profile.thumbnail2 = makethumbnail(profile.avatar.name, (300, 300))
                    profile.save()
        else:
            form = UserProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                if 'avatar' in request.FILES:
                    avatar = request.FILES['avatar']
                    profile.avatar = avatar
                    profile.save()
                    profile.thumbnail1 = makethumbnail(profile.avatar.name)
                    profile.thumbnail2 = makethumbnail(profile.avatar.name, (300, 300))
                profile.save()
            else:
                print(form.errors)
                context_dict = {'errors': form.errors, 'form': form}
                return render(request, 'forum/edit_profile.html', context_dict)

        context_dict = {'form': form, 'edit_success': True}
        return render(request, 'forum/edit_profile.html', context_dict)
    else:
        form = UserProfileForm()
        context_dict = {'form': form}
    return render(request, 'forum/edit_profile.html', context_dict)


def makethumbnail(imgfile, size=(200, 200)):
    thumbsdir = pjoin(settings.MEDIA_ROOT, 'profile_images/thumbs')
    if not os.path.exists(thumbsdir):
        print('Making thumb dir...', thumbsdir)
        os.mkdir(thumbsdir)

    fname, ext = os.path.splitext(imgfile)
    fname = fname.split('/')[1]

    thumb1size = str(size[0]) + 'x' + str(size[1])
    thumbnail = fname + '-thumb1-' + thumb1size + ext
    thumbnailfile = os.path.join(thumbsdir, thumbnail)

    try:
        thumb = Image.open(pjoin(settings.MEDIA_ROOT, imgfile))
        thumb.thumbnail(size, Image.ANTIALIAS)
        thumb.save(thumbnailfile)
        return 'profile_images/thumbs/' + thumbnail
    except:
        print("Error encountered. Skipping => ", thumbnailfile)
        return ''
