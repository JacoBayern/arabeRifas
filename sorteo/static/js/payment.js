// --- Helpers (Global scope within the script) ---
const showError = (input, message) => {
    input.classList.add('is-invalid');
    const feedback = input.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
      feedback.textContent = message;
    }
};

const clearError = (input) => {
    input.classList.remove('is-invalid');
    const feedback = input.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
      feedback.textContent = '';
    }
};

// --- Validation Functions ---
function validateStep2() {
  let isValid = true;
  
  // Obtener los campos
  const nameInput = document.getElementById('id_owner_name');
  const typeCISelect = document.getElementById('id_type_CI');
  const ciInput = document.getElementById('id_owner_ci');
  const emailInput = document.getElementById('id_owner_email');
  const phoneInput = document.getElementById('id_owner_phone');

  [nameInput, typeCISelect, ciInput, emailInput, phoneInput].forEach(clearError);

  // 1. Validar Nombre
  if (!nameInput.value.trim()) {
    showError(nameInput, 'El nombre es obligatorio.');
    isValid = false;
  }

  // 2. Validar Email con Regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailInput.value.trim()) {
    showError(emailInput, 'El correo electrónico es obligatorio.');
  } else if (!emailRegex.test(emailInput.value)) {
    showError(emailInput, 'Por favor, introduce un correo electrónico válido.');
    isValid = false;
  }

  // 3. Validar Teléfono Venezolano (0412, 0414, 0416, 0424, 0426)
  const phoneRegex = /^(0412|0414|0416|0424|0426)\d{7}$/;
  if (!phoneInput.value.trim()) {
    showError(phoneInput, 'El número de teléfono es obligatorio.');
    isValid = false;
  } else if (!phoneRegex.test(phoneInput.value)) {
    showError(phoneInput, 'Formato de teléfono inválido. Ej: 04141234567.');
    isValid = false;
  }

  // 4. Validar Cédula/RIF
  const ciValue = ciInput.value.trim();
  if (!ciValue) {
    showError(ciInput, 'El número de documento es obligatorio.');
  } else if (!/^\d+$/.test(ciValue)) {
    showError(ciInput, 'El documento solo debe contener números.');
    isValid = false;
  } else {
    const ciType = typeCISelect.value;
    if ((ciType === 'V' || ciType === 'E')) {
      if (!(ciValue.length >= 7 && ciValue.length <= 8)) {
        showError(ciInput, 'La cédula debe tener entre 7 y 8 dígitos.');
        isValid = false;
      }
    } else if (ciType === 'J') {
      if (!(ciValue.length >= 6 && ciValue.length <= 8)) {
        showError(ciInput, 'El RIF jurídico debe tener 10 dígitos.');
        isValid = false;
      }
    }
  }

  return isValid;
}

function validateStep4() {
    let isValid = true;
    const bankSelect = document.getElementById('id_bank_of_transfer');
    const referenceInput = document.getElementById('id_reference');
    const dateInput = document.getElementById('id_transferred_date');
    const amountInput = document.getElementById('id_transferred_amount');

    [bankSelect, referenceInput, dateInput, amountInput].forEach(clearError);

    // 1. Validar Banco (siempre es requerido para Pago Móvil)
    if (!bankSelect.value) {
        showError(bankSelect, 'Debes seleccionar el banco de origen.');
        isValid = false;
    }

    // 2. Validar Referencia
    if (!referenceInput.value.trim()) {
        showError(referenceInput, 'El número de referencia es obligatorio.');
        isValid = false;
    }

    // 3. Validar Fecha
    if (!dateInput.value) {
        showError(dateInput, 'La fecha de transferencia es obligatoria.');
        isValid = false;
    }

    // 4. Validar Monto
    const amountValue = amountInput.value.trim();
    if (!amountValue) {
        showError(amountInput, 'El monto transferido es obligatorio.');
        isValid = false;
    } else if (isNaN(parseFloat(amountValue)) || parseFloat(amountValue) <= 0) {
        showError(amountInput, 'Introduce un monto válido.');
        isValid = false;
    }

    return isValid;
}

