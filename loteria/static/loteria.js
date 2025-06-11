class LoteriaGame {
    constructor(gestos) {
        this.gestos = this.shuffleArray([...gestos]);
        this.gestoActual = 0;
        this.puntuacion = 0;
        this.procesandoSeleccion = false;
        this.intentosPorGesto = {}; // Ahora rastreamos intentos por GESTO, no por palabra
        this.initElements();
        this.setupEventListeners();
        
        if (this.gestos.length > 0) {
            this.mostrarGesto();
        }
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }
    
    initElements() {
        this.gestoImagen = document.getElementById('gesto-imagen');
        this.gestoVideo = document.getElementById('gesto-video');
        this.itemsLoteria = document.querySelectorAll('.item');
    }
    
    setupEventListeners() {
        this.itemsLoteria.forEach(item => {
            item.addEventListener('click', () => this.seleccionarPalabra(item));
        });
        
        this.gestoVideo.addEventListener('ended', () => {
            this.gestoVideo.style.display = 'none';
        });
    }
    
    mostrarGesto() {
        const gesto = this.gestos[this.gestoActual];
        
        // Resetear elementos multimedia
        this.gestoVideo.pause();
        this.gestoVideo.currentTime = 0;
        
        if (gesto.es_video) {
            this.gestoVideo.src = gesto.gesto;
            this.gestoVideo.style.display = 'block';
            this.gestoImagen.style.display = 'none';
            this.gestoVideo.play().catch(e => console.error("Error al reproducir video:", e));
        } else {
            this.gestoImagen.src = gesto.gesto;
            this.gestoImagen.style.display = 'block';
            this.gestoVideo.style.display = 'none';
        }
        
    }
    
    seleccionarPalabra(elemento) {
        const palabraTexto = elemento.querySelector('.palabra').textContent;
        const gestoActual = this.gestos[this.gestoActual];
        
        if (this.procesandoSeleccion || elemento.classList.contains('correcto')) return;
        this.procesandoSeleccion = true;

        if (!this.intentosPorGesto[this.gestoActual]) {
            this.intentosPorGesto[this.gestoActual] = 0;
        }
        this.intentosPorGesto[this.gestoActual]++;

        this.itemsLoteria.forEach(item => {
            if (!item.classList.contains('correcto')) {
                item.style.pointerEvents = 'none';
            }
        });

        if (palabraTexto === gestoActual.palabra) {
            const puntos = this.intentosPorGesto[this.gestoActual] === 1 ? 10 : 5;
            this.puntuacion += puntos;
            
            elemento.classList.add('correcto-permanente');
            elemento.classList.add('correcto');
            elemento.style.pointerEvents = 'none';
            
            const feedbackMessage = document.getElementById('feedback-message');
            feedbackMessage.textContent = this.intentosPorGesto[this.gestoActual] === 1 
                ? "¡Perfecto! +10 puntos" 
                : "¡Correcto! +5 puntos";
            feedbackMessage.style.color = "#fff";
            
            document.getElementById('puntuacion-valor').textContent = this.puntuacion;
            document.getElementById('puntuacion').style.display = 'block';

            this.gestoActual++;
            if (this.gestoActual < this.gestos.length) {
                setTimeout(() => {
                    this.mostrarGesto();
                    this.resetItems();
                    feedbackMessage.textContent = "Selecciona la palabra que corresponde al gesto mostrado";
                    feedbackMessage.style.color = "";
                    this.procesandoSeleccion = false;
                }, 1500);
            } else {
                // Juego completado - redirigir a la página finalizada
                setTimeout(() => {
                    window.location.href = `${window.location.pathname}?completado=1&puntuacion=${this.puntuacion}`;
                }, 2000);
            }
        } else {
            elemento.classList.add('incorrecto');
            const feedbackMessage = document.getElementById('feedback-message');
            feedbackMessage.textContent = "Inténtalo de nuevo";
            feedbackMessage.style.color = "#fff";

            setTimeout(() => {
                elemento.classList.remove('incorrecto');
                this.resetItems();
                feedbackMessage.textContent = "Selecciona la palabra que corresponde al gesto mostrado";
                feedbackMessage.style.color = "";
                this.procesandoSeleccion = false;
            }, 1500);
        }
    }

    resetItems() {
        this.itemsLoteria.forEach(item => {
            if (!item.classList.contains('correcto-permanente')) {
                item.style.pointerEvents = 'auto';
                item.classList.remove('incorrecto');
            }
        });
    }

}

document.addEventListener('DOMContentLoaded', () => {
    new LoteriaGame(window.loteriaData.gestos);
});