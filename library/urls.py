from django.urls import path
from . import views

urlpatterns = [
    # HTML Books
    path("books/", views.BookListView.as_view(), name="book_list"),
    path("books/new/", views.BookCreateView.as_view(), name="book_create"),
    path("books/<int:pk>/", views.BookDetailUpdateView.as_view(), name="book_detail_update"),
    path("books/<int:pk>/delete/", views.BookDeleteView.as_view(), name="book_delete"),

    # JSON Authors
    path("authors/", views.authors_collection, name="authors_collection"),
    path("authors/<int:author_id>/", views.author_item, name="author_item"),
]