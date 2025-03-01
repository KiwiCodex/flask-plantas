document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("btn-simular").addEventListener("click", generarNuevosValores);
});

function generarNuevosValores() {
    const moduloId = document.getElementById("btn-simular").getAttribute("data-modulo-id");

    fetch(`/modulos/simulacion_ajax/${moduloId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            const valores = data.valores_simulados;
            const estadoPlanta = document.getElementById("estado-planta");

            for (let variable in valores) {
                let valor = valores[variable];

                let estadoCelda = document.getElementById(`estado-${variable}`);
                let alertaCelda = document.getElementById(`alerta-${variable}`);
                let valorCelda = estadoCelda ? estadoCelda.closest("tr").querySelector(".valor") : null;

                if (!estadoCelda || !alertaCelda || !valorCelda) {
                    console.error(`No se encontró la celda para la variable: ${variable}`);
                    continue;
                }

                let min = parseFloat(estadoCelda.dataset.min);
                let max = parseFloat(estadoCelda.dataset.max);

                if (isNaN(min) || isNaN(max)) {
                    console.error(`Valores min/max no encontrados para ${variable}`);
                    continue;
                }

                let difMin = min - valor;
                let difMax = valor - max;

                let estadoTexto = "🟢 Dentro del rango ideal";
                if (difMax > 0 && difMax <= 4) {
                    estadoTexto = `🟡 Exceso de ${variable} +${difMax.toFixed(1)}`;
                } else if (difMax > 4 && difMax <= 9) {
                    estadoTexto = `🟠 Exceso de ${variable} +${difMax.toFixed(1)}`;
                } else if (difMax >= 10) {
                    estadoTexto = `🔴 Exceso de ${variable} +${difMax.toFixed(1)}`;
                } else if (difMin > 0 && difMin <= 4) {
                    estadoTexto = `🟡 Falta de ${variable} -${difMin.toFixed(1)}`;
                } else if (difMin > 4 && difMin <= 9) {
                    estadoTexto = `🟠 Falta de ${variable} -${difMin.toFixed(1)}`;
                } else if (difMin >= 10) {
                    estadoTexto = `🔴 Falta de ${variable} -${difMin.toFixed(1)}`;
                }

                let alertaTexto = "✅ Ok";
                if (valor < min || valor > max) {
                    alertaTexto = "⚠️ Alerta";
                } else if (Math.abs(valor - min) <= 2 || Math.abs(valor - max) <= 2) {
                    alertaTexto = "⚠️ Precaución";
                }

                // Actualizar valores en la tabla
                estadoCelda.innerHTML = estadoTexto;
                alertaCelda.innerHTML = alertaTexto;
                valorCelda.innerHTML = `<strong>${valor.toFixed(1)}</strong>`;
            }

            // Actualizar el estado de la planta
            estadoPlanta.className = `box ${data.estado_color}`;
            let emoji = { green: "😊", yellow: "😐", orange: "😟", red: "😭" }[data.estado_color];
            let texto = { green: "¡Todo bien!", yellow: "En cuidado", orange: "Preocupado", red: "Necesito ayuda" }[data.estado_color];
            estadoPlanta.innerHTML = `<span class="emoji">${emoji}</span><span class="texto">${texto}</span>`;
        })
        .catch(error => console.error("Error al obtener nuevos valores:", error));
}


document.addEventListener("DOMContentLoaded", function () {
    let botonSimular = document.getElementById("btn-simular");
    console.log("Verificación de botón:", botonSimular);

    if (botonSimular) {
        botonSimular.addEventListener("click", function () {
            console.log("Botón clickeado");
            generarNuevosValores();
        });
    } else {
        console.error("El botón no se encontró en el DOM.");
    }
});

