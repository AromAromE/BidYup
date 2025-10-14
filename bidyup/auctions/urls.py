from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("create", views.CreateView.as_view(), name="create_listing"),
    path("item/<int:pk>", views.ListingDetailView.as_view(), name="listing"),
    path("api/item/<int:item_id>/current_and_bids/", views.CurrentdBidsAPIView, name='current_bids'),
    path("item/<int:pk>/update/", views.UpdateItemView.as_view(), name='update_item'),
    path("item/<int:pk>/delete/", views.DeleteItemView.as_view(), name='delete_item'),
    path("item/<int:pk>/end/", views.EndAuctionView.as_view(), name="endlist"),
    path("myitem/", views.MyItemView.as_view(), name="myitem"),
    path("my-bids/", views.MyBidView.as_view(), name="my-bids"),
    path("profile/<int:pk>", views.ProfileView.as_view(), name="profile"),
    path("change_password/", views.ChangePasswordView.as_view(), name="change_password"),
    path("favorites/<int:pk>/", views.FavouriteView.as_view(), name="favorites"),
    path("item/<int:pk>/toggle_favourite/", views.ToggleFavouriteView.as_view(), name='toggle_favourite'),
    path("status/seller/", views.SellerStatusView.as_view(), name="status-seller"),
    path("status/buyer/", views.BuyerStatusView.as_view(), name="status-buyer"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
