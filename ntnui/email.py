import django.core.mail as mail

def send_mail(sbj, msg, sender, receiver):
    mail.send_mail(subject=sbj, message=msg, from_email=sender, recipient_list=receiver)