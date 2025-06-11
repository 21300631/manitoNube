let seleccionadas = [];
let puntos = 0;
let paresEncontrados = 0;
let totalPares = parseInt(document.getElementById('total-pares').value);
const basePath = document.getElementById('request-path').value;

document.querySelectorAll('.item').forEach(card => {
    card.addEventListener('click', () => {
        if (card.classList.contains('match') || card.classList.contains('flipped')) return;

        card.classList.add('flipped');
        seleccionadas.push(card);

        if (seleccionadas.length === 2) {
            const [c1, c2] = seleccionadas;
            
            // Deshabilitar todas las cartas temporalmente
            document.querySelectorAll('.item').forEach(c => {
                c.style.pointerEvents = 'none';
            });

            if (c1.dataset.id === c2.dataset.id && c1.dataset.tipo !== c2.dataset.tipo) {
                // Par correcto
                c1.classList.add('match');
                c2.classList.add('match');
                puntos += 10;
                paresEncontrados++;
                
                // Verificar si se completó el juego
                if (paresEncontrados === totalPares) {
                    setTimeout(() => {
                        // Redirigir con los parámetros correctos
                        window.location.href = `/desafio/finalMemorama?puntaje=${puntos}`;

                    }, 1500);
                } else {
                    // Rehabilitar las cartas después de un breve retraso
                    setTimeout(() => {
                        document.querySelectorAll('.item').forEach(c => {
                            if (!c.classList.contains('match')) {
                                c.style.pointerEvents = 'auto';
                            }
                        });
                    }, 1000);
                }
            } else {
                // Par incorrecto
                setTimeout(() => {
                    c1.classList.remove('flipped');
                    c2.classList.remove('flipped');
                    // Rehabilitar todas las cartas
                    document.querySelectorAll('.item').forEach(c => {
                        if (!c.classList.contains('match')) {
                            c.style.pointerEvents = 'auto';
                        }
                    });
                }, 1000);
            }
            seleccionadas = [];
        }
    });
});

// Función para verificar si el juego está completo
function verificarJuegoCompleto() {
    const cartasVolteadas = document.querySelectorAll('.item.flipped').length;
    const cartasEmparejadas = document.querySelectorAll('.item.match').length;
    
    // Si todas las cartas están emparejadas
    if (cartasEmparejadas === totalPares * 2) {
        setTimeout(() => {
            window.location.href = `${basePath}?completado=1&puntaje=${puntos}`;
        }, 1500);
    }
}