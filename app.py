import streamlit as st
import pandas as pd

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Bus Route to Nearest Restaurants",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Bus Route Finder to Nearest Restaurants")
st.write("Enter your current area to find nearby restaurants and the bus routes you can take.")

# -----------------------------
# Load datasets
# -----------------------------
@st.cache_data
def load_data():
    bus_df = pd.read_excel("Bus_Route.xlsx")
    restro_df = pd.read_excel("Restro.xlsx")
    area_df = pd.read_excel("area_proximity.csv.xlsx")
    return bus_df, restro_df, area_df

bus_df, restro_df, area_df = load_data()

# -----------------------------
# User input
# -----------------------------
current_location = st.text_input("📍 Enter your current area")

# -----------------------------
# Button
# -----------------------------
if st.button("Find Nearest Restaurants 🚀"):

    if current_location.strip() == "":
        st.warning("Please enter an area name.")
        st.stop()

    # -----------------------------
    # STEP 1: Find nearby areas by proximity
    # -----------------------------
    nearby = area_df[
        (area_df["Area_min"].str.lower() == current_location.lower()) |
        (area_df["Area_max"].str.lower() == current_location.lower())
    ].copy()

    if nearby.empty:
        st.error("No proximity data found for this area.")
        st.stop()

    nearby["Nearby_Area"] = nearby.apply(
        lambda row: row["Area_max"] if row["Area_min"].lower() == current_location.lower()
        else row["Area_min"], axis=1
    )

    nearby_sorted = nearby.sort_values("Proximity_Score")

    nearest_areas = nearby_sorted["Nearby_Area"].head(3).tolist()
    nearest_areas.insert(0, current_location)

    # -----------------------------
    # STEP 2: Get nearest restaurants
    # -----------------------------
    nearest_restaurants = restro_df[
        restro_df["Area"].str.lower().isin([a.lower() for a in nearest_areas])
    ]

    if nearest_restaurants.empty:
        st.error("No restaurants found near your location.")
        st.stop()

    # -----------------------------
    # STEP 3: Source bus stops
    # -----------------------------
    source_stops = bus_df[
        bus_df["area"].str.lower() == current_location.lower()
    ]

    if source_stops.empty:
        st.error("No bus stops found in your area.")
        st.stop()

    # -----------------------------
    # OUTPUT
    # -----------------------------
    st.subheader("🍽️ Nearest Restaurants & Bus Routes")

    for _, rest in nearest_restaurants.iterrows():
        with st.container():
            st.markdown(f"### 🍴 {rest['Name']}")
            st.write(f"📍 **Area:** {rest['Area']}")

            dest_stops = bus_df[
                bus_df["area"].str.lower() == rest["Area"].lower()
            ]

            if dest_stops.empty:
                st.warning("No bus stop near this restaurant.")
                continue

            common_buses = set(source_stops["bus_no"]).intersection(
                set(dest_stops["bus_no"])
            )

            if not common_buses:
                st.warning("No direct bus available.")
                continue

            for bus in common_buses:
                board = source_stops[source_stops["bus_no"] == bus].iloc[0]
                drop = dest_stops[dest_stops["bus_no"] == bus].iloc[0]

                st.success(f"""
                🚌 **Bus Number:** {bus}  
                🚏 **Boarding Stop:** {board['stop_name']}  
                🚏 **Drop Stop:** {drop['stop_name']}
                """)

            st.divider()
