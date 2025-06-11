document.addEventListener("DOMContentLoaded", () => {
    // Inicializar barra de progreso vertical
    const progressBar = document.getElementById("progressBar");
    const progresoInicial = parseInt(progressBar.dataset.progresoInicial) || 0;
    progressBar.style.height = `${progresoInicial}%`;
    
    const gestos = document.querySelectorAll(".gesto");
    const urlVerificacion = document.body.dataset.urlVerificacion;
    

    gestos.forEach(gesto => {
        gesto.addEventListener("click", () => {
            // Deshabilitar todos los gestos durante la verificación
            gestos.forEach(g => g.style.pointerEvents = 'none');
            
            // Limpiar selecciones previas
            gestos.forEach(g => g.classList.remove("correcto", "incorrecto"));
            
            const opcion_id = gesto.getAttribute("data-id");

            fetch(urlVerificacion, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: `opcion_id=${opcion_id}`
            })
            .then(response => {
                if (!response.ok) throw new Error('Error en la respuesta');
                return response.json();
            })
            .then(data => {
                
                
                // Actualizar barra de progreso si es correcto
                if (data.correcto) {
                    actualizarBarraProgreso(10);
                }
                
                // Avanzar después de un breve retraso
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 1000);
            })
            .catch(error => {
                console.error("Error:", error);
                gestos.forEach(g => g.style.pointerEvents = 'auto'); // Rehabilitar gestos
            });
        });
    });

    // Función para actualizar barra de progreso vertical
    function actualizarBarraProgreso(porcentaje) {
        const progresoActual = parseInt(progressBar.style.height) || 0;
        const nuevoProgreso = Math.min(progresoActual + porcentaje, 100);
        progressBar.style.height = `${nuevoProgreso}%`;
    }
    

    // Función para obtener el token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});