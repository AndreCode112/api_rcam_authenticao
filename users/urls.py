from django.urls import path
from .views import  login, RcamPostsPublicarFeed, RcamGetExtrairFeed, RcamDeletarFeed, checkTokenLoginRcam, docsApi



urlpatterns = [
   path('auth', login, name='auth_login'),
   path('auth/check',checkTokenLoginRcam, name='checkLoginValidatorTokenJwt'),
   path('posts/publicar', RcamPostsPublicarFeed, name='rcam_publicar_feed'),
   path('posts/extrair/feeds', RcamGetExtrairFeed, name='rcam_extrair_feeds'),
   path('posts/deletar/feed', RcamDeletarFeed,  name='rcam_delete_feed'),

   path('docs', docsApi, name='Docs_api')
]

