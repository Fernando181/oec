# Create your views here.

from django.http import HttpResponse
from usa.models import *

def index(request):
    allof = Msa.objects.all()
    output = ', <br>'.join([c.state for c in allof])
    return HttpResponse(output)
    
    