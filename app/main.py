#-------------------------- import libraries and functions
import pandas as pd
import streamlit as st
import sys
import os
from dataclasses import asdict
import plotly.express as px
import requests
import random
from datetime import datetime
from streamlit_pills import pills
from forecast import generate_forecast, generate_forecast_data
from functions import categorise_temperature, clean_outfit_data, clean_list_string

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Clothing_Item, Outfit, OutfitSelection 

# set page config # needs to be first st element
st.set_page_config(page_title="Clothing Configurator")


#-------------------------- import forecast variables from forecast.py

forecast_data = generate_forecast()
min_temp = (forecast_data["min_temp"])
max_temp = (forecast_data["max_temp"])
current_temp = (forecast_data["current_temp"])
feels_like_temp = (forecast_data["feels_like_temp"])
chance_of_rain = (forecast_data["chance_of_rain"])
min_temp_tomorrow = (forecast_data["min_temp_tomorrow"])
max_temp_tomorrow = (forecast_data["max_temp_tomorrow"])
chance_of_rain_tomorrow = (forecast_data["chance_of_rain_tomorrow"])
forecast_next_5_days = (forecast_data["forecast_next_5_days"])


#-------------------------- load and intitialise outfit and clothing data

# File paths
CSV_CLOTHING = "data/clothing_data.csv"
CSV_OUTFITS = "data/outfit_data.csv"
CSV_SELECTIONS = "data/worn_outfits.csv"

def load_data_from_csv(file_path, sep=";"):
    df = pd.read_csv(file_path, sep=sep)
    return [
        Clothing_Item(
            id=None,  
            name=row["name"], 
            clothing_type=row["clothing_type"], 
            season=row["season"], 
            colour=row["colour"], 
            material=row["material"]
        )  
        for _, row in df.iterrows()
    ]

# Load CSV with default columns if missing
def load_csv_file(file_path, default_columns, sep=";", clean_data=False):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, sep=sep)
        return clean_outfit_data(df) if clean_data else df
    return pd.DataFrame(columns=default_columns)

# Log outfit selection
def log_outfit_selection(outfit: OutfitSelection):
    new_entry = pd.DataFrame([{"outfit_name": outfit.name, "date_selected": outfit.date_selected}])
    new_entry.to_csv(CSV_SELECTIONS, mode="a", header=not os.path.exists(CSV_SELECTIONS), index=False)

# Load clothing data
clothes = load_data_from_csv(CSV_CLOTHING)
df = pd.DataFrame([asdict(clothing_item) for clothing_item in clothes])

# Initialize session state
st.session_state.setdefault("df", df)
st.session_state.setdefault("outfits_df", load_csv_file(CSV_OUTFITS, ["id", "name", "weather", "occasion", "clothing_items"], clean_data=True))
st.session_state.setdefault("selection_df", load_csv_file(CSV_SELECTIONS, ["date", "outfit"]))

#-------------------------- 
                            # START LAYOUT 
#-------------------------- 
st.image("./data/icon_clothing-projects.png", width=80)

st.title("What to wear... what to wear?")

    #------------------------ Show weather of the day & tomorrow

col1, col2 = st.columns([1, 1])
col1.markdown("#### Weather today:")
col1.write(f"❄️ Minimum temperature is: {round(min_temp)}.")
col1.write(f"☀️ Maximum temperature is: {round(max_temp)}.")
col1.write(f"🌧️ Chance of rain: {chance_of_rain}")
col1.write(f"🌡️ Current temperature is {round(current_temp)} but real feel is {round(feels_like_temp)}.")

col2.markdown("#### Weather tomorrow:")
col2.write(f"❄️ Minimum temperature is: {round(min_temp_tomorrow)}.")
col2.write(f"☀️ Maximum temperature is: {round(max_temp_tomorrow)}.")
col2.write(f"🌧️Chance of rain: {chance_of_rain_tomorrow}")
col2.write(f"🌡️ Current temperature is {round(current_temp)} but real feel is {round(feels_like_temp)}.")

    #------------------------ Outfit selection for today

temp = categorise_temperature(max_temp)

outfit_options = st.session_state.outfits_df[st.session_state.outfits_df['weather'].apply(lambda x: temp in x)]

def clean_list_string(value):
    return value.replace('[', '').replace(']', '').replace("'", "").strip()

if "random_outfits_rows" not in st.session_state:
    outfit_options = st.session_state.outfits_df[st.session_state.outfits_df['weather'].apply(lambda x: temp in x)]

