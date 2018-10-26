from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from .forms import CustomerSignUpForm,RestuarantSignUpForm,CustomerForm,RestuarantForm
from django.contrib.auth.decorators import login_required
from collections import Counter
from django.urls import reverse
from django.db.models import Q
from .models import Customer,Restaurant,Item,Menu,Order,orderItem,User


#### ---------- General Side -------------------#####

# Showing index page
def index(request):
	return render(request,'webapp/index.html',{})

def orderplaced(request):
	return render(request,'webapp/orderplaced.html',{})

# Showing Restaurants list to Customer
def restuarent(request):
	r_object = Restaurant.objects.all()
	query 	= request.GET.get('q')
	if query:
		r_object=Restaurant.objects.filter(Q(rname__icontains=query)).distinct()
		return render(request,'webapp/restaurents.html',{'r_object':r_object})
	return render(request,'webapp/restaurents.html',{'r_object':r_object})


# logout
def Logout(request):
	if request.user.is_restaurant:
		logout(request)
		return redirect("rlogin")
	else:
		logout(request)
		return redirect("login")

		

#### -----------------Customer Side---------------------- ######

# Creating Customer Account
def customerRegister(request):
	form =CustomerSignUpForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.is_customer=True
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("ccreate")
	context ={
		'form':form
	}			
	return render(request,'webapp/signup.html',context)


