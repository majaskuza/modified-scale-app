
#saving the output of the scale recording into a google spread sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope of the application
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load the credentials from the JSON key file
creds = ServiceAccountCredentials.from_json_keyfile_name('path/to/your/credentials.json', scope)

# Authorize the gspread client
client = gspread.authorize(creds)

# Open the Google Sheet by name
sheet = client.open("Your Google Sheet Name").sheet1  # You can also use .get_worksheet(index) if you have multiple sheets

# Example of writing data to the sheet
data = [
    ["Weight", "Time"],  # Headers
    [25.3, "2024-10-14 10:00"],  # Sample data
    [30.1, "2024-10-14 10:05"],
]
for row in data:
    sheet.append_row(row)  # Append each row to the Google Sheet

# Example of reading data from the sheet
all_data = sheet.get_all_records()  # Get all records as a list of dictionaries
print(all_data)  # Print the data read from the Google Sheet