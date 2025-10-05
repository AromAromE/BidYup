from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout
from .forms import LoginForm, CreateForm, RegisterForm, BidForm
from .models import Item, Bid
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
User = get_user_model()

class IndexView(View):
    def get(self, request):
        items = Item.objects.filter(status="active").order_by("-created_at")
        return render(request, "index.html", {"items": items})

class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()  # save the user first

            role = form.cleaned_data.get("role")
            group, created = Group.objects.get_or_create(name=role.capitalize())
            user.groups.add(group)

            return redirect("login")

        return render(request, "register.html", {"form": form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("index")
        form = LoginForm()  
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
        else:
            return render(request, "login.html", {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("index")

class CreateView(View):
    def get(self, request):
        form = CreateForm()
        return render(request, "create_listing.html", {"form": form})
    
    def post(self, request):
        form = CreateForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect("index")
        return render(request, "create_listing.html", {"form": form})

class ListingDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        bids = item.bids.order_by("-amount")
        return render(request, "listing.html", {"item": item, "bids": bids})

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        bids = item.bids.order_by("-amount")

        bid_amount = request.POST.get("bid_amount")
        if bid_amount:
            try:
                bid_amount = float(bid_amount)
            except ValueError:
                messages.error(request, "❌ ราคาที่กรอกไม่ถูกต้อง")
                return redirect("listing", pk=item.pk)

            with transaction.atomic():
                item = Item.objects.select_for_update().get(pk=item.pk)
                current_price = item.current_price or item.starting_price

                if bid_amount <= current_price:
                    messages.error(request, f"❌ การเสนอราคาต้องสูงกว่าราคาปัจจุบัน ({current_price})")
                else:
                    Bid.objects.create(amount=bid_amount, item=item, bidder=request.user)
                    item.current_price = bid_amount
                    item.save()
                    messages.success(request, f"✅ เสนอราคา {bid_amount} บาท สำเร็จ!")

        return redirect("listing", pk=item.pk)