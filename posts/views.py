from datetime import datetime

from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from posts.models import Post, PostTransaction
from posts.serializers import *


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Post details view for retrieving, updating or deleting a model instance."""

    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        """Get initial queryset

        Returns:
         - `superuser` -> all posts
         - `user` -> user posts
        """
        user = self.request.user
        queryset = Post.objects.all()
        if not user.is_superuser:
            queryset = Post.objects.filter(user=user)
        return queryset

    def put(self, request, *args, **kwargs):
        """Update post instance and log transaction in DB.

        Raises 403 if instance user is different.
        """
        instance = self.get_object()
        if request.user != getattr(instance, "user", None):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        with transaction.atomic():
            return_value = super().put(request, *args, **kwargs)
            log_transaction = PostTransaction(
                user=request.user, post=instance, action="UPDATE", date_time=datetime.today()
            )
            log_transaction.save()
        return return_value

    def patch(self, request, *args, **kwargs):
        """Update post instance and log transaction in DB.

        Raises 403 if instance user is different.
        """
        instance = self.get_object()
        if request.user != getattr(instance, "user", None):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        with transaction.atomic():
            return_value = super().patch(request, *args, **kwargs)
            log_transaction = PostTransaction(
                user=request.user, post=instance, action="UPDATE", date_time=datetime.today()
            )
            log_transaction.save()
        return return_value

    def delete(self, request, *args, **kwargs):
        """Delete post instance and log transaction in DB.

        403 is not raised since user gets its own post only.
        """
        with transaction.atomic():
            return_value = super().delete(request, *args, **kwargs)
            instance = self.get_object()
            log_transaction = PostTransaction(
                user=request.user, post=instance, action="DELETE", date_time=datetime.today()
            )
            log_transaction.save()
        return return_value


class ListCreatePostView(generics.ListCreateAPIView):
    """View for listing a queryset or creating a model instance."""

    permission_classes = [IsAdminUser]
    serializer_class = PostSerializer

    def get_queryset(self):
        """Filtering using query parameters in URL.

        Query Parameters:
        - category -> [publish, archive, draft]
        - username -> username
        """
        queryset = Post.objects.filter(user=self.request.user)
        if self.request.user.is_superuser:
            queryset = Post.objects.all()
        username = self.request.query_params.get("username")
        category = self.request.query_params.get("category")
        if username is not None:
            queryset = queryset.filter(user__username=username)
        if category is not None:
            queryset = queryset.filter(**{category: True})
        return queryset


class CreateUserView(generics.CreateAPIView):
    """View for creating a user instance."""

    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class PostLogView(generics.ListAPIView):
    """View for listing transactions."""

    queryset = PostTransaction.objects.all().order_by("date_time")
    serializer_class = PostLogSerializer
    permission_classes = [IsAdminUser]


class ArchivePostView(generics.UpdateAPIView):
    """Seprate view to mark post as archive.
    Done to prevent superuser from editing posts.
    """

    queryset = Post.objects.all()
    serializer_class = ArchivePostSerializer
    permission_classes = [IsAdminUser]

    def put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)


class PublicPostListView(generics.ListAPIView):
    """View to list all published posts."""

    serializer_class = PostSerializer
    queryset = Post.objects.filter(publish=True)
    permission_classes = [AllowAny]


class PublicPostView(generics.RetrieveAPIView):
    """View to see a  published post."""

    serializer_class = PostSerializer
    queryset = Post.objects.filter(publish=True)
    permission_classes = [AllowAny]
