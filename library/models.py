from __future__ import unicode_literals

import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    uemail = models.EmailField(_('email address'), unique=True)
    uname = models.CharField(_('user name'), max_length=30)
    date_joined = models.DateTimeField(_('date joined'), default=now)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(_('active'), default=True)

    objects = UserManager()

    USERNAME_FIELD = 'uemail'
    REQUIRED_FIELDS = ['uname']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.uname

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.uname

    def __str__(self):
        return "{}".format(self.uname)

    # def email_user(self, subject, message, from_email=None, **kwargs):
    #     '''
    #     Sends an email to this User.
    #     '''
    #     send_mail(subject, message, from_email, [self.email], **kwargs)


# class Manager(models.Model):
#     mid = models.CharField(max_length=10, primary_key=True)
#     mpass = models.CharField(max_length=32)
#     mname = models.CharField(max_length=10)
#     madress = models.CharField(max_length=100)
#     mphone = models.CharField(max_length=11)
#
#
# class User(models.Model):
#     uid = models.CharField(max_length=10, primary_key=True)
#     upass = models.CharField(max_length=32)
#     uname = models.CharField(max_length=10)
#     uclass = models.CharField(max_length=100)
#     umoney = models.DecimalField(max_digits=5, decimal_places=2)
#     umail = models.EmailField(max_length=30)


class Room(models.Model):
    """Reading Room"""

    # Fields
    rid = models.AutoField(verbose_name='阅览室编号', max_length=4, primary_key=True)
    rpos = models.CharField(verbose_name='阅览室位置', max_length=30)
    rname = models.CharField(verbose_name='阅览室名称', max_length=30)

    def __str__(self):
        return "{}".format(self.rpos)


class Book(models.Model):
    """A Book Model"""

    class Meta:
        ordering = ["bname"]

    # Fields
    bid = models.AutoField(max_length=10, primary_key=True)
    bname = models.CharField(max_length=10, verbose_name="书名")
    bauthor = models.CharField(max_length=100, verbose_name="作者")
    bpubtime = models.DateField(help_text="出版时间", verbose_name="出版时间")
    bpubcomp = models.CharField(max_length=30, verbose_name="出版社")
    bimage = models.ImageField(verbose_name="图书封面图", upload_to="photos/%Y/%m/%d", null=True)
    bsummary = models.TextField(verbose_name="摘要", default="无描述")

    # bcount = models.IntegerField(verbose_name="总数")
    # bincount = models.IntegerField(verbose_name="在架数")
    # isin = models.BooleanField(verbose_name="是否在架", default=1)
    # isordered = models.BooleanField()

    def get_absolute_url(self):
        """Return the url to access a particular book instance"""
        return reverse('book-detail', args=[str(self.bid)])

    def __str__(self):
        return "{}".format(self.bname)


class Bookcopy(models.Model):
    """A Book Copy Model"""

    class Meta:
        ordering = ['status']
        # permissions = (("can_mark_returned", "Mark Book As Returned"),)

    # Fields
    bcid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            help_text="Unique ID for this particular book across whole library", editable=False)
    loan_status = (
        ('m', 'Maintance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
    status = models.CharField(max_length=1, choices=loan_status, default='m', help_text='Book availability')

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookcopy')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, related_name='bookcopy')

    def __str__(self):
        return str(self.book.bname) + str(self.bcid)

    # isordered = models.BooleanField()
    # bsummery = models.TextField(verbose_name="摘要", default="无描述")
    # rid = models.OneToOneField(Room, verbose_name="阅览室编号", null=True)


class Borrow(models.Model):
    """Book Borrow Record"""

    class Meta:
        get_latest_by = "lenddate"
        ordering = ["isfinished", "-lenddate"]

    boid = models.AutoField(max_length=15, primary_key=True)
    lenddate = models.DateField(verbose_name="借出时间", default=now)
    returndate = models.DateField(verbose_name="还书时间", default=now)
    isfinished = models.BooleanField(default=False)
    # expectdate = models.DateField(null=True)
    # pemoney = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bookcopy = models.ForeignKey(Bookcopy, on_delete=models.CASCADE, related_name="borrow")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrow")

    def __str__(self):
        return str(self.boid)


class Penalty(models.Model):
    """罚款记录"""

    class Meta:
        get_latest_by = "pedate"
        ordering = ["isfinished", "pedate"]

    pid = models.AutoField(max_length=10, primary_key=True)
    pemoney = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pedate = models.DateField(default=now)
    isfinished = models.BooleanField(default=False)
    # one to one
    borrow = models.OneToOneField(Borrow, related_name="penalty", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="penalty")

    def __str__(self):
        return str(self.pid)


class Reserve(models.Model):
    """Book Reserve Record"""

    class Meta:
        get_latest_by = "adddate"
        ordering = ["-isbookavailable", "adddate"]

    reid = models.AutoField(max_length=10, primary_key=True)
    adddate = models.DateField(verbose_name="添加预约的时间", default=now)
    startdate = models.DateField(verbose_name="预约开始计算的时间", default=now)
    isbookavailable = models.BooleanField(default=False)
    isfinished = models.BooleanField(default=False)
    # lenddate = models.DateField(verbose_name="借出时间", default=now)
    # returndate = models.DateField(null=True, default=now)
    # expectdate = models.DateField(null=True)
    # pemoney = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reserve")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reserve")

    def __str__(self):
        return str(self.reid)