if not outfit_options.empty:
    sample_size = min(3, len(outfit_options))  # Ensure we don't sample more than available rows
    random_outfits_rows = outfit_options.sample(sample_size)
    st.session_state.random_outfits_rows = random_outfits_rows 

random_outfits_rows = st.session_state.random_outfits_rows


col1.markdown("#### Today's Random Selection")

with col1:
    
    for _, row in random_outfits_rows.iterrows():
        clean_weather = clean_list_string(str(row['weather']))
        clean_occasion = clean_list_string(str(row['occasion']))

        with st.expander(f"👕 {row['name']}"):
            st.write(f"**Clothing Items:** {row['clothing_items']}")
            st.write(f"**Weather:** {clean_weather} °C")
            st.write(f"**Occasion:** {clean_occasion}")

    #------------------------ Outfit selection for tomorrow

temp = categorise_temperature(max_temp_tomorrow)


outfit_options = st.session_state.outfits_df[st.session_state.outfits_df['weather'].apply(lambda x: temp in x)]

def clean_list_string(value):

        return value.replace('[', '').replace(']', '').replace("'", "").strip()

if "random_outfits_rows" not in st.session_state:

        outfit_options = st.session_state.outfits_df[st.session_state.outfits_df['weather'].apply(lambda x: temp in x)]

if not outfit_options.empty:
    sample_size = min(3, len(outfit_options))  # Ensure we don't sample more than available rows
    random_outfits_rows = outfit_options.sample(sample_size)
    st.session_state.random_outfits_rows = random_outfits_rows 

random_outfits_rows = st.session_state.random_outfits_rows

col2.markdown("#### Tomorrow's Random Selection")

with col2: 
    for _, row in random_outfits_rows.iterrows():
        clean_weather = clean_list_string(str(row['weather']))
        clean_occasion = clean_list_string(str(row['occasion']))

        with st.expander(f"👕 {row['name']}"):
            st.write(f"**Clothing Items:** {row['clothing_items']}")
            st.write(f"**Weather:** {clean_weather} °C")
            st.write(f"**Occasion:** {clean_occasion}")



    #------------------------ Outfit selection for next 5 days

from datetime import datetime, timedelta
import time

st.markdown("### Generate random outfits")

if st.button("Get Outfit Recommendations for the Next 5 Days"):

    col1, col2 = st.columns(2)
    progress_bar = col1.progress(0)
    status_text = st.empty() 

    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f"Loading... {i + 1}%")  
        time.sleep(0.008)  # Simulate a delay

    st.markdown("#### Outfit Recommendations for the next week:")

    today = datetime.today().date()

    data = generate_forecast_data()
    
    forecast_next_5_days = data["forecast"]["forecastday"]  

    for i in range(1, 7):  
        if i < len(forecast_next_5_days): 
            forecast_day = forecast_next_5_days[i]
            target_date = datetime.strptime(forecast_day["date"], "%Y-%m-%d").date()
            
            max_temp = float(forecast_day["day"]["maxtemp_c"])
            temp_var_min = float(forecast_day["day"]["mintemp_c"])
            print(f"Max temp on {target_date}: {max_temp}")

            temp = categorise_temperature(max_temp)

            def clean_list_string(value):
                if isinstance(value, list):
                    cleaned_values = [str(v).replace('[', '').replace(']', '').replace("'", "").strip() for v in value]
                    return ', '.join(cleaned_values)  
                return str(value).replace('[', '').replace(']', '').replace("'", "").strip()

            st.session_state.outfits_df['occasion'] = st.session_state.outfits_df['occasion'].apply(clean_list_string)

            
            outfit_options = st.session_state.outfits_df[
                (st.session_state.outfits_df['weather'].apply(lambda x: temp in x)) &
                (st.session_state.outfits_df["occasion"].apply(lambda x: "Business" in x))
            ]

            def clean_list_string(value):
                return value.replace('[', '').replace(']', '').replace("'", "").strip()

            if not outfit_options.empty:
                random_outfits_rows = outfit_options.sample(2)  
                st.session_state[f"random_outfits_{target_date}"] = random_outfits_rows 


            if f"random_outfits_{target_date}" in st.session_state:
                random_outfits_rows = st.session_state[f"random_outfits_{target_date}"]


                formatted_date = target_date.strftime("%A, the %-d of %B")  

                col1, col2 = st.columns(2)

                col1.write(f"📆 Outfits for **{formatted_date}**:")
                col2.write(f"🌡️ Temperature will range from {round(temp_var_min)} to {round(max_temp)}°C")
                for _, row in random_outfits_rows.iterrows():
                    clean_weather = clean_list_string(str(row['weather']))
                    clean_occasion = clean_list_string(str(row['occasion']))
                    outfit_name = str(row['name'])


                    with st.expander(f"👕 {row['name']}"):
                        st.write(f"**Clothing Items:** {row['clothing_items']}")
                        st.write(f"**Weather:** {clean_weather} °C")
                        st.write(f"**Occasion:** {clean_occasion}")


