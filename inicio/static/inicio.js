let myDoughnutChart;

   const APP_URLS = {
            puntosUsuario: "puntosUsuario/"
        };

function inicializarGrafica(puntosActuales, puntosFaltantes) {
    const ctx = document.getElementById('dona-grafica').getContext('2d');
    
    document.getElementById('puntos-usuario').textContent = puntosActuales;
    
    if (puntosFaltantes === 0) {
        const data = {
            labels: ['¡Todas las etapas completadas!'],
            datasets: [{
                data: [1],
                backgroundColor: ['rgb(75, 192, 192)'],
                hoverOffset: 4
            }]
        };

        const config = {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                }
            }
        };

        if (myDoughnutChart) {
            myDoughnutChart.destroy();
        }
        
        myDoughnutChart = new Chart(ctx, config);
        return;
    }
    
    const data = {
        labels: [
            `Puntos obtenidos: ${puntosActuales}`,
            `Faltan: ${puntosFaltantes}`
        ],
        datasets: [{
            data: [puntosActuales, puntosFaltantes],
            backgroundColor: [
                'rgb(239, 118, 122)',
                'rgb(255, 205, 86)'
            ],
            borderWidth: 1,
            hoverOffset: 4
        }]
    };

    const config = {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            cutout: '50%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label;
                        }
                    }
                }
            }
        }
    };

    if (myDoughnutChart) {
        myDoughnutChart.destroy();
    }
    
    myDoughnutChart = new Chart(ctx, config);
}

function calcularPuntosFaltantes(puntosActuales) {
    if (puntosActuales < 6800) return 6800 - puntosActuales;
    if (puntosActuales < 10200) return 10200 - puntosActuales;
    if (puntosActuales < 16200) return 16200 - puntosActuales;
    return 0; 
}


function bringToFront(element) {
    let cards = Array.from(document.querySelectorAll('.card')); 
    let selectedIndex = cards.indexOf(element); 

    let newOrder = [
        ...cards.slice(selectedIndex + 1), 
        ...cards.slice(0, selectedIndex),  
        element 
    ];

    newOrder.forEach((card, index) => {
        card.style.left = `${index * 80}px`; 
        card.style.zIndex = index + 1;
    });
}


function accesoEtapa(etapa, elemento) {
    event.preventDefault();
    event.stopPropagation();

    fetch(APP_URLS.puntosUsuario)
        .then(response => {
            if(!response.ok) throw new Error('Error en la red');
            return response.json();
        })
        .then(data => {
            const puntosNecesarios = parseInt(elemento.getAttribute('data-required-points'));
            const puntosUsuario = data.puntos;
            const leccionUsuario = data.leccion_actual;
            
            if(data.unlocked_stages[`etapa${etapa}`]) {
                window.location.href = `/lecciones/etapa${etapa}/`;
            } else {
                let mensaje = '';
                if(puntosUsuario < puntosNecesarios) {
                    mensaje = `Necesitas ${puntosNecesarios} puntos para desbloquear esta etapa.`;
                } else {
                    const etapas = data.etapas_lecciones;
                    let leccionesRequeridas = 0;
                    
                    if(etapa === 2) leccionesRequeridas = etapas.etapa1;
                    else if(etapa === 3) leccionesRequeridas = etapas.etapa1 + etapas.etapa2;
                    else if(etapa === 4) leccionesRequeridas = etapas.etapa1 + etapas.etapa2 + etapas.etapa3;
                    
                    const leccionesFaltantes = leccionesRequeridas - leccionUsuario;
                    mensaje = `Necesitas completar ${leccionesFaltantes} lecciones más de la etapa anterior.`;
                }
                
                Swal.fire({
                    title: '¡Ups!',
                    text: mensaje,
                    icon: 'warning',
                    confirmButtonText: 'Aceptar'
                });
            }
        })
        .catch(error => console.error(error));
}

document.addEventListener('DOMContentLoaded', function() {
    fetch(APP_URLS.puntosUsuario)
        .then(response => { 
            if (!response.ok) throw new Error('Error en la red');
            return response.json();
        })
        .then(data => {
            if(!data.unlocked_stages.etapa2){
                document.getElementById('etapa2-card').style.display = 'locked';
            }
            if(!data.unlocked_stages.etapa3){
                document.getElementById('etapa3-card').style.display = 'locked';
            }
            if(!data.unlocked_stages.etapa4){
                document.getElementById('etapa4-card').style.display = 'locked';
            }
        })
        .catch(error => console.error(error));
    });


document.addEventListener('DOMContentLoaded', function() {
    fetch(APP_URLS.puntosUsuario)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) throw new Error(data.error);
            
            for (let i = 2; i <= 4; i++) {
                const card = document.getElementById(`etapa${i}-card`).closest('.card');
            }
            
            const puntosFaltantes = calcularPuntosFaltantes(data.puntos);
            inicializarGrafica(data.puntos, puntosFaltantes);
            
            const nextStageText = document.querySelector('.texto-puntos span');
            if (!data.unlocked_stages.etapa2) {
                nextStageText.textContent = '2 (6800 pts y completar etapa 1)';
            } else if (!data.unlocked_stages.etapa3) {
                nextStageText.textContent = '3 (10200 pts y completar etapa 2)';
            } else if (!data.unlocked_stages.etapa4) {
                nextStageText.textContent = '4 (16200 pts y completar etapa 3)';
            } else {
                nextStageText.textContent = '¡Todas completadas!';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error',
                text: 'No se pudieron cargar los datos. Por favor intenta más tarde.',
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        });
});


document.addEventListener('DOMContentLoaded', function() {
    const nombreDesafio = document.getElementById('nombre-desafio');
    const enalceDesafio = document.getElementById('enlace-desafio');
    const descripcionDesafio = document.getElementById('descripcion');

    const minutos = new Date().getMinutes();

    const segmento = Math.floor(minutos / 2) % 3;

    let desafio, url, descripcion;

    switch (segmento) {
        case 0:
            desafio = "Contrarreloj";
            descripcion = "Un juego de velocidad y precisión donde debes completar tareas en el menor tiempo posible.";
            url = "/desafio/contrarreloj/";
            break;
        case 1:
            desafio = "Memorama";
            descripcion = "Un juego de memoria donde debes encontrar pares de cartas iguales.";
            url = "/desafio/memorama/";
            break;
        case 2:
            desafio = "Relacion";
            descripcion = "Un juego de asociación donde debes relacionar conceptos con imágenes.";
            url = "/desafio/relacion/";
            break;
    }

    nombreDesafio.textContent = desafio;
    descripcionDesafio.textContent = descripcion;

    fetch(APP_URLS.puntosUsuario)
        .then(response => response.json())
        .then(data => {
            if(data.puntos > 900){
                enalceDesafio.href = url;
            } else {
                enalceDesafio.href = "#";
                enalceDesafio.addEventListener('click', function(event) {
                    event.preventDefault();
                    Swal.fire({
                        title: '¡Ups!',
                        text: 'Necesitas al menos 900 puntos para acceder a los desafíos.',
                        icon: 'warning',
                        confirmButtonText: 'Aceptar'
                    });
                });
            }
        })
});

