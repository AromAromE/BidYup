from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from .models import Item, Order
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def close_auction(item_id):
    try:
        with transaction.atomic():
            item = Item.objects.get(pk=item_id)

            if item.status != "active":
                return f"⚠️ สินค้า '{item.title}' ถูกปิดแล้ว"

            item.status = "closed"
            item.save()

        # ส่งเมลหลังจาก commit แล้ว (อยู่นอก transaction)
        highest_bid = item.bids.order_by("-amount").first()
        winner = highest_bid.bidder if highest_bid else None
        if highest_bid:
            highest_bid.is_winner = True
            highest_bid.save()

        if winner:
            Order.objects.create(
                item=item,
                buyer=winner,
                payment_status="pending",
                delivery_status="pending"
            )

        seller = item.seller

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

        return f"Auction {item.title} closed, winner: {winner.username if winner else 'ไม่มีผู้ชนะ'}"

    except Item.DoesNotExist:
        return "❌ ไม่พบสินค้า"
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {str(e)}"
