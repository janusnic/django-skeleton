from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from core.utils.decorators import log
from . import models
from . import forms


@log
def index(request, template='user/cart/index.html', context={}):
    last_products = models.Product.objects.filter(is_active=True)[0:25]
    context['last_products'] = last_products
    return render(request, template, context)


@log
def product(request, product_id, template='user/cart/product.html', context={}):
    product_item = models.Product.objects.get(pk=product_id, is_active=True)

    # shopproduct list
    shopproduct_list = product_item.shopproduct_set.filter(shop__is_active=True)

    # lowest price
    product_lowest_price = None
    product_lowest_price_currency = ""
    for shopproduct in shopproduct_list:
        if not product_lowest_price or shopproduct.price < product_lowest_price:
            product_lowest_price = shopproduct.price
            product_lowest_price_currency = shopproduct.currency.title

    # productreview list
    productreview_list = product_item.productreview_set.filter(is_approved=True)

    # product rate
    product_rate = 0
    product_rate_sum = 0
    product_rate_count = 0
    for productreview in productreview_list:
        product_rate_sum += productreview.rating
        product_rate_count += 1
        product_rate = int(product_rate_sum / product_rate_count)

    # productreview form
    productreview_form = forms.ProductReviewForm()

    context['product_item'] = product_item
    context['shopproduct_list'] = shopproduct_list
    context['product_price'] = product_lowest_price
    context['product_price_currency'] = product_lowest_price_currency
    context['productreview_list'] = productreview_list
    context['product_rate'] = product_rate
    context['productreview_form'] = productreview_form
    return render(request, template, context)


@log
def product_review(request, product_id):
    productreview_form = forms.ProductReviewForm(request.POST or None)

    if request.method == 'POST':
        if productreview_form.is_valid():
            productreview = productreview_form.save(commit=False)
            productreview.product_id = product_id
            productreview.user = request.user
            productreview.save()
            messages.add_message(request, messages.INFO, _('Your review has successfully submitted for approve.'))
        else:
            messages.add_message(request, messages.ERROR, _('Please fix errors bellow.'))
    else:
        messages.add_message(request, messages.WARNING, _('Please post review data.'))

    return redirect(reverse('cart_product', args=(product_id, )))


@log
def shop(request, shop_id, template='user/cart/shop.html', context={}):
    shop_item = models.Shop.objects.get(pk=shop_id, is_active=True)
    shop_products = []
    related_shop_products = models.ShopProduct.objects.filter(shop=shop_item, product__is_active=True)

    # shopreview list
    shopreview_list = shop_item.shopreview_set.filter(is_approved=True)

    # calculate rate
    shop_rate = 0
    shop_rate_sum = 0
    shop_rate_count = 0
    for shopreview in shopreview_list:
        shop_rate_sum += shopreview.rating
        shop_rate_count += 1
        shop_rate = int(shop_rate_sum / shop_rate_count)

    for shop_product in related_shop_products:
        shop_products.append(shop_product.product)

    # shop review form
    shopreview_form = forms.ShopReviewForm()

    context['shop_item'] = shop_item
    context['shopreview_list'] = shopreview_list
    context['shop_rate'] = shop_rate
    context['shop_products'] = shop_products
    context['shopreview_form'] = shopreview_form
    return render(request, template, context)


@log
def shop_review(request, shop_id):
    shopreview_form = forms.ShopReviewForm(request.POST or None)

    if request.method == 'POST':
        if shopreview_form.is_valid():
            shopreview = shopreview_form.save(commit=False)
            shopreview.shop_id = shop_id
            shopreview.user = request.user
            shopreview.save()
            messages.add_message(request, messages.INFO, _('Your review has successfully submitted for approve.'))
        else:
            messages.add_message(request, messages.ERROR, _('Please fix errors bellow.'))
    else:
        messages.add_message(request, messages.WARNING, _('Please post review data.'))

    return redirect(reverse('cart_shop', args=(shop_id, )))

