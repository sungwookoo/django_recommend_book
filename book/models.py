from django.db import models
from django.conf import settings


# Create your models here.
class BookData(models.Model):
    class Meta:
        db_table = "book_data"

    master_seq = models.IntegerField(blank=False, null=False)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100, default='미정')
    price = models.CharField(max_length=100, default='없음')
    img_url = models.CharField(max_length=100, default='https://via.placeholder.com/150')
    description = models.CharField(max_length=100, default='없음')
    pub_date_2 = models.DateField(blank=True, default='', null=True)


class Like(models.Model):
    class Meta:
        db_table = "like"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(BookData, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    class Meta:
        db_table = "review"

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    book_master_seq = models.ForeignKey(BookData, on_delete=models.CASCADE)
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
