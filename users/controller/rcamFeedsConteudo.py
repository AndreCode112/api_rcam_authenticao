from django.http import HttpRequest
from .rcamCheckToken import RcamAuthTokenValidator
from  users.models import Post, PostImagem, PostFonte, PostEngajamento
from rest_framework import status


class RcamFeedsConteudo:
    def __init__(self):
        self.strErr:str = ""
        self.status:int
        self.response:dict = {}

    def _Postar_feed(self, request:HttpRequest) -> bool:
        try:

            instanceAuthToken:RcamAuthTokenValidator = RcamAuthTokenValidator()

            if not instanceAuthToken.execute(request):
                self.strErr = instanceAuthToken.strErr
                self.status = instanceAuthToken.status
                return False
            
            if instanceAuthToken.token:
                self.response['token'] = str(instanceAuthToken.token)
                self.status =  status.HTTP_202_ACCEPTED
                return True
            
        
            usuario = instanceAuthToken.user
            texto = request.data.get('texto', '')
            imagens = request.FILES.getlist('imagens')
            fontes = request.data.get('fontes', [])

            if not texto:
                self.strErr = "Texto do post é obrigatório."
                self.status = status.HTTP_400_BAD_REQUEST
                return False
            
            if len(imagens) > 4:
                self.strErr = "Um post não pode ter mais de 4 fotos."
                self.status = status.HTTP_400_BAD_REQUEST
                return False
        
        
            novo_post = Post.objects.create(autor=usuario, texto=texto)

            for img in imagens:
                PostImagem.objects.create(post=novo_post, imagem=img)

            for fonte_url in fontes:
                PostFonte.objects.create(post=novo_post, url=fonte_url)


            PostEngajamento.objects.create(post=novo_post)

            
            self.strErr = ""
            self.status = 201
            self.response = {
                "message": "Post criado com sucesso.",
                "post_id": novo_post.id
            }

            
            return True

        except Exception as e:
            self.strErr = f"Erro interno no servidor, contate o Administrador: {str(e)}"
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
        

    def _Obter_todos_feeds(self, request:HttpRequest) -> bool:
        try:
            instanceAuthToken: RcamAuthTokenValidator = RcamAuthTokenValidator()

            if not instanceAuthToken.execute(request):
                self.strErr = instanceAuthToken.strErr
                self.status = instanceAuthToken.status
                return False
            
            if instanceAuthToken.token:
                self.response['token'] = str(instanceAuthToken.token)
                self.status =  status.HTTP_202_ACCEPTED
                return True
            

            posts_qs = Post.objects.all().select_related('engajamento', 'autor').prefetch_related(
                'imagens', 
                'fontes', 
                'comentarios'
            ).order_by('-id')

            feed_data = []

            for post in posts_qs:
                lista_imagens = [img.imagem.url for img in post.imagens.all()]

                lista_fontes = [fonte.url for fonte in post.fontes.all()]

                autor_data = {
                    "id": post.autor.id,
                    "username": post.autor.username,
                }
                
                engajamento_obj = post.engajamento
                qtd_curtidas = engajamento_obj.total_curtidas  if  engajamento_obj.total_curtidas > 0 else 0
                
                qtd_comentarios = post.comentarios.count()

                post_dict = {
                    "id": post.id,
                    "autor": autor_data,
                    "texto": post.texto,
                    "imagens": lista_imagens,
                    "fontes": lista_fontes,
                    "data_criacao": post.criado_em.isoformat() if post.criado_em else None,
                    "engajamento": {
                        "curtidas": qtd_curtidas,
                        "comentarios": qtd_comentarios
                    }
                }
                feed_data.append(post_dict)

            
            self.response = {
                "message": "Todos os posts recuperados com sucesso.",
                "Posts": feed_data
            }
            
            self.strErr = ""
            self.status = status.HTTP_200_OK
            return True

        except Exception as e:
            self.strErr = f"Erro interno no servidor, contate o Administrador: {str(e)}"
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR 
            return False
        

    def _Deletar_post(self, request:HttpRequest) -> bool:
        try:
            instanceAuthToken:RcamAuthTokenValidator = RcamAuthTokenValidator()

            if not instanceAuthToken.execute(request):
                self.strErr = instanceAuthToken.strErr
                self.status = instanceAuthToken.status
                return False

            if instanceAuthToken.token:
                self.response['token'] = str(instanceAuthToken.token)
                self.status =  status.HTTP_202_ACCEPTED
                return True
            

            usuario = instanceAuthToken.user
            post_id = request.headers.get('idPost')

            if not post_id:
                self.strErr = "ID do post é obrigatório."
                self.status = status.HTTP_400_BAD_REQUEST
                return False

            
            post = Post.objects.get(id=post_id, autor=usuario)
            post.delete()
        
            self.strErr = ""
            self.status = 200
            self.response = {
                "message": "Post deletado com sucesso."
            }


            return True
        
        except Post.DoesNotExist:
            self.strErr = f"Erro ao tentar deletar o post, contate o Administrador"
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR    
            return False

        except Exception as e:
            self.strErr = f"Erro interno no servidor, contate o Administrador:  {str(e)}"
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False