
from flask import Flask, render_template, jsonify
import random
from datetime import datetime

app = Flask(__name__)

# --------------------------------
# SIMULATED SHELTER ENERGY SYSTEM
# --------------------------------

system = {
    "solar": 8.4,
    "battery": 78.0,
    "load": 5.2,
    "fuel": 82.0,
    "grid": False,
    "generator": False
}

BATTERY_CAPACITY = 120       # kWh
GENERATOR_TANK = 100         # litres
GENERATOR_CONSUMPTION = 2.2  # litres/hour

# Critical electrical loads (kW)
critical_loads = {
    "Medical Equipment": 2.0,
    "Emergency Lighting": 1.0,
    "Communication": 0.5,
    "Water Purification": 1.5
}


def update_simulation():

    # Simulate changing weather and electricity demand
    system["solar"] = round(
        random.uniform(2.0, 10.0), 2
    )

    system["load"] = round(
        random.uniform(4.0, 9.0), 2
    )

    # Simulate battery movement over a 5-minute interval
    net_energy = (
        system["solar"] - system["load"]
    ) * (5 / 60)

    battery_change = (
        net_energy / BATTERY_CAPACITY
    ) * 100

    system["battery"] = round(
        max(0, min(100, system["battery"] + battery_change)), 2
    )

    # Simulate gradual generator fuel consumption
    if system["generator"]:
        system["fuel"] = max(
            0, system["fuel"] - 0.18
        )

    # Automatic generator recommendation
    if system["battery"] < 25:
        system["generator"] = True

    elif system["battery"] > 70:
        system["generator"] = False


def get_backup_hours():

    critical_load = sum(critical_loads.values())

    battery_energy = (
        system["battery"] / 100
    ) * BATTERY_CAPACITY

    battery_hours = battery_energy / critical_load

    fuel_litres = (
        system["fuel"] / 100
    ) * GENERATOR_TANK

    generator_hours = (
        fuel_litres / GENERATOR_CONSUMPTION
    )

    # Conservative estimate:
    # Battery first, generator fuel afterwards.
    return round(
        battery_hours + generator_hours, 1
    )


def get_recommendations():

    recommendations = []

    if system["battery"] < 20:
        recommendations.append(
            "CRITICAL: Battery reserve is low. "
            "Prioritise essential loads."
        )

    elif system["battery"] < 40:
        recommendations.append(
            "WARNING: Conserve battery power "
            "and prepare generator backup."
        )

    else:
        recommendations.append(
            "Battery reserve is currently healthy."
        )

    if system["solar"] < 3:
        recommendations.append(
            "Low solar generation. Monitor "
            "battery discharge and weather conditions."
        )

    if system["fuel"] < 20:
        recommendations.append(
            "WARNING: Generator fuel is low. "
            "Arrange fuel replenishment."
        )

    if system["generator"]:
        recommendations.append(
            "Backup generator is activated."
        )

    if not system["grid"]:
        recommendations.append(
            "Grid outage detected. Operating in "
            "islanded emergency mode."
        )

    return recommendations


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/dashboard")
def dashboard():

    update_simulation()

    return jsonify({
        "solar": system["solar"],
        "battery": system["battery"],
        "load": system["load"],
        "fuel": round(system["fuel"], 1),
        "grid": system["grid"],
        "generator": system["generator"],
        "backup_hours": get_backup_hours(),
        "critical_load": sum(critical_loads.values()),
        "recommendations": get_recommendations(),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })


@app.route("/api/emergency")
def emergency():

    system["grid"] = False

    return jsonify({
        "message": "Emergency mode activated",
        "grid": system["grid"]
    })


@app.route("/api/grid/restore")
def restore_grid():

    system["grid"] = True

    return jsonify({
        "message": "Grid connection restored",
        "grid": system["grid"]
    })


if __name__ == "__main__":
    app.run(debug=True)
