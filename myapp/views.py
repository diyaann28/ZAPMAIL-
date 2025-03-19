from email.mime.text import MIMEText
import smtplib
from venv import logger
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse
from myapp.models import *
from django.core.mail import send_mail
from django.db.models import Max
import random
import myapp.classifier as cl
import imaplib
import email
import openai
from email.header import decode_header
from django.core.management.base import BaseCommand
from django.contrib import messages
from django.shortcuts import redirect
import emoji

from email.mime.multipart import MIMEMultipart

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from twilio.rest import Client

import http.client
import ssl
TOKEN = "tq84hxe9eb8r441m"
INSTANCE_ID = "instance110828"
def login(request):
    save_contact(TOKEN,INSTANCE_ID,"7034955751","Zapemail")
    if 'submit' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        if Login.objects.filter(username=username,password=password).exists():
            res = Login.objects.get(username=username,password=password)
            request.session['login_id']=res.pk
            login_id=request.session['login_id']

            if res.usertype =='admin':
                request.session['log']="in"
                return HttpResponse(f"<script>alert('welcome Admin');window.location='/adminhome'</script>")

            elif res.usertype =='user':
                if User.objects.filter(LOGIN_id=login_id).exists():
                    res2=User.objects.get(LOGIN_id=login_id)
                    if res2:
                        request.session['log']="in"
                        request.session['user_id']=res2.pk
                        # check_mail(res2.pk)
                        return HttpResponse(f"<script>alert('welcome user');window.location='/userhome'</script>")
                    else:
                        return HttpResponse(f"<script>alert('Invalid user ');window.location=/'login'</script>")
                else:
                        return HttpResponse(f"<script>alert('this patiend ID  does not exist');window.location='/login'</script>")

            elif res.usertype =='pending':
                return HttpResponse(f"<script>alert('you are not approved by admin....please wait for approval');window.location='/login'</script>")
            
            else:
                return HttpResponse(f"<script>alert('invalid user ');window.location='/login'</script>")

        else:
            return HttpResponse(f"<script>alert('invalid username or password');window.location='/login'</script>")
    return render(request,'public/login.html')
def remove_emojis(text):
    return emoji.replace_emoji(text, replace='')  
def check_mail(id):
    id = str(id)[2:]
    print("id",id)
    gg=User.objects.get(phoneno=id)
    ff=Emails.objects.filter(USER_id=gg.id)
    
    for i in ff:
        # remove the country code from the phone number
        
        uu = User.objects.get(id=gg.id)
        
        email_id=i.EMAIL
        password=i.password
        yournumber=uu.phoneno
        EMAIL_HOST = "imap.gmail.com"
        EMAIL_PORT = 993
        print("hereeeeeeeeeeeeeeeeeeeeeeeeee: "+ password,email_id,yournumber)
        ATTACHMENT_DIR = "attachments"
        import os
        os.makedirs(ATTACHMENT_DIR, exist_ok=True)

        try:
            # Connect to the mail server
            mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
            mail.login(email_id, password)

            # Select mailbox
            status, mailbox = mail.select("inbox")
            if status != "OK":
                print("Error selecting mailbox:", mailbox)
                mail.logout()
                exit()

            # Search for all emails
            status, messages = mail.search(None, "ALL")
            if not messages or messages == [b'']:  # No emails found
                print("No emails found.")
                mail.logout()
                exit()

            email_ids = messages[0].split()
            print(f"Found {len(email_ids)} emails.")

            for email_id in email_ids[-5:]:  # Fetch last 5 emails
                status, msg_data = mail.fetch(email_id, "(RFC822)")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Extract email details
                        email_from = msg.get("From", "(Unknown Sender)")
                        email_to = msg.get("To", "(Unknown Recipient)")
                        date_header = msg.get("Date")
                        
                        # Parse date and time
                        if date_header:
                            email_date = email.utils.parsedate_to_datetime(date_header)
                            email_date_str = email_date.strftime("%Y-%m-%d")
                            email_time_str = email_date.strftime("%H:%M:%S")
                        else:
                            email_date_str = "Unknown"
                            email_time_str = "Unknown"

                        # Extract subject
                        subject_header = msg["Subject"]
                        if subject_header:
                            subject, encoding = decode_header(subject_header)[0]
                        if isinstance(subject, bytes):
                            try:
                                subject = subject.decode(encoding or "utf-8", errors="replace")  # Use 'replace' to avoid errors
                            except UnicodeDecodeError:
                                subject = subject.decode("utf-8", errors="ignore")  # Fallback
                        else:
                                subject = "No Subject"

