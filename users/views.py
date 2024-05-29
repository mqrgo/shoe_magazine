from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from users import forms
from django.contrib.auth import authenticate, login, logout
from products import models
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from users.filters import OrderInfoFilter


# Create your views here.
def login_user(request):
    if request.method == 'POST':
        form = forms.LoginUserForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd.get('username'), password=cd.get('password'))
            if user and user.is_active:
                login(request, user)
                if request.session.get('promocode'):
                    del request.session['promocode']
                return redirect(reverse('products:index'))
    else:            
        form = forms.LoginUserForm()
        return render(request, 'users/login.html', {'form': form})


def logout_user(request):
    logout(request)
    if request.session.get('promocode'):
        del request.session['promocode']
    return redirect(reverse('users:login_user'))


@login_required
def lk(request):
    admin = False
    if request.user.is_staff:
        orders = models.OrderInfo.objects.filter(is_paid=True, in_archive=False)
        admin = True
    else:
        orders = models.OrderInfo.objects.filter(user_id=request.user.id, is_paid=True, in_archive=False)
    f = OrderInfoFilter(request.GET, queryset=orders)
    
    return render(request, 'users/lk.html', {'admin': admin, 'filter': f})



# @login_required
# def lk(request):
#     admin = False
#     user_data = {
#             'id': request.user.id,
#             'username': request.user.username,
#             'email': request.user.email,
#             'first_name': request.user.first_name,
#             'last_name': request.user.last_name,
#         }
#     if request.user.is_staff:
#         orders = models.OrderInfo.objects.all()
#         admin = True
#     else:
#         orders = models.OrderInfo.objects.filter(user_id=request.user.id)
#     f = OrderInfoFilter(request.GET, queryset=orders)
    
#     return render(request, 'users/lk.html', {'user_data': user_data, 'admin': admin, 'filter': f})