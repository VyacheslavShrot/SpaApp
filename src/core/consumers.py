import collections
import json

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from core.manager import CoreManager
from core.models import Comment, Messages
from user.models import User
from utils.logger import logger


@shared_task
def create_message(message: str, username: str, comment_id: str) -> None:
    comment: Comment = Comment.objects.get(id=comment_id)
    current_user: User = User.objects.get(username=username)

    Messages.objects.create(
        message=message,
        user=current_user,
        comment=comment
    )


@shared_task
def send_chat_messages(comment_id: str) -> None:
    messages: collections.Iterable = Messages.objects.filter(comment=comment_id)
    channel_layer = get_channel_layer()

    for message in messages:
        message: Messages
        async_to_sync(channel_layer.group_send)(
            f"chat_{comment_id}",
            {"type": "chat_message", "message": message.message}
        )


class CommentConsumer(WebsocketConsumer, CoreManager):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.username = None
        self.room_group_name = None
        self.comment_id = None

    def connect(self):
        try:
            self.comment_id: str = self.scope["url_route"]["kwargs"]["comment_id"]
            self.room_group_name: str = "chat_%s" % self.comment_id
            self.username: str = cache.get('username')

            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.accept()

            try:
                comment: Comment = self.get_comment("id", self.comment_id)
                self.send(text_data=json.dumps({"message": comment.text}))

                send_chat_messages.delay(self.comment_id)

            except ObjectDoesNotExist:
                self.send(text_data=json.dumps({"message": f"There is no such comment with this id {self.comment_id}"}))
            except ValueError:
                self.send(text_data=json.dumps({"message": f"Expected a number but got {self.comment_id}"}))
        except Exception as e:
            logger.error(f"An error occurred while connecting to websocket | {str(e)}")

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name, self.channel_name
            )
        except Exception as e:
            logger.error(f"An error occurred while disconnecting from websocket | {str(e)}")

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
            body: dict = self.get_body(data, 'message')

            message = body.get('message')
            create_message.delay(message, self.username, self.comment_id)

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "chat_message", "message": message}
            )
        except Exception as e:
            logger.error(f"An error occurred while receive text from client | {str(e)}")

    def chat_message(self, event):
        try:
            message: str = event["message"]

            self.send(text_data=json.dumps({"message": message}))
        except Exception as e:
            logger.error(f"An error occurred while chat | {str(e)}")
