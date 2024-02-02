from rest_framework import serializers
from .models import Users, Products, Address,Orders,EachItem


class UserSerial(serializers.ModelSerializer):
    class Meta(object):
        model = Users
        fields = [
            'name',
            'email',
            'username',
            'referal',
            'dob',
            'role',
            'down_leaf',
            'phone',
            'profile_pic',
            'earning'
        ]
class AddressSerial(serializers.ModelSerializer):
    class Meta:
        model= Address
        fields=[
            'door_number',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'landmark',
        ]
    
class Signup(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = ['name', 'email', 'phone', 'address', 'password', 'referal', 'username']

class ProductSerial(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'


class EachItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EachItem
        fields = ['product', 'quantity']