#------------------------
#------------------------

col1, col2 = st.columns([2, 1])


col1.markdown("<br><br>", unsafe_allow_html=True)
col2.markdown("<br><br>", unsafe_allow_html=True)
col1.markdown("### Browse more outfits here...")

#------------------------ Filter outfits and display outfits that match selections

df_full = st.session_state.outfits_df

# --- Initialize Filter Selections ---
if "weather_sel" not in st.session_state:
    st.session_state.weather_sel = "All"
if "occasion_sel" not in st.session_state:
    st.session_state.occasion_sel = "All"
if "clothing_sel" not in st.session_state:
    st.session_state.clothing_sel = "All"

# --- Helper Functions ---

def get_exploded_options(df, column, other_filters):
    """
    Returns the unique individual options for a column that might have comma-separated lists,
    after applying the provided filters (other_filters).
    """
    filtered = df.copy()
    # Apply each filter in other_filters
    for col, value in other_filters.items():
        if value != "All":
            if col == "clothing_items":
                filtered = filtered[filtered[col].str.contains(value, case=False, na=False)]
            else:
                filtered = filtered[filtered[col] == value]
    # Explode the values by splitting on comma
    options = (filtered[column]
               .dropna()
               .astype(str)
               .str.split(',')
               .explode()
               .str.strip()
               .unique())
    return sorted(options)

def get_options(df, column, other_filters):
    """
    Returns the unique options for a column (assumed not to contain lists)
    after applying filters from other_filters.
    """
    filtered = df.copy()
    for col, value in other_filters.items():
        if value != "All":
            if col == "clothing_items":
                filtered = filtered[filtered[col].str.contains(value, case=False, na=False)]
            else:
                filtered = filtered[filtered[col] == value]
    options = filtered[column].dropna().unique()
    return sorted(options)

def get_clothing_options(df, other_filters):
    """
    Returns the unique individual clothing items from the 'clothing_items' column
    after applying filters from other_filters (except clothing itself).
    """
    filtered = df.copy()
    for col, value in other_filters.items():
        if value != "All" and col != "clothing_items":
            filtered = filtered[filtered[col] == value]
    items = (filtered["clothing_items"]
             .dropna()
             .astype(str)
             .str.split(',')
             .explode()
             .str.strip()
             .unique())
    return sorted(items)

# --- Reset Filters Button ---
if col2.button("Reset Filters"):
    st.session_state.weather_sel = "All"
    st.session_state.occasion_sel = "All"
    st.session_state.clothing_sel = "All"
    st.rerun()

# --- Define Emoji Dictionaries for Pills ---
weather_emojis = {
    "All": "🤷‍♀️",
    "16-20": "🌤️",
    "12-16": "⛅️",
    "<0": "❄️",  
    "0-12": "🌥️",  
    "20-24": "☀️", 
    ">24": "🔥"
}
occasion_emojis = {
    "All": "🤷‍♀️",
    "Party": "💃",
    "Business": "👔",
    "Casual": "👕",
    "Formal": "👠"
}

# --- Compute Dynamic Options Sequentially ---

# 1. Compute weather options by exploding the weather column.
weather_options = ["All"] + get_exploded_options(df_full, "weather", {
    "occasion": st.session_state.occasion_sel,
    "clothing_items": st.session_state.clothing_sel
})
# If the current weather selection isn’t valid anymore, reset to "All"
if st.session_state.weather_sel not in weather_options:
    st.session_state.weather_sel = "All"

# --- Weather Widget ---
col1, col2, col3 = st.columns(3)
with col1:
    weather_pill = pills(
        "Select Temperature",
        options=[f"{weather_emojis.get(opt, '❓')} {opt}" for opt in weather_options],
        index=weather_options.index(st.session_state.weather_sel)
    )
    # Remove emoji prefix and update state
    st.session_state.weather_sel = weather_pill.split(" ", 1)[-1] if " " in weather_pill else weather_pill

