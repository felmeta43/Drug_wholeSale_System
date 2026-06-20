from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import UserProfile
from .forms import LoginForm, UserCreateForm, UserUpdateForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


class UserListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = UserProfile.objects.all().order_by('username')
        search = self.request.GET.get('search')
        role = self.request.GET.get('role')
        if search:
            queryset = queryset.filter(username__icontains=search) | \
                       queryset.filter(first_name__icontains=search) | \
                       queryset.filter(last_name__icontains=search)
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = UserProfile.ROLES
        return context

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ['accounts/_user_results.html']
        return [self.template_name]


class UserCreateView(LoginRequiredMixin, CreateView):
    model = UserProfile
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user_obj': request.user})
