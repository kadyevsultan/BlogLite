from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from blog.models import Post, SubPost


class SubPostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели SubPost.
    Включает поле для идентификатора родительского поста.
    """

    id = serializers.IntegerField(required=False)

    class Meta:
        model = SubPost
        exclude = ["post"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_subposts(self, value):
        if self.instanse is None:
            for item in value:
                if "id" in item:
                    raise serializers.ValidationError(
                        "При создании поста нельзя указывать ID подпостов."
                    )
        return value


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Post с вложенными под-постами.
    """

    subposts = SubPostSerializer(many=True, required=False)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "author",
            "created_at",
            "updated_at",
            "subposts",
            "likes_count",
            "views_count",
        ]
        read_only_fields = (
            "id",
            "author",
            "created_at",
            "updated_at",
            "likes_count",
            "views_count",
        )

    def get_likes_count(self, obj) -> int:
        return obj.likes.count()

    @transaction.atomic
    def create(self, validated_data):
        subposts_data = validated_data.pop("subposts", [])
        post = Post.objects.create(**validated_data)
        for subpost_data in subposts_data:
            subpost_data.pop("id", None)
            SubPost.objects.create(post=post, **subpost_data)
        return post

    @transaction.atomic
    def update(self, instance, validated_data):
        subposts_data = validated_data.pop("subposts", None)
        instance.title = validated_data.get("title", instance.title)
        instance.body = validated_data.get("body", instance.body)
        instance.save()

        if subposts_data is not None:
            existing_ids = []

            for subpost_data in subposts_data:
                subpost_id = subpost_data.get("id", None)

                if subpost_id:
                    try:
                        # Update
                        subpost = SubPost.objects.get(id=subpost_id, post=instance)
                        subpost.title = subpost_data.get("title", subpost.title)
                        subpost.body = subpost_data.get("body", subpost.body)
                        subpost.save()
                        existing_ids.append(subpost_id)
                    except SubPost.DoesNotExist:
                        raise ValidationError(
                            f"SubPost with id {subpost_id} not found for this post."
                        )

                else:
                    # Create
                    new_sub = SubPost.objects.create(post=instance, **subpost_data)
                    existing_ids.append(new_sub.id)

            # Delete missing subposts
            instance.subposts.exclude(id__in=existing_ids).delete()
        return instance
