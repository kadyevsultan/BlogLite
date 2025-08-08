import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from blog.models import Post


@pytest.mark.django_db
class TestLikes:
    def setup_method(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="user1", password="123"
        )
        self.user2 = get_user_model().objects.create_user(
            username="user2", password="456"
        )
        self.post = Post.objects.create(
            title="Test Post", body="Body", author=self.user
        )

    def test_like_is_unique(self):
        # Лайкаем пост первым пользователем
        self.client.force_authenticate(self.user)
        response1 = self.client.post(f"/api/posts/{self.post.id}/like/")
        assert response1.status_code == 200

        # Повторно лайкаем тот же пост — ожидаем либо снятие лайка, либо ошибку
        response2 = self.client.post(f"/api/posts/{self.post.id}/like/")
        # Если toggle — лайк снимается, можно проверить, что лайков стало 0
        self.post.refresh_from_db()
        assert self.post.likes.count() == 0 or response2.status_code != 200

        # Второй пользователь лайкает пост
        self.client.force_authenticate(self.user2)
        response3 = self.client.post(f"/api/posts/{self.post.id}/like/")
        assert response3.status_code == 200
        self.post.refresh_from_db()
        assert self.post.likes.count() == 1

    def test_cannot_duplicate_like(self):
        self.client.force_authenticate(self.user)
        self.client.post(f"/api/posts/{self.post.id}/like/")

        self.post.likes.add(self.user)
        self.post.likes.add(self.user)
        self.post.refresh_from_db()
        # Лайк от одного пользователя только один
        assert self.post.likes.filter(pk=self.user.pk).count() == 1
