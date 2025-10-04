from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('create', views.CreateView.as_view(), name='create_listing'),
#     path('listing/<int:listing_id>', views.listing, name='listing'),
#     path('categories', views.categories, name='categories'),
#     path('categories/<str:category_name>', views.category_listings, name='category_listings'),
#     path('watchlist', views.watchlist, name='watchlist'),
#     path('watchlist/<int:listing_id>', views.toggle_watchlist, name='toggle_watchlist'),
#     path('close_listing/<int:listing_id>', views.close_listing, name='close_listing'),
#     path('comment/<int:listing_id>', views.add_comment, name='add_comment'),
#     path('bid/<int:listing_id>', views.place_bid, name='place_bid'),
#     path('profile/<str:username>', views.profile, name='profile'),
#     path('profile/<str:username>/watchlist', views.profile_watchlist, name='profile_watchlist'),
#     path('profile/<str:username>/listings', views.profile_listings, name='profile_listings'),
#     path('profile/<str:username>/comments', views.profile_comments, name='profile_comments'),
#     path('profile/<str:username>/bids', views.profile_bids, name='profile_bids'),
#     path('profile/<str:username>/won_auctions', views.profile_won_auctions, name='profile_won_auctions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
