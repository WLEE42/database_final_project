from django.conf.urls import url, include

# from library.views import BookBorrowView
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^books/$', views.BookListView.as_view(), name="books"),
    # url('^book/create/$', views.BookCreate.as_view(), name="book-create"),
    url('book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),
    # url('^book/borrow/$', require_POST(BookBorrowView.as_view()), name='book-borrow'),
    url('^book/(?P<pk>\d+)/update/$', views.book_update, name='book-update'),
    # url('book/(?P<pk>\d+)/delete/$', views.BookDelete.as_view(), name='book-delete'),
    url('accounts/', include('django.contrib.auth.urls')),
    url('^accounts/register/$', views.register.as_view(), name="register"),
    url('^mybooks/$', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
]
