from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import serializers

from .models import Post, PostTransaction

UserModel = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    """Serialize Post model. Includes all fields."""

    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="username")

    def create(self, validated_data):
        """Override create method to log the transaction before saving"""
        request = self.context["request"]
        user_instance = request.user
        validated_data["user"] = user_instance
        with transaction.atomic():
            return_value = super().create(validated_data)
            log_transaction = PostTransaction(
                user=request.user, post=return_value, action="CREATE", date_time=datetime.today()
            )
            log_transaction.save()
        return return_value

    class Meta:
        fields = "__all__"
        model = Post


class UserSerializer(serializers.ModelSerializer):
    send_invite = serializers.BooleanField(required=True, write_only=True, initial=True)

    def create(self, validated_data):
        """Override create method to send credentials to created user.
        Uses send_invite flag to decide.

        """
        invite = validated_data.pop("send_invite")
        # Set a randomly generated password
        psswd = get_random_string(15)
        email = validated_data.get("email", None)
        uname = validated_data.get("username", None)
        validated_data["password"] = psswd

        with transaction.atomic():
            # if invite:
            #     send_mail(
            #         f"Welocme {uname} to BeyondIRR",
            #         f"We invite you to write blog psts on our website.\nYour current username and password is {uname}, {psswd}. We advice you to change it as soon as you login",
            #         None,
            #         [email],
            #     )
            return UserModel.objects.create_user(**validated_data)

    class Meta:
        model = UserModel
        fields = ["username", "email", "first_name", "last_name", "send_invite"]


class PostLogSerializer(serializers.ModelSerializer):
    """Serialize PostTransaction model. Includes all fields."""

    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="username")

    class Meta:
        model = PostTransaction
        fields = "__all__"


class ArchivePostSerializer(serializers.ModelSerializer):
    """Serialize Post model. Includes archive field only for superuser edits."""

    archive = serializers.BooleanField(write_only=True, initial=True)

    class Meta:
        model = Post
        fields = ["archive"]
