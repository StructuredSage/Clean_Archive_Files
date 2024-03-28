import sys
import os
import datetime
import json
import fsutil

#Get the environment from command line
#environment = "UAT"
environment = sys.argv[1]
location = sys.argv[2]

# Configure logging for ActiveBatch
def print_message(message, dir, exception):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    format_dir = f'"{dir}"'
    format_exception = f'{exception}' if exception is not None else ''
    error_message = f'{message} {format_dir} {format_exception}'
    print(f'{timestamp} - {error_message}')

# Check of config file exists
config_filename = f"config_{environment}.json"
config_file = fsutil.join_filepath(location, config_filename)

if not fsutil.exists(config_file):
    print_message("Config file", config_file, "not foud")
    sys.exit(1)

#read the config file
with open(config_file, "r") as f:
    config = json.load(f)

# Filter the paths based on Active flag
active_paths = [path for path in config.get(os.name) if path.get("Active",True)]

# loop through each row of the data and delete files and folder older than DeleteAfterDays
for row in active_paths:
    full_path = row["FullPath"]
    delete_after_days = row["DeleteAfterDays"]
    if fsutil.exists(full_path):
        for dir in fsutil.list_dirs(full_path):
            dir_age = datetime.datetime.now() - fsutil.get_dir_last_modified_date(dir)
            if dir_age.days > delete_after_days:
                try:
                    fsutil.delete_dir(dir)
                    print_message("Deleted Folder ", dir, None)
                except Exception as e:
                    print_message("Error Deleted Folder ", dir, str(e))
        for file in fsutil.list_files(full_path):
            file_age = datetime.datetime.now() - fsutil.get_file_last_modified_date(file)
            if file_age.days > delete_after_days:
                try:
                    fsutil.delete_file(file)
                    print_message("Deleted File ", dir, None)
                except Exception as e:
                    print_message("Error Deleted File ", dir, str(e))
    else:
        print_message("Path does not exist: ",full_path, None);


sys.exit(0)