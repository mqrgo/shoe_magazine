from dotenv import load_dotenv
from os import getenv

load_dotenv()

class DataBaseConfig:
    name = getenv('NAME')
    user = getenv('USER')
    password = getenv('PASSWORD')
    host = getenv('HOST')
    port = getenv('PORT')


class SMTPConfig:
    user = getenv('EMAIL_HOST_USER')
    password = getenv('EMAIL_HOST_PASSWORD')


class PaymentConfig:
    account_id = getenv('PAYMENT_ACC_ID')
    api_key = getenv('PAYMENT_API_KEY')


class PostOfficeConfig:
    login = getenv('PO_LOGIN')
    password = getenv('PO_PASSWORD')
    
    
    
db_config = DataBaseConfig()
smtp_config = SMTPConfig()
dj_secret_key = getenv('SECRET_KEY')
payment_config = PaymentConfig()
post_office_config = PostOfficeConfig()
