from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from .forms import LoginForm, CreateForm, RegisterForm
from .models import Item
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
# Create your views here.
User = get_user_model()

class IndexView(View):
    def get(self, request):
        items = Item.objects.filter(status="active").order_by('-created_at')
        return render(request, "index.html", {"items": items})

class RegisterView(View):

    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()  # save the user first

            role = form.cleaned_data.get('role')
            group, created = Group.objects.get_or_create(name=role.capitalize())
            user.groups.add(group)

            return redirect('login')

        return render(request, "register.html", {"form": form})



class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("index")
        form = LoginForm()  
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
        else:
            return render(request, "login.html", {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("index")
    

class CreateView(View):
    template_name = "create_listing.html"

    def get(self, request):
        form = CreateForm()
        return render(request, self.template_name, {"form": form})
    
    def post(self, request):
        form = CreateForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect('index')
        return render(request, self.template_name, {'form': form})