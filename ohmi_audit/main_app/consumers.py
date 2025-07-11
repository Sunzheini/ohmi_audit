import json
from channels.generic.websocket import AsyncWebsocketConsumer
from celery.result import AsyncResult


class TaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get task_id from URL and store it
        self.task_id = self.scope['url_route']['kwargs']['task_id']

        # Accept the WebSocket connection
        await self.accept()

        # Immediately send the task status
        await self.send_task_status()

    async def disconnect(self, close_code):
        # Optional: Handle the disconnect event if needed
        pass

    async def send_task_status(self):
        # Get the Celery task result
        result = AsyncResult(self.task_id)

        # Prepare the response data
        if result.ready():
            status = 'SUCCESS' if result.successful() else 'FAILURE'
            response_data = {
                'status': status,
                'result': result.result if status == 'SUCCESS' else None
            }
        else:
            # Task still running, send "PENDING" status
            response_data = {'status': 'PENDING', 'result': None}

        # Send the status update to WebSocket
        await self.send(text_data=json.dumps(response_data))

        # If the task is still running, check every 1 second
        if result.status != 'SUCCESS' and result.status != 'FAILURE':
            await self.send_task_status()  # Recurse to keep checking
