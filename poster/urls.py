from django.urls import path
from .views import ConnectedAccountList,ScheduledPostsView 

urlpatterns= [
 path('connected-accounts',ConnectedAccountList.as_view(),name="connected-account"),
 path('scheduled-posts',ScheduledPostsView.as_view(),name="scheduled-posts")
]