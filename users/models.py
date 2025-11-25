from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserToken(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='auth_tokens',
        verbose_name="Usuário"
    )
    access_token = models.TextField(verbose_name="Access Token")
    refresh_token = models.TextField(verbose_name="Refresh Token")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    user_agent = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dispositivo/Navegador")
    
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Token de Usuário"
        verbose_name_plural = "Tokens de Usuários"
        ordering = ['-created_at']

    def __str__(self):
        return f"Token de {self.user} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class Post(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    texto = models.TextField()
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post de {self.autor.username} em {self.criado_em.strftime('%d/%m/%Y')}"

class PostImagem(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='posts_img/')
    
    def save(self, *args, **kwargs):
        if self.post.imagens.count() >= 4 and not self.pk:
            raise ValidationError("Um post não pode ter mais de 4 fotos.")
        super().save(*args, **kwargs)


class PostFonte(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='fontes')
    url = models.URLField(max_length=200)
    descricao = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.url


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) 
    texto = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentário de {self.usuario.username}"


class PostEngajamento(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='engajamento')
    
    curtidas = models.ManyToManyField(User, related_name='posts_curtidos', blank=True)
    deslikes = models.ManyToManyField(User, related_name='posts_descurtidos', blank=True)

    @property
    def total_curtidas(self):
        return self.curtidas.count()

    @property
    def total_deslikes(self):
        return self.deslikes.count()
        
    def __str__(self):
        return f"Engajamento do Post {self.post.id}"
    
