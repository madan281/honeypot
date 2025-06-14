# Import library dependencies.
import pandas as pd
import re
import requests

# This file parses the various log files. The log files have different "formats" or information provided, so needed to create unique parsers for each.
# Each of these parsers takes the log file, gathers the specific information provided in the log, then returns the data in columns/rows Pandas dataframe type.

# Parser for the creds file. Returns IP Address, Username, Password.
def parse_creds_audits_log(creds_audits_log_file):
    data = []

    with open(creds_audits_log_file, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            if len(parts) == 5:
                timestamp, ip_address, username, password, country = parts
                data.append([timestamp, ip_address, username, password, country])

    df = pd.DataFrame(data, columns=["timestamp", "ip_address", "username", "password", "country"])
    return df


# Parser for commands entered during SSH session.
def parse_cmd_audits_log(cmd_audits_log_file):

    data = []
    
    with open(cmd_audits_log_file, 'r') as file:
         for line in file:
            match = re.search(r"\[(.*?)\] Command b'(.*?)' executed by (.*?)$", line)
            if match:
                timestamp, command, ip = match.groups()
                data.append({
                    "timestamp": timestamp,
                    "ip": ip,
                    "command": command
                })
    return pd.DataFrame(data)
# Calculator to generate top 10 values from a dataframe. Supply a column name, counts how often each value occurs, stores in "count" column, then return dataframe with value/count.
def top_10_calculator(dataframe, column):

    for col in dataframe.columns:
        if col == column:
            top_10_df = dataframe[column].value_counts().reset_index().head(10)
            top_10_df.columns = [column, "count"]

    return top_10_df

# Takes an IP address as string type, uses the Cleantalk API to look up IP Geolocation.
def get_country_code(ip):

    data_list = []
    # According to the CleanTalk API docs, API calls are rate limited to 1000 per 60 seconds.
    url = f"https://api.cleantalk.org/?method_name=ip_info&ip={ip}"
    try:
        response = requests.get(url)
        api_data = response.json()
        if response.status_code == 200:
            data = response.json()
            ip_data = data.get('data', {})
            country_info = ip_data.get(ip, {})
            data_list.append({'IP Address': ip, 'Country_Code': country_info.get('country_code')})
        elif response.status_code == 429:
            print(api_data["error_message"])
            print(f"[!] CleanTalk IP->Geolocation Rate Limited Exceeded.\n Please wait 60 seconds or turn Country=False (default).\n {response.status_code}")
        else:
            print(f"[!] Error: Unable to retrieve data for IP {ip}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"[!] Request failed: {e}")

    return data_list

# Takes a dataframe with the IP addresses, converts each IP address to country geolocation code.
def ip_to_country_code(dataframe):

    data = []

    for ip in dataframe['ip_address']:
        get_country = get_country_code(ip)
        parse_get_country = get_country[0]["Country_Code"]
        data.append({"IP Address": ip, "Country_Code": parse_get_country})
    
    df = pd.DataFrame(data)
    return df
def read_creds():
    try:
        df = parse_creds_audits_log("log_files/creds_audits.log")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        return []

def read_cmds():
    try:
        df = parse_cmd_audits_log("log_files/commands.log")
        return df["Command"].tolist() if "Command" in df else []
    except FileNotFoundError:
        return []
