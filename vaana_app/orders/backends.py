from django.conf import settings
from .models import Order, OrderItem
from users.models import User
from shippings.backends import ShippoShipmentAPI, ShippoTransactionAPI
from products.serializers import ParcelSerializer
from shippings.models import Address, Shipment
from shippings.serializers import *
import shippo
shippo.config.api_key = settings.SHIPPO_API_KEY

class OrderBackends(object):
    def getTotalPrice(self, items):
        total = 0
        for item in items:
            total+= item.product.price * item.quantity
        return total

    def getSellers(self, cart):
        sellers = []
        for item in cart.items.all():
            if item.product.created_by not in sellers:
                sellers.append(item.product.created_by)
        return sellers

    def getCartItemsBySeller(self, cart, seller):
        items = []
        for item in cart.items.all():
            if seller == item.product.created_by:
                items.append(item)
        return items
    
    def addcartItemsToOrder(self, items, order_item):
        for item in items:
            order_item.cart_items.add(item)

    def createItems(self, order, cart):
        sellers = self.getSellers(cart=cart)
        for seller in sellers:
            items = self.getCartItemsBySeller(cart=cart, seller=seller)
            total_prices = self.getTotalPrice(items=items)
            order_item = OrderItem.objects.create(
                order=order,
                seller=seller,
                status=OrderItem.INITIATED,
                total_prices=total_prices
            )
            order_item.save()
            self.addcartItemsToOrder(items=items, order_item=order_item)
        
        return OrderItem.objects.filter(order=order)
    
    def createOrderItems1(self, order, cart):
        items = cart.items.all()
        for item in items:
            seller = item.product.created_by
            total_prices = item.product.price * item.quantity
            order_item = OrderItem.objects.create(
                order=order,
                seller=seller,
                status=OrderItem.INITIATED,
                total_prices=total_prices,
                cart_item=item
            )
        return OrderItem.objects.filter(order=order)

class OrderItemBackend(object):
    def getAddressFrom(self, orderItem):
        seller = orderItem.seller
        
        data = {
            'company': seller.username,
            'name': seller.username,
            'state': seller.address.state,
            'street1': seller.address.street,
            'zip_code': seller.address.zipcode,
            'country': seller.address.country,
            'city': seller.address.state,
            'phone': seller.address.phone,
            'email': seller.email,
            'user': seller.id
        }
        serializer = ShippoAddressSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def getAddressTo(self, orderItem):
        shipping_address = orderItem.shipping_address
        return ShippoAddressSerializer(shipping_address).data

    def getParcels(self, items):
        parcels  = []
        for i in items:
            for j in range(0, i.quantity):
                parcels.append(ParcelSerializer(i.product.parcel).data)

        return parcels

    def storeShipment(self, data):
        shipment = Shipment.objects.create(
            object_id=data['object_id'],
            address_from=Address.objects.get(id=data['address_from']['id']),
            address_to=Address.objects.get(id=data['address_to']['id']),
        )
        
        return shipment

    def createShipment(self, orderItem):
        address_from = self.getAddressFrom(orderItem=orderItem)
        address_to = self.getAddressTo(orderItem=orderItem)
        parcels = [ParcelSerializer(orderItem.cart_item.product.parcel).data] #self.getParcels(items=orderItem.cart_items.all())
        data = {
            'address_from': address_from,
            'address_to': address_to,
            'parcels': parcels
        }
        shipmentApi = ShippoShipmentAPI()
        shipment = shipmentApi.create(shipment=data)
        data['object_id'] = shipment['object_id']
        shipmentJSON = ShippoShipmentSerializer(self.storeShipment(data=data)).data
        shipmentJSON['parcels'] = parcels
        shipmentJSON['rates'] = shipment['rates'] 

        return shipmentJSON

    def createTransaction(self, orderItem):
        shipment = shippo.Shipment.retrieve(orderItem.shipment.object_id)
        carrier_account = orderItem.shipment.carrier_account
        servicelevel_token = orderItem.shipment.servicelevel_token
        rate = orderItem.shipment.rate
        ''' address_from = orderItem.shipment.address_from
        address_to = orderItem.shipment.address_to '''
        data = {
            'rate': rate,
            'shipment': {
                'parcels': shipment['parcels'],
                'address_from': shipment['address_from'],
                'address_to': shipment['address_to'],
            },
            'carrier_account': '0a4365b4fca142e1b30d43de5cf80351',#carrier_account,
            'servicelevel_token': 'shippo_ups_account'#servicelevel_token
        }
        transactionAPI = ShippoTransactionAPI()

        return transactionAPI.create(transaction=data)

