import collections
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from core.manager import CoreManager
from core.models import Comment, Messages
from user.models import User
from utils.logger import logger


class CommentConsumer(WebsocketConsumer, CoreManager):

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

                messages: collections.Iterable = Messages.objects.filter(comment=self.comment_id)
                for message in messages:
                    message: Messages
                    self.send(text_data=json.dumps({"message": message.message}))

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

            comment: Comment = self.get_comment("id", self.comment_id)
            current_user: User = self.get_user('username', self.username)

            self.create_message(message, current_user, comment)

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
