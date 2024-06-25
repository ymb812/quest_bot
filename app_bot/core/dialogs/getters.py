from aiogram.enums import ContentType
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from core.database.models import Post
from settings import settings


async def get_menu_media(**kwargs):
    welcome_post = await Post.get(id=settings.welcome_post_id)
    media_content = MediaAttachment(ContentType.PHOTO, file_id=MediaId(file_id=welcome_post.photo_file_id))

    return {
        'media_content': media_content,
        'msg_text': welcome_post.text,
    }
