import pandas as pd
from datetime import datetime


local_file_path = "/Users/majaskuza/desktop/local_weight_record.xlsx"

def create_initial_recording_dataframe():
    columns = [
        "Date", "Cage", "ID", "Name", "Start weight", 
        "Training Start", "Training end", "Animal Fed at", 
        "Food amount", "percent", "Weight"
    ]
    return pd.DataFrame(columns=columns)

def create_initial_animal_data_dataframe():
    animal_data_headers = ["RFID", "name", "rig", "cage", "shift", "food", "Start weight", "ID"]
    return pd.DataFrame(columns=animal_data_headers)

def save_initial_dataframes(file_path):
    recording_df = create_initial_recording_dataframe()
    animal_data_df = create_initial_animal_data_dataframe()
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
        recording_df.to_excel(writer, index=False, sheet_name='Recording Entries')
        animal_data_df.to_excel(writer, index=False, sheet_name='Animal Data')
    print(f"Initial Excel file created at {file_path}.")

def load_animal_data_dataframe(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name="Animal Data")
    except FileNotFoundError:
        print("File not found. Make sure the Excel file is created first.")
        return pd.DataFrame()
    return df

def add_recording_entry(df, animal_df, name, weight):
    animal_info = animal_df[animal_df["name"] == name]
    
    if animal_info.empty:
        print(f"Warning: No data found for Name: {name}. Entry will not be added.")
        return df

    start_weight = animal_info["Start weight"].values[0]
    eighty_percent_weight = start_weight * 0.8
    id_ = animal_info["ID"].values[0]
    food_amount = animal_info["food"].values[0]
    cage = animal_info["cage"].values[0]  
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time
    
    percent = (weight / eighty_percent_weight) * 100  
    new_entry = {
        "RFID": rfid,
        "Date": date,
        "Cage": cage,
        "ID": id_,
        "Name": name,
        "Start weight": start_weight,
        "Training Start": "",        # Blank
        "Training end": "",          # Blank
        "Animal Fed at": "",         # Blank
        "Food amount": food_amount,
        "percent": percent,
        "Weight": weight
    }
    new_entry_df = pd.DataFrame([new_entry])
    df = pd.concat([df, new_entry_df], ignore_index=True).sort_values(by=["Name", "Date"]).reset_index(drop=True)
    
    return df


def save_recording_df(recording_df, file_path):
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists="replace") as writer:
        recording_df.to_excel(writer, index=False, sheet_name='Recording Entries')


"""
save_initial_dataframes(local_file_path)
# Load the updated animal data after manual additions
animal_data_df = load_animal_data_dataframe(local_file_path)
recording_df = create_initial_recording_dataframe()
#single entry to add 
recording_df = add_recording_entry(
    recording_df, animal_data_df,
    name="EC01", 
    weight=376
)
save_recording_df(recording_df, local_file_path)
"""



