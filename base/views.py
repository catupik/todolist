from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect)
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import get_object_or_404 
from base.forms import TaskForm
from base.models import Task
from .models import Task#, Category

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm  
    redirect_authenticated_user = True   
    success_url = reverse_lazy('tasks')   

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated :
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

        
class TaskList(LoginRequiredMixin,ListView):
    model = Task
    context_object_name = 'tasks'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = Task.get_incomplete_count().filter(user=self.request.user)
        
        search_input = self.request.GET.get('search-area') or ""
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)

        context['search_input'] = search_input    
        context["Status"] = Task.StatusChoice

        status_query = self.request.GET.get('status', '')
        status_code = getattr(Task.StatusChoice, status_query, None)
        if status_code:
            context['tasks'] = context['tasks'].filter(status=status_code)

#         tasks = Task.objects.all()
#         context = {
#         "tasks": tasks, 
        
#         "Status": Task.StatusChoice
# }
        
        return context

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task' 
    template_name = 'base/task.html'  

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'status', 'due_date']  
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'status', 'due_date']    
    success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy('tasks')

def update_task_status(
    request: HttpRequest, task_id: int, new_status: str) -> HttpResponse:

    if not new_status in Task.StatusChoice.values:
        return HttpResponseBadRequest("Invalid status")

    task = get_object_or_404(Task, id=task_id)

    task.status = new_status
    task.save()

    success_url = reverse_lazy('tasks')

    return HttpResponseRedirect(success_url)

def delete_task(request: HttpRequest, task_id: int) -> HttpResponse:

    task = get_object_or_404(Task, id=task_id)
    task.delete()

    success_url = reverse_lazy('tasks')

    return HttpResponseRedirect(success_url)

def filter_tasks(request: HttpRequest, status: str) -> HttpResponse:

    if not status in Task.StatusChoice.values:
        return HttpResponseBadRequest("Invalid status")

    if request.method == "POST":
        form = TaskForm(data=request.POST)
        if form.is_valid():
            form.save()

    tasks = Task.objects.filter(status=status).order_by("-created")

    form = TaskForm()

    context = {
        "tasks": tasks,
        "form": form,
        "Status": Task.StatusChoice,
        "filter_choice": status,
    }

    return render(request, "base/task_list.html", context)