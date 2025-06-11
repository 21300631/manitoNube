document.addEventListener('DOMContentLoaded', () => {
    console.log("Modo contrarreloj iniciado");
    
    // Elementos del DOM
    const videoElement = document.getElementById('inputVideo');
    const canvasElement = document.getElementById('outputCanvas');
    const canvasCtx = canvasElement.getContext('2d');
    const countdownElement = document.getElementById('countdown');
    const feedbackElement = document.getElementById('feedback');
    const relojElement = document.querySelector('.reloj span');
    const mensajeElement = document.querySelector('.mensaje span');
    
    // Variables de estado
    window.referenceLandmarks = null;
    let currentSimilarity = 0;
    let isGestureCorrect = false;
    let correctPoseStartTime = null;
    let score = 0;
    let tiempoRestante = 40; // 1 minuto en segundos
    let tiempoInicio = null;
    let ejercicioActual = 0;
    let totalEjercicios = 0;
    let tiempoPorEjercicio = 0;
    let temporizador = null;
    let recordingTimer = null;
    
    // Configuración
    const REQUIRED_CORRECT_TIME = 1000; // 1 segundo para considerar correcto
    const SIMILARITY_THRESHOLD = 80; // Porcentaje de similitud requerido
    const OPEN_HAND_THRESHOLD = 0.4; // Umbral para considerar mano abierta
    
    // Configuración de elementos
    videoElement.autoplay = true;
    videoElement.style.transform = "scaleX(-1)";
    canvasElement.style.width = '100%';
    // canvasElement.style.maxWidth = '400px';
    canvasElement.style.transform = "scaleX(-1)";
    canvasElement.style.borderRadius = '10px';
    
    // Añadir elementos al DOM
    
    
    // Inicializar MediaPipe Hands
    const hands = new Hands({
        locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });
    
    hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.5
    });
    
    // Conexiones de la mano
    const HAND_CONNECTIONS = [
        [0, 1], [1, 2], [2, 3], [3, 4],         // Pulgar
        [0, 5], [5, 6], [6, 7], [7, 8],         // Índice
        [0, 9], [9, 10], [10, 11], [11, 12],    // Medio
        [0, 13], [13, 14], [14, 15], [15, 16],  // Anular
        [0, 17], [17, 18], [18, 19], [19, 20],  // Meñique
        [5, 9], [9, 13], [13, 17]               // Base de los dedos
    ];
    
    // Función para mostrar feedback
    function showFeedback(message, isCorrect) {
        feedbackElement.textContent = message;
        feedbackElement.style.color = isCorrect ? '#00FF00' : '#FF0000';
        feedbackElement.style.backgroundColor = isCorrect ? 'rgba(0, 255, 0, 0.2)' : 'rgba(255, 0, 0, 0.2)';
        
        if (isCorrect) {
            feedbackElement.style.animation = 'blink 1s 2';
        } else {
            feedbackElement.style.animation = 'none';
        }
    }
    
    // Función para calcular similitud entre landmarks
    function calculateSimilarity(landmarks1, landmarks2) {
        if (!landmarks1 || !landmarks2 || landmarks1.length !== landmarks2.length) return 0;
        
        const fingerWeights = {
            thumb: 1.5, index: 1.2, middle: 1.0, ring: 0.9, pinky: 0.8
        };
        
        let totalWeightedDistance = 0;
        let totalWeight = 0;
        
        for (let i = 0; i < landmarks1.length; i++) {
            let weight = 1.0;
            if (i >= 1 && i <= 4) weight = fingerWeights.thumb;
            else if (i >= 5 && i <= 8) weight = fingerWeights.index;
            else if (i >= 9 && i <= 12) weight = fingerWeights.middle;
            else if (i >= 13 && i <= 16) weight = fingerWeights.ring;
            else if (i >= 17 && i <= 20) weight = fingerWeights.pinky;
            
            const dx = landmarks1[i].x - landmarks2[i].x;
            const dy = landmarks1[i].y - landmarks2[i].y;
            const dz = landmarks1[i].z - landmarks2[i].z;
            
            totalWeightedDistance += Math.sqrt(dx*dx + dy*dy + dz*dz) * weight;
            totalWeight += weight;
        }
        
        const averageDistance = totalWeightedDistance / totalWeight;
        let similarity = Math.max(0, 100 - (averageDistance * 200));
        
        // Penalizar si la mano está demasiado abierta
        if (isHandTooOpen(landmarks2)) {
            similarity *= 0.6;
        }
        
        return similarity;
    }
    
    // Detectar mano abierta
    function isHandTooOpen(landmarks) {
        if (!landmarks || landmarks.length < 21) return false;
        
        const wrist = landmarks[0];
        const fingerTips = [4, 8, 12, 16, 20];
        let totalDistance = 0;
        
        for (const tipIndex of fingerTips) {
            const tip = landmarks[tipIndex];
            const dx = tip.x - wrist.x;
            const dy = tip.y - wrist.y;
            totalDistance += Math.sqrt(dx*dx + dy*dy);
        }
        
        const averageDistance = totalDistance / fingerTips.length;
        return averageDistance > OPEN_HAND_THRESHOLD;
    }
    
    // Función para actualizar el temporizador
    function updateTimer() {
        const minutos = Math.floor(tiempoRestante / 60);
        const segundos = tiempoRestante % 60;
        relojElement.textContent = `${minutos}:${segundos < 10 ? '0' : ''}${segundos}`;
        
        if (tiempoRestante <= 0) {
            clearInterval(temporizador);
            endGame();
        } else {
            tiempoRestante--;
        }
    }
    
    function startGame() {
        tiempoInicio = Date.now();
        temporizador = setInterval(updateTimer, 1000);
        countdownElement.style.display = 'none';
        
        // Verifica que los landmarks estén cargados
        if (!window.referenceLandmarks) {
            console.error("Error: Landmarks no cargados");
            showFeedback("Error: Referencia no disponible", false);
            return;
        }
        
        console.log("Iniciando juego con:", window.PALABRA_ACTUAL, window.referenceLandmarks);
    }
    
    // Función para terminar el juego
   async function endGame() {
        // Detener la cámara
        if (videoElement.srcObject) {
            videoElement.srcObject.getTracks().forEach(track => track.stop());
        }
        
        // Mostrar mensaje temporal
        mensajeElement.textContent = `¡Tiempo terminado! Puntuación: ${score}`;
        
        try {
            const response = await fetch("/desafio/tiempo-terminado", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}',
                },
                body: JSON.stringify({ puntaje: score })
            });
            
            const data = await response.json();
            
            if (data.status === 'completed') {
                window.location.href = data.redirect_url;
            }
        } catch (error) {
            console.error('Error al finalizar el juego:', error);
            // Redirigir igualmente como fallback
            window.location.href = "/desafio/resultado/";
        }
    }
    
    // Función para contar regresiva antes de iniciar
    function startCountdown() {
        let count = 3;
        countdownElement.style.display = 'block';
        countdownElement.textContent = count;
        
        const countdownInterval = setInterval(() => {
            count--;
            countdownElement.textContent = count;
            
            if (count <= 0) {
                clearInterval(countdownInterval);
                startGame();
            }
        }, 1000);
    }
    
    // Manejo de resultados de MediaPipe
    hands.onResults(results => {
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.scale(-1, 1);
        canvasCtx.translate(-canvasElement.width, 0);
        
        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            const landmarks = results.multiHandLandmarks[0];
            const currentLandmarks = landmarks.map(point => ({
                x: point.x,
                y: point.y,
                z: point.z
            }));
            
            if (window.referenceLandmarks) {
                currentSimilarity = calculateSimilarity(window.referenceLandmarks, currentLandmarks);
                isGestureCorrect = currentSimilarity > SIMILARITY_THRESHOLD;
                
                // Dibujar landmarks con colores según la precisión
                const landmarkColor = isGestureCorrect ? '#00FF00' : '#FF0000';
                const connectionColor = isGestureCorrect ? '#00AA00' : '#AA0000';
                
                drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
                    color: connectionColor,
                    lineWidth: 3
                });
                
                drawLandmarks(canvasCtx, landmarks, {
                    color: landmarkColor,
                    lineWidth: 2,
                    radius: (idx) => [4, 8, 12, 16, 20, 0].includes(idx) ? 6 : 4
                });
                
                // Manejar gesto correcto
                if (isGestureCorrect) {
                    if (correctPoseStartTime === null) {
                        correctPoseStartTime = Date.now();
                    } else {
                        const elapsedTime = Date.now() - correctPoseStartTime;
                        const remainingTime = REQUIRED_CORRECT_TIME - elapsedTime;
                        
                        if (remainingTime > 0) {
                            showFeedback(`✓ Mantén la pose (${Math.ceil(remainingTime/1000)}s)`, true);
                        } else {
                            // Gesto completado correctamente
                            score++;
                            showFeedback("✓ ¡Correcto! +1 punto", true);
                            correctPoseStartTime = null;
                            
                            // Actualizar mensaje
                            mensajeElement.textContent = "¡Correcto!";
                            enviarRespuesta(true);

                            
                        }
                    }
                } else {
                    correctPoseStartTime = null;
                    showFeedback(`✗ Ajusta tu gesto (${currentSimilarity.toFixed(0)}%)`, false);
                }
            }
        } else {
            correctPoseStartTime = null;
            showFeedback("Muestra tu mano en el área", false);
        }
        
        canvasCtx.restore();
    });



    // Luego reemplaza el fetch original en tu código con:
    // Función para obtener el token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Iniciar cámara
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoElement.srcObject = stream;
            const camera = new Camera(videoElement, {
                onFrame: async () => {
                    canvasCtx.save();
                    canvasCtx.scale(-1, 1);
                    canvasCtx.translate(-videoElement.videoWidth, 0);
                    canvasCtx.drawImage(videoElement, 0, 0);
                    canvasCtx.restore();
                    await hands.send({ image: canvasElement });
                    
                    // Actualizar temporizador de grabación
                    if (tiempoInicio) {
                        const elapsed = Math.floor((Date.now() - tiempoInicio) / 1000);
                        const remaining = Math.max(0, tiempoRestante - elapsed);
                    }
                },
                width: 500,
                height: 400
            });
            camera.start();
            
            // Iniciar cuenta regresiva
            startCountdown();
        })
        .catch(err => {
            console.error("Error de cámara:", err);
            showFeedback("Error al acceder a la cámara", false);
        });
    
    // Animación CSS para feedback
    const style = document.createElement('style');
    style.textContent = `
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    `;
    document.head.appendChild(style);
});

window.landmarksCargados = function() {
    // Reiniciar el proceso de comparación con los nuevos landmarks
    console.log("Nuevos landmarks listos para usar:", referenceLandmarks);
    // Aquí puedes reiniciar cualquier temporizador o estado de comparación
};
