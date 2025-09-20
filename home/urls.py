from django.urls import path, include
from ninja import NinjaAPI
from .views import official_router, zone_router, contact_router, newsletter_router
from .news_views import news_router, category_router
from .image_views import image_router

api = NinjaAPI()

api.add_router("/zones/", zone_router)
api.add_router("/officials/", official_router)
api.add_router("/news/", news_router)
api.add_router("/news-categories/", category_router)
api.add_router("/contact/", contact_router)
api.add_router("/newsletter/", newsletter_router)
api.add_router("/images/", image_router)


urlpatterns = [
    path("", api.urls),
]
