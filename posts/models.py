from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import DEFAULT_DB_ALIAS, models


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    archive = models.BooleanField(default=False)
    publish = models.BooleanField(default=False)
    draft = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField(blank=False)


class PostTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=25)
    date_time = models.DateTimeField()
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)

    def save(self, force_insert=False, force_update=False, using=DEFAULT_DB_ALIAS, update_fields=None):
        """Override save method to issue notification for each transaction."""
        msg = str(self)
        email_super = User.objects.filter(is_superuser=True).values_list("email", flat=True)
        # send_mail(
        #     f"Hey Admin ",
        #     f"This is auto generated notification.\n{msg}\nNote - All date time is in UTC",
        #     None,
        #     email_super,
        # )
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"{self.date_time} - {self.user.username} {self.action} on post id {self.post.id}"
