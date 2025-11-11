from django.urls import path
from .views import ConnectedAccountList

urlpatterns= [
 path('connected-accounts',ConnectedAccountList.as_view(),name="connected-account")
]