from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import JSONField, ArrayField
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
  
class Users(models.Model): 
    name = models.CharField(max_length=100, blank = True, null= True)
    username = models.CharField(max_length=100,primary_key=True)
    referal = models.CharField(max_length=100)
    age = models.IntegerField(blank= True, null=True)
    phone = PhoneNumberField()
    email = models.EmailField(max_length=254,blank=True)
    profile_pic = models.ImageField(upload_to='profilePic/', blank=True, null=True) 
    dob = models.DateField(blank=True,null=True)
    password = models.CharField(max_length=50)
    doj = models.DateTimeField(auto_now_add=True)
    wishlist = models.ManyToManyField("home.Products",blank=True)
    address = models.ForeignKey('home.Address', verbose_name="Address", on_delete=models.CASCADE, blank=True, null=True)
    cart = models.ForeignKey("home.Cart", on_delete=models.SET_NULL,blank = True, null=True)
    payment_details = models.ForeignKey("home.PaymentDetails",on_delete=models.PROTECT, blank=True, null=True)
    last_OTP = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)],blank=True,null=True)
    OTP_sent_time = models.DateTimeField(null=True, blank=True)
    user_choise = [
        ("General Manager","General Manager"),
        ("Regional Manager","Regional Manager"),
        ("Team Manager","Team Manager"),
        ("Business Leader","Business Leader"),
        ("Customer","Customer"),
    ]
    role = models.CharField(max_length=50,choices=user_choise,default="Customer")
    down_leaf = models.ManyToManyField("home.Users",blank=True)
    earning = models.DecimalField(max_digits=10, decimal_places=3,default=Decimal(0.0))

    def __str__(self):
        return f"{self.username}({self.name})"
    
@receiver(pre_save, sender=Users)
def update_otp_sent_time(sender, instance, **kwargs):
    if instance.pk is not None: 
        old_instance = Users.objects.filter(pk=instance.pk).first() 
        if old_instance and old_instance.last_OTP != instance.last_OTP:
            instance.OTP_sent_time = timezone.now()

class Address(models.Model):
    user = models.ForeignKey(Users, verbose_name="User_Address", on_delete=models.CASCADE, related_name='addresses')
    door_number = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.country}"

class Products(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    product_id = models.CharField(max_length=100, primary_key=True)
    images = models.ImageField(upload_to="product/")
    mrp = models.DecimalField( max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    discount = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    sellingPrice = models.DecimalField( max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    stock = models.IntegerField()
    rating = models.DecimalField(validators=[MaxValueValidator(5),MinValueValidator(0)], max_digits=3,decimal_places= 2)
    freeDelivery = models.BooleanField(default=True)
    specification = models.JSONField(blank=True) # [{"label": "Case Diameter", "value": "4.4 Millimeters"}, {"label": "Brand Colour", "value": "Brown"}, {"label": "Brand Material Type", "value": "Plastic"}]
    specification_list = ArrayField(models.CharField(max_length=100),blank=True) 
    tag = ArrayField(models.CharField(max_length=50),blank=True,null=True)
    GME = models.DecimalField( max_digits=10, decimal_places=3)
    RME = models.DecimalField( max_digits=10, decimal_places=3)
    TME = models.DecimalField( max_digits=10, decimal_places=3)
    BLE = models.DecimalField( max_digits=10, decimal_places=3)
    @property
    def inStock(self)->bool: 
        return self.stock>0

    def __str__(self):
        return self.name

class DeliveryPartner(models.Model):
    dpid = models.CharField(max_length=50,primary_key=True)
    name = models.CharField(max_length=200)
    location = models.ForeignKey("home.Address", on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    orders_handling = models.ManyToManyField("home.Orders", related_name='order_handling_partners')

class EachItem(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
 
    def save(self, *args, **kwargs):
        if self.product:
            self.total = self.quantity * self.product.sellingPrice
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Product: {self.product} | Quantity:{self.quantity}"

class Cart(models.Model):
    cart_id = models.CharField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='carts')
    ordered_products = models.ManyToManyField(EachItem)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = sum(items.total for items in self.ordered_products.all())
        print(self.total)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user}"

@receiver(post_save, sender=EachItem)
def update_cart_total(sender, instance, **kwargs):
    # Update the Cart total whenever EachItem is saved
    cart = instance.user.cart
    if cart:
        cart.total = sum(item.total for item in cart.ordered_products.all())
        cart.save()

class PaymentDetails(models.Model):
    pay_id = models.CharField(primary_key=True,max_length=50)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16,unique=True)  # Assuming a 16-digit card number
    cardholder_name = models.CharField(max_length=255)
    expiration_date = models.CharField(max_length=7)  # MM/YYYY format
    cvv = models.CharField(max_length=4)  # 3 or 4-digit CVV/CVC
    billing_address = models.TextField()
    card_type = models.CharField(max_length=20)  # Visa, MasterCard, etc.
    zip_code = models.CharField(max_length=10)

class Orders(models.Model):
    user = models.ForeignKey(Users, on_delete=models.PROTECT)
    order_id = models.CharField(max_length=50, unique=True, primary_key=True)
    ordered_product = models.ForeignKey(Products,on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField(null=True,blank=True)
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.PROTECT,null=True,blank=True)
    delivery_charges = models.IntegerField(null=True,blank=True)
    total_cost = models.IntegerField(null=True,blank=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    dchoise = [
        ("Regular Delivery","Regular Delivery"),
        ("Instant Delivery","Instant Delivery"),
    ]
    delivery_type = models.CharField(choices=dchoise,null=True,blank=True)
    status_opt = [
        ("Out for Delivery","Out for Delivery"),
        ("Placed","Placed"),
        ("Dispatched","Dispatched"),
        ("Cancelled","Cancelled"),
        ("Refunded","Refunded"),
        ("Processing","Processing"),
        ("On Hold","On Hold"),
        ("Returned","Returned"),
        ("Completed","Completed"),
    ]
    status = models.CharField(choices=status_opt)
    pay_opt = [
        ("COD","Cash on Delivery"),
        ("UPI","Online Payment"),
        ("Card","Credit/Debit Card"),
        ("EMI","EMI"),
    ]
    payment_method = models.CharField(choices=pay_opt)
    expected_delivery = models.DateField(null=True,blank=True)