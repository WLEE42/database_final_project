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


class Room(models.Model):
    """Reading Room"""

    # Fields
    rid = models.AutoField(max_length=4, primary_key=True, verbose_name='阅览室编号')
    rpos = models.CharField(max_length=30, verbose_name='阅览室位置')
    rname = models.CharField(max_length=30, verbose_name='阅览室名称')

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
    bimage = models.ImageField(upload_to="photos/%Y/%m/%d", null=True, verbose_name="图书封面图")
    bsummary = models.TextField(default="无描述", verbose_name="摘要")

    def get_absolute_url(self):
        """Return the url to access a particular book instance"""
        return reverse('book-detail', args=[str(self.bid)])

    def __str__(self):
        return "{}".format(self.bname)


class Bookcopy(models.Model):
    """A Book Copy Model"""

    class Meta:
        ordering = ['status']

    # Fields
    bcid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            help_text="Unique ID for this particular book across whole library", editable=False)
    loan_status = (
        ('m', 'Maintance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
    status = models.CharField(max_length=1, choices=loan_status, default='a', help_text='Book availability')

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookcopy')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, related_name='bookcopy')

    def __str__(self):
        return str(self.book.bname) + " " + str(self.bcid)


class Borrow(models.Model):
    """Book Borrow Record"""

    class Meta:
        get_latest_by = "returndate"
        ordering = ["isfinished", "-returndate"]

    boid = models.AutoField(max_length=15, primary_key=True)
    lenddate = models.DateField(default=now, verbose_name="借出时间")
    returndate = models.DateField(default=now, verbose_name="还书时间")
    isfinished = models.BooleanField(default=False, verbose_name="是否已还书")

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
    pemoney = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="罚款金额")
    pedate = models.DateField(default=now, verbose_name="罚款开始计算的时间")
    isfinished = models.BooleanField(default=False, verbose_name="是否提交罚款")
    # one to one
    borrow = models.OneToOneField(Borrow, on_delete=models.CASCADE, related_name="penalty")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="penalty")

    def __str__(self):
        return str(self.pid)


class Reserve(models.Model):
    """Book Reserve Record"""

    class Meta:
        get_latest_by = "adddate"
        ordering = ["status", "adddate"]

    reid = models.AutoField(max_length=10, primary_key=True)
    adddate = models.DateField(verbose_name="添加预约的时间", default=now)
    startdate = models.DateField(verbose_name="预约开始计算的时间", default=now)
    reserve_status = (
        ('a_a', 'Book Available'),
        ('b_w', 'Waited for Book return'),
        ('c_o', 'Reserve Outdated'),
        ('d_f', 'Reserve Finished'),
    )
    status = models.CharField(max_length=3, choices=reserve_status, default='b_w', verbose_name="预约状态",
                              help_text='Reserve availability')

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reserve")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reserve")

    def __str__(self):
        return str(self.reid)
