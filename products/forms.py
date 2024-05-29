from django import forms
from products.models import OrderInfo

        
class UserOrder(forms.ModelForm):
   class Meta:
       model = OrderInfo
       fields = ['email', 'name', 'phone', 'address', 'comment', 'delivery_type']
       widgets = {
           'email': forms.TextInput(attrs={
               'class': 'form-input form-control',
               'placeholder': 'example@gmail.com'
           }),
           'name': forms.TextInput(attrs={
               'class': 'form-input form-control',
               'placeholder': 'Иванов Иван Иванович'
           }),
           'phone': forms.TextInput(attrs={
               'class': 'form-input form-control',
               'placeholder': '89377899878'
           }),
           'address': forms.TextInput(attrs={
               'class': 'form-input form-control',
               'placeholder': 'г. Москва ул. Пушкина д. Колотушкина 2'
           }),
           'comment': forms.Textarea(attrs={
               'class': 'form-input form-control form-textarea',
               'placeholder': 'Дополнительная информация'
           }),
           'delivery_type': forms.Select(attrs={
               'class': 'form-input form-control',
           })
       }
       

class OrderInfoAdminForm(forms.ModelForm):
    class Meta:
       model = OrderInfo
       fields = ['name', 'email', 'phone', 'address', 'comment', 'delivery_type', 'tracking_number', 'delivery_status', 'is_paid']