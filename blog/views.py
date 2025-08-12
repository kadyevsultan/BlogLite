from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from django.db.models import F

from blog.models import Post, SubPost
from blog.serializers import PostSerializer, SubPostSerializer


@extend_schema(tags=["Posts"])
class PostViewSet(viewsets.ModelViewSet):
    """
    API для управления постами.

    Поддерживает создание, обновление, удаление и просмотр постов.
    Включает вложенные SubPost-ы (только для чтения).
    """

    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer

    def create(self, request, *args, **kwargs):
        """
        Переопределение метода создания для создания сразу несколько постов.
        """
        data = request.data
        is_many = isinstance(data, list)

        serializer = self.get_serializer(data=data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(request=None, summary="Поставить или убрать лайк на пост.")
    @action(detail=True, methods=["post"], url_path="like")
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"detail": "Лайк убран"}, status=status.HTTP_200_OK)
        else:
            post.likes.add(user)
            return Response({"detail": "Лайк поставлен"}, status=status.HTTP_200_OK)

    @extend_schema(summary="Увеличить счётчик просмотров на 1")
    @action(detail=True, methods=["get"], url_path="views-count")
    def views_count(self, request, pk=None):
        post = self.get_object()

        Post.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)
        post.refresh_from_db()

        return Response({"views_count": post.views_count}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["SubPosts"],
)
class SubPostViewSet(viewsets.ModelViewSet):
    """
    API для управления вложенными SubPost-ами.
    """

    queryset = SubPost.objects.all()
    serializer_class = SubPostSerializer
