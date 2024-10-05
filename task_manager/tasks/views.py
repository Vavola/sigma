from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Task, Comment
from .forms import TaskForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.core.exceptions import PermissionDenied
from django import forms

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.filter(created_by=self.request.user)  # Фільтрація по власнику (created_by)
        
        # Фільтрація за статусом
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Фільтрація за пріоритетом
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TaskFilterForm(self.request.GET or None)
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'status', 'priority', 'deadline']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list')

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task-list')

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'tasks/comment_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.task_id = self.kwargs['pk']
        return super().form_valid(form)

class UserIsOwnerMixin:
    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if task.created_by != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(choices=Task.STATUS_CHOICES, required=False)
    priority = forms.ChoiceField(choices=Task.PRIORITY_CHOICES, required=False)
    