import logging
from datetime import datetime
from tortoise import fields
from tortoise.models import Model
from enum import Enum

logger = logging.getLogger(__name__)


class User(Model):
    class Meta:
        table = 'users'
        ordering = ['created_at']

    user_id = fields.BigIntField(pk=True, index=True)
    username = fields.CharField(max_length=32, index=True, null=True)
    is_registered = fields.BooleanField(default=False)
    status = fields.CharField(max_length=32, null=True)  # admin

    first_name = fields.CharField(max_length=64)
    last_name = fields.CharField(max_length=64, null=True)
    language_code = fields.CharField(max_length=2, null=True)
    is_premium = fields.BooleanField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @classmethod
    async def update_data(cls, user_id: int, first_name: str, last_name: str, username: str, language_code: str,
                          is_premium: bool):
        user = await cls.filter(user_id=user_id).first()
        if user is None:
            await cls.create(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                language_code=language_code,
                is_premium=is_premium,
            )
        else:
            await cls.filter(user_id=user_id).update(
                first_name=first_name,
                last_name=last_name,
                username=username,
                language_code=language_code,
                is_premium=is_premium,
                updated_at=datetime.now()
            )

    @classmethod
    async def set_status(cls, user_id: int, status: str | None):
        await cls.filter(user_id=user_id).update(status=status)


class Quest(Model):
    class Meta:
        table = 'quests'
        ordering = ['created_at']

    id = fields.IntField(pk=True)
    deeplink = fields.CharField(max_length=64)
    question = fields.TextField()
    answers = fields.JSONField(null=True)  # {'a': '...', 'b': '...', 'c': '...', 'd': '...'}
    correct_answer = fields.CharField(max_length=1, null=True)  # 'a', 'b', 'c', 'd'
    photo_file_id = fields.CharField(max_length=256, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    final_phrase = fields.TextField()


class UserQuest(Model):
    class Meta:
        table = 'users_quests'

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', to_field='user_id')
    quest = fields.ForeignKeyField('models.Quest', to_field='id')


class Post(Model):
    class Meta:
        table = 'static_content'

    id = fields.BigIntField(pk=True)
    text = fields.TextField(null=True)
    photo_file_id = fields.CharField(max_length=256, null=True)
    video_file_id = fields.CharField(max_length=256, null=True)
    video_note_id = fields.CharField(max_length=256, null=True)
    document_file_id = fields.CharField(max_length=256, null=True)
    sticker_file_id = fields.CharField(max_length=256, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
