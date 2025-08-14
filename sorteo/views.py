from django.shortcuts import redirect, render, get_object_or_404
from .models import Sorteo, Payment, Ticket, Premio
from django.http import JsonResponse
# from .forms import PaymentForm, SorteoForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Case, When, Value
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SorteoForm, PaymentForm, PremioForm, AdminPaymentForm
from django.views.decorators.http import require_http_methods
from django.db import transaction
import logging
import json
import random

# Create your views here.

def home(request):
    form = PaymentForm()
    sorteo = Sorteo.objects.filter(is_main=True).first()
    premios = Premio.objects.filter(sorteo=sorteo).order_by('position')

    context = {'form': form,
               'sorteo': sorteo,
               'premios': premios
               }

    return render(request, 'home.html', context)

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
    Lista todos los pagos con búsqueda, filtro y paginación.
    También maneja la creación de un nuevo pago a través de un formulario modal.
    """
    # Manejo del formulario para añadir un pago manual
    if request.method == 'POST':
        form = AdminPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.state = 'E'  # Los pagos manuales inician 'En Espera'
            payment.save()
            messages.success(request, f"Pago para '{payment.owner_name}' registrado exitosamente.")
            return redirect('payment_list')
        else:
            messages.error(request, "Error al registrar el pago. Por favor, revisa los campos del formulario.")
    else:
        form = AdminPaymentForm()

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
    ).order_by('state_order', '-created_at')

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
        'form': form,
        'form_has_errors': form.errors,
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
            return redirect('payment_list')
    else:
        form = AuthenticationForm()
    return render(request, 'administration/login.html', {'form': form})

@login_required
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
        instance = get_object_or_404(Sorteo, pk=sorteo_id)
        page_title = f'Editando Sorteo: {instance.title}'
    else:
        instance = None
        page_title = 'Crear Nuevo Sorteo'

    # Creamos el formset factory para los premios
    # extra=1: Muestra un formulario vacío para añadir un nuevo premio.
    # can_delete=True: Permite marcar premios para ser eliminados.
    PremioFormSet = inlineformset_factory(
        Sorteo, Premio, form=PremioForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = SorteoForm(request.POST, request.FILES, instance=instance)
        premio_formset = PremioFormSet(request.POST, request.FILES, instance=instance, prefix='premios')

        if form.is_valid() and premio_formset.is_valid():
            sorteo = form.save()
            premio_formset.instance = sorteo
            premio_formset.save()

            messages.success(request, f'Sorteo "{sorteo.title}" guardado exitosamente.')
            return redirect('sorteo_list')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = SorteoForm(instance=instance)
        premio_formset = PremioFormSet(instance=instance, prefix='premios')

    context = {
        'form': form,
        'premio_formset': premio_formset,
        'page_title': page_title
    }
    return render(request, 'sorteo/sorteo_form.html', context)

@login_required
def ticket_list(request, sorteo_id):
    """
    Lista los tickets de un sorteo específico, con búsqueda y paginación.
    """
    query = request.GET.get('q', '')

    sorteo = get_object_or_404(Sorteo, pk=sorteo_id)

    ticket_list = Ticket.objects.filter(sorteo=sorteo).order_by('serial')

    if query:
        ticket_list = ticket_list.filter(
            Q(owner_name__icontains=query) |
            Q(owner_ci__icontains=query) |
            Q(owner_email__icontains=query) |
            Q(serial__iexact=query)
        )

    paginator = Paginator(ticket_list, 20) # 20 tickets por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'sorteo': sorteo,
        'tickets': page_obj,
        'query': query,
    }
    return render(request, 'ticket/ticket_list.html', context)

@require_http_methods(["POST"])
def process_payment(request, sorteo_slug):
    """
    Procesa el formulario de pago enviado desde la página de inicio.
    """
    sorteo = get_object_or_404(Sorteo, slug=sorteo_slug)
    form = PaymentForm(request.POST, sorteo=sorteo)

    if form.is_valid():
        # El formulario es válido, procedemos a guardar el pago.
        payment = form.save(commit=False)
        payment.sorteo = sorteo
        payment.state = 'E'  # 'E' para 'En Espera'
        payment.save()

        messages.success(request, '¡Tu pago ha sido registrado! Está en proceso de verificación.')
        return redirect('payment_success', payment_serial=payment.serial)
    else:
        # El formulario tiene errores, lo devolvemos a la página de inicio para mostrarlos.
        messages.error(request, 'Hubo un error al procesar tu pago. Por favor, revisa los campos marcados en rojo.')
        
        # Necesitamos el contexto completo de la página de inicio para re-renderizarla.
        premios = Premio.objects.filter(sorteo=sorteo).order_by('position')
        context = {
            'form': form, # Pasamos el formulario con errores
            'sorteo': sorteo,
            'premios': premios
        }
        return render(request, 'home.html', context)

def payment_success(request, payment_serial):
    """
    Muestra una página de confirmación después de un pago exitoso.
    """
    payment = get_object_or_404(Payment, serial=payment_serial)
    return render(request, 'payment/payment_success.html', {'payment': payment})

@login_required
@require_http_methods(["POST"])
def verify_payment(request):
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        payment = get_object_or_404(Payment, pk=payment_id)

        if payment.state != 'E':
            return JsonResponse({'status': 'error', 'message': 'Este pago no está en espera de verificación.'}, status=400)

        sorteo = payment.sorteo
        tickets_to_generate = payment.tickets_quantity

        with transaction.atomic():
            # Bloqueamos el sorteo para evitar que otros procesos modifiquen los tickets vendidos al mismo tiempo.
            sorteo_locked = Sorteo.objects.select_for_update().get(pk=sorteo.id)

            if sorteo_locked.tickets_solds + tickets_to_generate > sorteo_locked.total_tickets:
                return JsonResponse({'status': 'error', 'message': 'No hay suficientes tickets disponibles para este sorteo.'}, status=400)

            # Obtenemos los números de tickets que ya existen para este sorteo.
            existing_serials = set(Ticket.objects.filter(sorteo=sorteo_locked).values_list('serial', flat=True))
            new_tickets = []
            generated_serials = set()
            
            # Generamos números aleatorios hasta tener la cantidad necesaria de tickets únicos.
            while len(generated_serials) < tickets_to_generate:
                potential_serial = random.randint(1, sorteo_locked.total_tickets)
                if potential_serial not in existing_serials and potential_serial not in generated_serials:
                    generated_serials.add(potential_serial)

            for serial in generated_serials:
                new_tickets.append(Ticket(
                    serial=serial,
                    owner_name=payment.owner_name,
                    owner_ci=payment.owner_ci,
                    owner_email=payment.owner_email,
                    owner_phone=payment.owner_phone,
                    sorteo=sorteo_locked,
                    payment=payment
                ))
            
            Ticket.objects.bulk_create(new_tickets)

            # Actualizamos el estado del pago y el contador de tickets del sorteo.
            payment.state = 'V'
            payment.save()

            sorteo_locked.tickets_solds += tickets_to_generate
            sorteo_locked.save()

        # Aquí podrías añadir la lógica para enviar un correo de confirmación.
        return JsonResponse({'status': 'success', 'message': 'Pago verificado y tickets generados exitosamente.'})

    except Exception as e:
        logging.error(f"Error al verificar el pago: {e}")
        return JsonResponse({'status': 'error', 'message': 'Ocurrió un error inesperado en el servidor.'}, status=500)

@login_required
@require_http_methods(["POST"])
def cancel_payment(request):
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        payment = get_object_or_404(Payment, pk=payment_id)

        if payment.state != 'E':
            return JsonResponse({'status': 'error', 'message': 'Solo se pueden cancelar pagos que están en espera.'}, status=400)

        payment.state = 'C'
        payment.save()
        return JsonResponse({'status': 'success', 'message': 'El pago ha sido cancelado exitosamente.'})
    except Exception as e:
        logging.error(f"Error al cancelar el pago: {e}")
        return JsonResponse({'status': 'error', 'message': 'Ocurrió un error inesperado en el servidor.'}, status=500)

def verify_tickets(request):
    """
    Busca y muestra los tickets de un usuario por su correo o cédula.
    """
    query = request.GET.get('q', '').strip()
    tickets_found = []

    if query:
        # Busca tickets que coincidan exactamente con el correo o la cédula.
        tickets_found = Ticket.objects.filter(
            Q(owner_email__iexact=query) | Q(owner_ci__iexact=query)
        ).select_related('sorteo').order_by('-created_at')

    context = {
        'query': query,
        'tickets': tickets_found,
    }
    return render(request, 'ticket/ticket_verify_results.html', context)