// --- Step Navigation ---
function nextStep(currentStep) {
  if(currentStep === 1) {
    const ticketsQuantityInput = document.getElementById('tickets_quantity');
    const ticketsQuantity = parseInt(ticketsQuantityInput.value);
    const step1Container = document.getElementById('step1');
    const errorContainer = document.getElementById('quantity-error');

    // Limpiar errores previos
    errorContainer.textContent = '';
    ticketsQuantityInput.classList.remove('is-invalid');

    // Validar cantidad mínima de boletos
    const minimumTickets = parseInt(step1Container.dataset.minimumTickets) || 0;
    if (minimumTickets > 0 && ticketsQuantity < minimumTickets) {
      errorContainer.textContent = `La compra mínima es de ${minimumTickets} boletos.`;
      ticketsQuantityInput.classList.add('is-invalid');
      return; // Detener si la validación falla
    }

    document.getElementById('final_tickets_quantity').value = ticketsQuantity;
    updateTotal();
  }
  
  // Validar campos del paso 2 antes de continuar
  if(currentStep === 2) {
    if (!validateStep2()) {
      return;
    }
    // Actualizar el monto total en el paso 3
    const totalAmount = document.getElementById('total-amount').textContent;
    document.getElementById('total-amount-step3').textContent = totalAmount;
  }
  
  // Ocultar paso actual y mostrar siguiente
  document.getElementById(`step${currentStep}`).style.display = 'none';
  document.getElementById(`step${currentStep + 1}`).style.display = 'block';
}

function prevStep(currentStep) { // Asegúrate de que esta función sea global
  document.getElementById(`step${currentStep}`).style.display = 'none';
  document.getElementById(`step${currentStep - 1}`).style.display = 'block';
}

// Manejo de cantidad de tickets
function addTickets(quantity) {
  const input = document.getElementById('tickets_quantity');
  const newValue = parseInt(input.value) + quantity;
  input.value = newValue;
  updateTotal();
}

function changeTickets(change) {
  const input = document.getElementById('tickets_quantity');
  const newValue = parseInt(input.value) + change;
  if(newValue >= 1) {
    input.value = newValue;
    updateTotal();
  }
}

function resetTickets() {
  document.getElementById('tickets_quantity').value = 1;
  updateTotal();
}

// Actualizar el total cuando cambia la cantidad
function updateTotal() {
  const quantityInput = document.getElementById('tickets_quantity');
  const quantity = parseInt(quantityInput.value) || 1;
  const priceContainer = document.getElementById('step1');
  const errorContainer = document.getElementById('quantity-error');

  if (!priceContainer || !priceContainer.dataset.ticketPrice) {
    // Si no se encuentra el precio, no se puede calcular nada.
    return;
  }

  // Limpiar el error de cantidad mínima si la cantidad actual es válida
  const minimumTickets = parseInt(priceContainer.dataset.minimumTickets) || 0;
  if (minimumTickets > 0 && quantity >= minimumTickets) {
    errorContainer.textContent = '';
    quantityInput.classList.remove('is-invalid');
  }

  // Django puede renderizar decimales con una coma (,) en la configuración regional 'es'.
  // Reemplazamos la coma por un punto para asegurar que parseFloat funcione correctamente.
  const priceString = priceContainer.dataset.ticketPrice.replace(',', '.');
  const price = parseFloat(priceString);

  if (isNaN(price)) {
    // Si el precio no es un número válido, no se puede calcular.
    return;
  }

  const total = quantity * price;
  
  document.getElementById('quantity-display').textContent = quantity;
  document.getElementById('total-amount').textContent = `Bs ${total.toFixed(2)}`;
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', function() {
    const purchaseForm = document.getElementById('purchase-form');
    if (purchaseForm) {
        purchaseForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevenir el envío automático

            if (validateStep4()) {
                const submitButton = purchaseForm.querySelector('button[type="submit"]');
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
                this.submit();
            }
        });
    }

    const quantityInput = document.getElementById('tickets_quantity');
    if(quantityInput) { quantityInput.addEventListener('change', updateTotal); }
    updateTotal();

    // --- Animación de Scroll Reveal ---
    const revealElements = document.querySelectorAll('.scroll-reveal');

    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target); // Para que la animación ocurra solo una vez
                }
            });
        }, {
            threshold: 0.1 // La animación se dispara cuando el 10% del elemento es visible
        });

        revealElements.forEach(el => revealObserver.observe(el));
    }
});
