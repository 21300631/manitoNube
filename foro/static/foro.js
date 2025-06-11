document.addEventListener('DOMContentLoaded', function () {
    // Función para obtener el token CSRF
    function getCSRFToken() {
        const cookie = document.cookie.match(/csrftoken=([^ ;]+)/);
        return cookie ? cookie[1] : null;
    }

    const csrftoken = getCSRFToken();

    // Delegación de eventos para los formularios de reporte
    document.body.addEventListener('submit', function (e) {
        if (e.target.classList.contains('form-report')) {
            e.preventDefault();
            const form = e.target;
            const publicacionId = form.dataset.publicacionId;

            fetch(`/foro/reportar/${publicacionId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.eliminada) {
                    const publicacionDiv = form.closest('.publicacion');
                    if (publicacionDiv) {
                        // Opcional: añadir animación antes de eliminar
                        publicacionDiv.style.transition = 'opacity 0.5s';
                        publicacionDiv.style.opacity = '0';
                        
                        setTimeout(() => {
                            publicacionDiv.remove();
                            // Opcional: mostrar un mensaje de que la publicación fue eliminada
                            const mensaje = document.createElement('div');
                            mensaje.textContent = 'La publicación ha sido eliminada por múltiples reportes.';
                            mensaje.classList.add('alert', 'alert-info');
                            publicacionDiv.parentNode.insertBefore(mensaje, publicacionDiv.nextSibling);
                            
                            setTimeout(() => mensaje.remove(), 3000);
                        }, 500);
                    }
                } else {
                    const label = form.querySelector('.report-count');
                    if (label) {
                        label.textContent = data.total_reportes;
                    }
                }
            })
            .catch(error => {
                console.error('Error al reportar:', error);
                // Opcional: mostrar mensaje de error al usuario
                alert('Ocurrió un error al reportar la publicación');
            });
        }
    });

    // Delegación de eventos para los formularios de like (similar al de reporte)
    document.body.addEventListener('submit', function (e) {
        if (e.target.classList.contains('form-like')) {
            e.preventDefault();
            const form = e.target;
            const publicacionId = form.dataset.publicacionId;

            fetch(`/foro/dar_like/${publicacionId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                const label = form.querySelector('.like-count');
                if (label) {
                    label.textContent = data.total_likes;
                }
            })
            .catch(error => {
                console.error('Error al dar like:', error);
            });
        }
    });
});