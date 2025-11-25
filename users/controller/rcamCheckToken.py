from datetime import datetime, timezone
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserToken

class RcamAuthTokenValidator:
    def __init__(self):
        self.strErr: str = ''
        self.status: int = 0
        self.token :str = ''
        self.user = None
        self.newRefreshtoken:bool =  False


    def validToken(self, refresh_token, exp_token:int = 0):
       try:
            if exp_token == 0:
                refresh_new_token = RefreshToken(refresh_token)
                self.token = str(refresh_new_token.access_token)
                return True

            data_datetime_token = datetime.fromtimestamp(exp_token, timezone.utc)
            data_atual = datetime.now(timezone.utc)

            if data_atual > data_datetime_token:
                refresh_new_token = RefreshToken(refresh_token)
                self.token = str(refresh_new_token.access_token)
                         
            return True

       except (TokenError, InvalidToken):
           newRefreshToken = RefreshToken.for_user(self.user)
           userToken = UserToken.objects.get(user= self.user)
           userToken.access_token = newRefreshToken.access_token
           userToken.refresh_token = newRefreshToken
           userToken.save()

           self.token = newRefreshToken.access_token
           self.newRefreshtoken = True

           return True

       except Exception as _:
           self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
           self.strErr= 'Erro interno no servidor, contate o Administrador'
           return False

    def execute(self, request: HttpRequest) -> bool:
        UserModel = get_user_model()

        try:
            auth_header:str = request.headers.get('Authorization')
        
            if not auth_header:
                self.strErr = "não autorizado [-1]"
                self.status = status.HTTP_401_UNAUTHORIZED
                return False
    
            prefix, Token = auth_header.split()
            if prefix.lower() != 'bearer':
                self.strErr = "não autorizado [0]"
                self.status = status.HTTP_401_UNAUTHORIZED
                return False
            

            userToken = UserToken.objects.get(access_token = Token)
            
            if userToken is None:
                self.strErr = 'não autorizado [1]'
                self.status = status.HTTP_401_UNAUTHORIZED
                return False
            

            if not userToken.is_active:
                self.strErr = 'não autorizado [2]'
                self.status = status.HTTP_401_UNAUTHORIZED
                return False
            
            
            UserAuth = UserModel.objects.get(id=userToken.user.id)
            
            if not UserAuth.is_active:
                self.strErr = "não autorizado [3]"
                self.status = status.HTTP_401_UNAUTHORIZED
                return False
            
            if not UserAuth.is_staff:
                self.strErr = "não autorizado [4]"
                self.status = status.HTTP_401_UNAUTHORIZED
                return False
            

            self.user = UserAuth
            
            
            token_user_token = AccessToken(userToken.access_token)
            token_user_token.verify()


            if not self.validToken(refresh_token= userToken.refresh_token, exp_token= token_user_token["exp"]):
                return False
            
            return True
        
        except ValueError as e:
            self.strErr = f"não autorizado -[1]"
            self.status = status.HTTP_401_UNAUTHORIZED
            return False
        
        except UserToken.DoesNotExist:
            self.strErr = "não autorizado -[2]"
            self.status = status.HTTP_401_UNAUTHORIZED
            return False
        
        except UserModel.DoesNotExist:
            self.strErr = "não autorizado -[3]"
            self.status = status.HTTP_401_UNAUTHORIZED
            return False
        
        except (TokenError, InvalidToken):
            if not self.validToken(refresh_token=userToken.refresh_token):
                return False
            

            if not self.newRefreshtoken:
                userToken.access_token = self.token 
                userToken.save()

            return True   
        
        except Exception as _:
            self.strErr = f"Erro interno no servidor, contate o Administrador"
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR 
            return False