from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .models import *


# Create your views here.


def index(request):
    num_books = Bookcopy.objects.all().count()
    num_borrowed_books = Bookcopy.objects.filter(status='o').count()
    num_in_books = Bookcopy.objects.filter(status='a').count()
    return render(request, 'library/index.html',
                  {'num_in_books': num_in_books, 'num_books': num_books, 'num_borrowed_books': num_borrowed_books})


class BookListView(generic.ListView):
    # pass
    model = Book
    paginate_by = 10

    # def get_queryset(self):
    #     return Book.objects.filter(bname__icontains='war')[:5]  # Get 5 books contianing the title war

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context


# def book_detail(request, book_id):
#     # book = get_object_or_404(Book, pk=book_id)
#     context = {'book': book}
#     return render(request, 'library/book_detail.html', context)


class BookDetailView(generic.DetailView):
    # pass
    model = Book


# @login_required
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = Bookcopy
    paginate_by = 10
    template_name = 'library/bookinstance_list_borrowed_user.html'

    # borrow_list = request.

    def get_queryset(self):
        # borrow_list = Bookcopy.borrow_set.filter
        # self.user = get_object_or_404(User, id = self.kwargs['id'])
        # borrow_ids = Borrow.filter(id=self.request.user).filter(isfinished = False).values_list('bcid', flat=True)
        # Bookcopy.objects.filter(bcid__in=borrow_ids)
        # return Bookcopy.
        return Bookcopy.objects.filter(status__exact='o').filter(borrow__id=self.request.user)


class BookCreate(PermissionsMixin, CreateView):
    model = Book
    fields = '__all__'


class BookUpdate(PermissionsMixin, UpdateView):
    model = Book
    fields = '__all__'


class BookDelete(PermissionsMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
