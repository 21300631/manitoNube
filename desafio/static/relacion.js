document.addEventListener('DOMContentLoaded', function() {
    // Elementos del juego
    const contador = document.getElementById('contador');
    const tiempoElement = document.getElementById('tiempo');
    const juegoConfig = document.getElementById('juego-config');
    const totalPares = juegoConfig ? parseInt(juegoConfig.dataset.totalPares) : 5;

    const elementos = {
        contador: document.getElementById('contador'),
        tiempoElement: document.getElementById('tiempo'),
        totalParesInput: document.getElementById('total-pares'),
        paresData: document.getElementById('pares-data')
    };
    
    console.log('Elementos encontrados al iniciar:', elementos);

    if (!elementos.paresData) {
        console.error('Error: Falta el elemento con los datos de pares');
        return;
    }

    const CONFIG_JUEGO = {
        paresPorGrupo: 5,
        totalGrupos: 4,
        tiempoPorRonda: 40,
        totalPares: elementos.totalParesInput ? 
                   parseInt(elementos.totalParesInput.value) : 
                   5 // Valor por defecto
    };
    
    // Variables de estado
    let seleccionado = null;
    let aciertos = 0;
    let tiempoRestante = CONFIG_JUEGO.tiempoPorRonda;
    let temporizador;
    let paresDisponibles = [];
    let paresActivos = [];
    let paresUsados = [];
    let grupoActual = 0;
    let gruposDePares = [];

    function inicializarJuego() {
        const paresIniciales = JSON.parse(document.getElementById('pares-data').textContent);
        paresDisponibles = [...paresIniciales.pares_correctos, ...paresIniciales.pares_reserva];
        
        if (paresDisponibles.length < 5) {
            console.error("¡No hay suficientes pares para jugar!");
            return;
        }
        
        crearGruposDePares();
        mostrarParesIniciales();
    }


    function crearGruposDePares() {
        // Mezcla todos los pares disponibles
        mezclarArray(paresDisponibles);
        
        // Divide en grupos de 5
        gruposDePares = [];
        for (let i = 0; i < paresDisponibles.length; i += 5) {
            const grupo = paresDisponibles.slice(i, i + 5);
            if (grupo.length > 0) {
                gruposDePares.push(grupo);
            }
        }
    }

    function mostrarParesIniciales() {
        // Obtén el grupo actual
        const grupo = gruposDePares[grupoActual % gruposDePares.length];
        
        // Limpia el tablero
        document.querySelector('.fila.palabras').innerHTML = '';
        document.querySelector('.fila.imagenes').innerHTML = '';

        // Extrae palabras e imágenes por separado
        const palabrasGrupo = grupo.map(par => par.palabra);
        const imagenesGrupo = grupo.map(par => par.imagen);
        
        // Mezcla independientemente las palabras y las imágenes
        mezclarArray(palabrasGrupo);
        mezclarArray(imagenesGrupo);
        
        // Crea los elementos mezclados
        palabrasGrupo.forEach(palabra => {
            document.querySelector('.fila.palabras').appendChild(crearElemento('palabra', palabra));
        });
        
        imagenesGrupo.forEach(imagen => {
            document.querySelector('.fila.imagenes').appendChild(crearElemento('imagen', imagen));
        });

        // Actualiza los pares activos (considerando la mezcla)
        paresActivos = grupo.map(par => ({
            palabra: par.palabra,
            imagen: par.imagen,
            esCorrecto: par.palabra.id === par.imagen.id
        }));
        
        // Verifica el balance después de cargar
        verificarBalance();
    }

    function crearElemento(tipo, datos) {
        const div = document.createElement('div');
        div.className = `item ${tipo}`;
        div.dataset.id = datos.id;
        div.dataset.palabra = datos.palabra;
        div.tabIndex = 0;
        
        if (tipo === 'palabra') {
            const span = document.createElement('span');
            span.textContent = datos.palabra;
            div.appendChild(span);
        } else {
            const img = document.createElement('img');
            img.src = datos.url;
            img.alt = `Gesto ${datos.palabra}`;
            img.style.maxWidth = '120px';
            img.style.borderRadius = '8px';
            div.appendChild(img);
        }
        
        div.addEventListener('click', () => manejarSeleccion(div));
        return div;
    }

    function manejarSeleccion(elemento) {
        // Evitar seleccionar elementos ya acertados
        if (elemento.classList.contains('acertado')) {
            return;
        }
    
        // Si se hace clic en el mismo elemento
        if (elemento === seleccionado) {
            elemento.classList.remove('seleccionado');
            seleccionado = null;
            return;
        }
    
        // Si hay un elemento seleccionado diferente
        if (seleccionado) {
            // Determinar tipos
            const esPalabraPrimero = seleccionado.classList.contains('palabra');
            const esImagenPrimero = seleccionado.classList.contains('imagen');
            
            // Validar combinación permitida (palabra-imagen o imagen-palabra)
            if ((esPalabraPrimero && elemento.classList.contains('imagen')) || 
                (esImagenPrimero && elemento.classList.contains('palabra'))) {
                
                const palabraId = esPalabraPrimero ? seleccionado.dataset.id : elemento.dataset.id;
                const imagenId = esPalabraPrimero ? elemento.dataset.id : seleccionado.dataset.id;
    
                if (esParCorrecto(palabraId, imagenId)) {
                    // Par correcto
                    aciertos++;
                    contador.textContent = aciertos;
                    
                    seleccionado.classList.add('acertado');
                    elemento.classList.add('acertado');
                    
                    setTimeout(() => {
                        reemplazarParCorrecto(palabraId, imagenId);
                    }, 300);
                } else {
                    // Par incorrecto
                    seleccionado.classList.add('error');
                    elemento.classList.add('error');
                    
                    setTimeout(() => {
                        seleccionado.classList.remove('seleccionado', 'error');
                        elemento.classList.remove('error');
                        seleccionado = null;
                    }, 500);
                }
            } else {
                // Selección inválida (dos palabras o dos imágenes)
                seleccionado.classList.remove('seleccionado');
                seleccionado = elemento;
                elemento.classList.add('seleccionado');
            }
        } else {
            // Nueva selección
            seleccionado = elemento;
            elemento.classList.add('seleccionado');
        }
    }

    function esParCorrecto(palabraId, imagenId) {
        return paresDisponibles.some(p => 
            p.palabra.id.toString() === palabraId && 
            p.imagen.id.toString() === imagenId
        );
    }

    function reemplazarParCorrecto(palabraId, imagenId) {
        // 1. Elimina el par acertado de los activos
        paresActivos = paresActivos.filter(p => !(p.palabra.id == palabraId && p.imagen.id == imagenId));

        // 2. Verifica si quedan pares correctos en el grupo actual
        const paresCorrectosRestantes = paresActivos.filter(p => p.esCorrecto).length;

        if (paresCorrectosRestantes === 0) {
            // 3. Si no quedan, pasa al siguiente grupo
            grupoActual++;
            console.log(" Rotando al grupo:", grupoActual % gruposDePares.length);
            
            // 4. Carga el nuevo grupo después de 0.5s (para que termine la animación)
            setTimeout(() => {
                mostrarParesIniciales();
            }, 500);
            return; // ¡Importante! Salir para no reponer pares innecesarios
        }

        // 5. Si aún hay pares, repone los faltantes
        setTimeout(() => {
            const totalParesVisibles = document.querySelectorAll('.fila.palabras .item').length;
            const paresNecesarios = 5 - totalParesVisibles;
            
            if (paresNecesarios > 0) {
                reponerPares(paresNecesarios);
            }
        }, 300);
    }

    
    function reponerPares(cantidad) {
    const grupo = gruposDePares[grupoActual % gruposDePares.length];
    
    // Obtener palabras e imágenes no mostradas
    const palabrasDisponibles = grupo.map(p => p.palabra).filter(p => 
        !document.querySelector(`.fila.palabras .item[data-id="${p.id}"]`)
    );
    
    const imagenesDisponibles = grupo.map(p => p.imagen).filter(i => 
        !document.querySelector(`.fila.imagenes .item[data-id="${i.id}"]`)
    );
    
    // Mezclar independientemente
    mezclarArray(palabrasDisponibles);
    mezclarArray(imagenesDisponibles);
    
    // Agregar nuevos pares manteniendo el balance
    const maxReposicion = Math.min(cantidad, palabrasDisponibles.length, imagenesDisponibles.length);
    
    for (let i = 0; i < maxReposicion; i++) {
        const palabra = palabrasDisponibles[i];
        const imagen = imagenesDisponibles[i];
        
        document.querySelector('.fila.palabras').appendChild(crearElemento('palabra', palabra));
        document.querySelector('.fila.imagenes').appendChild(crearElemento('imagen', imagen));
        
        paresActivos.push({
            palabra: palabra,
            imagen: imagen,
            esCorrecto: palabra.id === imagen.id
        });
    }
    
    verificarBalance();
    
    // Si no hay suficientes para reponer, rotar al siguiente grupo
    if (document.querySelectorAll('.fila.palabras .item').length < 5) {
        grupoActual++;
        setTimeout(() => mostrarParesIniciales(), 500);
    }
}



    function verificarBalance() {
        const palabras = document.querySelectorAll('.fila.palabras .item');
        const imagenes = document.querySelectorAll('.fila.imagenes .item');
        
        console.log(`Balance actual: ${palabras.length} palabras vs ${imagenes.length} imágenes`);
        
        if (palabras.length !== imagenes.length) {
            console.error('¡Desbalance detectado!', {
                palabras: palabras.length,
                imagenes: imagenes.length
            });
            
            // Corregir desbalance eliminando elementos extras
            while (palabras.length > imagenes.length && palabras.length > 0) {
                palabras[palabras.length - 1].remove();
            }
            
            while (imagenes.length > palabras.length && imagenes.length > 0) {
                imagenes[imagenes.length - 1].remove();
            }
        }
    }

    // 3. Funciones de Utilidad
    function mezclarArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function iniciarTemporizador() {
        temporizador = setInterval(() => {
            tiempoRestante--;
            const minutos = Math.floor(tiempoRestante / 60);
            const segundos = tiempoRestante % 60;
            tiempoElement.textContent = `${minutos}:${segundos < 10 ? '0' : ''}${segundos}`;
            
            if (tiempoRestante <= 0) {
                clearInterval(temporizador);
                finDelJuego();
            }
        }, 1000);
    }

     function finDelJuego() {
        clearInterval(temporizador);
        
        // Redirigir a la página final con los resultados
        const porcentajeExito = Math.round((aciertos / totalPares) * 100);
        const tiempoUsado = CONFIG_JUEGO.tiempoPorRonda - tiempoRestante;
        
        window.location.href = `${window.location.pathname}?completado=1&puntaje=${aciertos*10}&tiempo=${tiempoUsado}`;
    }

    function verificarEstadoGrupos() {
        console.log('--- Estado Actual ---');
        console.log('Grupo actual:', grupoActual % gruposDePares.length);
        console.log('Pares activos:', paresActivos.length);
        console.log('Pares correctos restantes:', 
            paresActivos.filter(p => p.esCorrecto).length);
        console.log('Elementos visibles:',
            'Palabras:', document.querySelectorAll('.fila.palabras .item').length,
            'Imágenes:', document.querySelectorAll('.fila.imagenes .item').length);
    }

    function verificarGrupos() {
        console.log('=== VERIFICACIÓN DE GRUPOS ===');
        console.log(`Total de grupos: ${gruposDePares.length}`);
        
        gruposDePares.forEach((grupo, index) => {
            console.log(`Grupo ${index + 1}:`);
            grupo.forEach(par => {
                console.log(`- ${par.palabra.palabra} (ID: ${par.palabra.id})`);
            });
        });
        
        console.log('Pares disponibles totales:', paresDisponibles.length);
    }
    
    // Llámala después de crearGruposDePares()

    // Inicializar el juego
    inicializarJuego();
    iniciarTemporizador();
    verificarEstadoGrupos();
    console.log("=== INICIO ===");
    console.log("Total pares disponibles:", paresDisponibles.length);
    console.log("Número de grupos:", gruposDePares.length);
    console.log("Grupos:", gruposDePares.map(g => g.map(p => p.palabra.palabra)));
    console.log("=== FIN ===");
    
}); 