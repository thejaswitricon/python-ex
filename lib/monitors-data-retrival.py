import csv
import os
import re
import subprocess
import time
import shutil
import requests

# Define the base directory where you want to search for subdirectories
BASE_DIRECTORY = "../dashboards/dynamic"

# Path to the data.csv file that contains folder names
data_csv_file = os.path.join(BASE_DIRECTORY, "data.csv")

# Check if the data.csv file exists
if os.path.exists(data_csv_file):
    # Read the folder names from data.csv
    folder_names = []
    with open(data_csv_file, mode="r", encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            folder_name = row.get("filename")
            if folder_name:
                folder_names.append(folder_name)
        # Construct the paths for CSV files within the current folder
        CSV_FILE_SOURCE = os.path.join(BASE_DIRECTORY, folder_name, "data-source.csv")
        destination_file = os.path.join(BASE_DIRECTORY, folder_name, "data.csv")
        PROVIDER_TF_PATH = "../terraform/provider.tf"
        DATA_TF_PATH = "data.tf"
        MONITORS_API_ENDPOINT = "https://synthetics.newrelic.com/synthetics/api/v3/monitors"
        BROWSER_APPS_API_ENDPOINT = "https://api.newrelic.com/v2/browser_applications.json"
        PAGE_SIZE = 100  # Number of monitors to retrieve per page
        shutil.copy(CSV_FILE_SOURCE, destination_file)
        APPLICATIONS_API_ENDPOINT = "https://api.newrelic.com/v2/applications.json"
        headers = {
            "Api-Key": os.environ.get("NEW_RELIC_API_KEY")
        }
    # Loop through each folder name and run your script for each folder
    for folder_name in folder_names:

        print(f"Processing CSV files in folder: {folder_name}")
        print(f"CSV_FILE_SOURCE: {CSV_FILE_SOURCE}")
        print(f"destination_file: {destination_file} \n")

        if headers["Api-Key"] is None:
            print("API_KEY environment variable is not set.")
            exit(1)

        def fetch_monitors_by_type(monitor_type):
            """
                fetch_monitors_by_type fetches the monitor through api call
            """
            monitor_offset = 0
            limit = PAGE_SIZE
            monitors_list = []

            while True:
                params = {
                    "offset": monitor_offset,
                    "limit": limit
                }

                response = requests.get(MONITORS_API_ENDPOINT, headers=headers, params=params, timeout=20)
                if response.status_code == 200:
                    monitors_data = response.json().get("monitors")
                    monitors_list.extend([monitor for monitor in monitors_data if monitor.get("type") == monitor_type])

                    if len(monitors_data) < PAGE_SIZE:
                        break
                    monitor_offset += PAGE_SIZE
                else:
                    print(f"Failed to retrieve {monitor_type} monitors")
                    break

            return monitors_list

        # Load CSV data and prepare a list of service names
        service_names = []

        with open(destination_file, mode="r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row["rowType"] == "service":
                    service_names.append(row["serviceName"])

        # Fetch monitors and update CSV file with monitor IDs
        for monitor_types in ["SIMPLE", "CERT_CHECK", "SCRIPT_API", "SCRIPT_BROWSER", "BROWSER"]:
            monitors = fetch_monitors_by_type(monitor_types)
            for monitor in monitors:
                for service_name in service_names:
                    if monitor["name"].startswith(service_name):
                        parts = monitor["name"].split()
                        if len(parts) > 1:
                            service_hash = parts[-1]
                            if service_hash.startswith("#"):
                                with open(destination_file, mode="r", encoding="utf-8") as csv_file:
                                    csv_reader = csv.DictReader(csv_file)
                                    data = list(csv_reader)
                                    for row in data:
                                        if row["serviceName"] == service_name:
                                            if row["rowType"] != "product":
                                                if "#health" in parts and "#ping" in parts and "#critical" in parts:
                                                    row["healthMonitorId"] = monitor["id"]
                                                elif "#ping" in parts and "#critical" in parts:
                                                    row["pingMonitorId"] = monitor["id"]
                                            elif "#script" in parts and "#critical" in parts:
                                                row["scriptMonitorId"] = monitor["id"]
                                with open(destination_file, mode="w", newline="", encoding="utf-8") as csv_file:
                                    fieldnames = data[0].keys()
                                    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                                    csv_writer.writeheader()
                                    csv_writer.writerows(data)
                                break

        # Updating Entity GUIDs and Application_id

        def fetch_application_names(filter_name, offset1):
            """
                fetches aapplications through api call
            """
            params = {
                "filter[name]": filter_name,
                "offset": offset1,
                "limit": PAGE_SIZE
            }

            response = requests.get(APPLICATIONS_API_ENDPOINT, headers=headers, params=params, timeout=20)

            if response.status_code == 200:
                applications_data = response.json().get("applications")
                return applications_data
            else:
                print(f"Failed to retrieve application names for filter: {filter_name}")
                return []

        def update_entity_guids_csv(tf_output):
            """
                updates csv with the entity_guid and helthMonitor_id
            """
            apps_data = {}
            apps_pattern = r'(\S+)\s*=\s*{[^}]*"application_id"\s*=\s*(\d+)[^}]*"guid"\s*=\s*"([^"]+)"[^}]*}'
            matches = re.finditer(apps_pattern, tf_output)
            
            for apps_match in matches:
                key = apps_match.group(1)
                application_id = int(apps_match.group(2))
                guid = apps_match.group(3)
                apps_data[key] = {"application_id": application_id, "guid": guid}

            # Read and update the CSV file
            updated_data = []
            with open(destination_file, 'r', encoding="utf-8") as csvfile:
                apps_csv_reader = csv.DictReader(csvfile)
                apps_fieldnames = apps_csv_reader.fieldnames
                for row1 in apps_csv_reader:
                    apps_service_name = row1.get('serviceName', '')
                    if apps_service_name in apps_data:
                        row1['apmEntityGuid'] = apps_data[apps_service_name]['guid']
                        row1['apmAppId'] = apps_data[apps_service_name]['application_id']
                    updated_data.append(row1)

            # Write the updated data back to the CSV file
            with open(destination_file, 'w', newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=apps_fieldnames)
                writer.writeheader()
                writer.writerows(updated_data)

        if __name__ == "__main__":
            matching_application_guids = {}

            with open(destination_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    service_name = row.get("serviceName")
                    if service_name:
                        offset = 0
                        while True:
                            applications_datas = fetch_application_names(service_name, offset)
                            if not applications_datas:
                                break

                            for app_data in applications_datas:
                                app_name = app_data.get("name")
                                matching_application_guids[app_name] = None
                                print(f"Matching application found: {app_name}")

                            if len(applications_datas) < PAGE_SIZE:
                                break

                            offset += PAGE_SIZE

            if matching_application_guids:
                with open("data.tf", "w", encoding="utf-8") as tf_file:
                    tf_file.write('''
        # Terraform data blocks
        ''')
                    for idx, service_name in enumerate(matching_application_guids, start=1):
                        tf_config = f'''
        data "newrelic_entity" "app_{idx}" {{
        name = "{service_name}"
        domain = "APM"
        }}
        '''
                        tf_output_config = f'''
        output "{service_name}" {{
      value = {{
        guid           = data.newrelic_entity.app_{idx}.guid
        application_id = data.newrelic_entity.app_{idx}.application_id
      }}
    }}
    '''
                        tf_file.write(tf_config)
                        tf_file.write('\n')
                        tf_file.write(tf_output_config)  # Adding output configuration
                        tf_file.write('\n')
                        print(f"Terraform configuration and output added for: {service_name}")

                # Read the content of provider.tf and data.tf
                with open(PROVIDER_TF_PATH, "r", encoding="utf-8") as provider_file, open(DATA_TF_PATH, "r", encoding="utf-8") as data_file:
                    provider_content = provider_file.read()
                    data_content = data_file.read()

                # Concatenate the content of provider.tf and data.tf with provider.tf content first
                combined_content = provider_content + data_content

                # Write the combined content back to data.tf
                with open(DATA_TF_PATH, "w", encoding="utf-8") as data_file:
                    data_file.write(combined_content)
                print("Terraform configurations written to data.tf")
                # Run terraform fmt to format the configuration file
                subprocess.run(['terraform', 'fmt'], check=True)  # nosec
                print("Terraform format check complete.")

                # Run terraform validate to check the configuration's validity
                validate_process = subprocess.run(['terraform', 'validate'], capture_output=True, text=True, check=False)  # nosec
                if validate_process.returncode == 0:
                    print("Terraform validation successful.")
                else:
                    print("Terraform validation failed:")
                    print(validate_process.stdout)
                    print(validate_process.stderr)

                subprocess.run(['terraform', 'init', '-input=false', '-backend=false'], check=True)  # nosec

                time.sleep(5)
                apply_process = subprocess.run(['terraform', 'apply', '-auto-approve', '-input=false'], capture_output=True, text=True, shell=True, check=False)  # nosec
                if apply_process.returncode == 0:
                    apply_output = apply_process.stdout
                    # print(apply_output)

                    def remove_ansi_escape_codes(text):
                        """
                            used to get the output through re
                        """
                        ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
                        return ansi_escape.sub('', text)

                    clean_apply_output = remove_ansi_escape_codes(apply_output)

                    # Define a re pattern to match the content after "0 destroyed.\n\nOutputs:\n\n"
                    PATTERN = r'0 destroyed\.\n\nOutputs:\n\n([\s\S]*)'

                    # Use re.search to find the matched content
                    match = re.search(PATTERN, clean_apply_output)

                    if match:
                        TF_OUTPUTS = match.group(1)
                    else:
                        TF_OUTPUTS = "No TF_OUTPUTS found."
                #pass TF_OUTPUTS to the function
                update_entity_guids_csv(TF_OUTPUTS)

                if os.path.exists('terraform.tfstate'):
                    os.remove('terraform.tfstate')

                if os.path.exists('terraform.tfstate.backup'):
                    os.remove('terraform.tfstate.backup')

                if os.path.exists('data.tf'):
                    os.remove('data.tf')

            else:
                print("No matching application names found")

        # Updating Browser Entity GUIDs

        def fetch_browser_names(filter_name, browser_offset):
            """
                fetch browser apps through api call
            """
            params = {
                "filter[name]": filter_name,
                "offset": browser_offset,
                "limit": PAGE_SIZE
            }

            response = requests.get(BROWSER_APPS_API_ENDPOINT, headers=headers, params=params, timeout=20)

            if response.status_code == 200:
                applications_data = response.json().get("browser_applications")
                return applications_data
            else:
                print(f"Failed to retrieve application names for filter: {filter_name}")
                return []

        def update_browser_guids_csv(browser_TF_OUTPUTS):
            """
                Updates the csv file with browser entity_guid
            """
           # Regular expression pattern
            browser_pattern = r'([^=]+)\s*=\s*"([^"]+)"'

            # Use re.findall to find all key-value pairs
            key_value_pairs = re.findall(browser_pattern, browser_TF_OUTPUTS)
            updated_rows = []
            # Iterate through the rows in the CSV file
            with open(destination_file, 'r', encoding="utf-8") as csvfile:
                browser_reader = csv.DictReader(csvfile)
                for browser_row in browser_reader:
                    browser_service_name = browser_row.get('serviceName', '')
                    updated_row = browser_row.copy()
                    # Iterate through the keys in TF_OUTPUTS
                    for key, value in key_value_pairs:
                        if browser_service_name == key.strip():
                            updated_row['browserEntityGuid'] = value.strip() if browser_row["rowType"] == "service" else ""
                    updated_rows.append(updated_row)

            with open(destination_file, 'w', newline='', encoding="utf-8") as csvfile:
                browser_fieldnames = updated_rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=browser_fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)

        if __name__ == "__main__":
            matching_browser_guid = {}

            with open(destination_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    service_name = row.get("serviceName")
                    row_type = row.get("rowType")
                    if service_name and row_type == "service":
                        OFFSET = 0
                        while True:
                            browser_data = fetch_browser_names(service_name, OFFSET)
                            if not browser_data:
                                break

                            for app_data in browser_data:
                                app_name = app_data.get("name")
                                if service_name != "pj-asc-dashboard-api":
                                    if service_name.lower() == app_name.lower():
                                        matching_browser_guid[app_name] = None
                                        print(f"Matching application found: {app_name}")

                            if len(browser_data) < PAGE_SIZE:
                                break

                            OFFSET += PAGE_SIZE

        if matching_browser_guid:
            with open("data.tf", "w", encoding="utf-8") as tf_file:
                tf_file.write('''
    # Terraform data blocks
    ''')
                for idx, service_name in enumerate(matching_browser_guid, start=1):
                    tf_config = f'''
    data "newrelic_entity" "app_{idx}" {{
    name = "{service_name}"
    domain = "BROWSER"
    }}
    '''
                    tf_output_config = f'''
    output "{service_name}" {{
    value = data.newrelic_entity.app_{idx}.guid
    }}
    '''
                tf_file.write(tf_config)
                tf_file.write('\n')
                tf_file.write(tf_output_config)  # Adding output configuration
                tf_file.write('\n')
                print(f"Terraform configuration and output added for Browser Application: {service_name}")

            # Read the content of provider.tf and data.tf
            with open(PROVIDER_TF_PATH, "r", encoding="utf-8") as provider_file, open(DATA_TF_PATH, "r", encoding="utf-8") as data_file:
                provider_content = provider_file.read()
                data_content = data_file.read()

            # Concatenate the content of provider.tf and data.tf with provider.tf content first
            combined_content = provider_content + data_content

            # Write the combined content back to data.tf
            with open(DATA_TF_PATH, "w", encoding="utf-8") as data_file:
                data_file.write(combined_content)

            print("Terraform configurations written to data.tf")
            
            # Run terraform fmt to format the configuration file
            subprocess.run(['terraform', 'fmt'], check=True)  # nosec
            print("Terraform format check complete.")

            # Run terraform validate to check the configuration's validity
            validate_process = subprocess.run(['terraform', 'validate'], capture_output=True, text=True, check=False)  # nosec  
            if validate_process.returncode == 0:
                print("Terraform validation successful.")
            else:
                print("Terraform validation failed:")
                print(validate_process.stdout)
                print(validate_process.stderr)

            subprocess.run(['terraform', 'init', '-input=false', '-backend=false'], check=True)  # nosec

            time.sleep(5)
            apply_process = subprocess.run(['terraform', 'apply', '-auto-approve', '-input=false'], capture_output=True, text=True, shell=True, check=False)  # nosec
            if apply_process.returncode == 0:
                apply_output = apply_process.stdout
                def remove_browser_ansi_escape_codes(text):
                    """
                        gets output of terraform apply
                    """
                    ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
                    return ansi_escape.sub('', text)

                clean_apply_output = remove_browser_ansi_escape_codes(apply_output)

                # Define a re pattern to match the content after "0 destroyed.\n\nOutputs:\n\n"
                BROWSER_PATTERN = r'0 destroyed\.\n\nOutputs:\n\n([\s\S]*)'

                # Use re.search to find the matched content
                match = re.search(BROWSER_PATTERN, clean_apply_output)

                if match:
                    TF_OUTPUTS = match.group(1)
                else:
                    TF_OUTPUTS = "No TF_OUTPUTS found."
                print(TF_OUTPUTS)
            # Update the CSV based on the TF_OUTPUTS dictionary
            update_browser_guids_csv(TF_OUTPUTS)
            print("CSV updated with GUIDs.")

            if os.path.exists('terraform.tfstate'):
                os.remove('terraform.tfstate')

            if os.path.exists('terraform.tfstate.backup'):
                os.remove('terraform.tfstate.backup')

            if os.path.exists('data.tf'):
                os.remove('data.tf')

else:
    print("data.csv file not found in the dynamic folder")
    
