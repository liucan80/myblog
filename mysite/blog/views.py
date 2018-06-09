from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .models import Post
from .forms import EmailPostForm
from django.core.mail import send_mail

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 2)  # 3 posts in each page
    page = request.GET.get('page', 1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="published")
    sent=False
    cd = None
    if request == 'POST':
        # Form was submit
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url=request.build_absolute_uri(post.get_absolute_url())
            subject='{} ({}) recommends you reading "{}"'.format(cd['name'],cd['email'],post.title)
            message='Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title,post_url,cd['name'],cd['comments'])
            to_email='190633933@qq.com'
            from_email='liucan190633933@163.com'
            send_mail(subject,message,from_email,to_email,fail_silently=False)
            sent=True
            # send email
        else:
            form = EmailPostForm()
        return render(request, 'blog/post/share.html',
                      {'post': post,
                       'form': form,
                       'sent':sent,
                       'cd': cd})
