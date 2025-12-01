from flask import Flask, jsonify

app = Flask(__name__)

# ------------------------
# CAMPUS PARKING DATA
# ------------------------

parking_info = {
    "title": "Fairfield University Campus Parking Map",

    "visitor_lots": ["C-1", "C-2", "C-3", "K-1"],

    "zones": {
        "Blue": {
            "label": "Blue Zone",
            "lots": [
                "A-1", "A-2", "A-3",
                "C-4", "C-5",
                "D-1",
                "G-1", "G-2", "G-3",
                "J-1", "J-2", "J-3",
                "K-1", "K-2", "K-3",
                "O-1",
            ],
        },
        "Dark Blue": {
            "label": "Dark Blue Zone",
            "lots": ["M-1"]
        },
        "Red": {
            "label": "Red Zone",
            "lots": ["F-1", "F-2"]
        },
        "Yellow": {
            "label": "Yellow Zone",
            "lots": ["H-2", "I-1"]
        },
        "Purple": {
            "label": "Purple Zone",
            "lots": ["M-2", "G-2"]
        },
        "Gold": {
            "label": "Gold Zone",
            "lots": ["N-1", "N-2"]
        },
        "Gray": {
            "label": "Gray Zone",
            "lots": ["H-1", "H-2"]
        },
        "Green": {
            "label": "Green Zone",
            "lots": ["B-1", "B-2", "B-3", "E-1", "G-3", "H-1", "H-2"],
        }
    },

    "walking_times": [
        {"description": "Dolan Campus → BCC", "minutes": 8},
        {"description": "BCC → Dolan School of Business", "minutes": 7},
        {"description": "Townhouses → BCC", "minutes": 8},
        {"description": "Village → BCC", "minutes": 4},
        {"description": "Regis Hall → RecPlex", "minutes": 4},
        {"description": "Dolan Campus → Dolan School of Business", "minutes": 15},
    ],
}

# -------- helper index: lot -> zones --------

lot_index = {}
for zone_name, z in parking_info["zones"].items():
    for lot in z["lots"]:
        lot_index.setdefault(lot, []).append(zone_name)

# ------------------------
# API ROUTES
# ------------------------

@app.get("/")
def home():
    return jsonify({"message": "Fairfield Parking API working!", "endpoints": [
        "/zones",
        "/zones/<zone_name>",
        "/lots/<lot_id>",
        "/walking-times"
    ]})

@app.get("/zones")
def get_zones():
    return jsonify(parking_info["zones"])

@app.get("/zones/<zone_name>")
def get_zone(zone_name):
    for name, z in parking_info["zones"].items():
        if name.lower() == zone_name.lower():
            return jsonify(z)
    return jsonify({"error": "Zone not found"}), 404

@app.get("/lots/<lot_id>")
def get_lot(lot_id):
    lot_id = lot_id.upper()
    if lot_id not in lot_index:
        return jsonify({"error": "Lot not found"}), 404

    return jsonify({
        "lot": lot_id,
        "zones": lot_index[lot_id],
        "is_visitor_lot": lot_id in parking_info["visitor_lots"]
    })

@app.get("/walking-times")
def get_walking():
    return jsonify(parking_info["walking_times"])

# ------------------------
# RUN APPLICATION
# ------------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8500, debug=True)


