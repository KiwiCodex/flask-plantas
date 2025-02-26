document.addEventListener("DOMContentLoaded", function () {
    const buscador = document.getElementById("buscador");
    const filas = document.querySelectorAll("tbody tr");

    buscador.addEventListener("input", function () {
        const filtro = buscador.value.toLowerCase();
        
        filas.forEach(fila => {
            const textoFila = fila.textContent.toLowerCase();
            fila.style.display = textoFila.includes(filtro) ? "" : "none";
        });

        // Reasignar eventos a los botones de eliminar después de filtrar
        asignarEventosEliminar();
    });

    function asignarEventosEliminar() {
        document.querySelectorAll(".btn-eliminar").forEach(button => {
            button.removeEventListener("click", eliminarRegistro); // Evita duplicar eventos
            button.addEventListener("click", eliminarRegistro);
        });
    }

    function eliminarRegistro(event) {
        event.preventDefault();
        const id = this.getAttribute("data-id");
        const url = this.getAttribute("data-url");

        Swal.fire({
            title: "¿Estás seguro?",
            text: "No podrás revertir esta acción",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar"
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(url, { method: "POST" })
                    .then(response => {
                        if (response.ok) {
                            Swal.fire("Eliminado", "El registro ha sido eliminado.", "success")
                                .then(() => location.reload());
                        } else {
                            Swal.fire("Error", "Hubo un problema al eliminar el registro.", "error");
                        }
                    });
            }
        });
    }

    // Inicializar eventos al cargar la página
    asignarEventosEliminar();
});
