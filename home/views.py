from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import Signup,ProductSerial, AddressSerial,UserSerial
from .models import Users, Products, Address,EachItem,Cart,Orders
from rest_framework import status,generics
from django.db.models import Q
import base64
from django.http import JsonResponse
import random,os
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal

BASE_DIR = settings.BASE_DIR 

@api_view(["POST"])
def login(request):   # {"username":"TitanNatesan","password":"1234567890"}
    if request.method == "POST":
        username = request.data.get('username')
        password = request.data.get('password')
        user = Users.objects.filter(username=username, password=password).first()
        if user:
            return Response(1)
        else:
            return Response({'message': 'Login failed'}, status=status.HTTP_401_UNAUTHORIZED)
        

@api_view(["POST"])
def signup1(request):   # {"username":"natesan","password":"12345678","referal":"mukilan@ref"}
    if request.method == "POST":
        data = request.data
        try:
            referal = Users.objects.get(username=data['referal'])
        except Users.DoesNotExist:
            return Response("Referal Dosent Exist")
        if data.get('username') and data.get('password') and data.get('referal'):
            return Response(1)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        data = request.data
        address = data.pop("address")
        user_serializer = Signup(data=data)
        address_serializer = AddressSerial(data=address)
        try:
            referal = Users.objects.get(username=data['referal'])
        except Users.DoesNotExist:
            return Response("Referal Doesnt Exist")
        
        if user_serializer.is_valid() and address_serializer.is_valid():
            user_instance = user_serializer.save()
            address_data = address_serializer.validated_data
            address_data['user'] = user_instance
            address_instance = Address(**address_data)
            address_instance.save()
            user_instance.address = address_instance
            user_instance.save()

            user = Users.objects.get(username=data['username'])
            referal.down_leaf.add(user)
            referal.save()
            return Response(1)
        return Response({"error": "Invalid data provided."}, status=400)


@api_view(["POST",'GET'])
def cart(request, username):
    if request.method == "POST":
        data = request.data
        product_id = data.get('product_id')
        try:
            user = Users.objects.get(username=username)
            product = Products.objects.get(product_id=product_id)
            try:
                cart = Cart.objects.get(user=username)
                try:
                    each_item = EachItem.objects.get(user=username,product=product_id)
                    each_item.quantity+=1
                    each_item.save()
                except EachItem.DoesNotExist:
                    each_item = EachItem(
                        user=user,
                        product=product,
                        quantity=1,
                    )
                    each_item.save()
                    cart = Cart.objects.get(user=username)
                    cart.ordered_products.add(each_item)
                    cart.save()
            except Cart.DoesNotExist:
                user_cart = Cart(
                    cart_id=user.username+"'s Cart",
                    user = user,
                )
                user_cart.save()
                user.cart = user_cart
                user.save()
                
                each_item = EachItem(
                    user=user,
                    product=product,
                    quantity=1,
                )
                each_item.save()
                user_cart.ordered_products.add(each_item)
                user_cart.save()
        except Users.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        except Products.DoesNotExist:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)
        return Response(1)
    
    if request.method == "GET":
        try:
            user = Users.objects.get(username=username)
            cart_items = EachItem.objects.filter(user=user)
            cart_data = []
            for item in cart_items:
                product_data = {
                    "product_id": item.product.product_id,
                    "name": item.product.name,
                    "quantity": item.quantity,
                    "total": item.total,
                }
                cart_data.append(product_data)
            response_data = {
                "username": user.username,
                "cart_items": cart_data,
                "cart_total": sum([i['total'] for i in cart_data]),

            }
            return Response(response_data)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def updateCart(request,opr):     # {"username":"TitanNatesan","product_id":"phone1"}
    if request.method == "POST":
        data = request.data 
        try:
            user = Users.objects.get(username=data['username'])
            product = Products.objects.get(product_id=data['product_id'])
        except Users.DoesNotExist:
            return Response("User not Found")
        except Products.DoesNotExist:
            return Response("Product not Found")           
        try:
            cart = Cart.objects.get(user=user)
            try:
                each = EachItem.objects.get(user=user,product=product)
            except EachItem.DoesNotExist:
                each = EachItem(
                    user=user,
                    product=product,
                    quantity=1,
                )
                each.save()
                cart = Cart.objects.get(user=user)
                cart.ordered_products.add(each)
                cart.save()
        except Cart.DoesNotExist:
            user_cart = Cart(
                cart_id=user.username+"'s Cart",
                user = user,
            )
            user_cart.save()
            user.cart = user_cart
            user.save()
            each = EachItem(
                user=user,
                product=product,
                quantity=1,
            )
            each.save()
            user_cart.ordered_products.add(each)
            user_cart.save()
        try:
            each.quantity = eval(str(each.quantity)+opr+"+1")
        except:
            return Response("Invalid URL (try .../updateCart/+/ or .../updateCart/-/)")
        if each.quantity>0:
            each.save()
        else:
            each.delete() 
        return Response("Updated")


@api_view(["GET"])
def address(request,username):
    if request.method == "GET":
        try:
            user = Users.objects.get(username=username)
            add = Address.objects.get(user = user)
        except Users.DoesNotExist:
            return Response("User not found")
        except Address.DoesNotExist:
            return Response("No Address Found")
        serial = AddressSerial(add)
        us = UserSerial(user)
        userdata = us.data
        if us.data['profile_pic']:
            img = us.data['profile_pic'] 
            img = str(BASE_DIR)+img
            userdata['profile_pic']= str(get_base64_encoded_image(img))

        data = {
            "user":userdata,
            "address":serial.data,
        }
        return Response(data)


