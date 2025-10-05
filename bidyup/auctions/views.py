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

from django.utils import timezone

#สำหรับใช้ celery ตอนตรวจจับว่าการประมูลจบ
from auctions.task import close_auction

#ใช้ตอนเช็คว่ามีราคาสูงสุดใหม่มั้ยโดนการเช็ค api
from django.http import JsonResponse

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
            user.role = form.cleaned_data.get("role")
            user.save()

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
            close_auction.apply_async(args=[item.id], eta=item.end_time)

            return redirect("index")

        return render(request, "create_listing.html", {"form": form})

class ListingDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        bids = item.bids.order_by("-amount")
        form = BidForm(current_price=item.current_price or item.starting_price)
        return render(request, "listing.html", {
            "item": item,
            "bids": bids,
            "form": form,
        })

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.status != "active":
            messages.error(request, "การประมูลนี้ปิดแล้ว")
            return redirect("listing", pk=item.pk)

        form = BidForm(request.POST, current_price=item.current_price or item.starting_price)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.item = item
            bid.bidder = request.user

            with transaction.atomic():
                item = Item.objects.select_for_update().get(pk=item.pk)
                bid.save()
                item.current_price = bid.amount
                item.save() 

            messages.success(request, f"✅ เสนอราคา {bid.amount} บาท สำเร็จ!")

            return redirect("listing", pk=item.pk)

        bids = item.bids.order_by("-amount")
        return render(request, "listing.html", {
            "item": item,
            "bids": bids,
            "form": form,
        })

def BidUpdateView(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    current_price = item.current_price or item.starting_price
    return JsonResponse({"current_price": float(current_price)})