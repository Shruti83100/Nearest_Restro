import pandas as pd

# -----------------------------
# Load datasets
# -----------------------------
bus_df = pd.read_excel("Bus_Route.xlsx")
restro_df = pd.read_excel("Restro.xlsx")
area_df = pd.read_excel("area_proximity.csv.xlsx")

# -----------------------------
# User Input
# -----------------------------
current_location = input("Enter your current area: ").strip()

# -----------------------------
# STEP 1: Find nearby areas sorted by proximity
# -----------------------------
nearby = area_df[
    (area_df["Area_min"].str.lower() == current_location.lower()) |
    (area_df["Area_max"].str.lower() == current_location.lower())
].copy()


if nearby.empty:
    print("❌ No proximity data found for this area.")
    exit()

# Identify the "other" area and keep proximity score
nearby["Nearby_Area"] = nearby.apply(
    lambda row: row["Area_max"] if row["Area_min"].lower() == current_location.lower()
    else row["Area_min"], axis=1
)

# Sort by proximity (nearest first)
nearby_sorted = nearby.sort_values("Proximity_Score")

# Take top N nearest areas (you can change this)
nearest_areas = nearby_sorted["Nearby_Area"].head(3).tolist()

# Include current area itself
nearest_areas.insert(0, current_location)

# -----------------------------
# STEP 2: Get restaurants ONLY from nearest areas
# -----------------------------
nearest_restaurants = restro_df[
    restro_df["Area"].str.lower().isin([a.lower() for a in nearest_areas])
]

if nearest_restaurants.empty:
    print("❌ No restaurants found near your location.")
    exit()

# -----------------------------
# STEP 3: Bus stops from current area
# -----------------------------
source_stops = bus_df[
    bus_df["area"].str.lower() == current_location.lower()
]

if source_stops.empty:
    print("❌ No bus stops found in your area.")
    exit()

# -----------------------------
# OUTPUT
# -----------------------------
print("\n🚌 NEAREST RESTAURANTS & BUS ROUTES\n")

for _, rest in nearest_restaurants.iterrows():
    print(f"🍽️ Restaurant Name : {rest['Name']}")
    print(f"📍 Area            : {rest['Area']}")

    dest_stops = bus_df[
        bus_df["area"].str.lower() == rest["Area"].lower()
    ]

    if dest_stops.empty:
        print("🚌 Bus Options     : No direct bus")
        print("-" * 45)
        continue

    common_buses = set(source_stops["bus_no"]).intersection(
        set(dest_stops["bus_no"])
    )

    if not common_buses:
        print("🚌 Bus Options     : No direct bus")
        print("-" * 45)
        continue

    for bus in common_buses:
        board = source_stops[source_stops["bus_no"] == bus].iloc[0]
        drop = dest_stops[dest_stops["bus_no"] == bus].iloc[0]

        print(f"🚌 Bus Number      : {bus}")
        print(f"🚏 Boarding Stop  : {board['stop_name']}")
        print(f"🚏 Drop Stop      : {drop['stop_name']}")

    print("-" * 45)
