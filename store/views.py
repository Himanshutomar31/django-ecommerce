from django.shortcuts import render, get_object_or_404
from category.models import Category
from .models import Product

def store(request, category_slug = None):
    categories = None
    products = None
    products = Product.objects.all().filter(is_available=True)
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=categories, is_available=True)
    product_count = products.count()
    data = {
        'products':products,
        'product_count':product_count
    }
    return render(request,'store/store.html',data)

def product_details(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e

    data = {
        'single_product' : single_product,
    }
    return render(request,'store/product-detail.html',data)