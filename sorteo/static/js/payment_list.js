/**
 * Envía una acción de pago (verificar/cancelar) al servidor.
 * @param {number} paymentId - El ID del pago.
 * @param {string} url - La URL del endpoint en el servidor.
 * @param {string} csrfToken - El token CSRF para la seguridad.
 */
function sendPaymentAction(paymentId, url, csrfToken) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ payment_id: paymentId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            Swal.fire('¡Hecho!', data.message, 'success').then(() => {
                location.reload(); // Recarga la página para ver los cambios
            });
        } else {
            Swal.fire('Error', data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire('Error', 'Ocurrió un error al comunicarse con el servidor.', 'error');
    });
}

/**
 * Inicia el proceso de verificación de un pago.
 * @param {number} paymentId - El ID del pago a verificar.
 */
function verifyPayment(paymentId) {
    const button = document.querySelector(`button[onclick="verifyPayment(${paymentId})"]`);
    const csrfToken = button.dataset.csrfToken;

    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción marcará el pago como verificado y generará los tickets. ¡No se puede deshacer!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, ¡verificar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            sendPaymentAction(paymentId, '/payment/verify/', csrfToken);
        }
    });
}

/**
 * Inicia el proceso de cancelación de un pago.
 * @param {number} paymentId - El ID del pago a cancelar.
 */
function cancelPayment(paymentId) {
    const button = document.querySelector(`button[onclick="cancelPayment(${paymentId})"]`);
    const csrfToken = button.dataset.csrfToken;

    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción marcará el pago como cancelado. ¡No se puede deshacer!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, ¡cancelar!',
        cancelButtonText: 'Volver'
    }).then((result) => {
        if (result.isConfirmed) {
            sendPaymentAction(paymentId, '/payment/cancel/', csrfToken);
        }
    });
}