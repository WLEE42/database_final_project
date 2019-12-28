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
    """主页，图书馆基础信息"""
    num_books = Bookcopy.objects.all().count()
    num_borrowed_books = Bookcopy.objects.filter(status='r').count() + Bookcopy.objects.filter(status='o').count()
    num_in_books = Bookcopy.objects.filter(status='a').count()
    num_users = User.objects.count()
    return render(request, 'library/index.html',
                  {'num_in_books': num_in_books, 'num_books': num_books, 'num_borrowed_books': num_borrowed_books,
                   'num_users': num_users})


class register(generic.FormView):
    """用户注册"""
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
    """书籍列表"""
    model = Book
    paginate_by = 10


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    """书籍详细信息"""
    # permission_required = ('book.can_look_detail',)
    model = Book


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """用户借书列表"""
    model = Borrow
    paginate_by = 10
    template_name = 'library/bookcopy_borrowed_user.html'

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
    """用户罚款列表"""
    model = Penalty
    paginate_by = 10
    template_name = 'library/penalties_user.html'

    def get_context_data(self, **kwargs):
        context = super(Penalties, self).get_context_data(**kwargs)
        for borrow_record in Borrow.objects.filter(user=self.request.user).filter(isfinished=False):
            if datetime.date.today() > borrow_record.returndate:
                # 所有未还书但已逾期的记录
                Penalty.objects.update_or_create(borrow=borrow_record, user=self.request.user, defaults={
                    "pedate": borrow_record.returndate,
                    "pemoney": (datetime.date.today() - borrow_record.returndate).days})
        # 罚金总和
        context["pemoney"] = Penalty.objects.filter(user=self.request.user).filter(
            isfinished__exact=False).aggregate(Sum("pemoney")).get('pemoney__sum')
        return context

    def get_queryset(self):
        return Penalty.objects.filter(user_id__exact=self.request.user.id)


class ReservedBook(LoginRequiredMixin, generic.ListView):
    """用户预约列表"""
    model = Reserve
    paginate_by = 10
    template_name = 'library/reserves_user.html'

    def get_queryset(self):
        for reserve in Reserve.objects.filter(user=self.request.user).filter(status="b_w"):
            returndate = Borrow.objects.filter(bookcopy__book=reserve.book).first().returndate
            if not reserve.startdate == returndate:
                reserve.startdate = returndate
                reserve.save()
        return Reserve.objects.filter(user=self.request.user)


@login_required
def book_reserve(request):
    """书籍预约api"""
    if request.method == "POST":
        try:
            bookcopy = Bookcopy.objects.get(bcid__exact=request.POST['bcid'])
        except Bookcopy.DoesNotExist:
            # 书籍不存在
            response = JsonResponse({"result": "warning", "message": "书籍不存在"})
            return response
        if Bookcopy.objects.filter(book=bookcopy.book).filter(status="a").exists():
            # 有其他可用书籍
            response = JsonResponse({"result": "warning", "message": "有其他可用书籍"})
            return response
        if Borrow.objects.filter(user=request.user).filter(isfinished=False).filter(
                bookcopy__book=bookcopy.book).exists():
            # 用户不可在借书的同时预约同一本书
            response = JsonResponse({"result": "warning", "message": "用户不可在借书的同时预约同一本书"})
            return response
        if bookcopy.status == 'r':
            if Reserve.objects.filter(book=bookcopy.book).filter(user=request.user).filter(status='a_a').exists():
                # 书籍已可用，请去借书
                response = JsonResponse({"result": "warning", "message": "书籍已可用，请去借书"})
                return response
        if bookcopy.status == 'o' or bookcopy.status == 'r':
            # 向Reserve表中添加一条记录
            reserve, created = Reserve.objects.get_or_create(book=bookcopy.book, user=request.user, status='b_w')
            if not created:
                response = JsonResponse({"result": "warning", "message": "不可重复预约"})
                return response
            # 估算预约可用的时间
            reserve.startdate = Borrow.objects.filter(bookcopy__book=bookcopy.book).earliest().returndate
            reserve.save()
            # 修改status
            response = JsonResponse({"result": "success", "message": "预约成功"})
        else:
            response = JsonResponse({"result": "warning", "message": "书籍状态不可预约"})
        return response


@login_required
def book_borrow(request):
    """书籍借阅api"""
    if request.method == "POST":
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            if Borrow.objects.filter(user=request.user).filter(isfinished=False).filter(
                    bookcopy__book=borrow.bookcopy.book).exists():
                # 用户不可在借书的同时借同一本书
                response = JsonResponse({"result": "warning", "message": "用户不可在借书的同时借同一本书"})
                return response
            if borrow.bookcopy.status == 'a':
                # 书籍可用
                borrow.user = request.user
                borrow.returndate = datetime.date.today() + relativedelta(months=3)
                # 更改Bookcopy的status
                Bookcopy.objects.filter(bcid__exact=borrow.bookcopy_id).update(status='o')
                borrow.save()
                response = JsonResponse({"result": "success", "message": "借书成功"})
            else:
                response = JsonResponse({"result": "warning", "message": "书籍不可用"})
        else:
            response = JsonResponse({"result": "warning", "message": "bookcopy bcid不正确"})
        return response


