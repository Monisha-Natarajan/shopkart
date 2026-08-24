import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from shop.form import CustomUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":products})

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:

            data = json.loads(request.body)
            product_qty = int(data['product_qty'])
            product_id = int(data['pid'])

            product_status = Product.objects.get(id=product_id)

            if product_status:
                if Cart.objects.filter(user=request.user, product_id=product_id):
                    return JsonResponse({'status':'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(
                            user=request.user,
                            product_id=product_id,
                            product_qty=product_qty
                        )
                        return JsonResponse({'status':'Product Added To Cart'}, status=200)
                    else:
                        return JsonResponse({'status':'Product Stock Not Available'}, status=200)

        else:
            return JsonResponse({'status':'Login to add cart'}, status=200)

    return JsonResponse({'status':'Invalid Access'}, status=200)

def fav_page(request):

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        if request.user.is_authenticated:

            data = json.loads(request.body)
            product_id = int(data['pid'])

            try:
                product_status = Product.objects.get(id=product_id)

                if Favourite.objects.filter(user=request.user, product_id=product_id).exists():
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)

                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)

            except Product.DoesNotExist:
                return JsonResponse({'status': 'Product Not Found'}, status=404)

        else:
            return JsonResponse({'status': 'Login to add Favourite'}, status=200)

    return JsonResponse({'status': 'Invalid Access'}, status=400)


def favviewpage(request):

    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, "shop/fav.html", {"fav": fav})

    else:
        return redirect("/")

def remove_fav(request, fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect("shop:favviewpage")

    
def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{"cart":cart})
    else:
        return redirect("/")

def remove_cart(request, cid):
    if request.user.is_authenticated:
        try:
            cartitem = Cart.objects.get(id=cid, user=request.user)
            cartitem.delete()
            messages.success(request, "Item removed from cart")
        except Cart.DoesNotExist:
            messages.error(request, "Cart item not found")
        return redirect("shop:cart")
    else:
        return redirect("shop:login")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out Successfully")
    return redirect("shop:home")

def login_page(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            pwd = request.POST.get('password')

            user = authenticate(request, username=name, password=pwd)

            if user is not None:
                login(request, user)
                messages.success(request, "Logged in Successfully")
                return redirect("shop:home")
            else:
                messages.error(request, "Invalid User Name or Password")
                return redirect("shop:login")

        return render(request, "shop/login.html")


def register(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration success you can Login Now...!")
            return redirect('shop:login')
    return render(request,"shop/register.html",{'form':form})

def collections(request):
    category=Catagory.objects.filter(status=0)
    return render(request,"shop/collections.html",{"category":category})

def collectionsview(request,name):
    if(Catagory.objects.filter(name=name,status=0)):
        products=Product.objects.filter(category__name=name)
        return render(request,"shop/products/index.html",{"products":products,"category_name":name})
    else:
        messages.warning(request,"No such category found")
        return redirect('shop:collections')

def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"shop/products/product_details.html",{"products":products})
        else:
            messages.error(request,"No such Products Found")
            return redirect('shop:collections')
    else:
        messages.error(request,"No such Catagory Found")
        return redirect('shop:collections')



    
