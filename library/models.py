from __future__ import unicode_literals

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
    uname = models.CharField(_('user name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=now)
    is_active = models.BooleanField(_('active'), default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'uemail'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_name(self):
        '''Return name'''

    def __str__(self):
        return self.uemail

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        return self.uname
        # full_name = '%s %s' % (self.first_name, self.last_name)
        # return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.uname
        # return self.first_name

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
    rid = models.AutoField(max_length=4, primary_key=True)
    rpos = models.CharField(max_length=30)
    rname = models.CharField(max_length=30)


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
    # bcount = models.IntegerField(verbose_name="总数")
    # bincount = models.IntegerField(verbose_name="在架数")
    # isin = models.BooleanField(verbose_name="是否在架", default=1)
    # isordered = models.BooleanField()
    bsummery = models.TextField(verbose_name="摘要", default="无描述")

    def get_absolute_url(self):
        """Return the url to access a particular book instance"""
        return reverse('book-detail', args=[str(self.bid)])


import uuid


class Bookcopy(models.Model):
    """A Book Copy Model"""

    class Meta:
        ordering = ['status']

    # Fields
    bcid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            help_text="Unique ID for this particular book across whole library")
    loan_status = (
        ('m', 'Maintance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
    status = models.CharField(max_length=1, choices=loan_status, blank=True, default='m', help_text='Book availability')
    bid = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    rid = models.ForeignKey(Room, null=True)
    # isordered = models.BooleanField()
    # bsummery = models.TextField(verbose_name="摘要", default="无描述")
    # rid = models.OneToOneField(Room, verbose_name="阅览室编号", null=True)


class Borrow(models.Model):
    """Book Borrow Record"""

    class Meta:
        ordering = ["lenddate"]

    boid = models.AutoField(max_length=15, primary_key=True)
    lenddate = models.DateField(verbose_name="借出时间")
    returndate = models.DateField(null=True)
    isfinished = models.BooleanField(default=False)
    # expectdate = models.DateField(null=True)
    pemoney = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bcid = models.ForeignKey(Bookcopy, null=True, related_name="borrow")
    id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

# class Penalty(models.Model):
#     """罚款记录"""
#
#     peid = models.AutoField(max_length=10, primary_key=True)
#     boid = models.OneToOneField(Borrow)
#     pemoney = models.DecimalField(max_digits=5, decimal_places=2)
#     pedate = models.DateField()
