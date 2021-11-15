from django.shortcuts import HttpResponse
import json
from django.views.generic import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from Business.BllMedicament import BllMedicament
import decimal


@method_decorator(csrf_exempt, "dispatch")
class Danger(View):
    def get(self, request):
        return render(request, 'danger/danger.html')

    def post(self, request):
        name = str(request.POST["name"])
        jsonData = BllMedicament().select_danger(name)
        return HttpResponse(json.dumps(jsonData, cls=DecimalEncoder))


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)
