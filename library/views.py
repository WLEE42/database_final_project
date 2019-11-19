import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.views import generic
from django.views.generic.edit import FormMixin

from library.forms import CustomUserCreationForm, BorrowForm
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


class BookDetailView(FormMixin, generic.DetailView):
    # pass
    # permission_required = ('book.can_look_detail',)
    model = Book
    form_class = BorrowForm

    def get_success_url(self):
        return reverse('my-borrowed', kwargs={})

    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            post = form.save(commit=False)
            post.returndate = datetime.date.today() + relativedelta(months=3)
            Bookcopy.objects.filter(bcid__exact=post.bcid_id).update(status='o')
            post.save()
            return
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(BookDetailView, self).form_valid(form)


# class BookBorrowView(LoginRequiredMixin, generic.FormView):
#     form_class = BorrowForm


# @login_required
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = Bookcopy
    paginate_by = 10
    template_name = 'library/bookcopy_list_borrowed_user.html'

    # borrow_list = request.

    def get_queryset(self):
        # borrow_list = Bookcopy.borrow_set.filter
        # self.user = get_object_or_404(User, id = self.kwargs['id'])
        # borrow_ids = Borrow.filter(id=self.request.user).filter(isfinished = False).values_list('bcid', flat=True)
        # Bookcopy.objects.filter(bcid__in=borrow_ids)
        # return Bookcopy.
        # queryset = Bookcopy.objects.filter(status__exact='o')
        # query2 = queryset.filter(borrow__id=self.request.user)
        return Bookcopy.objects.filter(status__exact='o').filter(borrow__id=self.request.user)


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = Bookcopy
    permission_required = 'bookcopy.can_mark_returned'
    template_name = 'library/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return Bookcopy.objects.filter(status__exact='o').order_by('due_back')


class register(generic.FormView):
    template_name = "library/register.html"
    form_class = CustomUserCreationForm
    success_url = "/accounts/login"

    def form_valid(self, form):
        uemail = form.cleaned_data['uemail']
        password = form.cleaned_data['password2']
        user = User.objects.create_user(uemail=uemail, password=password)
        return super().form_valid(form)


def book_update(request, pk):
    book = Book.objects.get(bid=pk)
    BookInlineFormSet = inlineformset_factory(Book, Bookcopy, fields=('rid',))
    if request.method == "POST":
        formset = BookInlineFormSet(request.POST, request.FILES, instance=book)
        if formset.is_valid():
            return HttpResponseRedirect(book.get_absolute_url())
    else:
        formset = BookInlineFormSet(instance=book)
    return render(request, 'manage_books.html', {'formset': formset})
