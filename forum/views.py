# -*- coding: utf-8 -*-
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core import exceptions
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.

from forum.forms import PostCreateForm, PostUpdateForm
from forum.models import Topic, Forum, ForumGroup, Post, Vote
from forum.perms import PostPermission, VotePermission, TopicPermission


def index(request):
    forum_groups = ForumGroup.objects.filter(group_type='f')
    forums = Forum.objects.filter(forum_group__in=forum_groups)\
                          .select_related('last_post', 'last_post__created_by', 'last_post__topic')
    return render(request, 'forum/forum_index.html', {'forum_groups': forum_groups, 'forums': forums})


def pagination_items(request, items, num_per_page):
    paginator = Paginator(items, num_per_page)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        items = paginator.page(page)
    except (InvalidPage, EmptyPage):
        items = paginator.page(paginator.num_pages)
    return items


def topic_list(request,
               forum_id,
               template="forum/topic_list.html",
               extra_context=None):
    forum = get_object_or_404(Forum, pk=forum_id)
    topics = Topic.objects.filter(forum_id=forum_id).select_related("last_post", "created_by", "last_post__created_by")
    topics = pagination_items(request, topics, 20)
    context = {
        'forum': forum,
        'topics': topics
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)


def topic_retrieve(request, forum_id, topic_id, template="forum/topic_retrieve.html"):
    forum = get_object_or_404(Forum, pk=forum_id)
    topic = get_object_or_404(Topic.objects.select_related('post', 'post__created_by', 'post__created_by__profile__avatar'),
                              pk=topic_id)
    posts = topic.posts.all().select_related('created_by', 'created_by__profile__avatar')
    if request.user.is_authenticated():
        votes = Vote.objects.filter(post__in=posts, created_by=request.user).values('post_id', 'type')
    else:
        votes = None
    return render(request, template, {
        'forum': forum,
        'topic': topic,
        'post': topic.post,
        'posts': posts,
        'votes': votes
    })


@login_required
def post_create(request, forum_id=None, topic_id=None, post_id=None, template="forum/post_create.html"):

    topic = forum = post = None

    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
    if topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)
        forum = topic.forum
    if post_id:
        post = get_object_or_404(Post, pk=post_id)

    # Check permission
    if not PostPermission(request.user).can_create_post():
        raise exceptions.PermissionDenied

    if request.POST:
        # if a request is submitted, handle this request
        form = PostCreateForm(request.POST, user=request.user, forum=forum, topic=topic, parent=post)
        if form.is_valid():
            post = form.save()
            if post.topic_post:
                return HttpResponseRedirect(reverse("forum:topic_retrieve", args=(forum.id, post.topic.id,)))
            else:
                return HttpResponseRedirect('../..')
        else:
            return render(request, template, {'form': form, 'forum': forum, 'topic': topic})
    else:
        form = PostCreateForm(user=request.user, forum=forum, topic=topic, parent=post)
        return render(request, template, {'form': form, 'forum': forum, 'topic': topic})


@login_required
def post_update(request, forum_id=None, topic_id=None, post_id=None, template="forum/post_update.html"):
    # TODO: if the content is not change, need to update update_at or not?
    forum = topic = post = None
    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
    if topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)
    if post_id:
        post = get_object_or_404(Post, pk=post_id)

    # check permission
    if not PostPermission(request.user).can_update_post(post):
        raise exceptions.PermissionDenied

    if request.POST:
        form = PostUpdateForm(instance=post, user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../..')
        else:
            return render(request, template, {'form': form, 'forum': forum, 'topic': topic})
    else:
        form = PostUpdateForm(instance=post)
        return render(request, template, {'form': form, 'forum': forum, 'topic': topic})


@login_required
def topic_create(request, forum_id=None, template="forum/topic_create.html"):
    return post_create(request, forum_id=forum_id, template=template)


@login_required
def vote_create(request, post_id=None):
    post = None
    if post_id:
        post = get_object_or_404(Post, pk=post_id)

    # Check user permission
    if not VotePermission(request.user).can_create_vote(post):
        raise exceptions.PermissionDenied

    # Check if user already vote this post
    user = request.user
    if already_voted(user, post):
        return JsonResponse({
            'success': 0,
            'message': 'You already voted'
        })

    if request.GET:
        vote_type = request.GET['type']
        vote = Vote(type=vote_type, post=post, created_by=request.user)
        vote.save()

        # Each upvote increases the user's contribution by 1
        if vote_type == Vote.UP_VOTE:
            voted_user_profile = post.created_by.profile
            voted_user_profile.contribution += 1
            voted_user_profile.save()

        return JsonResponse({
            'success': 1,
            'message': 'Vote successfully sent'
        })
    else:
        return JsonResponse({
            'success': 0,
            'message': 'Invalid request'
        })


def already_voted(user, post):
    return user.votes.filter(post=post).count() > 0


@login_required
def pin(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if TopicPermission(request.user).can_toggle_pin(topic):
        topic.is_pinned = True
        topic.save()
        messages.success(request, 'Chủ đề đã được ghim lên trang chủ')
    else:
        messages.warning(request, 'Bạn không có quyền thực hiện thao tác này')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def unpin(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if TopicPermission(request.user).can_toggle_pin(topic):
        topic.is_pinned = False
        topic.save()
        messages.success(request, 'Chủ đề đã được bỏ khỏi trang chủ')
    else:
        messages.warning(request, 'Bạn không có quyền thực hiện thao tác này')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def post_delete(request, post_id=None):
    if post_id:
        post = get_object_or_404(Post, pk=post_id)

    # check permission
    if not PostPermission(request.user).can_delete_post(post):
        raise exceptions.PermissionDenied

    if post.reply_on is not None:
        post.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        forum_id = post.topic.forum_id
        post.delete()
        # Now we can not redirect to previous page (because it no longer exist :( )
        return HttpResponseRedirect(reverse('forum:topic_list', args=(forum_id, )))
