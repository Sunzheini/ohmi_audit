"""
Celery task views.
Contains views for testing and monitoring Celery background tasks.
"""
from celery.result import AsyncResult
from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.generic import View

from ohmi_audit.main_app.tasks import long_running_task


def task_status(request, task_id):
    """
    Check the status of a Celery task by its ID.
    Returns JSON with task status, progress, and result.
    """
    task_result = AsyncResult(task_id)

    response_data = {
        'ready': task_result.ready(),
        'status': task_result.status,
        'result': task_result.result if task_result.ready() else None,
    }

    if task_result.status == 'PROGRESS':
        response_data['progress'] = task_result.info.get('current', 0)
        response_data['total'] = task_result.info.get('total', 1)

    return JsonResponse(response_data)


class TaskTestView(View):
    """
    View for testing Celery task execution and progress tracking.
    """
    template_name = 'main_app/index.html'
    page_title = 'Celery Task Test'
    page_name = 'Test Celery Tasks'

    def get_context_data(self, **kwargs):
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'redirect_to': self.request.GET.get('next', ''),
            'message': kwargs.get('message'),

            # need to pass the task ID to the template for tracking
            'task_id': kwargs.get('task_id'),
        }
        return context

    def get(self, request: HttpRequest):
        # Start the task and get its ID
        task = long_running_task.delay(duration=10)
        messages.success(request, 'Task started! Tracking progress...')

        context = self.get_context_data(
            task_id=task.id  # Pass task ID to template
        )
        return render(request, self.template_name, context)