# Customer Login
def customerLogin(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("profile")
			else:
				return render(request,'webapp/login.html',{'error_message':'Your account disable'})
		else:
			return render(request,'webapp/login.html',{'error_message': 'Invalid Login'})
	return render(request,'webapp/login.html')


# customer profile view
def customerProfile(request,pk=None):
	if pk:
		user = User.objects.get(pk=pk)
	else:
		user=request.user
	
	return render(request,'webapp/profile.html',{'user':user})


#Create customer profile 
def createCustomer(request):
	form = CustomerForm(request.POST or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		return redirect("profile")
	context={
	'form':form,
	'title':"Complete Your profile"
	}
	return render(request,'webapp/profile_form.html',context)


#  Update customer detail
def updateCustomer(request,id):
	form  	 = CustomerForm(request.POST or None,instance=request.user.customer)
	if form.is_valid():
		form.save()
		return redirect('profile')
	context={
	'form':form,
	'title':"Update Your profile"
	}
	return render(request,'webapp/profile_form.html',context)

def restuarantMenu(request,pk=None):

	menu = Menu.objects.filter(r_id=pk)
	rest = Restaurant.objects.filter(id=pk)

	items =[]
	for i in menu:
		item = Item.objects.filter(fname=i.item_id)
		for content in item:
			temp=[]
			temp.append(content.fname)
			temp.append(content.category)
			temp.append(i.price)
			temp.append(i.id)
			temp.append(rest[0].status)
			temp.append(i.quantity)
			items.append(temp)
	context = {
		'items'	: items,
		'rid' 	: pk,
		'rname'	: rest[0].rname,
		'rmin'	: rest[0].min_ord,
		'rinfo' : rest[0].info,
		'rlocation':rest[0].location,
	}
	return render(request,'webapp/menu.html',context)


@login_required(login_url='/login/user/')
def checkout(request):
	if request.POST:
		addr  = request.POST['address']
		ordid = request.POST['oid']
		Order.objects.filter(id=int(ordid)).update(delivery_addr = addr,
                                                    status=Order.ORDER_STATE_PLACED)
		return redirect('/orderplaced/')
	else:	
		cart = request.COOKIES['cart'].split(",")
		cart = dict(Counter(cart))
		items = []
		totalprice = 0
		uid = User.objects.filter(username=request.user)
		oid = Order()
		oid.orderedBy = uid[0]
		for x,y in cart.items():
			item = []
			it = Menu.objects.filter(id=int(x))
			if len(it):
				oiid=orderItem()
				oiid.item_id=it[0]
				oiid.quantity=int(y)
				oid.r_id=it[0].r_id
				oid.save()
				oiid.ord_id =oid
				oiid.save()
				totalprice += int(y)*it[0].price
				item.append(it[0].item_id.fname)
				it[0].quantity = it[0].quantity - y
				it[0].save()
				item.append(y)
				item.append(it[0].price*int(y))
			
			items.append(item)
		oid.total_amount=totalprice
		oid.save()
		context={
			"items":items,
			"totalprice":totalprice,
			"oid":oid.id
		}	
		return render(request,'webapp/order.html',context)




####### ------------------- Restaurant Side ------------------- #####

# creating restuarant account
def restRegister(request):
	form =RestuarantSignUpForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.is_restaurant=True
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("rcreate")
	context ={
		'form':form
	}			
	return render(request,'webapp/restsignup.html',context)	


# restuarant login
def restLogin(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("rprofile")
			else:
				return render(request,'webapp/restlogin.html',{'error_message':'Your account disable'})
		else:
			return render(request,'webapp/restlogin.html',{'error_message': 'Invalid Login'})
	return render(request,'webapp/restlogin.html')


# restaurant profile view
def restaurantProfile(request,pk=None):
	if pk:
		user = User.objects.get(pk=pk)
	else:
		user=request.user
	
	return render(request,'webapp/rest_profile.html',{'user':user})

# create restaurant detail
@login_required(login_url='/login/restaurant/')
def createRestaurant(request):
	form=RestuarantForm(request.POST or None,request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		return redirect("rprofile")
	context={
	'form':form,
	'title':"Complete Your Restaurant profile"
	}
	return render(request,'webapp/rest_profile_form.html',context)

#Update restaurant detail
@login_required(login_url='/login/restaurant/')
def updateRestaurant(request,id):
	form  	 = RestuarantForm(request.POST or None,request.FILES or None,instance=request.user.restaurant)
	if form.is_valid():
		form.save()
		return redirect('rprofile')
	context={
	'form':form,
	'title':"Update Your Restaurant profile"
	}
	return render(request,'webapp/rest_profile_form.html',context)


# add  menu item for restaurant	
@login_required(login_url='/login/restaurant/')		
def menuManipulation(request):
	if not request.user.is_authenticated:
		return redirect("rlogin") 
		
	rest=Restaurant.objects.filter(id=request.user.restaurant.id);
	rest=rest[0]
	if request.POST:
		type=request.POST['submit']
		if type =="Modify":
			menuid = int(request.POST['menuid'])
			memu= Menu.objects.filter(id=menuid).\
					update(price=int(request.POST['price']),quantity=int(request.POST['quantity']))
		elif type == "Add" :
			itemid=int(request.POST['item'])
			item=Item.objects.filter(id=itemid)
			item=item[0]
			menu=Menu()
			menu.item_id=item
			menu.r_id=rest
			menu.price=int(request.POST['price'])
			menu.quantity=int(request.POST['quantity'])
			menu.save()
		else:
			menuid = int(request.POST['menuid'])
			menu = Menu.objects.filter(id=menuid)
			menu[0].delete()

	menuitems=Menu.objects.filter(r_id=rest)
	menu=[]
	for x in menuitems:
		cmenu=[]
		cmenu.append(x.item_id)
		cmenu.append(x.price)
		cmenu.append(x.quantity)
		cmenu.append(x.id)
		menu.append(cmenu)

	menuitems = Item.objects.all()
	items = []
	for y in menuitems:
		citem = []
		citem.append(y.id)
		citem.append(y.fname)
		items.append(citem)

	context={
		"menu":menu,
		"items":items,
		"username":request.user.username,
	}
	return render(request,'webapp/menu_modify.html',context)

def orderlist(request):
	if request.POST:
		oid = request.POST['orderid']
		select = request.POST['orderstatus']
		select = int(select)
		order = Order.objects.filter(id=oid)
		if len(order):
			x = Order.ORDER_STATE_WAITING
			if select == 1:
				x = Order.ORDER_STATE_PLACED
			elif select == 2:
				x = Order.ORDER_STATE_ACKNOWLEDGED
			elif select == 3:
				x = Order.ORDER_STATE_COMPLETED
			elif select == 4:
				x = Order.ORDER_STATE_DISPATCHED
			elif select == 5:
				x = Order.ORDER_STATE_CANCELLED
			else:
				x = Order.ORDER_STATE_WAITING
			order[0].status = x
			order[0].save()

	orders = Order.objects.filter(r_id=request.user.restaurant.id).order_by('-timestamp')
	corders = []

	for order in orders:

		user = User.objects.filter(id=order.orderedBy.id)
		user = user[0]
		corder = []
		if user.is_restaurant:
			corder.append(user.restaurant.rname)
			corder.append(user.restaurant.info)
		else:
			corder.append(user.customer.f_name)
			corder.append(user.customer.phone)
		items_list = orderItem.objects.filter(ord_id=order)

		items = []
		for item in items_list:
			citem = []
			citem.append(item.item_id)
			citem.append(item.quantity)
			menu = Menu.objects.filter(id=item.item_id.id)
			citem.append(menu[0].price*item.quantity)
			menu = 0
			items.append(citem)

		corder.append(items)
		corder.append(order.total_amount)
		corder.append(order.id)

		x = order.status
		if x == Order.ORDER_STATE_WAITING:
		    continue
		elif x == Order.ORDER_STATE_PLACED:
		    x = 1
		elif x == Order.ORDER_STATE_ACKNOWLEDGED:
			x = 2
		elif x == Order.ORDER_STATE_COMPLETED:
			x = 3
		elif x == Order.ORDER_STATE_DISPATCHED:
			x = 4
		elif x == Order.ORDER_STATE_CANCELLED:
			x = 5
		else:
			continue

		corder.append(x)
		corder.append(order.delivery_addr)
		corders.append(corder)

	context = {
		"orders" : corders,
	}

	return render(request,"webapp/order-list.html",context)
	



