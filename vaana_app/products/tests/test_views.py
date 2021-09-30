from django.urls.base import reverse
from ..models import Product
from users.models import User
from stores.models import Store
from categories.models import Category

from django.test import TestCase
import uuid
from addresses.models import Address

class ProductTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='laye', email='abdoulaye.ndao@xegit.com', password='Passer123')
        self.user.save()
        self.product = Product(
            name = "Foods",
            slug = "foods",
            description = "Lorem ipsum dolor, sit amet consectetur adipisicing elit.",
            is_active = "True",
            created_by = self.user,
            price = "200",
            category = Category.objects.create(
                name = "Foods",
                slug = "foods",
                description = "Lorem ipsum dolor, sit amet consectetur adipisicing elit.",
                is_active = "True",
                created_by = self.user
            ),
            store = Store.objects.create(name = "Shop",
                            created_by = self.user,
                            address = Address.objects.create(
                                state = "Foods",
                                zipcode = "foods",
                                country = "Lorem ipsum dolor, sit amet consectetur adipisicing elit.",
                                street = "True",
                            ),                             
                            is_active = "True"
                        ),
            # image = "test",
            quantity ="50",
            views = 1
        )
        self.product.save()

    def tearDown(self):
        self.user.delete()

    def test_read_product(self):
        self.assertEqual(self.product.created_by, self.user)
        self.assertEqual(self.product.name, 'Foods')
        self.assertEqual(self.product.description, 'Lorem ipsum dolor, sit amet consectetur adipisicing elit.')
        self.assertEqual(self.product.slug, 'foods')
        self.assertEqual(self.product.is_active, 'True')

    def test_update_product_description(self):
        self.product.description = 'new description'
        self.product.save()
        self.assertEqual(self.product.description, 'new description')

    
    def test_update_product_name(self):
        self.product.name = 'new name'
        self.product.save()
        self.assertEqual(self.product.name, 'new name')


    # def test_no_products(self):
    #     response = self.client.get(reverse('products'), format='json')
    #     self.assertEqual(response.data, {'products': []})