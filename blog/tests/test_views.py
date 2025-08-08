import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from blog.models import Post


@pytest.mark.django_db
def test_views_count_atomic():
    user = get_user_model().objects.create_user(username="viewuser", password="123")
    client = APIClient()
    client.force_authenticate(user)
    post = Post.objects.create(title="Atomic", body="Body", author=user)

    url = f"/api/posts/{post.id}/views-count/"
    for _ in range(10):
        client.get(url)
    post.refresh_from_db()
    assert post.views_count == 10
