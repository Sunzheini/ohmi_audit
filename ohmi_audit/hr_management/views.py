from django.shortcuts import render


def hr_management_index_view(request):
    """
    HR Management Index View
    :param request: The HTTP request object.
    :return: Rendered HTML for the HR management index page.
    """
    return render(request, 'hr_management/hr_management_index.html')
