from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Item, Bid
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def close_auction(item_id):
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return "Item not found"

    if item.status != "active":
        return "Auction already closed"

    item.status = "closed"
    item.save()

    highest_bid = item.bids.order_by("-amount").first()
    winner = highest_bid.bidder if highest_bid else None
    seller = item.seller

    if winner:
        winner_message = (
            f"สวัสดี {winner.username},\n"
            f"คุณชนะการประมูลสินค้า '{item.title}'!\n"
            f"ราคาที่ชนะ: {item.current_price:,.2f} บาท\n\n"
            f"ติดต่อผู้ขาย:\n"
            f"ชื่อ: {seller.get_full_name()}\n"
            f"อีเมล: {seller.email}\n"
            f"โทรศัพท์: {getattr(seller, 'phone', 'ไม่ระบุ')}\n\n"
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
            f"โทรศัพท์ผู้ชนะ: {getattr(winner, 'phone', 'ไม่ระบุ')}\n"
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