# 2. Now compute occasion options using updated weather and current clothing.
occasion_options = ["All"] + get_options(df_full, "occasion", {
    "weather": st.session_state.weather_sel,
    "clothing_items": st.session_state.clothing_sel
})
if st.session_state.occasion_sel not in occasion_options:
    st.session_state.occasion_sel = "All"

with col2:
    occasion_pill = pills(
        "Select Occasion",
        options=[f"{occasion_emojis.get(opt, '❓')} {opt}" for opt in occasion_options],
        index=occasion_options.index(st.session_state.occasion_sel)
    )
    st.session_state.occasion_sel = occasion_pill.split(" ", 1)[-1] if " " in occasion_pill else occasion_pill

# 3. Finally, compute clothing options using updated weather and occasion.
clothing_options = ["All"] + get_clothing_options(df_full, {
    "weather": st.session_state.weather_sel,
    "occasion": st.session_state.occasion_sel
})
if st.session_state.clothing_sel not in clothing_options:
    st.session_state.clothing_sel = "All"

with col3:
    st.session_state.clothing_sel = st.selectbox(
        "Select Clothing Item",
        options=clothing_options,
        index=clothing_options.index(st.session_state.clothing_sel)
    )

# --- Apply All Filters to the DataFrame ---
filtered_outfits = df_full.copy()

# For weather, filter rows where the exploded weather values contain the selection.
if st.session_state.weather_sel != "All":
    filtered_outfits = filtered_outfits[
        filtered_outfits["weather"]
        .astype(str)
        .str.split(',')
        .apply(lambda items: st.session_state.weather_sel in [i.strip() for i in items])
    ]

if st.session_state.occasion_sel != "All":
    filtered_outfits = filtered_outfits[filtered_outfits["occasion"] == st.session_state.occasion_sel]

if st.session_state.clothing_sel != "All":
    filtered_outfits = filtered_outfits[
        filtered_outfits["clothing_items"].str.contains(st.session_state.clothing_sel, case=False, na=False)
    ]

#st.write("### Filtered Outfits", filtered_outfits)



#-----------------------------------------

# ---- DISPLAY FILTERED OUTFITS AS CARDS ----
st.markdown("##### Outfits that match your selection:", len(filtered_outfits))

def clean_list_string(value):
    # Remove any square brackets, quotes, and extra spaces
    return value.replace('[', '').replace(']', '').replace("'", "").strip()

if filtered_outfits.empty:
    st.warning("No outfits match the selected filters.")
else:
    for _, row in filtered_outfits.iterrows():
        # Retrieve just the outfit name from the row
        outfit_name = str(row['name'])

        col1, col2, col3 = st.columns([0.5, 4, 0.5])
        # Display outfit with a button to select
        with col2:
            with st.expander(f"👕 {row['name']}"):
                st.write(f"**Clothing Items:** {row['clothing_items']}")
                st.write(f"**Weather:** {clean_weather} °C")
                st.write(f"**Occasion:** {clean_occasion}")


# ---- DASHBOARD METRICS ----



# ---- CHARTS ----

st.markdown(" ## 👗 Outits in Numbers")
        # Columns for KPIs
col1, col2 = st.columns(2)

    # Total outfits
col1.metric("Total Outfits", len(st.session_state.outfits_df))

    # Number of filtered outfits
col2.metric("Total Clothing Items", len(st.session_state.df))


if st.button("Show More Outfit metrics"):


    col1, col2 = st.columns(2)
    progress_bar = col1.progress(0)
    status_text = st.empty()  # Placeholder for status message

    # Simulate some work (e.g., data fetching, processing) with a loop
    for i in range(100):
        # Update the progress bar
        progress_bar.progress(i + 1)
        status_text.text(f"Calculating Metrics... {i + 1}%")  # Update loading text
        time.sleep(0.008)  # Simulate a delay

    with st.expander("📊 Outfit Distribution"):

        if not st.session_state.outfits_df.empty:
            # Pie chart for occasions
            fig1 = px.pie(st.session_state.outfits_df, names="occasion", title="Outfits by Occasion")
            st.plotly_chart(fig1, use_container_width=True)

            # Bar chart for weather distribution
            fig2 = px.pie(st.session_state.outfits_df, names="weather", title="Outfits by Weather")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No outfit data available to display charts.")


