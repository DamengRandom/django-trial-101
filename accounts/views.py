from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only

@unauthenticated_user
def register(request):
    # if request.user.is_authenticated:
    #     return redirect('home')
    # else:
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            # group = Group.objects.get(name='customer')
            # user.groups.add(group) # add user to customer group !!

            messages.success(request, 'account was created for ' + username)

            return redirect('signin')
    
    context = { 'form': form }

    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def signin(request):
    # if request.user.is_authenticated:
    #     return redirect('home')
    # else:
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Either username OR password is not correct')

    context = {}

    return render(request, 'accounts/signin.html', context)


def signout(request):
    logout(request)
    return redirect('signin')


@login_required(login_url='signin')
# @admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    # total counts
    total_customers = customers.count()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'customers': customers, 'total_customers': total_customers, 'total_orders': total_orders, 'delivered': delivered, 'pending': pending}

    # return HttpResponse('Home Page')
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='signin')
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products': products})


@login_required(login_url='signin')
# @allowed_users(allowed_roles=['admin'])
def customer(request, primary_key_id):
    customer = Customer.objects.get(id=primary_key_id)
    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = { 'customer': customer, 'orders': orders, 'total_orders': total_orders, 'myFilter': myFilter }
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='signin')
# @allowed_users(allowed_roles=['admin'])
def createOrder(request, primary_key_customer_id):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'))
    customer = Customer.objects.get(id=primary_key_customer_id)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form = OrderForm(initial={'customer': customer})

    if request.method == 'POST':
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    # context = { 'form': form }
    context = { 'formset': formset }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='signin')
# @allowed_users(allowed_roles=['admin'])
def updateOrder(request, primary_key_order_id):
    order = Order.objects.get(id=primary_key_order_id)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = { 'form': form }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='signin')
# @allowed_users(allowed_roles=['admin'])
def deleteOrder(request, primary_key_order_id):
    order = Order.objects.get(id=primary_key_order_id)

    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = { 'item': order }
    return render(request, 'accounts/delete_order.html', context)
