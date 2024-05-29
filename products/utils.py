import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from yookassa import Payment, Configuration
from main import settings
from products.models import OrderInfo
from main.celery import app
from products.send_email import send_user_email



def parse_iso_date(date_str):
    date = datetime.fromisoformat(date_str)
        
    return date.strftime('%d-%m-%Y')


def get_send_order_info(barcode: str):
    url = "https://tracking.russianpost.ru/rtm34"
    headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
    info = list()
    namespaces = { 'ns3': 'http://russianpost.org/operationhistory/data', 'S': 'http://www.w3.org/2003/05/soap-envelope'}
    soap_request = """
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:oper="http://russianpost.org/operationhistory" xmlns:data="http://russianpost.org/operationhistory/data" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/">
       <soap:Header/>
       <soap:Body>
          <oper:getOperationHistory>
             <data:OperationHistoryRequest>
                <data:Barcode>"""+barcode+"""</data:Barcode>
                <data:MessageType>0</data:MessageType>
                <data:Language>RUS</data:Language>
             </data:OperationHistoryRequest>
             <data:AuthorizationHeader ns1:mustUnderstand="1">
                <data:login>"""+settings.POST_OFFICE_LOGIN+"""</data:login>
                <data:password>"""+settings.POST_OFFICE_PASSWORD+"""</data:password>
             </data:AuthorizationHeader>
          </oper:getOperationHistory>
       </soap:Body>
    </soap:Envelope>
    """
    
    response = requests.post(url, data=soap_request, headers=headers)
    root = ET.fromstring(response.text)

    for record in root.findall('.//ns3:historyRecord', namespaces):
        place = record.find('.//ns3:OperationAddress/ns3:Description', namespaces).text
        date = record.find('.//ns3:OperationParameters/ns3:OperDate', namespaces).text
        date = parse_iso_date(date)
        status = record.find('.//ns3:OperationParameters/ns3:OperAttr/ns3:Name', namespaces)
        if status is not None and status.text not in ['Единичный', 'Упрощенный предзаполненный', 'Адресату почтальоном', 'Иная']:
            tmp_info = {
                'place': place,
                'date': date,
                'status': status.text,
            }
            info.append(tmp_info)
            
    return info



def make_cart(cart_items):
    ordered_products = []
    for item in cart_items:
        tmp = dict(title=f'{item.product.brand} - {item.product.title}', articul=item.product.article, size=item.size, amount=item.amount)
        ordered_products.append(tmp)
    return ordered_products
 
 
def last_check_items(cart_items):
    tmp = [item.product.stock.get(size=item.size).amount >= item.amount for item in cart_items]
    if all(tmp):
        for item in cart_items:
            stock = item.product.stock.get(size=item.size)
            stock.amount -= item.amount
            stock.save()
        return True
    else:
        for item in cart_items:
            stock_amount = item.product.stock.get(size=item.size).amount
            if stock_amount < item.amount:
                item.amount = stock_amount
                item.save()
        return False
     

def create_payment(total_price, order_number):
   try:
        Configuration.account_id = settings.PAYMENT_ID
        Configuration.secret_key = settings.PAYMENT_API_KEY
        payment = Payment.create({
            "amount": {
                "value": str(total_price),
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card" 
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"http://127.0.0.1:8000/success_order/?order_number={str(order_number)}" 
            },
            "description": f"{str(order_number)}",
            "metadata": {
                "order_id": str(order_number)
            }
        })

        confirmation_url = payment.confirmation.confirmation_url
        
        return payment.id, confirmation_url
   except Exception:
        return None, None
    
    
@app.task
def testtest():
    Configuration.account_id = settings.PAYMENT_ID
    Configuration.secret_key = settings.PAYMENT_API_KEY
    me = Payment.list()
    yookassa_order_list = list()
    for i in me:
        tmp = i[1]
        for j in tmp:
            if isinstance(j, dict):
                yookassa_order_list.append(j['metadata'].get('order_id'))
    orders = OrderInfo.objects.filter(is_paid=False)
    for order in orders:
        if str(order.order_number) in yookassa_order_list:
            order.is_paid = True
            order.cart.cart_items.all().delete()
            order.save()
            user_data = {field.name: getattr(order, field.name) for field in OrderInfo._meta.fields if field.name != 'user' and field.name != 'cart'}
            user_data['order_date'] = user_data['order_date'].isoformat()
            send_user_email.delay(user_data)
            
      