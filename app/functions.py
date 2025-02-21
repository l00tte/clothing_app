import pandas as pd

def categorise_temperature(x):
    """Categorizes temperature into predefined ranges."""

    try:
        # Convert input to float (handle cases like "20°C")
        max_temp = float(str(x).replace("°C", ""))  

        # Define categories
        if max_temp < 0.0:
            return "<0"
        elif max_temp < 12:
            return "0-12"
        elif max_temp < 16:
            return "12-16"
        elif max_temp < 20:
            return "16-20"
        elif max_temp < 24:
            return "20-24"
        else:
            return ">24"

    except ValueError:
        return "Unknown" 

def clean_list_string(value):

    try: 
        x = str(value).replace('[', '').replace(']', '').replace("'", "").strip()
        return x
    except ValueError:
        return value

def clean_outfit_data(df):
    df["weather"] = df["weather"].apply(clean_list_string)
    df["occasion"] = df["occasion"].apply(clean_list_string)  

    return df  
