document.addEventListener('DOMContentLoaded', () => {
    // Verificar si es un ejercicio de video (usando la variable global definida en el HTML)
    if (IS_VIDEO_EXERCISE) {
        console.log("Ejercicio de video detectado");
        
        // Elementos del DOM
        const videoElement = document.getElementById('inputVideo');
        const canvasElement = document.getElementById('outputCanvas');
        const recordButton = document.getElementById('recordBtn');
        const nextButton = document.getElementById('nextBtn');
        const countdownElement = document.getElementById('countdown');
        const recordingTimerElement = document.getElementById('recordingTimer');
        const gestoVideo = document.getElementById('gestoVideo');
        const palabraActual= gestoVideo.dataset.palabra;
        const palabraJsonUrl = gestoVideo.dataset.palabraJson;

        let referenceLandmarks = null;

        console.log(`Palabra actual: ${palabraActual}`);
        console.log(`URL de landmarks: ${palabraJsonUrl}`);
        
        if (typeof LANDMARKS_JSON_URL !== 'undefined') {
            console.log("JSON de la palabra:", LANDMARKS_JSON_URL);
        }
        // Opción 2: Obtener el JSON mediante fetch
        else if (palabraJsonUrl) {
            fetch(palabraJsonUrl)
                .then(response => response.json())
                .then(jsonData => {
                    console.log("JSON de la palabra obtenido:", jsonData);
                    // Aquí puedes usar jsonData como necesites
                })
                .catch(error => {
                    console.error("Error obteniendo JSON de la palabra:", error);
                });
        }

        if (palabraJsonUrl) {
            fetch(palabraJsonUrl)
                .then(response => response.json())
                .then(jsonData => {
                    referenceLandmarks = jsonData;
                    console.log("Landmarks de referencia cargados:", referenceLandmarks);
                })
                .catch(error => {
                    console.error("Error cargando JSON de referencia:", error);
                });
        }
        

        // Mostrar el botón de grabar
        if (recordButton) {
            recordButton.style.display = 'inline-block';
            recordButton.disabled = false;
        } else {
            console.error("Botón de grabación no encontrado");
        }
        
        // Configuración inicial
        if (canvasElement) {
            canvasElement.width = 640;
            canvasElement.height = 480;
            const ctx = canvasElement.getContext('2d');
            
            let mediaRecorder;
            let recordedChunks = [];
            let isRecording = false;
            let countdownInterval;
            let recordingTimerInterval;
            let allHandLandmarks = []; // Almacenará landmarks de mano por frame
            let hands;
            
            ctx.imageSmoothingEnabled = true;
            videoElement.playsInline = true;
            videoElement.muted = true;

            // Configurar MediaPipe Hands
            async function setupHandTracking() {
                const hands = new Hands({
                    locateFile: (file) => {
                        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
                    }
                });
                
                hands.setOptions({
                    maxNumHands: 2,
                    modelComplexity: 1,
                    minDetectionConfidence: 0.5,
                    minTrackingConfidence: 0.4
                });
                
                hands.onResults(onHandsResults);
                
                return hands;
            }

            // Función para normalizar landmarks
            function normalizeLandmarks(landmarks) {
                if (!landmarks || landmarks.length === 0) return null;
                
                // 1. Convertir a array de puntos {x, y, z}
                const points = landmarks.map(p => ({x: p.x, y: p.y, z: p.z}));
                
                // 2. Calcular centroide
                const centroid = points.reduce((acc, p) => {
                    acc.x += p.x;
                    acc.y += p.y;
                    acc.z += p.z;
                    return acc;
                }, {x: 0, y: 0, z: 0});
                
                centroid.x /= points.length;
                centroid.y /= points.length;
                centroid.z /= points.length;
                
                // 3. Centrar los puntos
                const centered = points.map(p => ({
                    x: p.x - centroid.x,
                    y: p.y - centroid.y,
                    z: p.z - centroid.z
                }));
                
                // 4. Calcular escala basada en la distancia muñeca (punto 0) a dedo medio (punto 12)
                const wrist = centered[0];
                const middleFinger = centered[12];
                const scale = Math.sqrt(
                    Math.pow(middleFinger.x - wrist.x, 2) +
                    Math.pow(middleFinger.y - wrist.y, 2) +
                    Math.pow(middleFinger.z - wrist.z, 2)
                );
                
                if (scale === 0) return null;
                
                // 5. Normalizar y aplicar pesos a puntos clave
                return centered.map((p, i) => ({
                    id: i,
                    x: p.x / scale,
                    y: p.y / scale,
                    z: p.z / scale
                }));
            }

            function goToNextExercise() {
                // Detener la cámara primero
                if (mediaRecorder) {
                    mediaRecorder.stop();
                }
                if (videoElement.srcObject) {
                    videoElement.srcObject.getTracks().forEach(track => track.stop());
                }
                
                // Enviar la petición para avanzar
                fetch('/repaso/siguiente/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        error: false
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        window.location.href = data.redirect_url;
                    } else {
                        // Forzar recarga limpia de la página
                        window.location.href = data.redirect_url;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Recargar de todas formas si hay error
                    window.location.href = '/repaso/';
                });
            }

            
            function procrustesAlignment(userLandmarks, referenceLandmarks) {
                // Convertir landmarks a matrices para numeric.js
                const userPoints = userLandmarks.map(p => [p.x, p.y, p.z]);
                const refPoints = referenceLandmarks.map(p => [p.x, p.y, p.z]);
                
                // Centrar los puntos
                const userCentered = centerPoints(userPoints);
                const refCentered = centerPoints(refPoints);
                
                // Calcular matriz de covarianza
                const H = numeric.dot(numeric.transpose(userCentered), refCentered);
                
                // SVD
                const svd = numeric.svd(H);
                
                // Calcular matriz de rotación
                const R = numeric.dot(svd.V, numeric.transpose(svd.U));
                
                // Aplicar rotación y traslación
                const aligned = numeric.dot(userPoints, R);
                
                // Convertir de vuelta al formato de landmarks
                return aligned.map((point, i) => ({
                    id: userLandmarks[i].id,
                    x: point[0],
                    y: point[1],
                    z: point[2]
                }));
            }

            function centerPoints(points) {
                const centroid = points.reduce((acc, p) => {
                    acc[0] += p[0];
                    acc[1] += p[1];
                    acc[2] += p[2];
                    return acc;
                }, [0, 0, 0]).map(v => v / points.length);
                
                return points.map(p => [
                    p[0] - centroid[0],
                    p[1] - centroid[1],
                    p[2] - centroid[2]
                ]);
            }

            // Función para calcular la similitud entre dos conjuntos de landmarks
            function calculateSimilarity(userLandmarks, referenceLandmarks) {
                if (!userLandmarks || !referenceLandmarks) return 0;
                
                // 1. Normalizar ambos conjuntos
                const normalizedUser = normalizeLandmarks(userLandmarks);
                const normalizedRef = normalizeLandmarks(referenceLandmarks);

                
                
                if (!normalizedUser || !normalizedRef) return 0;
                
                // 2. Alinear usando Procrustes (opcional, puede ser costoso computacionalmente)
                const alignedUser = procrustesAlignment(normalizedUser, normalizedRef);
                
                // 3. Pesos para diferentes partes de la mano
                const weights = {
                    palm: [0, 1, 5, 9, 13, 17], // Puntos de la palma
                    thumb: [1, 2, 3, 4],         // Pulgar
                    index: [5, 6, 7, 8],         // Índice
                    middle: [9, 10, 11, 12],    // Medio
                    ring: [13, 14, 15, 16],      // Anular
                    pinky: [17, 18, 19, 20]      // Meñique
                };
                
                let totalError = 0;
                let totalWeight = 0;
                
                // 4. Comparar punto por punto con pesos diferentes
                for (let i = 0; i < alignedUser.length; i++) {
                    const userPoint = alignedUser[i];
                    const refPoint = normalizedRef[i];
                    
                    // Determinar el peso según la parte de la mano
                    let weight = 1.0;
                    if (weights.thumb.includes(i)) weight = 1.3;
                    if (weights.index.includes(i)) weight = 1.5;
                    if (weights.middle.includes(i)) weight = 1.4;
                    if (weights.palm.includes(i)) weight = 0.8;
                    
                    const dx = userPoint.x - refPoint.x;
                    const dy = userPoint.y - refPoint.y;
                    const dz = userPoint.z - refPoint.z;
                    
                    const error = Math.sqrt(dx*dx + dy*dy + dz*dz) * weight;
                    totalError += error;
                    totalWeight += weight;
                }
                
                if (totalWeight === 0) return 0;
                
                const avgError = totalError / totalWeight;
                
                // 5. Convertir error a similitud (0-1)
                // Ajustar estos parámetros según tus necesidades
                const similarity = Math.exp(-2.5 * avgError);
                
                return Math.max(0, Math.min(1, similarity));
            }

           

            // Función para procesar todos los frames y calcular la similitud promedio
            function processAllFrames(userFrames, referenceFrames) {
                if (!userFrames || userFrames.length === 0 || !referenceFrames || referenceFrames.length === 0) return 0;
                
                // 1. Muestrear frames para igualar longitud
                const sampledUserFrames = sampleFrames(userFrames, referenceFrames.length);
                
                // 2. Encontrar el mejor desplazamiento temporal (DTW básico)
                let bestSimilarity = 0;
                const maxOffset = Math.min(3, referenceFrames.length); // Pequeño margen para sincronización
                
                for (let offset = -maxOffset; offset <= maxOffset; offset++) {
                    let currentSimilarity = 0;
                    let comparisons = 0;
                    
                    for (let i = 0; i < referenceFrames.length; i++) {
                        const refIdx = i;
                        const userIdx = i + offset;
                        
                        if (userIdx < 0 || userIdx >= sampledUserFrames.length) continue;
                        
                        const refFrame = referenceFrames[refIdx];
                        const userFrame = sampledUserFrames[userIdx];
                        
                        if (!refFrame || !userFrame) continue;
                        
                        refFrame.forEach(refHand => {
                            const userHand = userFrame.find(h => h.handedness === refHand.handedness);
                            if (userHand) {
                                const similarity = calculateSimilarity(userHand.landmarks, refHand.landmarks);
                                currentSimilarity += similarity;
                                comparisons++;
                            }
                        });
                    }
                    
                    if (comparisons > 0) {
                        currentSimilarity /= comparisons;
                        if (currentSimilarity > bestSimilarity) {
                            bestSimilarity = currentSimilarity;
                        }
                    }
                }
                
                return bestSimilarity * 100; // Convertir a porcentaje
            }

            function sampleFrames(frames, targetCount) {
                if (frames.length <= targetCount) return [...frames];
                
                const sampled = [];
                const step = frames.length / targetCount;
                
                for (let i = 0; i < targetCount; i++) {
                    const index = Math.floor(i * step);
                    sampled.push(frames[index]);
                }
                
                return sampled;
            }

            // Función para calcular la distancia entre dos conjuntos de landmarks
            function calculateMovement(prevLandmarks, currentLandmarks) {
                if (!prevLandmarks || !currentLandmarks) return 0;
                
                let totalMovement = 0;
                const minLandmarks = Math.min(prevLandmarks.length, currentLandmarks.length);
                
                for (let i = 0; i < minLandmarks; i++) {
                    const dx = prevLandmarks[i].x - currentLandmarks[i].x;
                    const dy = prevLandmarks[i].y - currentLandmarks[i].y;
                    const dz = prevLandmarks[i].z - currentLandmarks[i].z;
                    totalMovement += Math.sqrt(dx*dx + dy*dy + dz*dz);
                }
                
                return totalMovement / minLandmarks; // Movimiento promedio por landmark
            }

            // Función para filtrar frames sin movimiento
            function filterStaticFrames(frames, movementThreshold = 0.005) {
                if (frames.length < 2) return frames;
                
                const filteredFrames = [frames[0]]; // Siempre incluir el primer frame
                
                for (let i = 1; i < frames.length; i++) {
                    const prevFrame = frames[i-1];
                    const currentFrame = frames[i];
                    
                    // Calcular movimiento para cada mano en el frame
                    let maxMovement = 0;
                    
                    for (let handIndex = 0; handIndex < currentFrame.length; handIndex++) {
                        const currentHand = currentFrame[handIndex];
                        const prevHand = prevFrame.find(h => 
                            h.handedness === currentHand.handedness);
                        
                        if (prevHand) {
                            const movement = calculateMovement(
                                prevHand.landmarks, 
                                currentHand.landmarks
                            );
                            maxMovement = Math.max(maxMovement, movement);
                        }
                    }
                    
                    // Solo incluir frames con movimiento significativo
                    if (maxMovement > movementThreshold) {
                        filteredFrames.push(currentFrame);
                    }
                }
                
                console.log(`Frames originales: ${frames.length}, Frames filtrados: ${filteredFrames.length}`);
                return filteredFrames;
            }           


            function stopRecording() {
                if (!isRecording) return;
                
                isRecording = false;
                if (recordingTimerElement) recordingTimerElement.style.display = 'none';
                if (mediaRecorder) {
                    mediaRecorder.onstop = () => {
                        const filteredLandmarks = filterStaticFrames(allHandLandmarks);
                        console.log("Total frames usuario:", allHandLandmarks.length);
                        console.log("Total frames referencia:", referenceLandmarks.length);

                        // Calcular similitud con los landmarks de referencia
                        if (referenceLandmarks && filteredLandmarks.length > 0) {
                            const similarityPercentage = processAllFrames(allHandLandmarks, referenceLandmarks);
                            let similitudFinal = similarityPercentage * 2;
                            console.log(`Similitud promedio: ${similarityPercentage.toFixed(1)}%`);
                            
                            // Determinar si aprobó o no
                            const isApproved = similitudFinal >= 80;

                            if (similitudFinal >= 100) {
                                similitudFinal = 100; // Limitar al 100% máximo
                            }

                            const resultMessage = isApproved 
                                ? `¡Felicidades! Tu ejecución tuvo una similitud del <b>${similitudFinal.toFixed(1)}%</b> con el gesto de referencia. <span style="color:green;">✅ APROBADO</span>`
                                : `Tu ejecución tuvo una similitud del <b>${similarityPercentage.toFixed(1)}%</b> con el gesto de referencia. <span style="color:red;">❌ NO APROBADO</span> (Se requiere 80% o más)`;
                            
                            Swal.fire({
                                title: isApproved ? '¡Aprobado!' : 'Intenta de nuevo',
                                html: resultMessage,
                                icon: isApproved ? 'success' : 'error',
                                confirmButtonText: 'Entendido',
                                customClass: {
                                    popup: 'result-popup',
                                    title: isApproved ? 'approved-title' : 'not-approved-title'
                                }
                            }).then((result) => {
                                if (isApproved) {
                                    goToNextExercise();
                                }
                            });

                            console.log(`Similitud promedio: ${similarityPercentage.toFixed(1)}% - ${isApproved ? 'APROBADO' : 'NO APROBADO'}`);
                        } else {
                            Swal.fire({
                                title: 'Error',
                                text: 'No se pudieron comparar los landmarks. Asegúrate de que se detectaron tus manos correctamente.',
                                icon: 'error'
                            });
                        }
                    };
                    mediaRecorder.stop();
                }
                if (nextButton) nextButton.disabled = false;
                if (recordButton) recordButton.disabled = false;
                if (gestoVideo) gestoVideo.play();
            }

            // Procesar resultados de detección de manos
            function onHandsResults(results) {
                // Dibujar video en canvas
                ctx.save();
                ctx.scale(-1, 1);
                ctx.translate(-canvasElement.width, 0);
                ctx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
                ctx.restore();
                
                // Solo procesar landmarks si estamos grabando
                if (isRecording && results.multiHandLandmarks) {
                    const frameHandLandmarks = [];
                    
                    // Procesar cada mano detectada
                    results.multiHandLandmarks.forEach((handLandmarks, handIndex) => {
                        const landmarks = handLandmarks.map((landmark, id) => ({
                            id: id,
                            x: landmark.x,
                            y: landmark.y,
                            z: landmark.z
                        }));
                        
                        frameHandLandmarks.push({
                            handIndex: handIndex,
                            handedness: results.multiHandedness[handIndex].label, // 'Left' o 'Right'
                            landmarks: landmarks
                        });
                    });
                    
                    allHandLandmarks.push(frameHandLandmarks);
                    
                    // Opcional: mostrar en consola (puede ser mucho output)
                    console.log(`Landmarks de manos frame ${allHandLandmarks.length}:`, frameHandLandmarks);
                }
            }

            // Procesar cada frame del video
            async function processVideoFrame() {
                if (videoElement.readyState >= 2) {
                    await hands.send({image: videoElement});
                }
                requestAnimationFrame(processVideoFrame);
            }

            function showAlert() {
                Swal.fire({
                    title: 'Instrucciones',
                    text: 'Tienes 2 segundos para realizar el ejercicio. Cuando estés listo, presiona el botón "Grabar" y cuando termines mantente quieto.',
                    icon: 'info',
                    confirmButtonText: 'Entendido'
                });
            }

            function startRecording() {
                if (isRecording) return;
                
                if (gestoVideo) gestoVideo.pause();
                
                // Reiniciar almacenamiento de landmarks
                allHandLandmarks = [];
                
                let count = 3;
                if (countdownElement) {
                    countdownElement.style.display = 'block';
                    countdownElement.textContent = count;
                }
                if (recordButton) recordButton.disabled = true;
                
                countdownInterval = setInterval(() => {
                    count--;
                    if (countdownElement) countdownElement.textContent = count;
                    
                    if (count <= 0) {
                        clearInterval(countdownInterval);
                        if (countdownElement) countdownElement.style.display = 'none';
                        actuallyStartRecording();
                    }
                }, 1000);
            }

            function actuallyStartRecording() {
                isRecording = true;
                recordedChunks = [];
                if (recordingTimerElement) {
                    recordingTimerElement.style.display = 'block';
                }
                
                try {
                    const stream = canvasElement.captureStream(25);
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
                    
                    mediaRecorder.ondataavailable = (e) => {
                        if (e.data.size > 0) {
                            recordedChunks.push(e.data);
                        }
                    };
                    
                    mediaRecorder.start(100);
                    
                    let secondsLeft = 2;
                    if (recordingTimerElement) recordingTimerElement.textContent = secondsLeft;
                    
                    recordingTimerInterval = setInterval(() => {
                        secondsLeft--;
                        if (recordingTimerElement) recordingTimerElement.textContent = secondsLeft;
                        
                        if (secondsLeft <= 0) {
                            clearInterval(recordingTimerInterval);
                            stopRecording();
                        }
                    }, 1000);
                } catch (error) {
                    console.error("Error al iniciar grabación:", error);
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo iniciar la grabación',
                        icon: 'error'
                    });
                    isRecording = false;
                    if (recordingTimerElement) recordingTimerElement.style.display = 'none';
                    if (recordButton) recordButton.disabled = false;
                    if (gestoVideo) gestoVideo.play();
                }
            }

            

            if (recordButton) {
                recordButton.addEventListener('click', startRecording);
            }
            
            // Inicializar el tracker de manos y luego la cámara
            setupHandTracking().then((h) => {
                hands = h;
                
                setTimeout(showAlert, 500);
                
                navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width: 640, 
                        height: 480,
                        facingMode: 'user' 
                    } 
                })
                .then(stream => {
                    if (videoElement) {
                        videoElement.srcObject = stream;
                        videoElement.play()
                            .then(() => {
                                processVideoFrame();
                            })
                            .catch(error => {
                                console.error("Error al reproducir video:", error);
                            });
                    }
                })
                .catch(err => {
                    console.error("Error de cámara:", err);
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo acceder a la cámara. Asegúrate de haber dado los permisos necesarios.',
                        icon: 'error'
                    });
                });
            });
        } else {
            console.error("Elemento canvas no encontrado");
        }
    } 

    else {
        console.log("Ejercicio de imagen detectado");
        // Variables globales
        let currentSimilarity = 0;
        let isGestureCorrect = false;
        let correctPoseStartTime = null;
        const REQUIRED_CORRECT_TIME = 2000; // 2 segundos para confirmar el gesto
        let hands = null;
        let camera = null;

        // Umbrales de calibración
        const calibrationValues = {
            openHandThreshold: 0.4,
            similarityThreshold: 80
        };

        // Elementos del DOM
        const videoElement = document.getElementById('inputVideo');
        const canvasElement = document.getElementById('outputCanvas');
        const canvasCtx = canvasElement.getContext('2d');
        const feedbackElement = document.getElementById('feedback');
        const noRecuerdoBtn = document.getElementById('noRecuerdoBtn');

        videoElement.style.display = 'block'; // O 'none' si prefieres que no sea visible
        videoElement.style.position = 'absolute';
        videoElement.style.opacity = '0';
        videoElement.style.width = '1px';
        videoElement.style.height = '1px';

        // Configuración inicial del canvas
        canvasElement.style.width = '100%';
        canvasElement.style.maxWidth = '400px';
        canvasElement.style.borderRadius = '10px';
        canvasElement.style.display = 'block';


        // Conexiones de la mano
        const HAND_CONNECTIONS = [
            [0, 1], [1, 2], [2, 3], [3, 4],         // Pulgar
            [0, 5], [5, 6], [6, 7], [7, 8],         // Índice
            [0, 9], [9, 10], [10, 11], [11, 12],    // Medio
            [0, 13], [13, 14], [14, 15], [15, 16],  // Anular
            [0, 17], [17, 18], [18, 19], [19, 20],  // Meñique
            [5, 9], [9, 13], [13, 17],              // Base de los dedos
            [0, 5], [0, 9], [0, 13], [0, 17]       // Conexiones adicionales
        ];

        // Inicialización
        function init() {
            // Configurar feedback
            feedbackElement.style.display = "block";
            feedbackElement.textContent = "Inicializando cámara...";
            
            // Primero cargar los landmarks de referencia si es necesario
            if (!IS_VIDEO_EXERCISE && LANDMARKS_JSON_URL) {
                loadReferenceLandmarks().then(() => {
                    // Luego iniciar la cámara
                    startCamera();
                }).catch(error => {
                    console.error("Error cargando landmarks:", error);
                    startCamera(); // Iniciar cámara igualmente
                });
            } else {
                // Iniciar cámara directamente si no hay landmarks para cargar
                startCamera();
            }
            
            // Configurar eventos
            setupEventListeners();
        }

        // Cargar landmarks de referencia
        function loadReferenceLandmarks() {
            return new Promise((resolve, reject) => {
                const correctedUrl = LANDMARKS_JSON_URL.replace('/static/static/', '/static/');
                
                fetch(correctedUrl)
                    .then(response => {
                        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
                        return response.json();
                    })
                    .then(data => {
                        referenceLandmarks = data.map(point => ({
                            x: point.x,
                            y: point.y,
                            z: point.z
                        }));
                        console.log("Referencia cargada:", referenceLandmarks);
                        resolve();
                    })
                    .catch(error => {
                        console.error("Error cargando landmarks:", error);
                        showFeedback("Error cargando gesto de referencia", false);
                        reject(error);
                    });
            });
        }

        // Configurar MediaPipe Hands
        function setupMediaPipe() {
            hands = new Hands({
                locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
            });

            hands.setOptions({
                maxNumHands: 2,
                modelComplexity: 1,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.3
            });

            hands.onResults(onResults);
        }   


        // Manejar resultados de MediaPipe
        function onResults(results) {
            // Dibujar el frame de la cámara en modo espejo
            canvasCtx.save();
            canvasCtx.scale(-1, 1);
            canvasCtx.translate(-canvasElement.width, 0);
            canvasCtx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.restore();

            // Procesar landmarks
            if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                const landmarks = results.multiHandLandmarks[0];
                
                // Ajustar landmarks para que coincidan con la imagen en modo espejo
                const mirroredLandmarks = landmarks.map(point => ({
                    x: 1 - point.x, // Invertir coordenada X
                    y: point.y,
                    z: point.z
                }));
                
                const currentLandmarks = mirroredLandmarks.map(point => ({
                    x: point.x,
                    y: point.y,
                    z: point.z
                }));
                
                if (referenceLandmarks) {
                    currentSimilarity = calculateSimilarity(referenceLandmarks, currentLandmarks);
                    isGestureCorrect = currentSimilarity > calibrationValues.similarityThreshold;
                    
                    // Dibujar landmarks (ya ajustados para modo espejo)
                    const landmarkColor = isGestureCorrect ? '#00FF00' : '#FF0000';
                    const connectionColor = isGestureCorrect ? '#00AA00' : '#AA0000';
                    
                    drawConnectors(canvasCtx, mirroredLandmarks, HAND_CONNECTIONS, {
                        color: connectionColor,
                        lineWidth: 3
                    });
                    
                    drawLandmarks(canvasCtx, mirroredLandmarks, {
                        color: landmarkColor,
                        lineWidth: 2,
                        radius: (idx) => [4, 8, 12, 16, 20, 0].includes(idx) ? 6 : 4
                    });
                    
                    handleGestureFeedback();
                }
            } else {
                correctPoseStartTime = null;
                showFeedback("Muestra tu mano en el área", false);
            }
        }

        function goToNextExercise() {
            // Detener la cámara primero
            if (camera) {
                camera.stop();
            }
            if (videoElement.srcObject) {
                videoElement.srcObject.getTracks().forEach(track => track.stop());
            }
            
            // Enviar la petición para avanzar
            fetch('/repaso/siguiente/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    error: false
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'completed') {
                    window.location.href = data.redirect_url;
                } else {
                    // Forzar recarga limpia de la página
                    window.location.href = data.redirect_url;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Recargar de todas formas si hay error
                window.location.href = '/repaso/';
            });
        }


        function handleGestureFeedback() {
            if (isGestureCorrect) {
                if (correctPoseStartTime === null) {
                    correctPoseStartTime = Date.now();
                } else {
                    const elapsedTime = Date.now() - correctPoseStartTime;
                    const remainingTime = REQUIRED_CORRECT_TIME - elapsedTime;
                    
                    if (remainingTime > 0) {
                        showFeedback(`✓ Mantén la pose (${Math.ceil(remainingTime/1000)}s)`, true);
                    } else {
                        showFeedback("✓ ¡Correcto!", true);
                        goToNextExercise();
                        
                        // Usar CURRENT_WORD_ID en lugar de currentWordId
                        // fetch('/repaso/siguiente/', {
                        //     method: 'POST',
                        //     headers: {
                        //         'Content-Type': 'application/x-www-form-urlencoded',
                        //         'X-CSRFToken': getCookie('csrftoken')
                        //     },
                        //     body: `palabra_id=${CURRENT_WORD_ID}`
                        // }).then(() => {
                        //     window.location.href = "/repaso/";
                        // }).catch(error => {
                        //     console.error('Error:', error);
                        //     window.location.href = "/repaso/";
                        // });
                    }
                }
            } else {
                correctPoseStartTime = null;
                showFeedback(`✗ Ajusta tu gesto (${currentSimilarity.toFixed(0)}%)`, false);
            }
        }
        // Función auxiliar para obtener cookies


        // Modificar la función calculateSimilarity para usar landmarks normalizados
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
                similarity *= 0.6; // Reducción más agresiva
            }
            
            return similarity;
        }

        // Detectar mano demasiado abierta
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
            return averageDistance > calibrationValues.openHandThreshold;
        }


        // Mostrar feedback visual
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

        // Configurar eventos
        function setupEventListeners() {
            // Iniciar cámara cuando el DOM esté listo
            document.addEventListener('DOMContentLoaded', startCamera);

            //Configuracion elementos del video
            videoElement.autoplay = true;
            // videoElement.style.transform = "scaleX(-1)";
            canvasElement.style.width = '100%';
            canvasElement.style.maxWidth = '400px';
            // canvasElement.style.transform = "scaleX(-1)";
            canvasElement.style.borderRadius = '10px';

            
                        // Botón "No lo recuerdo"
            if (noRecuerdoBtn) {
                noRecuerdoBtn.addEventListener('click', () => {
                    Swal.fire({
                        title: '¿No recuerdas este gesto?',
                        text: 'Se registrará como error y pasaremos al siguiente ejercicio',
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#3085d6',
                        cancelButtonColor: '#d33',
                        confirmButtonText: 'Sí, no lo recuerdo',
                        cancelButtonText: 'Cancelar'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            // Enviar petición al servidor
                            fetch('/repaso/no-recuerdo/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: `palabra_id=${CURRENT_WORD_ID}`
                            })
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Error en la respuesta del servidor');
                                }
                                return response.json();
                            })
                            .then(data => {
                                if (data.status === 'completed') {
                                    window.location.href = FINISH_URL;
                                } else {
                                    window.location.href = "/repaso/"; // Redirigir a la misma URL que los otros casos
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                Swal.fire('Error', 'Hubo un problema al registrar tu respuesta', 'error');
                            });
                        }
                    });
                });
            }
            
            
        }

        // Iniciar cámara
        function startCamera() {
            navigator.mediaDevices.getUserMedia({ 
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                } 
            })
            .then(stream => {
                videoElement.srcObject = stream;
                
                return new Promise((resolve) => {
                    videoElement.onloadedmetadata = () => {
                        videoElement.play();
                        resolve();
                    };
                });
            })
            .then(() => {
                // Configurar canvas con las dimensiones reales del video
                canvasElement.width = videoElement.videoWidth;
                canvasElement.height = videoElement.videoHeight;
                
                console.log(`Dimensiones del video: ${videoElement.videoWidth}x${videoElement.videoHeight}`);
                
                // Iniciar MediaPipe Hands si no está inicializado
                if (!hands) {
                    setupMediaPipe();
                }
                
                // Iniciar el procesamiento de frames
                camera = new Camera(videoElement, {
                    onFrame: async () => {
                        try {
                            await hands.send({ image: videoElement });
                        } catch (error) {
                            console.error("Error procesando frame:", error);
                        }
                    },
                    width: videoElement.videoWidth,
                    height: videoElement.videoHeight
                });
                camera.start();
            })
            .catch(err => {
                console.error("Error de cámara:", err);
                showFeedback("Error al acceder a la cámara", false);
                Swal.fire({
                    title: 'Error de cámara',
                    text: 'No se pudo acceder a la cámara. Por favor, asegúrate de haber dado los permisos necesarios.',
                    icon: 'error',
                    confirmButtonText: 'Entendido'
                });
            });
        }


        // Animación CSS para feedback
        const style = document.createElement('style');
        style.textContent = `
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        `;
        document.head.appendChild(style);

        // Inicializar la aplicación
        init();
    }


    // Función auxiliar para obtener cookies
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
    

});