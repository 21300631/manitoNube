document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('form').addEventListener('submit', function (e) {
        const archivo = document.getElementById('media').files[0];
        const edadUsuario = parseInt(document.getElementById('user-edad').value);
        if (archivo) {
            const tipo = archivo.type;
            const tamaño = archivo.size;

            // Validar si es menor de edad y quiere subir media
            if (edadUsuario < 18) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Acceso restringido',
                    text: 'Debes ser mayor de 18 años para subir contenido multimedia.',
                });
                return; // detener el envío
            }

            // Validar tamaño de imagen
            if (tipo.startsWith('image/') && tamaño > 500 * 1024) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Imagen demasiado grande',
                    text: 'La imagen debe ser menor a 500KB.',
                });
                return;
            }

            // Validar tamaño de video
            if (tipo.startsWith('video/') && tamaño > 10 * 1024 * 1024) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Video demasiado grande',
                    text: 'El video debe ser menor a 10MB.',
                });
                return;
            }

            // Validar tipo de archivo
            if (!tipo.startsWith('image/') && !tipo.startsWith('video/')) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Tipo de archivo no permitido',
                    text: 'Solo se permiten imágenes o videos.',
                });
                return;
            }
        }

    });
});

const edadUsuario = parseInt(document.getElementById('user-edad').value);
console.log("Edad del usuario:", edadUsuario);