from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from blog.models import Post, SubPost
from blog.serializers import PostSerializer, SubPostSerializer


@extend_schema(
    tags=['Posts']
    )
class PostViewSet(viewsets.ModelViewSet):
    """
    API для управления постами.

    Поддерживает создание, обновление, удаление и просмотр постов.
    Включает вложенные SubPost-ы (только для чтения).
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def create(self, request, *args, **kwargs):
        """
        Переопределение метода создания для создания сразу несколько постов.
        """
        data = request.data
        is_many = isinstance(data, list)

        serializer = self.get_serializer(data=data, many=is_many)
        serializer.is_valid(raise_exception=True)

        if is_many:
            instances = []
            for item in serializer.validated_data:
                instances.append(Post(author=request.user, **item))
            Post.objects.bulk_create(instances)
            response_serializer = self.get_serializer(instances, many=True)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema(
    tags=['SubPosts'],)
class SubPostViewSet(viewsets.ModelViewSet):
    queryset = SubPost.objects.all()
    serializer_class = SubPostSerializer