# Ensure subject length does not exceed MySQL column size (255 characters)
                        subject = subject[:255]

                        # Extract email content
                        email_content = ""
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                email_content = part.get_payload(decode=True).decode(errors="ignore")

                        # Extract attachments
                        attachments = []
                        for part in msg.walk():
                            if part.get_content_disposition() == "attachment":
                                filename = part.get_filename()
                                if filename:
                                    filename, encoding = decode_header(filename)[0]
                                    if isinstance(filename, bytes):
                                        filename = filename.decode(encoding or "utf-8")

                                    file_path = os.path.join(ATTACHMENT_DIR, filename)
                                    with open(file_path, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    attachments.append(filename)

                        # Print structured email details
                        print("\n-------------------------------------")
                        print(f"Email From: {email_from}")
                        print(f"Email To: {email_to}")
                        print(f"Date: {email_date_str} | Time: {email_time_str}")
                        print(f"Subject: {subject}")
                        print(f"Content:\n{email_content[:500]}")  # Show first 500 chars
                        print(f"Attachments: {', '.join(attachments) if attachments else 'None'}")

                        # spam=cl.check(msg)
                        spam = "ham"
                        print(spam,"----"*100)
                        if spam =="ham":
                            spam="not spam"
                        
                        if Email.objects.filter(email_from=email_from,email_to=email_to,content=email_content[:500],status='viewed').exists():
                            send(yournumber, "No New Emails, Enjoy Your Day! ")
                        else:
                            latest_email = Email.objects.order_by('-id').first()
                            if latest_email:
                                code_next=latest_email.code+1
                            else:
                                code_next=1000
                            subject = remove_emojis(subject)
                            dd=Email()
                            dd.email_from=email_from
                            dd.email_to=email_to
                            dd.subject=subject
                            dd.content=email_content[:500]
                            dd.date=email_date_str
                            dd.time=email_date_str
                            dd.attatchment=', '.join(attachments) if attachments else 'None'
                            dd.status="viewed"
                            dd.code=code_next
                            dd.result=spam
                            dd.save()


                            # client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

                            message_body = f"""
📩 *New Email Received* 📩

📧 *From*: {dd.email_from}
📨 *To*: {dd.email_to}
📝 *Subject*: {dd.subject}
📝 *Content*: {dd.content}
📅 *Date*: {dd.date} ⏰ {dd.time}
📎 *Attachments*: {dd.attatchment if dd.attatchment else 'None'}

📌 *Status*: {dd.status}
🔢 *Code*: {dd.code}
"""


                            # message = client.messages.create(
                            #     from_=TWILIO_WHATSAPP_NUMBER,
                            #     body=message_body,
                            #     to=yournumber
                            # )
                            if spam == "not spam":
                                send_message_to_whatsapp(message_body,dd.email_from,yournumber)
                                print(f"WhatsApp Message Sent! SID")

            mail.logout()

        except imaplib.IMAP4.error as e:
            print(f"IMAP error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    return "ok"

def index(request):
     return render(request,'public/index.html')

def adminhome(request):
     return render(request,'admin/adminhome.html')

def userhome(request):
     return render(request,'user/userhome.html')

def register(request):
     if 'submit' in request.POST:
        # Generate a 4-digit random number
        random_number = random.randint(1000, 9999)
        username=request.POST['username']
        password=request.POST['password']
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        number=request.POST['number']
        email=request.POST['email']
        place=request.POST['place']
        pincode=request.POST['pincode']
        post=request.POST['post']
        city=request.POST['city']
        districts=request.POST['districts']
        otp1=request.POST['otp1']
        otp = request.session['otp']
        if int(otp) == int(otp1):
            q=Login(username=username,password=password,usertype='user')
            q.save()
            q1=User(LOGIN=q,firstname=firstname,lastname=lastname,username=username,email=email,phoneno=number,place=place,pincode=pincode,post=post,city=city)
            q1.save()
            
            message_body = f"""
🎉 *Congratulations, {firstname}!* 🎉

You have successfully registered on *ZapMail*! 🎉

👉 To complete your setup, please create a mail password by following this link: [Google App Passwords](https://myaccount.google.com/apppasswords)

We’re excited to have you on board! 🚀


If you have any questions or need assistance, feel free to reach out. 📬
""" 
            send(number,message_body)
            return HttpResponse(f"<script>alert('Registered successfully');window.location='/login'</script>")
        else:
            return HttpResponse(f"<script>alert('OTP doesnot match');window.location='/login'</script>")
          
     return render(request,'public/register.html')

def otp_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print("============================================",email)
        
        if not email:
            return JsonResponse({'message': 'Email is required.'}, status=400)
        
        # Generate a 4-digit OTP
        request.session['otp']=""
        otp = random.randint(1000, 9999)
        request.session['otp'] = otp
        
        # Send email with OTP
        send_mail(
            'Your OTP Code',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,
            [email]
        )
        
        return JsonResponse({'message': 'OTP has been sent to your email.'})
    
    return JsonResponse({'message': 'Invalid request.'}, status=400)


def admin_view_user(request):
     data=User.objects.all()
     return render(request,'admin/admin_view_user.html',{'data':data})

def user_view_profile(request):
    user_id=request.session['user_id']
    data=User.objects.get(id=user_id)
    return render(request,'user/user_view_profile.html',{'data':data})

def user_feedback(request):
    if 'submit' in request.POST:
        user_id=request.session['user_id']
        feedback1=request.POST['feedback1']
        rating=request.POST['rating']
        q=Feedback(USER_id=user_id,feedback=feedback1,rating=rating)
        q.save()
        return HttpResponse(f"<script>alert('Feedback added');window.location='/user_feedback'</script>")
    return render(request,'user/user_feedback.html')

def admin_feedback(request):
     data=Feedback.objects.all()
     return render(request,'admin/admin_feedback.html',{'data':data})

def user_complaint(request):
    user_id=request.session['user_id']
    data=Complaint.objects.filter(USER_id=user_id)
    if 'submit' in request.POST:
        complaint=request.POST['complaint']
        q=Complaint(USER_id=user_id,complaint=complaint,reply="pending")
        q.save()
        return HttpResponse(f"<script>alert('Complaint added');window.location='/user_complaint'</script>")
    return render(request,'user/user_complaint.html',{'data':data})

def admin_complaint(request):
     data=Complaint.objects.all()
     if 'submit' in request.POST:
        id=request.POST['id']
        reply=request.POST['reply']
        complaint=Complaint.objects.get(id=id)
        complaint.reply=reply
        complaint.save()
        return HttpResponse(f"<script>alert('Reply added');window.location='/admin_complaint'</script>")
     return render(request,'admin/admin_complaint.html',{'data':data})

def user_manage_emailacc(request):
     user_id=request.session['user_id']
     data=Emails.objects.filter(USER_id=user_id)
     return render(request,'user/user_manage_emailacc.html',{'data':data})


def sedd(request):
    spam=[]
    if'Submit'in request.POST:
        msg=request.POST['msg']
        print("oooo",msg)
           
        # spam=cl.check(msg)
        spam = "ham"
        print(spam,"----"*100)
        if spam =="ham":
            spam="not spam"

 
    return render(request,"user/sendmsg.html",{"data":spam})

def sendsms(request):
    
    sub = request.POST['msg']
    print(sub,)
   
    
    spam=cl.check(sub)
    print(spam,"----"*100)
    

    return render(request,"user/sendmsg.html",{"data":spam})

def mail(s,email,mesg):
    try:
        gmail = smtplib.SMTP('smtp.gmail.com', 587)
        gmail.ehlo()
        gmail.starttls()
        gmail.login('dhakshidhav@gmail.com', 'qopfmoivmqhueqrc')
    except Exception as e:
        print("Couldn't setup email!!" + str(e))
    msg = MIMEText(mesg)
    print(msg)
    msg['Subject'] = s
    msg['To'] = email
    msg['From'] = 'dhakshidhav@gmail.com'
    try:
        gmail.send_message(msg)
        return '''<script>alert("Success");window.location="/sendessage"</script>'''
    except Exception as e:
        print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert("COULDN'T SEND EMAIL");window.location="/sendessage"</script>'''


def user_add_emailacc(request):
     user_id=request.session['user_id']
     if 'submit' in request.POST:
        email=request.POST['email']
        password=request.POST['password']
        q=Emails(USER_id=user_id,EMAIL=email,password=password)
        q.save()
        return HttpResponse(f"<script>alert('Email added');window.location='/user_add_emailacc'</script>")
     return render(request,'user/user_add_emailacc.html')

def user_delete_email(request, id):
    Emails.objects.get(id=id).delete()
    return HttpResponse(f"<script>alert('Email deleted');window.location='/user_manage_emailacc'</script>")

def user_edit_emailacc(request,id):
     data=Emails.objects.get(id=id)
     if 'submit' in request.POST:
        email=request.POST['email']
        password=request.POST['password']
        data.EMAIL=email
        data.password=password
        data.save()
        return HttpResponse(f"<script>alert('Email edited');window.location='/user_manage_emailacc'</script>")
     return render(request,'user/user_edit_emailacc.html',{'data':data})

def user_edit_profile(request):
     user_id=request.session['user_id']
     data=User.objects.get(id=user_id)
     if 'submit' in request.POST:
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        number=request.POST['number']
        email=request.POST['email']
        place=request.POST['place']
        pincode=request.POST['pincode']
        post=request.POST['post']
        city=request.POST['city']
        districts=request.POST['districts']
        data.firstname=firstname
        data.lastname=lastname
        data.phoneno=number
        data.email=email
        data.place=place
        data.pincode=pincode
        data.post=post
        data.city=city
        data.district=districts
        data.save()
        return HttpResponse(f"<script>alert('Profile edited');window.location='/user_view_profile'</script>")
     return render(request,'user/user_edit_profile.html',{'data':data})

def and_user_register(request):
    username = request.POST['username']
    password = request.POST['password']
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    email = request.POST['email']
    phone = request.POST['phone']
    place = request.POST['place']
    pin = request.POST['pin']
    post = request.POST['post']
    city = request.POST['city']
    m = Login(username=username,password=password,usertype = 'user')
    m.save()
    m1 = User(firstname=firstname , lastname=lastname ,email=email , username=username , phoneno=phone , place=place , post=post , city=city , pincode=pin , LOGIN_id=m.pk)
    m1.save()
    return JsonResponse({'status':'ok'})

def and_login(request):
    username = request.POST['username']
    password = request.POST['password']
    
    print(f"Received login attempt for username: {username}")
    
    if Login.objects.filter(username=username, password=password).exists():
        qa = Login.objects.get(username=username, password=password)
        lid = qa.pk
        print(f"Login successful for user ID: {lid} with usertype: {qa.usertype}")
        
        if qa.usertype == 'user':
            try:
                qd = User.objects.get(LOGIN_id=lid)
                print(f"User found: {qd}")
                uid = qd.pk
                return JsonResponse({'status': 'ok', 'lid': lid, 'uid': uid, 'usertype': 'user'})
            except User.DoesNotExist:
                print("User does not exist.")
                return JsonResponse({'status': 'no'})
        else:
            print("Invalid usertype.")
            return JsonResponse({'status': 'no'})
    else:
        print("Login failed.")
        return JsonResponse({'status':'no'})

def save_contact(token, instance_id, number, contact_name):
    conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())
    payload = f"token={token}&to={number}&name={contact_name}"
    headers = {'content-type': "application/x-www-form-urlencoded"}

    # ✅ API to Save Contact as "ZapEmail"
    conn.request("POST", f"/{instance_id}/contacts/add", payload, headers)
    res = conn.getresponse()
    data = res.read()

    print("[✅] Contact Name Saved as:", contact_name)


import datetime

def add_rating(request):
    uid = request.POST['uid']
    rating = request.POST['rating']
    review = request.POST['review']
    date =  datetime.date.today()
    m = Feedback(USER_id = uid, rating = rating,date=date,feedback=review)
    m.save()
    return JsonResponse({'status':'ok'})

import http.client
import ssl

def send(TO_NUMBER, MESSAGE):
    # Establish a secure connection
    conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())

    # Build payload
    payload = f"token={TOKEN}&to={TO_NUMBER}&body={MESSAGE}"
    payload = payload.encode('utf-8').decode('iso-8859-1')

    # Send the request
    headers = {'content-type': "application/x-www-form-urlencoded"}
    conn.request("POST", f"/{INSTANCE_ID}/messages/chat", payload, headers)

    # Get the response
    res = conn.getresponse()
    data = res.read()

    # Print the response
    print(data.decode("utf-8"))

# Example usage
# send_whatsapp_message("your_token", "receiver_number", "Hello, this is a test message!", "your_instance_id")

def send_message_to_whatsapp(email_subject, email_from,TO_number):
  

    # Replace with your UltraMsg token and instance ID
    
    TO_NUMBER = TO_number # Receiver's WhatsApp number with country code
    save_contact(TOKEN, INSTANCE_ID, TO_NUMBER, "ZapEmail")
    # ✅ Dynamic Message with "ZapEmail"
    MESSAGE = f"""
        📩 *New Email Received in ZapEmail*
    ----------------------------------------
    *From:* {email_from}
    *Subject:* {email_subject}

    ✅ Please check your email panel on ZapEmail.
        """

    # Establish a secure connection
    conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())

    # Build payload
    payload = f"token={TOKEN}&to={TO_NUMBER}&body={MESSAGE}"
    payload = payload.encode('utf-8').decode('iso-8859-1')

    # Send the request
    headers = {'content-type': "application/x-www-form-urlencoded"}
    conn.request("POST", f"/{INSTANCE_ID}/messages/chat", payload, headers)

    # Get the response
    res = conn.getresponse()
    data = res.read()

    # Print the response
    print(data.decode("utf-8"))



def reply_email(request):
    if request.method == 'POST':
        try:
            # Parse incoming data
            data = json.loads(request.body)
            
            # Extract the message content
            if 'data' not in data:
                return JsonResponse({'status': 'error', 'message': 'Invalid request format'})
            
            whatsapp_data = data['data']
            message_body = whatsapp_data.get('body', '')
            
            # Check if this is a reply to an email notification
            quoted_msg = whatsapp_data.get('quotedMsg', {})
            quoted_body = quoted_msg.get('body', '')
            
            if not quoted_body or 'New Email Received' not in quoted_body:
                print("NOT A REPLY MSG!")
                # return JsonResponse({'status': 'error', 'message': 'Not a reply to an email notification'})
            
            # Extract the email address from the quoted message
            email_from_match = re.search(r'\*From\*:\s*(.*?)(?:\n|$)', quoted_body)
            if not email_from_match:
                return JsonResponse({'status': 'error', 'message': 'Could not find sender email'})
            
            # Extract the email address from the "From" line
            sender_line = email_from_match.group(1).strip()
            email_regex = r'<([^>]+)>'
            match = re.search(email_regex, sender_line)
            
            if match:
                recipient_email = match.group(1)
            else:
                # If no <email> format, use the whole string if it looks like an email
                if '@' in sender_line:
                    recipient_email = sender_line
                else:
                    return JsonResponse({'status': 'error', 'message': 'Could not parse email address'})
            
            # Extract subject from the quoted message
            subject_match = re.search(r'\*Subject\*:\s*(.*?)(?:\n|$)', quoted_body)
            subject = subject_match.group(1).strip() if subject_match else "Re: No Subject"
            
            if not subject.startswith("Re:") and not subject.startswith("RE:"):
                subject = f"Re: {subject}"
            
            # Get the phone number of the user who sent the WhatsApp message
            phone_number = whatsapp_data.get('from', '').split('@')[0]
            if phone_number.startswith('91'):  # Remove country code if present
                phone_number = phone_number[2:]
            
            # Get user's email credentials from database
            try:
                user = User.objects.get(phoneno=phone_number)
                email_account = Emails.objects.filter(USER_id=user.id).first()
                
                if not email_account:
                    return JsonResponse({'status': 'error', 'message': 'No email account configured for this user'})
                
                sender_email = email_account.EMAIL
                password = email_account.password
                
                # Compose email
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                
                # Add Reply-To header
                msg.add_header('Reply-To', sender_email)
                
                # Add in-reply-to and references if available
                # These would need to be stored from the original email
                
                # Email body
                msg.attach(MIMEText(message_body, 'plain'))
                
                # Send email
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, password)
                    server.send_message(msg)
                body="The reply had been sent to the email: "+recipient_email
                send(phone_number,body)
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Email reply sent',
                    'details': {
                        'to': recipient_email,
                        'from': sender_email,
                        'subject': subject
                    }
                })
                
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'})
            except Emails.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Email account not configured'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Error sending email: {str(e)}'})
                
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'})
                        
         
import imaplib
import email
from email.header import decode_header
from django.conf import settings


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import os

from myapp.models import Email  # Import your Email model


# def get_summary(request,email_text):
#     apikey=
    

#     openai.api_key = "your_openai_api_key"


#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "Summarize the following email in 3-4 sentences, keeping important details."},
#             {"role": "user", "content": email_text}
#         ]
#     )
#     print(response["choices"][0]["message"]["content"])

# # Example usage:

#     return "ok"

import re
import nltk
from nltk.tokenize import sent_tokenize

def simple_summary(email_content):
    # Tokenize into sentences
    sentences = sent_tokenize(email_content)

    # Extract sentences that contain important words
    important_sentences = [s for s in sentences if re.search(r"(meeting|deadline|important|action|urgent|ASAP)", s, re.I)]

    # If no important sentence is found, return the first 2 sentences as a summary
    return " ".join(important_sentences[:3]) if important_sentences else " ".join(sentences[:2])
import json
@csrf_exempt
def ultramsg_webhook(request):
    """Webhook to receive WhatsApp replies and update email status."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            sender = data.get("from", "")  # WhatsApp sender number
            message = data.get("body", "").strip()  # Message text
            
            if sender and message:
                # Save WhatsApp reply to the database
                # reply = WhatsAppReply.objects.create(sender=sender, message=message)
                
                # Extract a 4-digit code from the message (if any)
                match = re.search(r"\b\d{4}\b", message)
                if match:
                    code = match.group()  # Extracted 4-digit code
                    
                    try:
                        # Find the email with this code
                        email = Email.objects.get(code=code)
                        email.status = "Replied"
                        email.save()
                        
                        # Send confirmation message
                        confirmation_msg = f"✅ Your response has been linked to email {code}. Status updated!"
                        # send_whatsapp_message(sender, confirmation_msg)

                        return JsonResponse({"status": "success", "message": "Email status updated."}, status=200)
                    
                    except Email.DoesNotExist:
                        error_msg = "⚠️ No matching email found for this code."
                        # send_whatsapp_message(sender, error_msg)
                        return JsonResponse({"status": "error", "message": "Invalid code"}, status=400)

                return JsonResponse({"status": "success", "message": "Reply saved but no code found."}, status=200)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "GET method not allowed"}, status=405)



def manage_mail(request):
    mail = request.POST['mail']
    password = request.POST['password']
    q1=Emails(EMAIL=mail,password=password)
    q1.save()
    return JsonResponse({"status": "success", "message": "successfully added"}, status=200)



def user_viewmails(request):
    a=Emails.objects.all()
    l=[]
    for i in a:
        l.append({
            "mail":i.mail,
            "password":i.password
        })
    return JsonResponse({"status":"success","data":l})



        
          


def check(request, id):
    send(id,"PLEASE WAIT...FETCHING....")
    print(request)
    print(id)
    # Call the check_mail function with the provided ID
    result = check_mail(id)
   
    # Provide feedback
    if result == "ok":
        messages.success(request, f"Successfully checked emails for user {id}")
        return HttpResponse(f"Successfully checked emails for user {id}")
    else:
        messages.error(request, f"Error checking emails for user {id}")
        return HttpResponse(f"Error checking emails for user {id}")
    
