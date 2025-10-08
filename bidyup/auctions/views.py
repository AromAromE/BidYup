from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout
from .forms import LoginForm, CreateForm, RegisterForm, BidForm, ProfileForm
from .models import *
from django.db.models import Count

from django.db import transaction

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.utils import timezone
from django.core.exceptions import PermissionDenied
#สำหรับใช้ celery ตอนตรวจจับว่าการประมูลจบ
from auctions.task import close_auction
#ส่งเมลที่ตัว seller กดปิดเอง
from django.conf import settings
from django.core.mail import send_mail
#ใช้ตอนเช็คว่ามีราคาสูงสุดใหม่มั้ยโดนการเช็ค api
from django.http import JsonResponse

# Create your views here.
User = get_user_model()

class IndexView(View):
    def get(self, request):
        cat = request.GET.get("cat", "")
        category_id = request.GET.get("category", "")

        items = Item.objects.filter(status="active").order_by("-created_at")

        if cat:
            items = items.filter(title__icontains=cat)

        if category_id:
            items = items.filter(category_id=category_id)

        categories = Category.objects.annotate(ic=Count('items'))

        return render(request, "index.html", {"items": items, "categories": categories,})

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
        return redirect("login")

class CreateView(PermissionRequiredMixin, View):
    permission_required = ["auctions.add_item"]
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
class UpdateItemView(View):
    def get(self, request, pk):
        item = Item.objects.get(pk=pk)
        form = CreateForm(instance=item)

        if item.seller != request.user:
            raise PermissionDenied
    
        return render(request, "update_item.html", {"form": form, "item": item})
    
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        form = CreateForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("listing", pk=item.pk)
        return render(request, "update_item.html", {"form": form, "pk": pk})

class DeleteItemView(View):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.seller != request.user and not request.user.is_staff:
            raise PermissionDenied

        return render(request, "delete_item.html", {"item": item})
    
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.seller != request.user and not request.user.is_staff:
            raise PermissionDenied
    
        item.delete()
        return redirect("index")
    
class EndAuctionView(View):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.seller != request.user:
            raise PermissionDenied

        return render(request, "endlist.html", {"item": item})
        
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.seller != request.user:
            raise PermissionDenied
        try:
            with transaction.atomic():  # ทำให้ทุกอย่างในบล็อกนี้เป็น transaction
                # ปิดการประมูล
                item.status = "closed"
                item.end_time = timezone.now()
                item.save()

                highest_bid = item.bids.order_by("-amount").first()
                winner = highest_bid.bidder if highest_bid else None

                if highest_bid:
                    highest_bid.is_winner = True
                    highest_bid.save()

                seller = item.seller

                # ส่งอีเมลผู้ชนะ
                if winner:
                    winner_message = (
                        f'สวัสดี {winner.username},\n'
                        f'คุณชนะการประมูลสินค้า "{item.title}"!\n'
                        f'ราคาที่ชนะ: {item.current_price:,.2f} บาท\n\n'
                        f'ติดต่อผู้ขาย:\n'
                        f'ชื่อ: {seller.get_full_name()}\n'
                        f'อีเมล: {seller.email}\n'
                        f'เบอร์โทรศัพท์: {getattr(seller, "phone", "ไม่ระบุ")}\n\n'
                        f'ขอบคุณที่ใช้ BidYup!'
                    )

                    send_mail(
                        subject=f"🎉 คุณชนะการประมูล: {item.title}",
                        message=winner_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[winner.email],
                    )

                # ส่งอีเมลผู้ขาย
                seller_message = (
                    f'สวัสดี {seller.get_full_name()},\n'
                    f'การประมูลสินค้า "{item.title}" ได้ปิดแล้ว\n'
                )

                if highest_bid:
                    seller_message += (
                        f'ผู้ชนะ: {winner.get_full_name()} ({winner.username})\n'
                        f'ราคาที่ชนะ: {item.current_price:,.2f} บาท\n'
                        f'อีเมลผู้ชนะ: {winner.email}\n'
                        f'เบอร์โทรศัพท์ผู้ชนะ: {getattr(winner, "phone", "ไม่ระบุ")}\n'
                    )
                else:
                    seller_message += "ไม่มีผู้เสนอราคาใดๆ สำหรับสินค้านี้\n"

                seller_message += "\nขอบคุณที่ใช้ BidYup!"

                send_mail(
                    subject=f'🔨 การประมูลสินค้าของคุณ "{item.title}" ปิดแล้ว',
                    message=seller_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[seller.email],
                )

        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)} ระบบไม่สามารถปิดการประมูลได้")
            return redirect("index")

        messages.success(request, "ปิดการประมูลเรียบร้อยแล้ว ระบบได้ส่งอีเมลแจ้งผู้เกี่ยวข้องแล้ว")
        return redirect("index")


def CurrentdBidsAPIView(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    current_price = float(item.current_price or item.starting_price)
    bids = [
        {
            "bidder": bid.bidder.username,
            "amount": float(bid.amount),
            "time": bid.time.strftime("%d/%m/%Y %H:%M")
        }
        for bid in item.bids.order_by('-time')
    ]
    return JsonResponse({"current_price": current_price, "bids": bids})

class MyItemView(PermissionRequiredMixin, View):
    permission_required = ["auctions.add_item"]
    def get(self, request):
        items = Item.objects.filter(status="active", seller=request.user).order_by("-created_at")
        return render(request, "myitem.html", {"items": items})

class MyBidView(View):
    def get():
        pass
    def post():
        pass

class ProfileView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.pk != request.user.pk: 
            raise PermissionDenied
        user = get_object_or_404(User, pk=pk)
        form = ProfileForm(instance=user)
        return render(request, "profile.html", {"form": form, "user": user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.pk != request.user.pk: 
            raise PermissionDenied
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "อัปเดตโปรไฟล์เรียบร้อยแล้ว")
            return redirect("profile", pk=user.pk)
        return render(request, "profile.html", {"form": form, "user": user})

class FavouriteView(View):
    def get():
        pass
    def post():
        pass