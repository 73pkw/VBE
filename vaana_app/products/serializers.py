from users.serializers import UserSerializer
from rest_framework import serializers
from .models import Parcel, Product, ProductReview
from files.serializers import FileSerializer

class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = [
            "id",
            "object_id",
            "parcel_length",
            "parcel_width",
            "parcel_weight",
            "parcel_height",
            "distance_unit",
            "mass_unit"
        ]

class ProductReviewResultSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ProductReview
        fields = [
            "id",
            "title",
            "comment",
            "rating",
            "product",
            "user",
            "created_at",
            "updated_at",
        ]
class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = [
            "id",
            "title",
            "comment",
            "rating",
            "product",
            "user",
            "created_at",
            "updated_at",
        ]
        
class ProductSerializer(serializers.ModelSerializer):
    reviews = ProductReviewSerializer(many=True)
    images = serializers.ListField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "category",
            "is_active",
            "quantity",
            "views",
            "rating",
            "images",
            "created_by",
            "created_at",
            "updated_at",
            "store",
            "reviews",
        ]
    
    def create(self, validated_data):
        return Product.objects.create_user(**validated_data)
        
class ProductResponseSerializer(serializers.ModelSerializer):
    reviews = ProductReviewResultSerializer(many=True)
    images = FileSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "category",
            "is_active",
            "quantity",
            "views",
            "rating",
            "images",
            "created_by",
            "created_at",
            "updated_at",
            "store",
            "reviews",
        ]

