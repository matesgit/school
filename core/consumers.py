import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.contenttypes.models import ContentType
from asgiref.sync import sync_to_async
from .models import *

database_sync_to_async = sync_to_async  # alias for clarity

# Global dict to track unique connections per room group name
online_users = {}  # {room_group_name: set(channel_name)}

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'groupchat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Track unique channel connections
        if self.room_group_name not in online_users:
            online_users[self.room_group_name] = set()
        online_users[self.room_group_name].add(self.channel_name)

        # Broadcast updated online count
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_count',
                'count': len(online_users[self.room_group_name]),
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Remove connection from tracking
        if self.room_group_name in online_users:
            online_users[self.room_group_name].discard(self.channel_name)
            if not online_users[self.room_group_name]:
                del online_users[self.room_group_name]

            # Broadcast updated online count
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_count',
                    'count': len(online_users.get(self.room_group_name, [])),
                }
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        message = data.get('message')
        sender_type = data.get('sender_type')
        sender_id = data.get('sender_id')

        # New file fields (optional)
        file_data = data.get('file')      # base64 data URI string, e.g. "data:image/png;base64,iVBORw0KG..."
        filename = data.get('filename')   # original filename string

        if not sender_type or not sender_id:
            await self.send(text_data=json.dumps({'error': 'Invalid sender info'}))
            return

        if not message and not file_data:
            await self.send(text_data=json.dumps({'error': 'Message or file must be provided'}))
            return

        try:
            if sender_type == 'lector':
                sender_model = Lector
            elif sender_type == 'student':
                sender_model = Student
            else:
                raise ValueError("Invalid sender_type")

            sender = await database_sync_to_async(sender_model.objects.get)(id=sender_id)
            sender_content_type = await database_sync_to_async(ContentType.objects.get_for_model)(sender_model)

            group = await database_sync_to_async(Group.objects.get)(pk=self.room_name)

            chat_message = GroupChatMessage(
                group=group,
                sender_content_type=sender_content_type,
                sender_object_id=sender.id,
                message=message or ''  # save empty string if no text message
            )

            # Save file data if present
            if file_data and filename:
                chat_message.file_url = file_data  # Assuming you have this field on your model as TextField or URLField
                chat_message.filename = filename

            await database_sync_to_async(chat_message.save)()

            payload = {
                'type': 'group_chat_message',
                'message': message,
                'sender_type': sender_type,
                'sender_id': sender_id,
                'sender_name': str(sender),
                'timestamp': chat_message.timestamp.isoformat(),
            }

            if file_data and filename:
                payload['file_url'] = file_data
                payload['filename'] = filename

            await self.channel_layer.group_send(self.room_group_name, payload)

        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def group_chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_type': event['sender_type'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
            'file_url': event.get('file_url'),      # optional
            'filename': event.get('filename'),      # optional
        }))

    async def user_count(self, event):
        # Send online user count to WebSocket with a clear key 'online_count'
        await self.send(text_data=json.dumps({
            'type': 'user_count',
            'online_count': event['count'],
        }))


#   PRIVATE CHAT


online_users = {}  # key: room_group_name, value: set of channel names


class PrivateChatConsumer(AsyncWebsocketConsumer):
    def get_room_group_name(self, sender_type, sender_id, receiver_type, receiver_id):
        participants = sorted([(sender_type, sender_id), (receiver_type, receiver_id)])
        return f'privatechat_{participants[0][0]}_{participants[0][1]}_{participants[1][0]}_{participants[1][1]}'

    async def connect(self):
        self.sender_type = self.scope['url_route']['kwargs']['sender_type']
        self.sender_id = self.scope['url_route']['kwargs']['sender_id']
        self.receiver_type = self.scope['url_route']['kwargs']['receiver_type']
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']

        self.room_group_name = self.get_room_group_name(
            self.sender_type, self.sender_id, self.receiver_type, self.receiver_id
        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        online_users.setdefault(self.room_group_name, set()).add(self.channel_name)
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'presence_update',
            'online_count': len(online_users[self.room_group_name])
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        if self.room_group_name in online_users:
            online_users[self.room_group_name].discard(self.channel_name)
            if not online_users[self.room_group_name]:
                del online_users[self.room_group_name]
            else:
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'presence_update',
                    'online_count': len(online_users[self.room_group_name])
                })

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat')

        if message_type == 'signal':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'signal_forward',
                    'sender_id': self.sender_id,
                    'sender_type': self.sender_type,
                    'signal_data': data.get('signal_data'),
                }
            )
            return

        if message_type == 'chat':
            message = data.get('message')
            sender_type = data.get('sender_type')
            sender_id = data.get('sender_id')
            receiver_type = data.get('receiver_type')
            receiver_id = data.get('receiver_id')

            if not all([message, sender_type, sender_id, receiver_type, receiver_id]):
                return await self.send(text_data=json.dumps({'error': 'Incomplete message data'}))

            try:
                sender_model = Lector if sender_type == 'lector' else Student
                receiver_model = Lector if receiver_type == 'lector' else Student

                sender = await sync_to_async(sender_model.objects.get)(id=sender_id)
                receiver = await sync_to_async(receiver_model.objects.get)(id=receiver_id)

                sender_ct = await sync_to_async(ContentType.objects.get_for_model)(sender_model)
                receiver_ct = await sync_to_async(ContentType.objects.get_for_model)(receiver_model)

                msg = PrivateChat(
                    sender_content_type=sender_ct,
                    sender_object_id=sender.id,
                    receiver_content_type=receiver_ct,
                    receiver_object_id=receiver.id,
                    message=message
                )
                await sync_to_async(msg.save)()

                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'private_chat_message',
                    'message': message,
                    'sender_id': sender_id,
                    'sender_type': sender_type,
                    'sender_name': str(sender),
                    'timestamp': msg.timestamp.isoformat()
                })

            except Exception as e:
                await self.send(text_data=json.dumps({'error': str(e)}))

    async def private_chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_type': event['sender_type'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp']
        }))

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'online_count': event['online_count']
        }))

    async def signal_forward(self, event):
        if event['sender_id'] != self.sender_id or event['sender_type'] != self.sender_type:
            await self.send(text_data=json.dumps({
                'type': 'signal',
                'signal_data': event['signal_data']
            }))


