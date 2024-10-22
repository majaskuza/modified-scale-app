import pandas as pd
from datetime import datetime

def create_general_info_spreadsheet(url):
    general_info_data = {
        'Cage': [],
        'ID': [],
        'Name': [],
        'Start weight': [],
        '80% weight': []
    }
    general_info_df = pd.DataFrame(general_info_data)
    general_info_df.to_excel(url, index=False, engine='openpyxl')

#function to add the weight information from a single session into the excel spreedsheet
def add_recording_entry(url, subjid, weight, animal_fed_at='', training_end='', food_amount=''):
    timestamp = datetime.now().strftime("%H:%M")  
    percent = 0.8 * weight  
    new_entry = {
        'Date': datetime.now().strftime("%Y-%m-%d"),  
        'Subjid': subjid,
        'Training Start': timestamp,
        'Training End': training_end,
        'Animal Fed At': animal_fed_at,
        'Food Amount': food_amount,
        'Percent': percent,
        'Weight': weight
    }
    try:
        df = pd.read_excel(url)
    except FileNotFoundError:
        df = pd.DataFrame(columns=new_entry.keys())  # Create an empty DataFrame with the columns
    df = df.append(new_entry, ignore_index=True)
    df.to_excel(url, index=False)

  

#example usage of above functions
#url = "https://liveuclac.sharepoint.com/sites/swcpil/_layouts/15/Doc.aspx?sourcedoc=%7BB059A3FD-2266-4A44-986E-DAF8D4305725%7D&file=Edmund%20-%20automatic%20weight.xlsx"
#create_general_info_spreadsheet(url)
