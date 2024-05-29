from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import BadHeaderError
from django.http import HttpResponse
import json
from celery import shared_task


@shared_task
def send_user_email(user_data):
    user_email = user_data.get('email')
    admin_email = 'shinkansentourist@yandex.ru'
    subject = f'Заказ № {user_data.get('order_number')}'
    message = 'Это тестовое письмо в формате текста.'
    order = user_data.get('order')
    del_type = 'CDEK' if user_data.get('delivery_type') == 'CD' else 'Почта России'
    order_list = ''
    for item in order:
        order_list += f'<li>{item.get('title')} x {item.get('articul')} x {item.get('size')} x {item.get('amount')}</li>'
    html_message = f'''
    <html>
        <head></head>
        <body>
            <h1>Спасибо за заказ!</h1>
            <p><strong>{user_data.get('name')}</strong>, Ваш заказ был сформирован.</p>
            <p>В течении 2-х дней мы сформируем заказ, и отправим его Вам!</p>
            <p>Отследить заказ вы можете на нашем сайте, в разделе "Отследить заказ"</p>
            <h4>Получатель:</h4>
            <ul>
                <li>Номер заказа: <strong>{user_data.get('order_number')}</strong></li>
                <li>ФИО: <strong>{user_data.get('name')}</strong></li>
                <li>Телефон: <strong>{user_data.get('phone')}</strong></li>
                <li>Почта: <strong>{user_email}</strong></li>
                <li>Адрес доставки: <strong>{user_data.get('address')}</strong></li>
                <li>Метод доставки: <strong>{del_type}</strong></li>
            </ul>
            <h4>Товары:</h4>
            <ol>
                {order_list}
            </ol>
        </body>
    </html>
    '''
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email, admin_email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)
        return True
    except BadHeaderError:
        return HttpResponse('Найден некорректный заголовок.')
    except Exception as e:
        return HttpResponse(f'Ошибка SMTP: {e}')
    