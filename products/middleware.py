from django.utils.deprecation import MiddlewareMixin
from products.models import Cart


class CreateAnonymSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.session_key:
            request.session.save()
            
        request.anonymous_session_id = request.session.session_key
        request.anonymous_session_data = request.session.items()
        if not Cart.objects.filter(user=request.anonymous_session_id).exists():
            Cart.objects.create(user=request.anonymous_session_id)
        