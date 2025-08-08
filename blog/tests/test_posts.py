import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from blog.models import Post


@pytest.mark.django_db
class TestPosts:
    def setup_method(self):
        self.user = get_user_model().objects.create_user(
            username="bulkuser", password="123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_bulk_create_posts(self):
        posts_data = [
            {"title": "Bulk 1", "body": "Body 1"},
            {"title": "Bulk 2", "body": "Body 2"},
        ]
        resp = self.client.post("/api/posts/", posts_data, format="json")
        assert resp.status_code == 201
        assert len(resp.data) == 2
        # Проверим, что автор — текущий пользователь
        for post in resp.data:
            assert post["author"] == self.user.id

    def test_single_post_create(self):
        post_data = {"title": "Single", "body": "Single body"}
        resp = self.client.post("/api/posts/", post_data, format="json")
        assert resp.status_code == 201
        assert resp.data["title"] == "Single"
        assert resp.data["author"] == self.user.id

    def test_create_post_with_subposts(self):
        post_data = {
            "title": "WithSub",
            "body": "Main body",
            "subposts": [
                {"title": "Sub 1", "body": "Body 1"},
                {"title": "Sub 2", "body": "Body 2"},
            ],
        }
        resp = self.client.post("/api/posts/", post_data, format="json")
        assert resp.status_code == 201
        assert len(resp.data["subposts"]) == 2
        post_id = resp.data["id"]
        post_obj = Post.objects.get(pk=post_id)
        assert post_obj.subposts.count() == 2

    def test_create_post_missing_title(self):
        post_data = {"body": "No title"}
        resp = self.client.post("/api/posts/", post_data, format="json")
        assert resp.status_code == 400  # Ожидаем ошибку валидации

    def test_create_post_missing_body(self):
        post_data = {"title": "No body"}
        resp = self.client.post("/api/posts/", post_data, format="json")
        assert resp.status_code == 400  # Ожидаем ошибку валидации

    def test_bulk_create_posts_with_subposts(self):
        posts_data = [
            {"title": "Bulk 1", "body": "Body 1"},
            {"title": "Bulk 2", "body": "Body 2"},
            {
                "title": "Bulk 3",
                "body": "Body 3",
                "subposts": [
                    {"title": "Sub 1", "body": "Body 1"},
                    {"title": "Sub 2", "body": "Body 2"},
                ],
            },
            {
                "title": "Bulk 4",
                "body": "Body 4",
                "subposts": [
                    {"title": "Sub 1", "body": "Body 1"},
                    {"title": "Sub 2", "body": "Body 2"},
                ],
            },
        ]
        resp = self.client.post("/api/posts/", posts_data, format="json")
        assert resp.status_code == 201
        assert len(resp.data) == 4
        # Проверим, что автор — текущий пользователь
        for post in resp.data:
            assert post["author"] == self.user.id