@login_required
def mybooks_renew(request):
    """书籍续订api"""
    if request.method == "POST":
        borrow = Borrow.objects.filter(isfinished__exact=False).get(bookcopy__bcid__exact=request.POST['bcid'])
        try:
            borrow.bookcopy.book.reserve
        except Reserve.DoesNotExist:
            response = JsonResponse({"result": "warning", "message": "该书已被预约，无法续借"})
        else:
            if borrow.returndate - relativedelta(months=5) > borrow.lenddate:
                response = JsonResponse({"result": "warning", "message": "最多只能续借六个月"})
            elif datetime.date.today() > borrow.returndate:
                response = JsonResponse({"result": "warning", "message": "已逾期"})
            else:
                borrow.returndate += relativedelta(months=3)
                borrow.save()
                response = JsonResponse({"result": "success", "message": "续订成功"})
        return response


@login_required
def mybooks_return(request):
    """书籍归还api"""
    if request.method == "POST":
        bookcopy = Bookcopy.objects.get(bcid__exact=request.POST['bcid'])
        if bookcopy.status == "o":
            borrow = Borrow.objects.filter(isfinished__exact=False).get(bookcopy__exact=bookcopy)
            # 此时，returndate为应该还书的时间，通过应还书时间与现在时间计算罚金
            if datetime.date.today() > borrow.returndate:
                Penalty.objects.update_or_create(borrow=borrow, user=request.user, defaults={
                    "pedate": borrow.returndate,
                    "pemoney": (datetime.date.today() - borrow.returndate).days})
            # 更新returndate为实际还书时间
            borrow.returndate = datetime.date.today()
            borrow.isfinished = True
            try:
                reserve = Reserve.objects.filter(status="b_w").filter(book=bookcopy.book).earliest()
            except Reserve.DoesNotExist:
                # 书籍未被预约
                bookcopy.status = "a"
            else:
                # 书籍被预约，通知用户
                # reserve.user.email_user() 未实现
                bookcopy.status = "r"
                # 处理预约
                reserve.status = "a_a"
                reserve.startdate = datetime.date.today()
                reserve.save()
            borrow.save()
            bookcopy.save()
            response = JsonResponse({"result": "success", "message": "还书成功"})
        else:  # maintaince or avaible
            response = JsonResponse({"result": "warning", "message": "该书籍未借出"})
        return response


@login_required
def reserve_borrow(request):
    """预约记录完成借书api"""
    if request.method == "POST":
        try:
            reserve = Reserve.objects.get(reid__exact=request.POST['reid'])
        except Reserve.DoesNotExist:
            response = JsonResponse({"result": "warning", "message": "记录不存在"})
            return response
        if reserve.status == "c_o":
            response = JsonResponse({"result": "warning", "message": "预约已过期"})
        elif reserve.status == "b_w":
            response = JsonResponse({"result": "warning", "message": "该书未还，无法借阅"})
        elif reserve.status == "d_f":
            response = JsonResponse({"result": "warning", "message": "预约已完成，不能继续借书"})
        else:
            reserve.status = "d_f"
            # 预约完成借阅
            bookcopy = reserve.book.bookcopy_set.filter(status='r').first()
            # first()指被预约的bookcopy中的任意一个
            bookcopy.status = 'o'
            # 更新bookcopy的status
            reserve.save()
            bookcopy.save()
            # 创建borrow记录
            Borrow.objects.create(bookcopy=bookcopy, user=request.user,
                                  returndate=datetime.date.today() + relativedelta(months=3))
            response = JsonResponse({"result": "success", "message": "预约借书成功"})
        return response


@login_required
def penalty_pay(request):
    """支付罚款"""
    if request.method == "POST":
        try:
            penalty = Penalty.objects.get(pid__exact=request.POST['pid'])
        except Penalty.DoesNotExist:
            response = JsonResponse({"result": "warning", "message": "记录不存在"})
            return response
        if penalty.isfinished:
            response = JsonResponse({"result": "warning", "message": "罚款已缴纳"})
        elif not penalty.borrow.isfinished:
            response = JsonResponse({"result": "warning", "message": "请先还书"})
        else:
            penalty.isfinished = True
            penalty.save()
            response = JsonResponse({"result": "success", "message": "缴纳罚金成功"})
        return response
