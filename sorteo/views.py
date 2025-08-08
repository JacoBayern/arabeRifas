from django.shortcuts import redirect, render, get_object_or_404
from .models import Sorteo, Payment, Ticket
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
# from .forms import PaymentForm, SorteoForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Case, When, Value
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SorteoForm
import logging

# Create your views here.

def home(request):
    return render(request, 'home.html')

@login_required
def sorteo_list(request):
    """
    Lista todos los sorteos con búsqueda, filtro y paginación.
    """
    query = request.GET.get('q', '')
    state_filter = request.GET.get('state', '')

    sorteo_list = Sorteo.objects.all().order_by('-date_lottery')

    if state_filter:
        sorteo_list = sorteo_list.filter(state=state_filter)

    if query:
        sorteo_list = sorteo_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    paginator = Paginator(sorteo_list, 10)  # 10 sorteos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'sorteos': page_obj,
        'query': query,
        'state_filter': state_filter,
        'states': Sorteo.ESTATE,
    }
    return render(request, 'sorteo/sorteo_list.html', context)

@login_required
def payment_list(request):
    """
    List all payments with search and pagination.
    """
    query = request.GET.get('q', '')
    state_filter = request.GET.get('state', '')

    # Ordenar por estado: 'En Espera' primero, luego el resto por fecha.
    payment_list = Payment.objects.annotate(
        state_order=Case(
            When(state='E', then=Value(1)),
            When(state='V', then=Value(2)),
            When(state='C', then=Value(3)),
            default=Value(4)
        )
    ).order_by('state_order', 'created_at')

    # Aplicar filtro de estado si se proporciona uno
    if state_filter and state_filter in ['E', 'V', 'C']:
        payment_list = payment_list.filter(state=state_filter)
    
    if query:
        payment_list = payment_list.filter(
            Q(owner_name__icontains=query) |
            Q(owner_ci__icontains=query) |
            Q(owner_email__icontains=query) |
            Q(reference__icontains=query) |
            Q(serial__icontains=query)
        )

    paginator = Paginator(payment_list, 15)  # Muestra 15 pagos por página
    page_number = request.GET.get('page')
    payments_page = paginator.get_page(page_number)

    context = {
        'payments': payments_page,
        'query': query,
        'state_filter': state_filter,
    }

    return render(request, 'payment/payment_list.html', context)

def login(request):
    """                 
    Login view
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('sorteo:payment_list')
    else:
        form = AuthenticationForm()
    return render(request, 'administration/login.html', {'form': form})

def logout_view(request):
    """
    Logout view
    """
    auth_logout(request)
    return redirect('home')

@login_required
def sorteo_edit(request, sorteo_id=None):
    """
    Crea o edita un sorteo.
    """
    if sorteo_id:
        # Editar un sorteo existente
        instance = get_object_or_404(Sorteo, pk=sorteo_id)
        page_title = f'Editando Sorteo: {instance.title}'
    else:
        # Crear un nuevo sorteo
        instance = None
        page_title = 'Crear Nuevo Sorteo'

    if request.method == 'POST':
        form = SorteoForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            sorteo = form.save()
            messages.success(request, f'Sorteo "{sorteo.title}" guardado exitosamente.')
            return redirect('sorteo_list')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = SorteoForm(instance=instance)

    context = {'form': form, 'page_title': page_title}
    return render(request, 'sorteo/sorteo_form.html', context)
