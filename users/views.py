from django.shortcuts import render
from .controller.rcamAuth import rcamAuth
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .controller.rcamFeedsConteudo import RcamFeedsConteudo
from .controller.rcamCheckToken import RcamAuthTokenValidator 


@require_http_methods(["POST"])
@api_view(['POST'])
def login(request):
    instanceRcamAuth: rcamAuth = rcamAuth()
    if not instanceRcamAuth._authenticar(request):
        return Response(
            {
                "message": instanceRcamAuth.strErr
            },
            status=instanceRcamAuth.status
        )
    
    return Response(
        instanceRcamAuth.response,
        status=instanceRcamAuth.status
    )


@require_http_methods(["POST"])
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def RcamPostsPublicarFeed(request):
    instanceRcamFeedsConteudo: RcamFeedsConteudo = RcamFeedsConteudo()
    if not instanceRcamFeedsConteudo._Postar_feed(request):
        return Response(
            {
                "message": instanceRcamFeedsConteudo.strErr
            },
            status=instanceRcamFeedsConteudo.status
        )
    
    return Response(
        instanceRcamFeedsConteudo.response,
        status=instanceRcamFeedsConteudo.status
    )



@require_http_methods(["GET"])
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def RcamGetExtrairFeed(request):
    instanceRcamFeedsConteudo: RcamFeedsConteudo = RcamFeedsConteudo()
    if not instanceRcamFeedsConteudo._Obter_todos_feeds(request):
        return Response(
            {
                "message": instanceRcamFeedsConteudo.strErr
            },
            status=instanceRcamFeedsConteudo.status
        )
    
    return Response(
        instanceRcamFeedsConteudo.response,
        status=instanceRcamFeedsConteudo.status
    )


@require_http_methods(["DELETE"])
@api_view(['DELETE'])
@authentication_classes([])
@permission_classes([])
def RcamDeletarFeed(request):
    instanceRcamFeedsConteudo: RcamFeedsConteudo = RcamFeedsConteudo()
    if not instanceRcamFeedsConteudo._Deletar_post(request):
        return Response(
            {
                "message": instanceRcamFeedsConteudo.strErr
            },
            status=instanceRcamFeedsConteudo.status
        )
    
    return Response(
        instanceRcamFeedsConteudo.response,
        status=instanceRcamFeedsConteudo.status
    )


@require_http_methods(["POST"])
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def checkTokenLoginRcam(request):
    instanceAuthToken:RcamAuthTokenValidator = RcamAuthTokenValidator()
    response: dict= {}
    mensagem: str = ''
    if not instanceAuthToken.execute(request):
        return Response(
            {
                "message": instanceAuthToken.strErr
            },
            status=instanceAuthToken.status
        )
        
    status_ = 200
    mensagem = 'Token validado com sucesso'
    if instanceAuthToken.token:
        mensagem = 'Novo token gerado com sucesso.'
        response['token'] = str(instanceAuthToken.token)

    response['message'] = mensagem
    return Response(
        response,
        status=status_
    )
    
        

def page_404(request, exception):
   return render(request, '404.html', status=404)



def docsApi(request):
    return render(request, 'docs.html')
