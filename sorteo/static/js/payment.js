function nextStep(currentStep) {
  if(currentStep === 1) {
    const ticketsQuantity = document.getElementById('tickets_quantity').value;
    document.getElementById('final_tickets_quantity').value = ticketsQuantity;
    
    updateTotal();
  }
  
  // Validar campos requeridos en el paso actual
  if(currentStep === 2) {
    const requiredFields = document.querySelectorAll('#step2 [required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
      if(!field.value.trim()) {
        field.classList.add('is-invalid');
        isValid = false;
      } else {
        field.classList.remove('is-invalid');
      }
    });
    
    if(!isValid) {
      alert('Por favor completa todos los campos requeridos.');
      return;
    }
  }
  
  // Ocultar paso actual y mostrar siguiente
  document.getElementById(`step${currentStep}`).style.display = 'none';
  document.getElementById(`step${currentStep + 1}`).style.display = 'block';
  
  // Configurar campos dinámicos para el método de pago
  if(currentStep === 2) {
    const methodSelect = document.getElementById('id_method');
    const bankFields = document.getElementById('bank-fields');
    
    function toggleBankFields() {
      if(methodSelect.value === 'P') {
        bankFields.style.display = 'block';
        document.getElementById('id_bank_of_transfer').required = true;
      } else {
        bankFields.style.display = 'none';
        document.getElementById('id_bank_of_transfer').required = false;
      }
    }
    
    methodSelect.addEventListener('change', toggleBankFields);
    toggleBankFields(); // Ejecutar al cargar el paso
  }
}

function prevStep(currentStep) {
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
  const quantity = parseInt(document.getElementById('tickets_quantity').value);
  const price = parseFloat('{{ sorteo.ticket_price }}');
  const total = quantity * price;
  
  document.getElementById('quantity-display').textContent = quantity;
  document.getElementById('total-amount').textContent = `Bs ${total.toFixed(2)}`;
}

// Inicializar eventos
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('tickets_quantity').addEventListener('change', updateTotal);
  updateTotal(); // Calcular total inicial
});