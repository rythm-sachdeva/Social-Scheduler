from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken



class CustomRegisterSerialiser(RegisterSerializer):

    def get_cleaned_data(self):
        return super().get_cleaned_data()
    
    def save(self, request):
        user = super().save(request)

        refresh = RefreshToken.for_user(user=user)
        user.refresh = str(refresh)
        user.access = str(refresh.access_token)

        return user


    
    
