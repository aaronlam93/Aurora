# After downloading app data, we have the following
import json
import pandas as pd
import os

# Directory containing JSON files
directory = '/Users/aaronlam/Library/CloudStorage/OneDrive-TheUniversityofSydney(Staff)/13. Projects/SDM_MobileApp/999. SOFTWARE/Aurora-Firebase 2/TEST/'
output_directory = os.path.join(directory, 'output')

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

summary_data=[]

# Correct answers dictionary
correct_answers = {
    "ACTOR": "movie", "BLACK": "standing", "BORROW": "circle", "BUYER": "early", "DAWN": "morning", 
    "DIME": "quarter", "DINNER": "food", "FAR": "close", "FEET": "girl", "FORK": "knife", 
    "FORWARD": "outside", "GARBAGE": "can", "GOLD": "money", "GRANDMA": "hour", "GROOM": "minimum", 
    "INCREASE": "call", "INTELLIGENT": "smart", "LEMON": "sour", "MAN": "boy", "MOTHER": "daughter", 
    "NAIL": "finger", "ODD": "uncle", "PLUS": "summer", "PRINCE": "many", "RECKLESS": "full", 
    "RICH": "mail", "SALT": "water", "SHIRT": "innocent", "SISTER": "glass", "SWAMP": "over", 
    "SYRUP": "maple", "TODAY": "yesterday"
}

# Function to extract prompts and responses with study-id and initials
def extract_prompts_responses_with_ids(data, study_id, initials):
    records = []
    trial_completeness = {}
    trial_performance = {}

    for test in data.get("Word-Pair-Tests", []) + data.get("Word-Quad-Tests", []):
        session_id = test.get("session-id")
        description = test.get("description")
        bot_prompts = 0
        correct_responses = 0

        for key, result in test.items():
            if key.startswith("result"):
                user_response = result.get("user", "")
                bot_prompt = result.get("bot", "")
                bot_prompts += 1
                if bot_prompt and bot_prompt in correct_answers and correct_answers[bot_prompt].lower() == user_response.lower():
                    correct_responses += 1
                records.append({
                    "study_id": study_id,
                    "initials": initials,
                    "session_id": session_id,
                    "description": description,
                    "bot_prompt": bot_prompt,
                    "user_response": user_response
                })
        
        if description not in trial_completeness:
            trial_completeness[description] = []
            trial_performance[description] = []
        
        # Adjust bot_prompts to 32 if it is greater than 32
        if bot_prompts > 32:
            bot_prompts = 32
        
        trial_completeness[description].append(bot_prompts)
        trial_performance[description].append(correct_responses)
    
    return records, trial_completeness, trial_performance


# Function to extract demographic data
def extract_demographic_data(data, study_id, initials):
    demographic_keys = ["profile-sleep-tonight", "profile-wakeup-tomorrow", "sleep-last-night", "hours-slept", "sleep-compared-to-normal", "wake-up-today", "birth-year", "gender"]
    demographic_data = {key: data.get(key, "") for key in demographic_keys}
    demographic_data.update({
        "study_id": study_id,
        "initials": initials
    })
    return demographic_data
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath) as f:
            data = json.load(f)
        
        study_id = data.get("study-id", "")
        initials = data.get("initials", "")
        
        # Extract data with study-id and initials
        records_with_ids, trial_completeness, trial_performance = extract_prompts_responses_with_ids(data, study_id, initials)
        
        # Extract demographic data
        demographic_data = extract_demographic_data(data, study_id, initials)
        
        if study_id:
            print(f"Data found for study_id: {study_id}")
        else:
            print(f"No study_id found. Initials: {initials}")
        
        # Combine records into DataFrames
        df_prompts_responses = pd.DataFrame(records_with_ids)
        df_demographic = pd.DataFrame([demographic_data])
        df_trial_completeness = pd.DataFrame.from_dict(trial_completeness, orient='index').transpose()
        df_trial_performance = pd.DataFrame.from_dict(trial_performance, orient='index').transpose()

        # Generate filenames
        base_filename = study_id if study_id else initials
        csv_file_prompts_responses_path = os.path.join(output_directory, f'{base_filename}_responses.csv')
        csv_file_demographic_path = os.path.join(output_directory, f'{base_filename}_demographics.csv')
        csv_file_completeness_path = os.path.join(output_directory, f'{base_filename}_completeness.csv')
        csv_file_performance_path = os.path.join(output_directory, f'{base_filename}_performance.csv')
        
        # Save the DataFrames to CSV files in the output directory
        df_prompts_responses.to_csv(csv_file_prompts_responses_path, index=False)
        df_demographic.to_csv(csv_file_demographic_path, index=False)
        df_trial_completeness.to_csv(csv_file_completeness_path, index=False)
        df_trial_performance.to_csv(csv_file_performance_path, index=False)
        # Append summary data
        summary_entry = {
            "study_id": study_id,
            "initials": initials
        }
        for description in trial_completeness:
            summary_entry[f"{description}_completeness"] = trial_completeness[description][0]  # Assuming one entry per trial
            summary_entry[f"{description}_performance"] = trial_performance[description][0]  # Assuming one entry per trial
        summary_data.append(summary_entry)

        print(f'Processed {filename}')

# Create summary DataFrame and save to CSV
df_summary = pd.DataFrame(summary_data)
summary_csv_path = os.path.join(output_directory, 'summary.csv')
df_summary.to_csv(summary_csv_path, index=False)
print(f'Summary file created at {summary_csv_path}')