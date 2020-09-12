from django.shortcuts import render
from django.http import  HttpResponse
from .functions import *
# Create your views here.
def home_view(request, *args,**kwargs):
	context={'pib':graficar_pib(),
				'inflacion':graficar_inflacion(),
				'tasas_interes':graficar_tasas_interes(),
				'tipo_cambio':graficar_tipo_cambio()}
	return render(request,"graficas.html",context)
	#print(request.user)
	#return render(request,"grafica_pib.html",{})

def grafica_view(request,*args,**kwargs):
	grafica_pib = graficar_pib()
	context = {'grafica':grafica_pib}
	return render(request,"graficas.html",context)

def priviet_view(request,*args,**kwargs):
	print(request.user,"is being a kuk")
	return HttpResponse("<h1>priviet ma nigga welcome \n to the bonezone fuk</h1>")


def contact_view(request,*args,**kwargs):
	print(request.user)
	return render(request,"contact.html",{})


def about_view(request,*args,**kwargs):
	print(request.user)
	return render(request,"about.html",{})	