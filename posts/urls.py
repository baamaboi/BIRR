from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path("api/log/", views.PostLogView.as_view(), name="post-log"),
    path("api/posts/", views.ListCreatePostView.as_view(), name="post"),
    path("api/posts/<str:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("api/posts/archive/<str:pk>/", views.ArchivePostView.as_view(), name="post-archive"),
    path("posts/", views.PublicPostListView.as_view(), name="public-post-list"),
    path("posts/view/", views.PublicPostView.as_view(), name="public-post-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
