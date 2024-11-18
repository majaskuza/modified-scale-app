# Database with RFID

Database (used in Duan-Erlich lab) to access with a VPN: [http://apoc.deneuro.org:8501/](http://apoc.deneuro.org:8501/)

## Main

### Create New Animal
- `subjid` should follow the convention, e.g., `JLI-R-001`

### Mark Animals' Arrival
- `stattime` if left blank will automatically record the time of submitting the form

### Create New Cage for Animals
- Place all animals that are in that cage, separated by a comma

### Assign Animal RFID
- RFID tagging should occur at least a week after habituation
- Once an animal is injected for scanning, it should be tagged with the animal's RFID
- After tagging, the animal must be weighed every week
  - A Slack bot channel will automatically check the weight every week

To verify that the process has been stored correctly, you can use the Slack Animal bot and Bpod bot, which display the new entries.  
Data from the past 7 days can be pulled into a CSV file and sent via Slack.

## Updating Animal Status

### Put Animals on Water Restriction
- Record the weight, which will be used as the baseline for the animal's water restriction weight
- Weigh the animal with the scale
- Click to update to the latest baseline

### Change Animal Watering Status
- Can change from free water to controlled

### Assign Animals to Existing Cages
- Used to move an animal to an existing or new cage

### Sacrifice Animal
- Marks the animal as deceased

## Mass View (Available After Entering the Animal in the Database)
- Displays the baseline weight
- If you plan to change the restriction status, the animal should be on the list of water-controlled animals
- Under "utility," you can add a comment to note any surgeries performed
- You can select a specific animal by manually adjusting the ending of the URL to the animal's ID

## RFID Information
- The last 4 digits are the ID of the animal
- Order from this website (£1 each): [https://www.doowa-rfid.com/](https://www.doowa-rfid.com/)
- You can email the company to request specific digits you are interested in
