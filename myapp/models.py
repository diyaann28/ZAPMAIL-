from django.db import models

# Create your models here.
class Login(models.Model):
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    usertype=models.CharField(max_length=50)

class User(models.Model):
    LOGIN=models.ForeignKey(Login,on_delete=models.CASCADE)
    firstname=models.CharField(max_length=50)
    lastname=models.CharField(max_length=50)
    username=models.CharField(max_length=50)
    email=models.CharField(max_length=50)
    phoneno=models.CharField(max_length=50)
    place=models.CharField(max_length=50)
    pincode=models.CharField(max_length=50)
    post=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    
class Complaint(models.Model):
    USER=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateField(auto_now=True)
    complaint=models.CharField(max_length=50)
    reply=models.CharField(max_length=50)

class Feedback(models.Model):
    USER=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateField(auto_now=True)
    feedback=models.CharField(max_length=50)
    rating=models.CharField(max_length=50)

class Email(models.Model):
    email_from=models.CharField(max_length=1000)
    email_to=models.CharField(max_length=1000)
    content=models.TextField()
    attatchment=models.CharField(max_length=500)
    subject=models.CharField(max_length=500,default="")
    date=models.CharField(max_length=50,default="")
    time=models.CharField(max_length=50,default="")
    status=models.CharField(max_length=50,default="")
    code=models.IntegerField(default=1000)
    result=models.CharField(max_length=1000,default="")


class Emails(models.Model):
    EMAIL=models.CharField(max_length=1000)
    USER=models.ForeignKey(User,on_delete=models.CASCADE)
    password=models.CharField(max_length=50)

class Summarize(models.Model):
    summarize=models.CharField(max_length=50)
    EMAIL=models.ForeignKey(Email,on_delete=models.CASCADE)

class Remainder(models.Model):
    EMAIL=models.ForeignKey(Email,on_delete=models.CASCADE)
    date=models.CharField(max_length=50)
    time=models.CharField(max_length=50)