#------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("----------------------------------------------------")
st.markdown("### Manage Items and Outfits")
#------------------------
if "df" not in st.session_state:
    # Initialize the dataframe for clothing items if it doesn't exist yet
    if os.path.exists(csv_file_path):
        st.session_state.df = pd.read_csv(csv_file_path, sep=";")
    else:
        st.session_state.df = pd.DataFrame(columns=["id", "name", "clothing_type", "season", "colour", "material"])

if "outfits_df" not in st.session_state:
    # Initialize the dataframe for outfits if it doesn't exist yet
    if os.path.exists(csv_file_path_outfits):
        st.session_state.outfits_df = pd.read_csv(csv_file_path_outfits, sep=";")
    else:
        st.session_state.outfits_df = pd.DataFrame(columns=["name", "weather", "occasion", "clothing_items"])


#------------------------
# Create a new clothing item (with "Save" button)
#------------------------
st.write("#### Create a new clothing item")

name = st.text_input("Clothing item name:")
type = st.text_input("Type:")
season = st.text_input("Season:")
colour = st.text_input("Colour:")
material = st.text_input("Material:")

if st.button("Save new clothing item") and name and type and season and colour and material:
    new_item = Clothing_Item(
        id=None,
        name=name,
        clothing_type=type,
        season=season,
        colour=colour,
        material=material
    )

    new_item_dict = asdict(new_item)
    new_item_df = pd.DataFrame([new_item_dict])
    st.session_state.df = pd.concat([st.session_state.df, new_item_df], ignore_index=True)
    st.session_state.df.to_csv(csv_file_path, sep=";", index=False)

    st.success(f"New clothing item '{name}' added!")

#------------------------
# Change or Delete Clothing Items (with "Save" button)
#------------------------
st.write("#### Manage Clothing Items (Change/Delete)")

# Handle the data editor with dynamic rows
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic")
st.session_state.df = edited_df

if st.button("Save Changes to Clothing Items"):
    st.session_state.df.to_csv(csv_file_path, sep=";", index=False)
    st.success("Clothing items have been saved!")

#------------------------
# Create a new Outfit (with "Save" button)
#------------------------
st.write("#### Create a new Outfit")

# User input for outfit details
outfit_name = st.text_input("Outfit Name:", value="My New Outfit")
weather = st.multiselect("Weather:", ["<0", "0-12", "12-16", "16-20", "20-24", ">24"])
occasion = st.multiselect("Occasion:", ["Casual", "Formal", "Business", "Party"])

# Convert st.session_state.df back to Clothing_Item objects
clothing_items_list = [
    Clothing_Item(
        id=row["id"],
        name=row["name"],
        clothing_type=row["clothing_type"],
        season=row["season"],
        colour=row["colour"],
        material=row["material"]
    )
    for _, row in st.session_state.df.iterrows()
]

# Select clothing items
selected_items = st.multiselect(
    "Select Clothing Items:",
    options=[item.name for item in clothing_items_list],
    default=[],
)

if st.button("Save Outfit") and outfit_name and selected_items:
    if os.path.exists(csv_file_path_outfits):
        outfits_df = pd.read_csv(csv_file_path_outfits, sep=";")
        st.session_state.outfits_df = outfits_df
    else:
        outfits_df = pd.DataFrame(columns=["name", "weather", "occasion", "clothing_items"])
        st.session_state.outfits_df = outfits_df

    selected_clothing_objects = [item for item in clothing_items_list if item.name in selected_items]

    clothing_items_str = ", ".join([item.name for item in selected_clothing_objects])

    new_outfit = Outfit(
        id=None,
        name=outfit_name,
        weather=weather,
        occasion=occasion,
        clothing_items=clothing_items_str
    )

    new_outfit_dict = asdict(new_outfit)
    new_outfit_df = pd.DataFrame([new_outfit_dict])
    st.session_state.outfits_df = pd.concat([st.session_state.outfits_df, new_outfit_df], ignore_index=True)

    st.session_state.outfits_df.to_csv(csv_file_path_outfits, sep=";", index=False)

    st.success(f"Outfit '{outfit_name}' saved!")

#------------------------
# Manage Outfits (Change/Delete) (with "Save" button)
#------------------------
st.write("#### Manage Outfits (Change/Delete)")

edited_outfits = st.data_editor(st.session_state.outfits_df, num_rows='dynamic')
st.session_state.outfits_df = edited_outfits

if st.button("Save Changes to Outfits"):
    st.session_state.outfits_df.to_csv(csv_file_path_outfits, sep=";", index=False)
    st.success("Outfits have been saved!")