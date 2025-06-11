document.addEventListener("DOMContentLoaded", function () {
    const notificaciones = document.querySelector(".banners");
    const items = document.querySelectorAll(".ejercicio");
    const videoElement = document.getElementById("ejercicioVideo");
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'video-loading';
    loadingMessage.textContent = 'Cargando ejercicio...';
    videoElement.parentNode.appendChild(loadingMessage);

    const videoUrls = [
        "https://manito-bucket1.s3.amazonaws.com/calentamiento/abrirCerrar.mp4",
        "https://manito-bucket1.s3.amazonaws.com/calentamiento/munecas.mp4",
        "https://manito-bucket1.s3.amazonaws.com/calentamiento/circulosAfuera.mp4",
        "https://manito-bucket1.s3.amazonaws.com/calentamiento/circulosAdentro.mp4",
        "https://manito-bucket1.s3.amazonaws.com/calentamiento/dedoDedo.mp4",
        "https://manito-bucket1.s3.amazonaws.com/calentamiento/dedosUp.mp4",
        "https://manito-bucket1.s3.amazonaws.com/calentamiento/sacudir.mp4"
    ];

    let index = 0;
    let intervalo;

    function iniciarCarrusel() {
        loadingMessage.style.display = 'block';
        videoElement.style.display = 'none';
        cargarVideo(index);
        intervalo = setInterval(moverCarrusel, 10000);
    }

    function cargarVideo(indice) {
        if (indice >= videoUrls.length) return;

        videoElement.onloadeddata = null;
        videoElement.onerror = null;
        
        videoElement.src = videoUrls[indice];
        videoElement.load();

        videoElement.onloadeddata = function() {
            loadingMessage.style.display = 'none';
            videoElement.style.display = 'block';
            videoElement.play().catch(e => {
                console.error("Error al reproducir:", e);
                loadingMessage.innerHTML = 'Click para comenzar ejercicio';
                loadingMessage.style.display = 'block';
                loadingMessage.onclick = () => {
                    videoElement.play();
                    loadingMessage.style.display = 'none';
                };
            });
        };

        videoElement.onerror = function() {
            console.error("Error cargando video:", videoUrls[indice]);
            loadingMessage.innerHTML = `Error cargando video (${indice+1}/${videoUrls.length})<br>Intenta recargar la página`;
            loadingMessage.style.display = 'block';
            
            setTimeout(() => {
                if (index < videoUrls.length - 1) {
                    index++;
                    cargarVideo(index);
                }
            }, 2000);
        };
    }

    function moverCarrusel() {
        items.forEach(item => item.style.fontWeight = "normal");
        
        if (index >= items.length - 1) {
            clearInterval(intervalo);
            mostrarFelicitaciones();
            return;
        }

        index++;
        items[index].style.fontWeight = "bold";
        
        let desplazamiento = -index * 41;
        notificaciones.style.transform = `translateY(${desplazamiento}px)`;
        
        cargarVideo(index);
    }

    function mostrarFelicitaciones() {
        videoElement.pause();
        Swal.fire({
            title: "¡Felicidades!",
            text: "Has completado los ejercicios 🎉",
            icon: "success",
            confirmButtonText: "Aceptar"
        }).then(() => {
            window.location.href = "/inicio/"; 
        });
    }

    items.forEach((item, i) => {
        item.addEventListener('click', () => {
            clearInterval(intervalo);
            index = i;
            items.forEach(it => it.style.fontWeight = "normal");
            item.style.fontWeight = "bold";
            notificaciones.style.transform = `translateY(${-index * 41}px)`;
            cargarVideo(index);
            intervalo = setInterval(moverCarrusel, 10000);
        });
    });

    iniciarCarrusel();
});