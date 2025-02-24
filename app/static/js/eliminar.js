document.addEventListener("DOMContentLoaded", function () {
    // Seleccionamos todos los botones con la clase 'btn-eliminar'
    document.querySelectorAll(".btn-eliminar").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();  // Evita cualquier acción predeterminada

            const id = this.getAttribute("data-id");  // Obtiene el ID desde el botón
            const url = this.getAttribute("data-url"); // Obtiene la URL de eliminación

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
        });
    });
});
