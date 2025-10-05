from django.core.mail import send_mail
from django.conf import settings

def notify_winner(bid):
    item = bid.item
    winner = bid.bidder
    seller = item.seller

    subject = f"🎉 คุณชนะการประมูล: {item.title}"
    message = (
        f"สวัสดี {winner.username},\n\n"
        f"คุณชนะการประมูลสินค้า '{item.title}'!\n"
        f"ราคาที่ชนะ: {item.current_price:,.2f} บาท\n\n"
        f"ติดต่อผู้ขาย:\n"
        f"ชื่อ: {seller.get_full_name()}\n"
        f"อีเมล: {seller.email}\n"
        f"โทรศัพท์: {getattr(seller, 'phone', 'ไม่ระบุ')}\n\n"
        f"ขอบคุณที่ใช้ BidYup!"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [winner.email],
        fail_silently=False,
    )
