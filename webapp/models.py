from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save

class User(AbstractUser):
	is_customer   = models.BooleanField(default=False)
	is_restaurant = models.BooleanField(default=False)


class Customer(models.Model):
	user 		= models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	f_name   	= models.CharField(max_length=20,blank=False)
	l_name		= models.CharField(max_length=20,blank=False)
	city  		= models.CharField(max_length=40,blank=False)
	phone 		= models.CharField(max_length=10,blank=False)
	address		= models.TextField()

	def __str__(self):
		return self.user.username
	
class Restaurant(models.Model):
	user        = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	rname 		= models.CharField(max_length=100,blank=False)
	info	 	= models.CharField(max_length=40,blank=False)
	min_ord		= models.CharField(max_length=5,blank=False)
	location    = models.CharField(max_length=40,blank=False)
	r_logo      = models.FileField(blank=False)

	REST_STATE_OPEN    = "Open"
	REST_STATE_CLOSE   = "Closed"
	REST_STATE_CHOICES =(
			(REST_STATE_OPEN,REST_STATE_OPEN),
			(REST_STATE_CLOSE,REST_STATE_CLOSE)
		)
	status 	= models.CharField(max_length=50,choices=REST_STATE_CHOICES,default=REST_STATE_OPEN,blank=False)
	approved = models.BooleanField(blank=False,default=True)

	def __str__(self):
		return self.rname
		
class Item(models.Model):
	id 			= models.AutoField(primary_key=True)
	fname 		= models.CharField(max_length=30,blank=False)
	category 	= models.CharField(max_length=50,blank=False)

	def __str__(self):
		return self.fname

class Menu(models.Model):
	id 		 = models.AutoField(primary_key=True)
	item_id  = models.ForeignKey(Item,on_delete=models.CASCADE)
	r_id     = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
	price    = models.IntegerField(blank=False)
	quantity = models.IntegerField(blank=False,default=0)

	def __str__(self):
		return self.item_id.fname+' - '+str(self.price)
	

class Order(models.Model):
	id 				= models.AutoField(primary_key=True)
	total_amount    = models.IntegerField(default=0)
	timestamp       = models.DateTimeField(auto_now_add=True)
	delivery_addr   = models.CharField(max_length=50,blank=True)
	orderedBy       = models.ForeignKey(User ,on_delete=models.CASCADE)
	r_id			= models.ForeignKey(Restaurant ,on_delete=models.CASCADE)
	
	ORDER_STATE_WAITING 	 = "Waiting"
	ORDER_STATE_PLACED 		 = "Placed"
	ORDER_STATE_ACKNOWLEDGED = "Acknowledged"
	ORDER_STATE_COMPLETED    = "Completed"
	ORDER_STATE_CANCELLED    = "Cancelled"
	ORDER_STATE_DISPATCHED   = "Dispatched"

	ORDER_STATE_CHOICES = (
		(ORDER_STATE_WAITING,ORDER_STATE_WAITING),
	    (ORDER_STATE_PLACED, ORDER_STATE_PLACED),
	    (ORDER_STATE_ACKNOWLEDGED, ORDER_STATE_ACKNOWLEDGED),
	    (ORDER_STATE_COMPLETED, ORDER_STATE_COMPLETED),
	    (ORDER_STATE_CANCELLED, ORDER_STATE_CANCELLED),
	    (ORDER_STATE_DISPATCHED, ORDER_STATE_DISPATCHED)
	)
	status = models.CharField(max_length=50,choices=ORDER_STATE_CHOICES,default=ORDER_STATE_WAITING)
	
	def __str__(self):
		return str(self.id) +' '+self.status


class orderItem(models.Model):
	id 			= models.AutoField(primary_key=True)
	item_id 	= models.ForeignKey(Menu ,on_delete=models.CASCADE)
	ord_id  	= models.ForeignKey(Order,on_delete=models.CASCADE)
	quantity 	= models.IntegerField(default=0)
	
	def __str__(self):
		return str(self.id) 







		
		



		

