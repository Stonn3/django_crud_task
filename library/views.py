import json
from datetime import date

from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DeleteView
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator

from .models import Book, Author, Genre


# ---------- HTML: Books (CBV) ----------

class BookListView(ListView):
    model = Book
    template_name = "library/book_list.html"
    context_object_name = "books"


class BookCreateView(CreateView):
    model = Book
    fields = ["title", "author", "isbn", "publication_year", "genres", "co_authors", "summary"]
    template_name = "library/book_form.html"
    success_url = reverse_lazy("book_list")


class BookDetailUpdateView(View):
    template_name = "library/book_detail.html"

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        authors = Author.objects.all()
        genres = Genre.objects.all()
        return render(request, self.template_name, {"book": book, "authors": authors, "genres": genres})

    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        book.title = request.POST.get("title") or ""
        book.author_id = request.POST.get("author") or None
        book.isbn = request.POST.get("isbn") or ""
        book.publication_year = int(request.POST.get("publication_year") or 0)
        book.co_authors = request.POST.get("co_authors") or ""
        book.summary = request.POST.get("summary") or ""
        book.save()

        book.genres.set(request.POST.getlist("genres"))
        return redirect("book_list")

    @method_decorator(csrf_exempt)
    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return JsonResponse({"deleted": True})


class BookDeleteView(DeleteView):
    model = Book
    template_name = "library/book_confirm_delete.html"
    success_url = reverse_lazy("book_list")


# ---------- helpers (Authors JSON) ----------

def _author_to_dict(a: Author) -> dict:
    return {
        "id": a.id,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "bio": a.bio,
        "birth_date": a.birth_date.isoformat() if a.birth_date else None,
    }


def _parse_birth_date(value):
    if value in (None, "", "null"):
        return None
    if isinstance(value, date):
        return value
    d = parse_date(str(value))
    if d is None:
        raise ValueError("birth_date must be YYYY-MM-DD")
    return d


def _read_json(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")


# ---------- JSON: Authors ----------

@csrf_exempt
def authors_collection(request):
    if request.method == "GET":
        authors = [_author_to_dict(a) for a in Author.objects.all().order_by("id")]
        return JsonResponse(authors, safe=False)

    if request.method == "POST":
        try:
            payload = _read_json(request)
            birth_date = _parse_birth_date(payload.get("birth_date"))
        except ValueError as e:
            return HttpResponseBadRequest(str(e))

        a = Author.objects.create(
            first_name=payload.get("first_name", ""),
            last_name=payload.get("last_name", ""),
            bio=payload.get("bio"),
            birth_date=birth_date,
        )
        return JsonResponse(_author_to_dict(a), status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def author_item(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    if request.method == "GET":
        return JsonResponse(_author_to_dict(author))

    if request.method == "PUT":
        try:
            payload = _read_json(request)
            if "birth_date" in payload:
                author.birth_date = _parse_birth_date(payload.get("birth_date"))
        except ValueError as e:
            return HttpResponseBadRequest(str(e))

        if "first_name" in payload:
            author.first_name = payload.get("first_name") or ""
        if "last_name" in payload:
            author.last_name = payload.get("last_name") or ""
        if "bio" in payload:
            author.bio = payload.get("bio")

        author.save()
        return JsonResponse(_author_to_dict(author))

    if request.method == "DELETE":
        author.delete()
        return JsonResponse({"deleted": True})

    return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])