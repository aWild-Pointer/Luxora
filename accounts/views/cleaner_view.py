from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from luxora_utils.permissions import role_required


@login_required
@role_required('cleaner')
def cleaner(request):
    context = {
        'active_page': 'clean_room'
    }
    return render(request,"accounts/cleaner/cleaner.html", context)