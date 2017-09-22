from django.shortcuts import render


# Create your views here.
def dash_pages(request):
    return render(request, "dash.html")
