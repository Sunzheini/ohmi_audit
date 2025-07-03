from django.core.paginator import Paginator
from functools import wraps


def paginate_results(model=None, items_per_page=10):
    """
    Decorator to paginate results for a view method.
    :param model: The model to paginate results from. If None, no pagination is applied.
    :param items_per_page: Number of items to display per page.
    :return: A decorator that wraps the view method to add pagination functionality.
    """
    def decorator(view_method):
        @wraps(view_method)
        def wrapper(view_instance, *args, **kwargs):
            # Get the original context
            context = view_method(view_instance, *args, **kwargs)

            items = model.objects.all().order_by('-id') if model else []

            if items is not []:
                paginator = Paginator(items, items_per_page)
                page_number = view_instance.request.GET.get('page')
                page_obj = paginator.get_page(page_number)

            # Add the paginated items to the context
            context['data_for_content_container_wrapper_bottom'] = page_obj
            context['page_obj'] = page_obj  # Explicitly pass page_obj for template again

            return context

        return wrapper

    return decorator
