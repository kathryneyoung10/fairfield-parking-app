from flask import Flask, jsonify

app = Flask(__name__)

# ------------------------
# DATA FROM CAMPUS MAP
# ------------------------

parking_info = {
    "title": "Fairfield University Campus Parking Map",

    "decal_instruction": (
        "PLEASE ADHERE DECAL TO THE LOWER LEFT-HAND CORNER OF "
        "THE WINDSHIELD (Driver’s side)."
    ),

    "visitor_policy": (
        "Visitors may park in lots C-1, C-2, C-3, and K-1, or they may obtain "
        "a visitor pass for additional parking."
    ),

    "faculty_staff_policy": (
        "Faculty and staff are requested to park in blue zone areas when "
        "possible. However, the University reserves the right to restrict "
        "lots when necessary."
    ),

    "liability_notice": "Parking at Fairfield University is at your own risk.",

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
            "notes": "Primary blue zone parking."
        },
        "Dark Blue": {
            "label": "Dark Blue Zone",
            "lots": ["M-1"],
            "notes": ""
        },
        "Red": {
            "label": "Red Zone",
            "lots": ["F-1", "F-2"],
            "notes": ""
        },
        "Yellow": {
            "label": "Yellow Zone",
            "lots": ["H-2", "I-1"],
            "notes": ""
        },
        "Purple": {
            "label": "Purple Zone",
            "lots": ["M-2", "G-2"],
            "notes": ""
        },
        "Gold": {
            "label": "Gold Zone",
            "lots": ["N-1", "N-2"],
            "notes": ""
        },
        "Gray": {
            "label": "Gray Zone",
            "lots": ["H-1", "H-2"],
            "notes": ""
        },
        "Green": {
            "label": "Green Zone",
            "lots": ["B-1", "B-2", "B-3", "E-1", "G-3", "H-1", "H-2"],
            "notes": (
                "Green zone. Additional parking from 4 p.m. through 7 a.m. "
                "includes lots M-1, M-2, and all blue lots except A-1, C-3, and G-2."
            ),
        },
    },

    "visitor_lots": ["C-1", "C-2", "C-3", "K-1"],

    "after_hours_parking": {
        "time_window": "4 p.m. – 7 a.m.",
        "includes": {
            "extra_lots": ["M-1", "M-2"],
            "all_blue_lots": True,
            "excluded_lots": ["A-1", "C-3", "G-2"],
        },
        "description": (
            "Additional parking from 4 p.m. through 7 a.m. includes lots M-1, "
            "M-2, and all blue lots except A-1, C-3, and G-2."
        ),
    },

    "walking_times": [
        {
            "description": "Dolan Campus to Barone Campus Center (BCC)",
            "minutes": 8,
        },
        {
            "description": "BCC to Dolan School of Business",
            "minutes": 7,
        },
        {
            "description": "Townhouses to BCC",
            "minutes": 8,
        },
        {
            "description": "Village to BCC",
            "minutes": 4,
        },
        {
            "description": "Regis Hall to RecPlex",
            "minutes": 4,
        },
        {
            "description": "Dolan Campus to Dolan School of Business",
            "minutes": 15,
        },
    ],

    "friday_parking": {
        "morning_lots": ["G-3", "H-2"],
        "afternoon_lots": ["D-1", "E-1"],
        "shuttle_note": (
            "Shuttle service from the above parking lots to the Barone Campus "
            "Center building will be available on Friday."
        ),
    },

    "buildings": [
        "Kelley Center",
        "Walsh Athletic Center",
        "Library",
        "Barone Campus Center",
        "Canisius Hall",
        "Regis Hall",
        "Nursing",
        "Quick Center",
        "The Village",
        "Dolan School of Business",
        "#42 Bellarmine Road",
        "Southwell Hall",
        "Bellarmine Hall",
        "Fairfield Prep",
        "Rec Plex",
        "Alumni Hall",
        "Jogues Hall",
        "Loyola Hall",
        "Alumni House",
        "McAuliffe Hall",
        "Townhouse Complex",
        "Dolan Campus",
    ],
}

# -------- helper index: lot -> zones --------

lot_index = {}
for zone_name, zone_data in parking_info["zones"].items():
    for lot in zone_data["lots"]:
        lot_index.setdefault(lot, []).append(zone_name)


# ------------------------
# API ENDPOINTS
# ------------------------

@app.get("/")
def root():
    return jsonify({
        "title": parking_info["title"],
        "endpoints": {
            "/info": "Full parking info (zones, rules, walking times, etc.)",
            "/zones": "All zones with lots.",
            "/zones/<zone_name>": "One zone by name, e.g. Blue, Green.",
            "/lots/<lot_id>": "Details for a specific lot, e.g. A-1.",
            "/walking-times": "Walking-time table.",
            "/after-hours": "After-hours parking rules.",
            "/friday-parking": "Friday parking + shuttle info.",
            "/buildings": "List of labeled buildings from the map.",
        }
    })


@app.get("/info")
def get_info():
    return jsonify(parking_info)


@app.get("/zones")
def get_zones():
    zones_summary = {
        name: {
            "label": data["label"],
            "lots": data["lots"],
            "notes": data.get("notes", "")
        }
        for name, data in parking_info["zones"].items()
    }
    return jsonify(zones_summary)


@app.get("/zones/<zone_name>")
def get_zone(zone_name: str):
    normalized = zone_name.replace("%20", " ").strip().lower()
    for name, data in parking_info["zones"].items():
        if name.lower() == normalized:
            payload = data.copy()
            payload["name"] = name
            return jsonify(payload)
    return jsonify({"error": "Zone not found"}), 404


@app.get("/lots/<lot_id>")
def get_lot(lot_id: str):
    lot_id = lot_id.upper()
    zones = lot_index.get(lot_id)
    if not zones:
        return jsonify({"error": "Lot not found"}), 404

    zone_details = []
    for z in zones:
        zd = parking_info["zones"][z]
        zone_details.append({
            "zone_key": z,
            "label": zd["label"],
            "notes": zd.get("notes", ""),
        })

    return jsonify({
        "lot": lot_id,
        "zones": zones,
        "zone_details": zone_details,
        "is_visitor_lot": lot_id in parking_info["visitor_lots"],
    })


@app.get("/walking-times")
def get_walking_times():
    return jsonify(parking_info["walking_times"])


@app.get("/after-hours")
def get_after_hours():
    # Also compute the actual list of lots allowed after hours
    blue_lots = set(parking_info["zones"]["Blue"]["lots"])
    excluded = set(parking_info["after_hours_parking"]["includes"]["excluded_lots"])
    allowed_blue = sorted(list(blue_lots - ex