@api_view(["POST"])
def placeOrder(request):
    '''
    {
  "user": "qwertyuiop",  
  "product_id":"phone1",
  "delivery_type": "Regular Delivery",
  "pay_method": "UPI"
}
    '''
    if request.method == "POST":
        try:
            user = Users.objects.get(username=request.data['user'])
            product = Products.objects.get(product_id=request.data['product_id'])
        except Users.DoesNotExist:
            return Response({"detail": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except Products.DoesNotExist:
            return Response({"detail": "Product Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            each = EachItem.objects.get(user=user, product=product)
        except EachItem.DoesNotExist:
            each = EachItem(
                user=user,
                product=product,
                quantity=1
            )
            each.save()
            return Response({"detail": "Cart Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        allOrders = Orders.objects.all()
        print(request.data)
        each = EachItem.objects.get(user=user,product=product)
        order = Orders.objects.create(user=user,order_id=str(user.username)+getDateAndTime())
        order.ordered_product = product
        order.quantity = each.quantity 
        order.total_cost = each.quantity*product.sellingPrice
        order.delivery_charges = 0 if (each.quantity*product.sellingPrice)>200 else 40
        order.delivery_type = request.data['delivery_type']
        order.status = "Placed"
        order.payment_method = request.data['pay_method']
        order.expected_delivery = add_working_days(str(datetime.now().date()),7)
        order.save()
        each.delete()

        while user.referal!='null':
            user = Users.objects.get(username=user.referal)
            if user.role == "General Manager":
                user.earning += product.sellingPrice * (product.GME)/Decimal(100) * Decimal(order.quantity)
                user.save()
            elif user.role == "Regional Manager":
                user.earning += product.sellingPrice * (product.RME)/Decimal(100) * Decimal(order.quantity)
                user.save()
            elif user.role =="Team Manager":
                user.earning += product.sellingPrice * (product.TME)/Decimal(100) * Decimal(order.quantity)
                user.save()
            elif user.role == 'Business Leader' :
                user.earning += product.sellingPrice * (product.BLE)/Decimal(100) * Decimal(order.quantity)
                user.save()
            else:
                break

        return Response(1)


def getDateAndTime():
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%m%d%Y%H%M")
    return str(formatted_date)

def add_working_days(start_date, num_days):
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    for _ in range(num_days):
        current_date += timedelta(days=1)
        while current_date.weekday() in [5, 6]:  # Skip weekends (5 is Saturday, 6 is Sunday)
            current_date += timedelta(days=1)
    return current_date.strftime('%Y-%m-%d')


@api_view(["GET","POST"])
def viewUser(request,username):
    if request.method == "POST":
        userdata = request.data.pop("user")
        addressData = request.data.pop("address")
        try:
            user = Users.objects.get(username=userdata['username'])
            user.name = userdata['name']
            user.phone = userdata['phone']
            user.email = userdata['email']
            user.save()
            try:
                address = Address.objects.get(user=user)
                address.door_number = addressData['door_number']
                address.address_line1 = addressData['address_line1']
                address.address_line2 = addressData['address_line2']
                address.city = addressData['city']
                address.state = addressData['state']
                address.postal_code = addressData['postal_code']
                address.landmark = addressData['landmark']
                address.save()
            except Address.DoesNotExist:
                Address.objects.create(
                    user=user,
                    door_number=addressData['door_number'],
                    address_line1=addressData['address_line1'],
                    address_line2=addressData['address_line2'],
                    city=addressData['city'],
                    state=addressData['state'],
                    postal_code=addressData['postal_code'],
                    landmark=addressData['landmark']
                )
        except Users.DoesNotExist:
            return Response("User not found")
        return Response("Updated")
    
    if request.method == "GET":
        try:
            user = Users.objects.get(username=username)
            add = Address.objects.get(user = user)
        except Users.DoesNotExist:
            return Response("User not found")
        except Address.DoesNotExist:
            return Response("No Address Found")
        serial = AddressSerial(add)
        us = UserSerial(user)
        userdata = us.data
        if us.data['profile_pic']:
            img = us.data['profile_pic'] 
            img = str(BASE_DIR)+img
            userdata['profile_pic']= str(get_base64_encoded_image(img))

        data = {
            "user":userdata,
            "address":serial.data,
        }
        return Response(data)


class ProductsSearchView(generics.ListAPIView):
    serializer_class = ProductSerial

    def get_queryset(self):
        query = self.request.query_params.get('query', '')

        return Products.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tag__icontains=query) |
            Q(specification__contains=[{"label": query}]) |  # Assuming specification is a list of dictionaries
            Q(specification_list__contains=[query])
        )

        
@api_view(["GET"])
def viewProduct(request,pi):
    products = Products.objects.all().values()
    if request.method == "GET":
        return Response("Not")

@api_view(["GET"])
def viewProducts(request):
    products = Products.objects.all().values()
    serializer = ProductSerial(products, many=True)
    return Response(list(products))

def get_base64_encoded_image(img_path):
    with open(img_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded_image}"

def generate_otp():
    return ''.join(random.choices('0123456789', k=4))

def send_otp_email(email, otp):
    subject = 'Your OTP'
    message = f'Your OTP is: {otp}\n Do not share this OTP'
    from_email = 'mukilan@gmail.com'  # Update with your email
    send_mail(subject, message, from_email, [email])

@api_view(['POST'])
def generate_and_send_otp(request):
    print("111")
    if request.method == 'POST':
        email = request.POST.data['email']
        otp = generate_otp()
        send_otp_email(email, otp)
        print("otp sent",otp)
        request.session['otp'] = otp
        return Response("OTP sent successfully. Check your email.")
    return Response(0)
