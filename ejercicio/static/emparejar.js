document.addEventListener('DOMContentLoaded', () => {
    // Inicializar barra de progreso
    const progressBar = document.getElementById('progressBar');
    const progresoInicial = parseInt(progressBar.dataset.progresoInicial) || 0;
    progressBar.style.height = `${progresoInicial}%`;
    
    // Elementos del DOM
    const palabras = document.querySelectorAll('.palabra');
    const gestos = document.querySelectorAll('.gesto');
    const btnVerificar = document.getElementById('btn-verificar');
    const urlVerificacion = document.body.dataset.urlVerificacion;
    

    // Estado de la aplicación
    let seleccionActual = { palabra: null, gesto: null };
    let paresSeleccionados = [];
    let contadorPareado = 1;

    const feedbackEl = document.getElementById('feedback');

    // Manejo de selecciones
    function manejarSeleccion(elementos, tipo) {
        elementos.forEach(elemento => {
            elemento.addEventListener('click', () => {
                if (elemento.classList.contains('emparejada')) return;

                // Limpiar selecciones previas del mismo tipo
                elementos.forEach(el => el.classList.remove('seleccionada'));
                elemento.classList.add('seleccionada');

                seleccionActual[tipo] = elemento;
                verificarPar();
            });
        });
    }

    manejarSeleccion(palabras, 'palabra');
    manejarSeleccion(gestos, 'gesto');

    // Verificar par seleccionado
    function verificarPar() {
        if (seleccionActual.palabra && seleccionActual.gesto) {
            const palabraID = seleccionActual.palabra.dataset.id;
            const gestoID = seleccionActual.gesto.dataset.id;

            // Verificar si ya fue emparejado
            const yaEmparejado = paresSeleccionados.some(
                par => par.palabra_id === palabraID || par.gesto_id === gestoID
            );

            if (!yaEmparejado) {
                paresSeleccionados.push({
                    palabra_id: palabraID,
                    gesto_id: gestoID
                });

                animarEmparejamiento(seleccionActual.palabra, seleccionActual.gesto, contadorPareado);
                contadorPareado++;

                // Deshabilitar elementos emparejados
                seleccionActual.palabra.classList.add('emparejada');
                seleccionActual.gesto.classList.add('emparejada');
            }

            // Resetear selección
            seleccionActual = { palabra: null, gesto: null };

            // Habilitar botón cuando todos los pares están hechos
            btnVerificar.disabled = paresSeleccionados.length !== palabras.length;
        }
    }

    // Animación al emparejar
    function animarEmparejamiento(palabraEl, gestoEl, numeroPar) {
        const clase = `pareado-${numeroPar}`;
        palabraEl.classList.add(clase);
        gestoEl.classList.add(clase);
        palabraEl.classList.remove('seleccionada');
        gestoEl.classList.remove('seleccionada');
    }

    // Verificar emparejamientos con el servidor
    btnVerificar.addEventListener('click', () => {
        btnVerificar.disabled = true; // Deshabilitar botón durante la verificación
        
        // Deshabilitar todas las interacciones durante la verificación
        palabras.forEach(p => p.style.pointerEvents = 'none');
        gestos.forEach(g => g.style.pointerEvents = 'none');
        
        fetch(urlVerificacion, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ pares: paresSeleccionados })
        })
        .then(res => {
            if (!res.ok) throw new Error('Error en la respuesta');
            return res.json();
        })
        .then(data => {

            feedbackEl.textContent = data.mensaje;  // Actualizar el mensaje
            feedbackEl.className = data.todos_correctos ? 'correcto' : 'incorrecto';
            
            // Actualizar barra de progreso si es correcto
            if (data.todos_correctos) {
                actualizarBarraProgreso(10);
            }
            
            // Avanzar después de un breve retraso
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 1000);
        })
        .catch(error => {
            console.error('Error:', error);
            btnVerificar.disabled = false;
            palabras.forEach(p => p.style.pointerEvents = 'auto');
            gestos.forEach(g => g.style.pointerEvents = 'auto');
        });
    });


    // Función para actualizar la barra de progreso
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
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});