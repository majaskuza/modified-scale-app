import pandas as pd

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

def add_recording_entry(url, subjid, training_start, weight, animal_fed_at, training_end):
    try:
        df = pd.read_excel(url, engine='openpyxl')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Date', 'Subjid', 'Training Start', 'Training End', 'Animal Fed At', 'Food Amount', 'Percent', 'Weight'])
    percent = 0.8 * weight
    new_entry = {
        'Date': pd.Timestamp.now().date(),
        'Subjid': subjid,
        'Training Start': training_start,
        'Training End': training_end,
        'Animal Fed At': '', #  blank for manual entry
        'Food Amount': '',  
        'Percent': percent,
        'Weight': weight
    }
    df = df.append(new_entry, ignore_index=True)
    df.to_excel(url, index=False, engine='openpyxl')



#example usage of above functions
url = "https://liveuclac.sharepoint.com/sites/swcpil/_layouts/15/Doc.aspx?sourcedoc=%7BB059A3FD-2266-4A44-986E-DAF8D4305725%7D&file=Edmund%20-%20automatic%20weight.xlsx"
create_general_info_spreadsheet(url)
add_recording_entry(url, subjid='HAA-1105431', training_start='2024-10-22', weight=320, animal_fed_at='', training_end='')
