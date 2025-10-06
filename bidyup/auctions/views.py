from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout
from .forms import LoginForm, CreateForm, RegisterForm, BidForm
from .models import Item, Bid

from django.db import transaction

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.utils import timezone

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
            return redirect("index")
    
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
            return redirect("index")

        return render(request, "delete_item.html", {"item": item})
    
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.seller != request.user and not request.user.is_staff:
            return redirect("index")
    
        item.delete()
        return redirect("index")
    
class EndAuctionView(View):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.seller != request.user:
            return redirect("index")

        return render(request, "endlist.html", {"item": item})
        
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.seller != request.user:
            return redirect("index")

        try:
            with transaction.atomic():  # ทำให้ทุกอย่างในบล็อกนี้เป็น transaction
                # ปิดการประมูล
                item.status = "closed"
                item.end_time = timezone.now()
                item.save()

                highest_bid = item.bids.order_by('-amount').first()
                winner = highest_bid.bidder if highest_bid else None

                if highest_bid:
                    highest_bid.is_winner = True
                    highest_bid.save()

                seller = item.seller

                # ส่งอีเมลผู้ชนะ
                if winner:
                    winner_message = (
                        f"สวัสดี {winner.username},\n"
                        f"คุณชนะการประมูลสินค้า '{item.title}'!\n"
                        f"ราคาที่ชนะ: {item.current_price:,.2f} บาท\n\n"
                        f"ติดต่อผู้ขาย:\n"
                        f"ชื่อ: {seller.get_full_name()}\n"
                        f"อีเมล: {seller.email}\n"
                        f"เบอร์โทรศัพท์: {getattr(seller, 'phone', 'ไม่ระบุ')}\n\n"
                        f"ขอบคุณที่ใช้ BidYup!"
                    )

                    send_mail(
                        subject=f"🎉 คุณชนะการประมูล: {item.title}",
                        message=winner_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[winner.email],
                    )

                # ส่งอีเมลผู้ขาย
                seller_message = (
                    f"สวัสดี {seller.get_full_name()},\n"
                    f"การประมูลสินค้า '{item.title}' ได้ปิดแล้ว\n"
                )

                if highest_bid:
                    seller_message += (
                        f"ผู้ชนะ: {winner.get_full_name()} ({winner.username})\n"
                        f"ราคาที่ชนะ: {item.current_price:,.2f} บาท\n"
                        f"อีเมลผู้ชนะ: {winner.email}\n"
                        f"เบอร์โทรศัพท์ผู้ชนะ: {getattr(winner, 'phone', 'ไม่ระบุ')}\n"
                    )
                else:
                    seller_message += "ไม่มีผู้เสนอราคาใดๆ สำหรับสินค้านี้\n"

                seller_message += "\nขอบคุณที่ใช้ BidYup!"

                send_mail(
                    subject=f"🔨 การประมูลสินค้าของคุณ '{item.title}' ปิดแล้ว",
                    message=seller_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[seller.email],
                )

        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)} ระบบไม่สามารถปิดการประมูลได้")
            return redirect("index")

        messages.success(request, "ปิดการประมูลเรียบร้อยแล้ว ระบบได้ส่งอีเมลแจ้งผู้เกี่ยวข้องแล้ว")
        return redirect("index")


def BidUpdateView(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    current_price = item.current_price or item.starting_price
    return JsonResponse({"current_price": float(current_price)})