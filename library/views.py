import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import generic

from library.forms import CustomUserCreationForm, BorrowForm
from .models import *


# Create your views here.


def index(request):
    num_books = Bookcopy.objects.all().count()
    num_borrowed_books = Bookcopy.objects.filter(status='r').count() + Bookcopy.objects.filter(status='o').count()
    num_in_books = Bookcopy.objects.filter(status='a').count()
    num_users = User.objects.count()
    return render(request, 'library/index.html',
                  {'num_in_books': num_in_books, 'num_books': num_books, 'num_borrowed_books': num_borrowed_books,
                   'num_users': num_users})


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    # def get_queryset(self):
    #     return Book.objects.filter(bname__icontains='war')[:5]  # Get 5 books contianing the title war

    # def get_context_data(self, **kwargs):
    # Call the base implementation first to get the context
    # context = super(BookListView, self).get_context_data(**kwargs)
    # Create any data and add it to the context
    # context['some_data'] = 'This is just some data'
    # return context


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    # permission_required = ('book.can_look_detail',)
    model = Book

    # def get_context_data(self, **kwargs):
    #     context = super(BookDetailView, self).get_context_data(**kwargs)
    #        context['form'] = self.get_form()
    # return context
    # form_class = BorrowForm

    # def get_success_url(self):
    #     return reverse('book-detail', kwargs={})

    # def post(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return HttpResponseForbidden()
    #     # self.object = self.get_object()
    #     # form = self.get_form()
    #     form = BorrowForm(request.POST)
    #     if form.is_valid():
    #         post = form.save(commit=False)
    #         post.id = self.request.user
    #         post.returndate = datetime.date.today() + relativedelta(months=3)
    #         Bookcopy.objects.filter(bcid__exact=post.bcid_id).update(status='o')
    #         post.save()
    #         return
    #     else:
    #         return self.form_invalid(form)

    # def form_valid(self, form):
    #     return super(BookDetailView, self).form_valid(form)


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = Borrow
    paginate_by = 10
    template_name = 'library/bookcopy_borrowed_user.html'

    # borrow_list = request.
    def get_context_data(self, **kwargs):
        context = super(LoanedBooksByUserListView, self).get_context_data(**kwargs)
        sum = 0
        for borrow_record in context['borrow_list']:
            sum += borrow_record.pemonery
        context["pemoney"] = sum
        return context

    def get_queryset(self):
        # return Bookcopy.objects.filter(borrow__isfinished__exact=False).filter(status__exact='o').filter(borrow__id=self.request.user)
        borrow_list = Borrow.objects.filter(id_id=self.request.user)
        for borrow_recode in borrow_list.filter(isfinished__exact=False):
            if datetime.date.today() > borrow_recode.returndate:
                borrow_recode.pemoney = (datetime.date.today() - borrow_recode.returndate).days
        return borrow_list


# class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
#     """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
#     model = Bookcopy
#     permission_required = 'bookcopy.can_mark_returned'
#     template_name = 'library/bookinstance_list_borrowed_all.html'
#     paginate_by = 10
#
#     def get_queryset(self):
#         return Bookcopy.objects.filter(status__exact='o').order_by('due_back')


class register(generic.FormView):
    template_name = "library/register.html"
    form_class = CustomUserCreationForm
    success_url = "/accounts/login"

    def form_valid(self, form):
        form.save()
        uemail = form.cleaned_data.get('uemail')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(uemail=uemail, password=raw_password)
        login(self.request, user)
        return redirect('index')


# def book_update(request, pk):
#     book = Book.objects.get(bid=pk)
#     BookInlineFormSet = inlineformset_factory(Book, Bookcopy, fields=('rid',))
#     if request.method == "POST":
#         formset = BookInlineFormSet(request.POST, request.FILES, instance=book)
#         if formset.is_valid():
#             return HttpResponseRedirect(book.get_absolute_url())
#     else:
#         formset = BookInlineFormSet(instance=book)
#     return render(request, 'manage_books.html', {'formset': formset})


@login_required
def book_reserve(request):
    if request.method == "POST":
        bookcopy = Bookcopy.objects.filter(bcid__exact=request.POST.bcid_id)
        # if bookcopy
        # 修改status
        response = JsonResponse({"message": "succ"})
        return response


@login_required
def book_borrow(request):
    if request.method == "POST":
        form = BorrowForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.id = request.user
            post.returndate = datetime.date.today() + relativedelta(months=3)
            Bookcopy.objects.filter(bcid__exact=post.bcid_id).update(status='o')
            post.save()
            response = JsonResponse({"message": "succ"})
        else:
            response = JsonResponse({"error": "error"})
            response.status_code = 403
    return response


@login_required
def mybooks_renew(request):
    if request.method == "POST":
        # bookcopy = Bookcopy.objects.get(bcid__exact=request.POST['bcid'])
        borrow = Borrow.objects.filter(bcid__exact=request.POST['bcid']).latest()
        if datetime.date.today() > borrow.returndate:
            data = {"error": "已逾期"}
        elif borrow.returndate - relativedelta(months=3) > borrow.lenddate:
            data = {"error": "最多只能续借六个月"}
        else:
            borrow.returndate += relativedelta(months=3)
            borrow.save()
            data = {"message": "succ"}
        return JsonResponse(data)


@login_required
def mybooks_return(request):
    if request.method == "POST":
        bookcopy = Bookcopy.objects.get(bcid__exact=request.POST['bcid'])
        if bookcopy.status == "r":
            borrow = Borrow.objects.filter(bcid__exact=request.POST['bcid']).latest()
            bookcopy.status = "a"
            if datetime.date.today() > borrow.returndate:
                borrow.pemoney = (datetime.date.today() - borrow.returndate).days
            borrow.returndate = datetime.date.today()
            borrow.isfinished = True
            response = JsonResponse({"message": "succ"})
        elif bookcopy.status == "o":
            borrow = Borrow.objects.filter(bcid__exact=request.POST['bcid']).latest()
            bookcopy.status = "a"
            if datetime.date.today() > borrow.returndate:
                borrow.pemoney = (datetime.date.today() - borrow.returndate).days
            borrow.returndate = datetime.date.today()
            borrow.isfinished = True
            response = JsonResponse({"message": "succ"})
        else:  # maintaince or avaible
            response = JsonResponse({"error": "succ"})
            response.status_code = 403
        return response


class Penalties(LoginRequiredMixin, generic.ListView):
    pass


class ReservedBook(LoginRequiredMixin, generic.ListView):
    pass
