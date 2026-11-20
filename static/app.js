
let gridDisconnected = true;

let history = {
    labels: [],
    solar: [],
    load: []
};

let energyChart;

function setupChart() {
    const ctx = document.getElementById("energyChart");

    energyChart = new Chart(ctx, {
        type: "line",

        data: {
            labels: history.labels,

            datasets: [
                {
                    label: "Solar Generation (kW)",
                    data: history.solar,
                    borderColor: "#e8ad35",
                    backgroundColor: "rgba(232,173,53,0.1)",
                    fill: true,
                    tension: 0.35
                },
                {
                    label: "Consumption (kW)",
                    data: history.load,
                    borderColor: "#27875a",
                    backgroundColor: "rgba(39,135,90,0.1)",
                    fill: true,
                    tension: 0.35
                }
            ]
        },

        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: false,

            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}


async function updateDashboard() {
    try {
        const response = await fetch("/api/dashboard");

        if (!response.ok) {
            throw new Error("API unavailable");
        }

        const data = await response.json();

        document.getElementById("solar").textContent =
            data.solar + " kW";

        document.getElementById("battery").textContent =
            data.battery + "%";

        document.getElementById("load").textContent =
            data.load + " kW";

        document.getElementById("fuel").textContent =
            data.fuel + "%";

        document.getElementById("backup").textContent =
            data.backup_hours;

        document.getElementById("critical").textContent =
            data.critical_load + " kW";

        document.getElementById("battery-bar").style.width =
            data.battery + "%";

        document.getElementById("generator-status").textContent =
            data.generator ? "Generator Active" : "Generator Standby";

        document.getElementById("generator-label").textContent =
            data.generator ? "Active" : "Standby";

        document.getElementById("grid-label").textContent =
            data.grid ? "Connected" : "Disconnected";

        document.getElementById("grid-status").textContent =
            data.grid
                ? "Normal grid supply restored."
                : "Shelter operating on independent energy sources.";

        document.getElementById("emergency-button").textContent =
            data.grid ? "Simulate Grid Failure" : "Restore Grid";

        document.getElementById("emergency-button").style.background =
            data.grid ? "#bd513d" : "#286044";

        document.getElementById("clock").textContent =
            data.timestamp;

        document.getElementById("updated").textContent =
            "Last updated: " + data.timestamp;

        gridDisconnected = !data.grid;

        // Update energy graph
        history.labels.push(data.timestamp);
        history.solar.push(data.solar);
        history.load.push(data.load);

        if (history.labels.length > 12) {
            history.labels.shift();
            history.solar.shift();
            history.load.shift();
        }

        energyChart.update();

        // Display recommendations
        const container =
            document.getElementById("recommendations");

        container.innerHTML = "";

        data.recommendations.forEach(message => {
            const item = document.createElement("div");

            item.className = "recommendation";

            if (
                message.includes("CRITICAL")
            ) {
                item.classList.add("critical");
            } else if (
                message.includes("WARNING")
            ) {
                item.classList.add("warning");
            }

            item.textContent = message;

            container.appendChild(item);
        });

        document.getElementById("connection").textContent =
            "● SYSTEM ONLINE";

    } catch (error) {
        document.getElementById("connection").textContent =
            "● CONNECTION ERROR";

        document.getElementById("connection").style.color =
            "#d94d3f";

        console.error(error);
    }
}


async function toggleEmergency() {

    const endpoint = gridDisconnected
        ? "/api/grid/restore"
        : "/api/emergency";

    try {
        const response = await fetch(endpoint);

        if (!response.ok) {
            throw new Error("Could not change grid status");
        }

        await updateDashboard();

    } catch (error) {
        console.error(error);
        alert("Unable to update grid status.");
    }
}


// Start dashboard
setupChart();
updateDashboard();

// Refresh readings every 3 seconds
setInterval(updateDashboard, 3000);
