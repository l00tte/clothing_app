import pandas as pd
import streamlit as st
import sys
import os
from dataclasses import asdict
import plotly.express as px
import requests
import random
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#print(sys)
from models import Clothing_Item, Outfit, OutfitSelection 

st.set_page_config(page_title="Clothing Configurator")


#----------------------------------------------------- weather API 

api_key = "d8010fa049994fddab9160209251602"
base_url = "http://api.weatherapi.com/v1/forecast.json?key=d8010fa049994fddab9160209251602&q=Berlin&days=5&aqi=no&alerts=no"

response = requests.get(base_url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    data = response.json()

    
    # Extract the min and max temperatures from the forecast data
    forecast_day = data["forecast"]["forecastday"][0]["day"]
    min_temp = forecast_day["mintemp_c"]
    max_temp = forecast_day["maxtemp_c"]
    current_temp = data["current"]["temp_c"]
    feels_like_temp = data["current"]["feelslike_c"]

    chance_of_rain = forecast_day["daily_will_it_rain"]

    forecast_tomorrow = data["forecast"]["forecastday"][1]["day"]
    
    max_temp_tomorrow = forecast_tomorrow["maxtemp_c"]
    print("tomorrow", max_temp_tomorrow)
    min_temp_tomorrow = forecast_tomorrow["mintemp_c"]
    chance_of_rain_tomorrow = forecast_tomorrow["daily_chance_of_rain"]

    forecast_days = data.get("forecast", {}).get("forecastday", [])

    forecast_next_5_days = {}

    for i in range(1, min(6, len(forecast_days))):  # Start from index 1 to skip today
        forecast_day = forecast_days[i]["day"]
        date = forecast_days[i]["date"]
        
        forecast_next_5_days[date] = {
            "max_temp": forecast_day["maxtemp_c"],
            "min_temp": forecast_day["mintemp_c"],
            "chance_of_rain": forecast_day["daily_chance_of_rain"],
        }

    
    
else:
    print(f"Error: Unable to fetch data. Status code {response.status_code}")


#-----------------------------------------------------


def load_data_from_csv(file_path, sep):
    df = pd.read_csv(file_path, sep=sep)
    clothes = []
    for _, row in df.iterrows():
        clothing_item = Clothing_Item(
            id=None,  
            name=row["name"], 
            clothing_type=row["clothing_type"], 
            season=row["season"], 
            colour=row["colour"], 
            material=row["material"]
        )  
        clothes.append(clothing_item)

    return clothes

clothes = load_data_from_csv("data/clothing_data.csv", sep=";")  
csv_file_path = "data/clothing_data.csv"
csv_file_path_outfits = "data/outfit_data.csv"
csv_file_path_selected = "data/worn_outfits.csv"

import os
import pandas as pd

# Log outfit selection by saving to a CSV file
def log_outfit_selection(outfit: OutfitSelection):
    # Path to log file
    log_file = csv_file_path_selected
    
    # Check if the log file exists, if not create it with headers
    if os.path.exists(log_file):
        log_df = pd.read_csv(log_file)
    else:
        log_df = pd.DataFrame(columns=["outfit_name", "date_selected"])
    
    # Append new log entry
    new_log_entry = pd.DataFrame([{"outfit_name": outfit.name, "date_selected": outfit.date_selected}])

    # Concatenate the existing log_df with the new entry
    log_df = pd.concat([log_df, new_log_entry], ignore_index=True)
    
    # Save the updated log to CSV
    log_df.to_csv(log_file, index=False)

    
df = pd.DataFrame([asdict(clothing_item) for clothing_item in clothes])


if "df" not in st.session_state:
    st.session_state.df = df

def load_outfits():
    if os.path.exists(csv_file_path_outfits):
        return pd.read_csv(csv_file_path_outfits, sep=";")
    else:
        return pd.DataFrame(columns=["id", "name", "weather", "occasion", "clothing_items"])

def load_selection():
    if os.path.exists(csv_file_path_selected):
        return pd.read_csv(csv_file_path_selected, sep=";")
    else:
        return pd.DataFrame(columns=["date","outfit"])

# Initialize session state
if "outfits_df" not in st.session_state:
    outfits_df = load_outfits()
    st.session_state.outfits_df = outfits_df

if "selection_df" not in st.session_state:
    selection_df = load_selection()
    st.session_state.selection_df = selection_df



st.markdown(
    """
    <style>
    .main {
        background-color: #9bb5bf;  /* Change this to the color you want */
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.image("./data/icon_clothing-projects.png", width=80)

st.title("What to wear... what to wear?")

st.markdown("#### Weather today:")
st.write(f"❄️The minimum temperature is: {round(min_temp)}.")
st.write(f"☀️The maximum temperature is: {round(max_temp)}.")
st.write(f"🌡️The current temperature is {round(current_temp)} but real feel is {round(feels_like_temp)}.")
st.write(f"🌧️Chance of rain: {chance_of_rain}")

#------------------------

st.markdown("## Outfit Recommendations for this weather:")

max_temp_str = str(max_temp).replace("°C", "").strip()
max_temp = float(max_temp_str)
print("max temp", max_temp)

if max_temp < 0.0:
    temp = "<0"
elif 0 <= max_temp < 12:
    temp = "0-12"
elif 12 <= max_temp < 16:
    temp = "12-16"
elif 16 <= max_temp < 20:
    temp = "16-20"
elif 20 <= max_temp < 24:
    temp = "20-24"
else:
    temp = ">24"



outfit_options = st.session_state.outfits_df[st.session_state.outfits_df['weather'].apply(lambda x: temp in x)]

def clean_list_string(value):
    # Remove any square brackets, quotes, and extra spaces
    return value.replace('[', '').replace(']', '').replace("'", "").strip()

if "random_outfits_rows" not in st.session_state:
    # Filter outfits that match the selected weather range (temp)
    outfit_options = st.session_state.outfits_df[st.session_state.outfits_df['weather'].apply(lambda x: temp in x)]

    if not outfit_options.empty:
        # Select 3 random outfit rows
        random_outfits_rows = outfit_options.sample(3)
        st.session_state.random_outfits_rows = random_outfits_rows  # Store them in session state

# Retrieve the stored random outfits
random_outfits_rows = st.session_state.random_outfits_rows

# Display the outfits
st.write("🎉 Randomly Selected Outfits for this weather:")
for _, row in random_outfits_rows.iterrows():
    # Clean weather and occasion for display
    clean_weather = clean_list_string(str(row['weather']))
    clean_occasion = clean_list_string(str(row['occasion']))

    with st.expander(f"👕 {row['name']} ({clean_weather}, {clean_occasion})"):
        st.write(f"**Clothing Items:** {row['clothing_items']}")

#------------------------

if st.button("Get outfit recommendations for tomorrow"):
    st.markdown("## Outfit Recommendations for tomorrow:")
    max_temp = max_temp_tomorrow
    max_temp_str = str(max_temp).replace("°C", "").strip()
    max_temp = float(max_temp_str)
    print("max temp", max_temp)

    if max_temp < 0.0:
        temp = "<0"
    elif 0 <= max_temp < 12:
        temp = "0-12"
    elif 12 <= max_temp < 16:
        temp = "12-16"
    elif 16 <= max_temp < 20:
        temp = "16-20"
    elif 20 <= max_temp < 24:
        temp = "20-24"
    else:
        temp = ">24"



    outfit_options = st.session_state.outfits_df[st.session_state.outfits_df['weather'].apply(lambda x: temp in x)]

    def clean_list_string(value):
        # Remove any square brackets, quotes, and extra spaces
        return value.replace('[', '').replace(']', '').replace("'", "").strip()

    if "random_outfits_rows" not in st.session_state:
        # Filter outfits that match the selected weather range (temp)
        outfit_options = st.session_state.outfits_df[st.session_state.outfits_df['weather'].apply(lambda x: temp in x)]

        if not outfit_options.empty:
            # Select 3 random outfit rows
            random_outfits_rows = outfit_options.sample(3)
            st.session_state.random_outfits_rows = random_outfits_rows  # Store them in session state

    # Retrieve the stored random outfits
    random_outfits_rows = st.session_state.random_outfits_rows

    # Display the outfits
    st.write("🎉 Randomly Selected Outfits for this weather:")
    for _, row in random_outfits_rows.iterrows():
        # Clean weather and occasion for display
        clean_weather = clean_list_string(str(row['weather']))
        clean_occasion = clean_list_string(str(row['occasion']))

        with st.expander(f"👕 {row['name']} ({clean_weather}, {clean_occasion})"):
            st.write(f"**Clothing Items:** {row['clothing_items']}")

#------------------------

from datetime import datetime, timedelta

if st.button("Get outfit recommendations for the next 5 days"):
    st.markdown("## Outfit Recommendations for the next week:")

    today = datetime.today().date()
    
    forecast_next_5_days = data["forecast"]["forecastday"]  # Assuming this contains the next 5 days

    for i in range(1, 6):  # Loop through the next 5 days
        if i < len(forecast_next_5_days):  # Prevent IndexError
            forecast_day = forecast_next_5_days[i]
            target_date = datetime.strptime(forecast_day["date"], "%Y-%m-%d").date()
            
            max_temp = float(forecast_day["day"]["maxtemp_c"])
            temp_var_min = float(forecast_day["day"]["mintemp_c"])
            print(f"Max temp on {target_date}: {max_temp}")

            # Temperature range classification
            if max_temp < 0.0:
                temp = "<0"
            elif 0 <= max_temp < 12:
                temp = "0-12"
            elif 12 <= max_temp < 16:
                temp = "12-16"
            elif 16 <= max_temp < 20:
                temp = "16-20"
            elif 20 <= max_temp < 24:
                temp = "20-24"
            else:
                temp = ">24"


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

            # Function to clean list-like strings
            def clean_list_string(value):
                return value.replace('[', '').replace(']', '').replace("'", "").strip()

            if not outfit_options.empty:
                random_outfits_rows = outfit_options.sample(2)  # Pick 2 random outfits
                st.session_state[f"random_outfits_{target_date}"] = random_outfits_rows  # Store in session state

            # Retrieve stored outfits
            if f"random_outfits_{target_date}" in st.session_state:
                random_outfits_rows = st.session_state[f"random_outfits_{target_date}"]

                # Display outfits
                formatted_date = target_date.strftime("%A, the %-d of %B")  # For Unix/Mac
                # formatted_date = target_date.strftime("%A, the %#d of %B")  # Use this on Windows

                st.write(f"Selected Outfits for **{formatted_date}**:")
                st.write(f"Temperature will range from {round(temp_var_min)} to {round(max_temp)}°C")
                for _, row in random_outfits_rows.iterrows():
                    clean_weather = clean_list_string(str(row['weather']))
                    clean_occasion = clean_list_string(str(row['occasion']))
                    outfit_name = str(row['name'])


                    with st.expander(f"👕 {row['name']} ({clean_weather}, {clean_occasion})"):
                        st.write(f"**Clothing Items:** {row['clothing_items']}")

#------------------------
#------------------------

st.write("### Browse more outfits...")

#------------------------

def reset_filters():
    st.session_state.weather_filter = "All"
    st.session_state.occasion_filter = "All"
    st.session_state.clothing_filter = "All"

# ---- RESET FILTERS BUTTON ----
if st.button("Reset Filters"):
    reset_filters()
    st.rerun()  # Rerun the app to reset the filter states

# ---- FILTERING OUTFITS BASED ON THE SELECTED FILTERS ----
# Default values for filters if they don't exist in session state
if 'weather_filter' not in st.session_state:
    st.session_state.weather_filter = "All"
if 'occasion_filter' not in st.session_state:
    st.session_state.occasion_filter = "All"
if 'clothing_filter' not in st.session_state:
    st.session_state.clothing_filter = "All"


def get_unique_options(df, column_name):
    # Split by comma, explode, strip, and remove square brackets
    return df[column_name].dropna().astype(str) \
        .str.replace(r'[\[\]\'"]', '', regex=True) \
        .str.split(',') \
        .explode() \
        .str.strip() \
        .unique()

# Get unique weather options
unique_weather = get_unique_options(st.session_state.outfits_df, "weather")

# Get unique occasion options
unique_occasion = get_unique_options(st.session_state.outfits_df, "occasion")

col1, col2, col3 = st.columns(3)
# Weather filter in the first column
with col1:
    weather_filter = st.selectbox(
        "Select Weather",
        options=["All"] + [str(item) for item in unique_weather],  # Ensure proper formatting
        index=0
    )

# Occasion filter in the second column
with col2:
    occasion_filter = st.selectbox(
        "Select Occasion",
        options=["All"] + [str(item) for item in unique_occasion],  # Ensure proper formatting
        index=0
    )

clothing_items_list = st.session_state.outfits_df["clothing_items"].dropna().astype(str) \
    .str.split(',') \
    .explode() \
    .str.strip() \
    .unique()

with col3:
# Add 'All' option to the beginning of the list
    clothing_filter = st.selectbox(
        "Select clothing item",
        options=["All"] + list(clothing_items_list),  # Convert to list and pass to the selectbox
        index=0
    )



# Apply filters to dataframe
filtered_outfits = st.session_state.outfits_df.copy()

# Filter based on the weather
if weather_filter != "All":
    filtered_outfits = filtered_outfits[filtered_outfits["weather"] == weather_filter]

# Filter based on the occasion
if occasion_filter != "All":
    filtered_outfits = filtered_outfits[filtered_outfits["occasion"] == occasion_filter]

if clothing_filter:
    # Ensure all clothing items are strings and handle NaN by replacing them with an empty string
    filtered_outfits['clothing_items'] = filtered_outfits['clothing_items'].fillna('').astype(str)

    # Create a new column that holds the list of clothing items as individual items
    filtered_outfits['clothing_items_list'] = filtered_outfits['clothing_items'].apply(lambda x: [item.strip() for item in x.split(',')] if x else [])

    # Apply the filter: for each row, check if the clothing filter matches any item in the clothing_items_list
    filtered_outfits = filtered_outfits[filtered_outfits['clothing_items_list'].apply(
        lambda items: any(clothing_filter.lower() in item.lower() for item in items))
    ]

# ---- DISPLAY FILTERED OUTFITS AS CARDS ----
st.markdown("### 🛍️Outfit Options")

def clean_list_string(value):
    # Remove any square brackets, quotes, and extra spaces
    return value.replace('[', '').replace(']', '').replace("'", "").strip()

if filtered_outfits.empty:
    st.warning("No outfits match the selected filters.")
else:
    for _, row in filtered_outfits.iterrows():
        # Retrieve just the outfit name from the row
        outfit_name = str(row['name'])

        # Display outfit with a button to select
        with st.expander(f"👕 {outfit_name}"):
            st.write(f"**Clothing Items:** {row['clothing_items']}")
            
           # if st.button(f"Select this Outfit for today"):
           #     # Create an OutfitSelection object with the name and current date
            #    outfit = OutfitSelection(name=outfit_name, date_selected=None)
                
                # Log the outfit selection
            #    log_outfit_selection(outfit)
             #   st.success(f"Outfit '{outfit_name}' selected for today!")



# ---- DASHBOARD METRICS ----
st.markdown("### 👗Outfits in Numbers")

# Columns for KPIs
col1, col2 = st.columns(2)

# Total outfits
col1.metric("Total Outfits", len(st.session_state.outfits_df))

# Number of filtered outfits
col2.metric("Matching Outfits", len(filtered_outfits))

# ---- CHARTS ----
if st.button("Show Outfit metrics"):
    st.subheader("📊 Outfit Distribution")

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