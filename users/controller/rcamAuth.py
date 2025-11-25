from django.http import HttpRequest
from rest_framework import status
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserToken

class rcamAuth:
    def __init__(self):
          self.strErr: str = ''
          self.status: int
          self.response:dict = {}
    
    def _authenticar(self, request: HttpRequest)-> bool: 
        try:
            email = request.headers.get('usuario')
            password = request.headers.get('senha')
            token_auth = request.headers.get('chave')

            if not email:
                self.strErr = "usuário é obrigatório"
                self.status= status.HTTP_400_BAD_REQUEST
                return False
            
            if not password:
                self.strErr = "senha é obrigatória"
                self.status= status.HTTP_400_BAD_REQUEST
                return False
            
            if not token_auth:
                self.strErr = "chave de authenticação é obrigatório"
                self.status= status.HTTP_400_BAD_REQUEST
                return False
    
            if token_auth != settings.ADMIN_LOGIN_SECRET_KEY:
                self.strErr = "não autorizado"
                self.status= status.HTTP_401_UNAUTHORIZED
                return False      

            user_auth = authenticate(request, username=email, password=password)

            if user_auth is None:
                self.strErr =  "não autorizado"
                self.status=status.HTTP_401_UNAUTHORIZED
                return False
            
            if not user_auth.is_staff and not user_auth.is_superuser:
                self.strErr = "não autorizado"
                self.status=status.HTTP_401_UNAUTHORIZED
                return False
            
            
            if UserToken.objects.filter(user=user_auth).exists():
                UserTokenExist = UserToken.objects.get(user=user_auth)
                if UserTokenExist.is_active and UserTokenExist.access_token:
                    self.strErr = ''
                    self.status = status.HTTP_200_OK
                    self.response = {
                            "message": "Autenticado com sucesso!", 
                            "token": str(UserTokenExist.access_token),
                        }
                    return True
                UserTokenExist.delete()
                                
                    
            
            refreshToken = RefreshToken.for_user(user_auth)
            UserToken.objects.create(
                user=user_auth,
                access_token=str(refreshToken.access_token),
                refresh_token=str(refreshToken),
                user_agent=request.headers.get('User-Agent', '')
            )

            self.strErr = ''
            self.status = status.HTTP_200_OK
            self.response = {
                "message": "Autenticado com sucesso!",
                "token": str(refreshToken.access_token),
            }

            return True
        except Exception as e:
            self.status= status.HTTP_500_INTERNAL_SERVER_ERROR
            self.strErr = self.strErr + ' ' +   str(e)
            return False