from django.db import models
from django.urls import reverse


# Create your models here.


class Manager(models.Model):
    mid = models.CharField(max_length=10, primary_key=True)
    mpass = models.CharField(max_length=32)
    mname = models.CharField(max_length=10)
    madress = models.CharField(max_length=100)
    mphone = models.CharField(max_length=11)


class User(models.Model):
    uid = models.CharField(max_length=10, primary_key=True)
    upass = models.CharField(max_length=32)
    uname = models.CharField(max_length=10)
    uclass = models.CharField(max_length=100)
    umoney = models.DecimalField(max_digits=5, decimal_places=2)
    umail = models.EmailField(max_length=30)


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
    expectdate = models.DateField(null=True)
    pemoney = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bcid = models.ForeignKey(Bookcopy, null=True)
    uid = models.ForeignKey(User, null=True)

# class Penalty(models.Model):
#     """罚款记录"""
#
#     peid = models.AutoField(max_length=10, primary_key=True)
#     boid = models.OneToOneField(Borrow)
#     pemoney = models.DecimalField(max_digits=5, decimal_places=2)
#     pedate = models.DateField()
