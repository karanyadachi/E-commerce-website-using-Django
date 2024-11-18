from django.urls import path

from . import views

urlpatterns = [
        #Leave as empty string for base url
	# path('', views.index, name="index"),
    path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update-item"),
    path('process_order/', views.processOrder, name='process_order'),
    path('thankyou/', views.thankyou, name="thankyou")

]