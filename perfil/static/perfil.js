document.getElementById('id_nueva_imagen').addEventListener('change', function(e) {
    // Mostrar el botón de guardar
    document.querySelector('.guardar-cambios-btn').classList.add('visible');
    
    // Mostrar vista previa de la imagen seleccionada
    if (e.target.files && e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = function(event) {
            document.getElementById('preview-imagen').src = event.target.result;
        };
        reader.readAsDataURL(e.target.files[0]);
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("darkModeToggle");
    
    // 1. Primero establecer el estado inicial DESACTIVADO explícitamente
    toggle.checked = false;
    document.body.classList.remove("dark");
    document.body.classList.add("light");
    
    // 2. Luego verificar localStorage (sobrescribe el estado inicial si existe)
    const localStorageTheme = localStorage.getItem('darkMode');
    if (localStorageTheme !== null) {
        const isDark = localStorageTheme === 'true';
        toggle.checked = isDark;
        document.body.classList.toggle("dark", isDark);
        document.body.classList.toggle("light", !isDark);
    }
    
    // 3. Finalmente consultar al backend (sobrescribe ambos anteriores)
    fetch("/perfil/obtener-tema/")  // Necesitarás crear este endpoint
        .then(response => response.json())
        .then(data => {
            const isDark = data.theme === "dark";
            toggle.checked = isDark;
            document.body.classList.toggle("dark", isDark);
            document.body.classList.toggle("light", !isDark);
            localStorage.setItem('darkMode', isDark);
        })
        .catch(error => {
            console.error("Error al obtener tema:", error);
            // Mantener los valores de localStorage si falla la solicitud
        });

    // Manejar cambios en el toggle
    toggle.addEventListener("change", function () {
        const isDark = toggle.checked;
        
        // Actualizar UI inmediatamente
        document.body.classList.toggle("dark", isDark);
        document.body.classList.toggle("light", !isDark);
        
        // Guardar en localStorage
        localStorage.setItem('darkMode', isDark);
        
        // Enviar al backend
        fetch("/perfil/cambiar-tema/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ theme: isDark ? "dark" : "light" }),
        });
    });

    // CSRF helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});