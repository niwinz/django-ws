# Create your views here.

from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic import View


class TestView(View):
    def get(self, request):
        return render_to_response("template.html", {})
