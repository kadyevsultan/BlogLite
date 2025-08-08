import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from blog.models import Post, SubPost


@pytest.mark.django_db
class TestSubPosts:
    def setup_method(self):
        self.user = get_user_model().objects.create_user(
            username="subuser", password="123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        # Создаем пост с двумя под-постами
        self.post_data = {
            "title": "MainPost",
            "body": "Main body",
            "subposts": [
                {"title": "Sub 1", "body": "Body 1"},
                {"title": "Sub 2", "body": "Body 2"},
            ],
        }
        self.post_resp = self.client.post("/api/posts/", self.post_data, format="json")
        self.post_id = self.post_resp.data["id"]
        self.subposts = self.post_resp.data["subposts"]

    def test_add_subpost_to_existing_post(self):
        # Добавляем новый subpost к существующему посту
        patch_data = {
            "subposts": [
                # Сохраняем старые
                {"id": self.subposts[0]["id"], "title": "Sub 1", "body": "Body 1"},
                {"id": self.subposts[1]["id"], "title": "Sub 2", "body": "Body 2"},
                # Новый subpost без id
                {"title": "Sub 3", "body": "Body 3"},
            ]
        }
        resp = self.client.patch(
            f"/api/posts/{self.post_id}/", patch_data, format="json"
        )
        assert resp.status_code == 200
        assert len(resp.data["subposts"]) == 3
        post_obj = Post.objects.get(pk=self.post_id)
        assert post_obj.subposts.count() == 3
        assert post_obj.subposts.filter(title="Sub 3").exists()

    def test_edit_subpost(self):
        sub_id = self.subposts[0]["id"]
        patch_data = {
            "subposts": [
                {"id": sub_id, "title": "Edited title", "body": "Edited body"},
                {"id": self.subposts[1]["id"], "title": "Sub 2", "body": "Body 2"},
            ]
        }
        resp = self.client.patch(
            f"/api/posts/{self.post_id}/", patch_data, format="json"
        )
        assert resp.status_code == 200
        edited = next(sp for sp in resp.data["subposts"] if sp["id"] == sub_id)
        assert edited["title"] == "Edited title"
        assert edited["body"] == "Edited body"
        # Проверяем в базе
        db_sub = SubPost.objects.get(pk=sub_id)
        assert db_sub.title == "Edited title"
        assert db_sub.body == "Edited body"

    def test_delete_subpost(self):
        # Удаляем первый subpost (не передаем его id)
        patch_data = {
            "subposts": [
                {"id": self.subposts[1]["id"], "title": "Sub 2", "body": "Body 2"},
            ]
        }
        resp = self.client.patch(
            f"/api/posts/{self.post_id}/", patch_data, format="json"
        )
        assert resp.status_code == 200
        assert len(resp.data["subposts"]) == 1
        post_obj = Post.objects.get(pk=self.post_id)
        assert post_obj.subposts.count() == 1
        assert not post_obj.subposts.filter(id=self.subposts[0]["id"]).exists()

    def test_update_nonexistent_subpost(self):
        patch_data = {
            "subposts": [
                {"id": 999999, "title": "NoSuch", "body": "Should fail"},
                {"id": self.subposts[1]["id"], "title": "Sub 2", "body": "Body 2"},
            ]
        }
        resp = self.client.patch(
            f"/api/posts/{self.post_id}/", patch_data, format="json"
        )
        assert resp.status_code == 400
        assert "not found" in str(resp.data).lower()

    def test_subposts_readonly_in_get(self):
        resp = self.client.get(f"/api/posts/{self.post_id}/")
        assert resp.status_code == 200
        assert "subposts" in resp.data
        assert isinstance(resp.data["subposts"], list)
        assert (
            len(resp.data["subposts"])
            == Post.objects.get(pk=self.post_id).subposts.count()
        )
        # Проверяем что поля совпадают
        for sub in resp.data["subposts"]:
            db_sub = SubPost.objects.get(pk=sub["id"])
            assert sub["title"] == db_sub.title
            assert sub["body"] == db_sub.body
