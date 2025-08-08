from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinLengthValidator

# Create your models here.
class Sorteo(models.Model):
    ESTATE = [
        ('B', 'BORRADOR'),
        ('A', 'ACTIVO'),
        ('F', 'FINALIZADO'),
        ('V', 'VENDIDO')
    ]

    title = models.CharField(('Titulo'),max_length=50)
    slug = models.SlugField(unique=True, max_length=110, editable=False)
    description = models.TextField(('Descripción'))
    date_lottery = models.DateTimeField(("Fecha del Sorteo"), auto_now=False, auto_now_add=False)
    prize_picture = models.ImageField(("Foto del premio"), upload_to='premios/')
    ticket_price = models.DecimalField(("Precio del ticket"), max_digits=5, decimal_places=2)
    state = models.CharField(("Estado del sorteo"), choices=ESTATE, default='B', blank=False)
    total_tickets = models.PositiveIntegerField(("Máxima cantidad de tickets a vender"), blank=False)
    tickets_solds = models.PositiveIntegerField(("Tickets vendidos"), editable=False, default=0)
    lottery_conditions = models.TextField(("Condiciones del sorteo"))
    video_promo = models.FileField(
        ("Video promocional"),
        upload_to='videos_promocionales/',
        null=True,
        blank=True,
        help_text="Sube un video promocional del sorteo"
    )

    class Meta:
        verbose_name = 'Sorteo'
        verbose_name_plural = 'Sorteos'


class Ticket(models.Model):
    serial = models.PositiveIntegerField(("Número de ticket"))
    owner_name = models.CharField(("Nombre del propietario"), max_length=50)
    owner_ci = models.CharField(('Cedula del propietario'),max_length=8, validators=[MinLengthValidator(6)])
    owner_email = models.EmailField(("Correo del propietario"), max_length=254)
    owner_phone = PhoneNumberField(verbose_name='Telefono del propietario', region='VE')
    sorteo = models.ForeignKey("sorteo.sorteo", verbose_name="Sorteo", on_delete=models.CASCADE, related_name='tickets', null=False, blank=False)
    payment = models.ForeignKey("sorteo.payment", verbose_name="Pago", on_delete=models.CASCADE, related_name='tickets', null=False, blank=False)
    created_at = models.DateTimeField(("Fecha de Creación"), auto_now_add=True, editable=False)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        unique_together = [['serial', 'sorteo']]

class Payment(models.Model):
    #TODO signal para el update_at
    #TODO lógica para creación de tickets
    PAYMENT_METHODS = [
        ('P', 'Pago Móvil')
        ]
    PAYMENT_STATES =[
        ('V', 'Verificado'),
        ('E', 'En Espera'),
        ('C', 'Cancelado')
    ]

    CI_TYPE_CHOICES = [
        ('V', 'Venezolano'),
        ('E', 'Extranjero'),
        ('J', 'Jurídico'),
    ]
    BANK_CHOICES = [
        ('0102', 'Banco de Venezuela'),
        ('0104', 'Banco Venezolano de Crédito'),
        ('0105', 'Banco Mercantil'),
        ('0108', 'Banco Provincial'),
        ('0114', 'Bancaribe'),
        ('0115', 'Banco Exterior'),
        ('0128', 'Banco Caroní'),
        ('0134', 'Banesco'),
        ('0137', 'Banco Sofitasa'),
        ('0138', 'Banco Plaza'),
        ('0151', 'BFC Banco Fondo Común'),
        ('0156', '100% Banco'),
        ('0157', 'DelSur Banco Universal'),
        ('0163', 'Banco del Tesoro'),
        ('0166', 'Banco Agrícola de Venezuela'),
        ('0168', 'Bancrecer'),
        ('0169', 'Mi Banco'),
        ('0171', 'Banco Activo'),
        ('0172', 'Bancamiga'),
        ('0174', 'Banplus'),
        ('0175', 'Banco Bicentenario del Pueblo'),
        ('0177', 'Banfanb'),
        ('0191', 'BNC Banco Nacional de Crédito'),
    ]
    owner_name = models.CharField(("Nombre del propietario"), max_length=50)
    owner_ci = models.CharField(('Cedula del propietario'),max_length=8, validators=[MinLengthValidator(6)])
    owner_email = models.EmailField(("Correo del propietario"), max_length=254)
    owner_phone = PhoneNumberField(verbose_name='Telefono del propietario', region='VE')
    method = models.CharField(("Método de Pago"), max_length=50, choices=PAYMENT_METHODS)
    reference = models.CharField(max_length=30)
    state = models.CharField(("Estado"), max_length=50, choices=PAYMENT_STATES)
    created_at = models.DateTimeField(("Fecha de creación"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(("Ultima actualización"), auto_now=False, null=True, editable=False)
    tickets_quantity = models.PositiveBigIntegerField()
    serial = models.CharField(("Serial de la transacción"), max_length=50, editable=False, blank=True)
    sorteo = models.ForeignKey('Sorteo', on_delete=models.CASCADE, related_name='pagos')
    transferred_amount = models.DecimalField(("Monto transferido"), max_digits=10, decimal_places=2)
    transferred_date = models.DateField(("Fecha de transferencia"), auto_now=False, auto_now_add=False)
    type_CI = models.CharField(("Tipo de cédula"), max_length=1, choices=CI_TYPE_CHOICES, default='V')
    bank_of_transfer = models.CharField(("Banco de transferencia"), max_length=4, choices=BANK_CHOICES)
    payment_verification_note = models.TextField(("Nota de verificación del pago"), blank=True, null=True)
    is_payment_registered = models.BooleanField(("Pago registrado"), default=False, editable=False)
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'