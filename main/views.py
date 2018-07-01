import os
from django.shortcuts import render
from django.views import generic
from .models import Post

# Create your views here.

class IndexView(generic.TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(status=0).order_by('-created_at').values()
        images = Post.objects.filter(status=0).order_by('-created_at').only('image_path')

        context['posts'] = posts
        context['images'] = images
        context['zip'] = zip(posts, images)

        return context
