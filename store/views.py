import datetime
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json;
from .models import *
from .utils import cookieCart, guestOrder

# def index(request):
#     if request.method == 'POST':
#         un = request.POST.get('username')
#         pw = request.POST.get('password')
#         no = list(range(1, 6))
#         if (un == "karan" and pw == 'karan') or (un == "admin" and pw == 'admin') or (un == "store" and pw == 'store'):
#             # return HttpResponse("<h1><center>Done!</center></h1>")
#             return render(request, 'store/store.html', {'no':no})
#         else:
#             return HttpResponse("<h1><center>Incorrect Username or Password</center></h1>")
#     else:
#         return render(request, 'store/index.html')
    
    
def store(request):

    if request.user.is_authenticated:
        customer=request.user.customer
        order, created=Order.objects.get_or_create(customer=customer, complete=False)
        items= order.orderitem_set.all()
        cartItems=order.get_cart_items

    else:
        # items= []  #empty crt fr non-logged in usrs
        # order={'get_cart_total':0, 'get_cart_items':0}
        # cartItems=order['get_cart_items']
        cookieData = cookieCart(request) 
        cartItems = cookieData['cartItems']
        


    products=Product.objects.all()
    context = {'products' :products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    if request.user.is_authenticated:
        customer=request.user.customer
        order, created=Order.objects.get_or_create(customer=customer, complete=False)
        items= order.orderitem_set.all()
        cartItems=order.get_cart_items

    else:
        cookieData = cookieCart(request) 
        cartItems = cookieData['cartItems']
        order = cookieData['order']  
        items = cookieData['items'] 
            
    context={'items':items,'order':order, 'cartItems': cartItems}
    return render(request, 'store/cart.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created=Order.objects.get_or_create(customer=customer, complete=False)
        items= order.orderitem_set.all()
        cartItems=order.get_cart_items
        

    else:
        # items= []  #empty crt fr non-logged in usrs
        # order={'get_cart_total':0, 'get_cart_items':0}
        # cartItems=order['get_cart_items']
        cookieData = cookieCart(request) 
        cartItems = cookieData['cartItems']
        order = cookieData['order']  
        items = cookieData['items'] 
        
    context={'items':items,'order':order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html',context)

def thankyou(request):
    return render(request, 'store/tq.html')

def updateItem(request):
    data= json.loads(request.body)
    productId =data['productId']
    action =data['action']

    print('Action:',action)
    print('productId:', productId)

    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        # If the user is not authenticated, you can handle guest users (e.g., use cookie data)
        cookieData = cookieCart(request)
        customer = None  # No customer for guest users

    
    product=Product.objects.get(id=productId)
    order, created= Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created= OrderItem.objects.get_or_create(order=order, product=product)

    if action== 'add':
        orderItem.quantity=(orderItem.quantity +1)
    elif action == 'remove':
        orderItem.quantity=(orderItem.quantity -1)
    
    orderItem.save()

    if orderItem.quantity <=0:
        orderItem.delete()

    return JsonResponse('Item was added',safe=False )



def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    # Handle authenticated users or guest users
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        # Logic for guest order (if applicable)
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    # Only mark the order as complete if the total matches
    if total == order.get_cart_total:
        order.complete = True

    order.save()

    # Create shipping address if applicable
    if order.complete:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            pincode=data['shipping']['pincode'],
            #country=data['shipping']['country'],  
        )

    return JsonResponse('Order Placed..', safe=False)