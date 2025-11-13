from ninja import NinjaAPI

from config.utils import get_attr, get_status_code
from template_service.api import router

api = NinjaAPI()

api.add_router("template-service/", router)


@api.exception_handler(Exception)
def global_exception_handler(request, exc):
    message = get_attr(exc, "message", "An unexpected error occurred.")
    detail = get_attr(exc, "detail") or str(exc)
    status_code = get_status_code(exc, default=500)
    response_data = {"message": message, "error": detail}
    return api.create_response(request, response_data, status=status_code)
