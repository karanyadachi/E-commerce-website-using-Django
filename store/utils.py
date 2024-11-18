import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])  #cart is string we need to parse it and turns it to python dictionary
    except:
        cart = {}

    print('Cart:', cart)
    items= []  #empty crt fr non-logged in usrs
    order={'get_cart_total':0, 'get_cart_items':0}
    cartItems=order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]["quantity"]

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"] )

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]["quantity"]

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL': product.imageURL,

                },
                'quantity': cart[i]["quantity"],
                'get_total': total
                }
            items.append(item)

        except:
            pass
    return{'cartItems': cartItems,'order':order,'items':items}

def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    # Check if a customer already exists for this email (for returning guests)
    customer, created = Customer.objects.get_or_create(email=email)
    if created:
        customer.name = name
        customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )

    return customer, order
