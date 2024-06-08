import os
import json

file_path = '../WebUI/public/log/newlastnewlatestnewtest.json'

# Load existing progress data
# progress = {}

# if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
#     with open(file_path, 'r') as file:
#         progress = json.load(file)


# Update progress
progress={
    "stage": "preCheck",
    "progress": 0.2
}

# Save updated progress data
with open(file_path, 'w') as file:
    json.dump(progress, file)

# Print the stage
print(progress["stage"])
