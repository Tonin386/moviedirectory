from django.shortcuts import render

def home(request):
	return render(request, 'index.html', locals())

# Create your views here.
