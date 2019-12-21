import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
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


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    # permission_required = ('book.can_look_detail',)
    model = Book


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = Borrow
    paginate_by = 10
    template_name = 'library/bookcopy_borrowed_user.html'

    # borrow_list = request.
    def get_context_data(self, **kwargs):
        context = super(LoanedBooksByUserListView, self).get_context_data(**kwargs)
        for borrow_record in Borrow.objects.filter(user_id__exact=self.request.user.id).filter(isfinished__exact=False):
            if datetime.date.today() > borrow_record.returndate:
                # 所有未还书但已逾期的记录
                Penalty.objects.update_or_create(borrow=borrow_record, user=self.request.user, defaults={
                    "pedate": borrow_record.returndate,
                    "pemoney": (datetime.date.today() - borrow_record.returndate).days})
        # 罚金总和
        context["pemoney"] = Penalty.objects.filter(user_id__exact=self.request.user.id).filter(
            isfinished__exact=False).aggregate(Sum("pemoney")).get('pemoney__sum')
        return context

    def get_queryset(self):
        borrow_list = Borrow.objects.filter(user_id__exact=self.request.user.id)
        return borrow_list


class Penalties(LoginRequiredMixin, generic.ListView):
    model = Penalty
    paginate_by = 10
    template_name = 'library/penalties_user.html'

    def get_context_data(self, **kwargs):
        context = super(Penalties, self).get_context_data(**kwargs)
        for borrow_record in Borrow.objects.filter(user_id__exact=self.request.user.id).filter(isfinished__exact=False):
            if datetime.date.today() > borrow_record.returndate:
                # 所有未还书但已逾期的记录
                Penalty.objects.update_or_create(borrow=borrow_record, user=self.request.user, defaults={
                    "pedate": borrow_record.returndate,
                    "pemoney": (datetime.date.today() - borrow_record.returndate).days})
        # 罚金总和
        context["pemoney"] = Penalty.objects.filter(user_id__exact=self.request.user.id).filter(
            isfinished__exact=False).aggregate(Sum("pemoney")).get('pemoney__sum')
        return context

    def get_queryset(self):
        return Penalty.objects.filter(user_id__exact=self.request.user.id)


class ReservedBook(LoginRequiredMixin, generic.ListView):
    model = Reserve
    paginate_by = 10
    template_name = 'library/reserves_user.html'

    def get_queryset(self):
        return Reserve.objects.filter(user_id__exact=self.request.user.id)


@login_required
def book_reserve(request):
    """书籍预约"""
    if request.method == "POST":
        bookcopy = Bookcopy.objects.get(bcid__exact=request.POST['bcid'])
        if bookcopy.status == 'o' or bookcopy.status == 'r':
            # 向Reserve表中添加一条记录
            _, created = Reserve.objects.get_or_create(book=bookcopy.book, user=request.user, isfinished=False)
            if not created:
                response = JsonResponse({"error": "不可重复预约"})
                response.status_code = 403
            # 修改status
            response = JsonResponse({"message": "succ"})
        else:
            response = JsonResponse({"error": "不可预约"})
            response.status_code = 403
        return response


@login_required
def book_borrow(request):
    """书籍借阅"""
    if request.method == "POST":
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            if borrow.bookcopy.status == 'a':
                borrow.user = request.user
                borrow.returndate = datetime.date.today() + relativedelta(months=3)
                # 更改Bookcopy的status
                Bookcopy.objects.filter(bcid__exact=borrow.bookcopy_id).update(status='o')
                borrow.save()
                response = JsonResponse({"message": "succ"})
            else:
                response = JsonResponse({"error": "书籍不可用"})
                response.status_code = 403
        else:
            response = JsonResponse({"error": "error"})
            response.status_code = 403
    return response


@login_required
def mybooks_renew(request):
    if request.method == "POST":
        borrow = Borrow.objects.filter(isfinished__exact=False).get(bookcopy__bcid__exact=request.POST['bcid'])
        if borrow.returndate - relativedelta(months=3) > borrow.lenddate:
            response = JsonResponse({"error": "最多只能续借六个月"})
            response.status_code = 403
        elif borrow.bookcopy.book.reserve:
            response = JsonResponse({"error": "该书已被预约，无法续借"})
            response.status_code = 403
        elif datetime.date.today() > borrow.returndate:
            response = JsonResponse({"error": "已逾期"})
            response.status_code = 403
        else:
            borrow.returndate += relativedelta(months=3)
            borrow.save()
            response = JsonResponse({"message": "succ"})
        return response


@login_required
def mybooks_return(request):
    if request.method == "POST":
        bookcopy = Bookcopy.objects.get(bcid__exact=request.POST['bcid'])
        if bookcopy.status == "o":
            borrow = Borrow.objects.filter(isfinished__exact=False).get(bookcopy__exact=bookcopy)
            # 此时，returndate为应该还书的时间
            if datetime.date.today() > borrow.returndate:
                Penalty.objects.update_or_create(borrow=borrow, user=request.user, defaults={
                    "pedate": borrow.returndate,
                    "pemoney": (datetime.date.today() - borrow.returndate).days})
            # 更新returndate为实际还书时间
            borrow.returndate = datetime.date.today()
            borrow.isfinished = True
            try:
                reserve = Reserve.objects.filter(isfinished__exact=False).filter(book=bookcopy.book).earliest()
            except Reserve.DoesNotExist:
                # 书籍未被预约
                bookcopy.status = "a"
            else:
                # 书籍被预约
                bookcopy.status = "r"
                # 处理预约
                reserve.isbookavaiable = True
                reserve.startdate = datetime.date.today()
                reserve.save()
                # 通知user,未实现
            borrow.save()
            bookcopy.save()
            response = JsonResponse({"message": "succ"})
        else:  # maintaince or avaible
            response = JsonResponse({"error": "该书籍未借出"})
            response.status_code = 403
        return response


@login_required
def reserve_borrow(request):
    return None


@login_required
def penalty_pay(request):
    return None
