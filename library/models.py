from django.db import models

class Author(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

class Genre(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, null=True)

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)
    isbn = models.CharField(max_length=32, unique=True)
    publication_year = models.IntegerField()
    genres = models.ManyToManyField(Genre, blank=True)
    co_authors = models.CharField(max_length=255, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)