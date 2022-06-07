from django.db import models
from django.conf import settings


# Create your models here.

# book_data.append({'master_seq': df['master_seq'][index], 'title': df['title'][index], 'img': df['img_url'][index],
#                   'description': df['description'][index], 'author': df['author'][index],'price': df['price'][index],'pub_date': df['pub_date_2'][index],
#                   'publisher': df['publisher'][index]})
class Book(models.Model):
    class Meta:
        db_table = "book"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=50)
    description = models.TextField()
    pub_date = models.DateField()
    like_users = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    img_url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    class Meta:
        db_table = "review"

    content = models.TextField()
    # star = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    book_master_seq = models.CharField(max_length=100)
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class BookData(models.Model):
    class Meta:
        db_table = "book_data"

    master_seq = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100, default='미정')
    price = models.CharField(max_length=100, default='없음')
    img_url = models.CharField(max_length=100, default='https://via.placeholder.com/150')
    description = models.CharField(max_length=100, default='없음')
    pub_date_2 = models.DateField(blank=True, default='', null=True)
