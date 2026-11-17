{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 \
# ==========================================\
# ETL PROJECT - LARGEST BANKS\
# ==========================================\
\
# Import required libraries\
\
import requests\
from bs4 import BeautifulSoup\
import pandas as pd\
import numpy as np\
import sqlite3\
from datetime import datetime\
\
\
# ==========================================\
# TASK 1: LOG PROGRESS\
# ==========================================\
\
def log_progress(message):\
    '''Logs the progress of the ETL process.'''\
\
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")\
\
    with open("/home/project/code_log.txt", "a") as file:\
        file.write(f"\{timestamp\} : \{message\}\\n")\
\
\
# ==========================================\
# TASK 2: EXTRACT DATA\
# ==========================================\
\
def extract(url, table_attribs):\
    '''Extracts bank market capitalization data.'''\
\
    response = requests.get(url, timeout=30)\
    response.raise_for_status()\
\
    soup = BeautifulSoup(response.text, "lxml")\
\
    heading = soup.find(id="By_market_capitalization")\
\
    if heading is None:\
        raise ValueError("Market capitalization heading not found")\
\
    table = heading.find_next("table")\
\
    if table is None:\
        raise ValueError("Market capitalization table not found")\
\
    data = []\
\
    for row in table.find_all("tr")[1:]:\
        columns = row.find_all("td")\
\
        if len(columns) >= 3:\
            bank_name = columns[1].get_text(strip=True)\
            market_cap = columns[2].get_text(strip=True)\
            market_cap = float(market_cap.replace(",", ""))\
\
            data.append([bank_name, market_cap])\
\
    df = pd.DataFrame(data, columns=table_attribs)\
\
    return df\
\
\
# ==========================================\
# TASK 3: TRANSFORM DATA\
# ==========================================\
\
def transform(df, csv_path):\
    '''Converts market capitalization into GBP, EUR and INR.'''\
\
    exchange_rate_df = pd.read_csv(csv_path)\
\
    exchange_rate = exchange_rate_df.set_index(\
        "Currency"\
    ).to_dict()["Rate"]\
\
    gbp_rate = float(exchange_rate["GBP"])\
    eur_rate = float(exchange_rate["EUR"])\
    inr_rate = float(exchange_rate["INR"])\
\
    df["MC_GBP_Billion"] = [\
        np.round(x * gbp_rate, 2)\
        for x in df["MC_USD_Billion"]\
    ]\
\
    df["MC_EUR_Billion"] = [\
        np.round(x * eur_rate, 2)\
        for x in df["MC_USD_Billion"]\
    ]\
\
    df["MC_INR_Billion"] = [\
        np.round(x * inr_rate, 2)\
        for x in df["MC_USD_Billion"]\
    ]\
\
    return df\
\
\
# ==========================================\
# TASK 4: LOAD DATA TO CSV\
# ==========================================\
\
def load_to_csv(df, output_path):\
    '''Saves the DataFrame to a CSV file.'''\
\
    df.to_csv(output_path, index=False)\
\
\
# ==========================================\
# TASK 5: LOAD DATA TO DATABASE\
# ==========================================\
\
def load_to_db(df, sql_connection, table_name):\
    '''Saves the DataFrame to a SQL database table.'''\
\
    df.to_sql(\
        table_name,\
        sql_connection,\
        if_exists="replace",\
        index=False\
    )\
\
\
# ==========================================\
# TASK 6: RUN SQL QUERIES\
# ==========================================\
\
def run_query(query_statement, sql_connection):\
    '''Executes an SQL query and prints its results.'''\
\
    print("\\nSQL Query:")\
    print(query_statement)\
\
    query_output = pd.read_sql_query(\
        query_statement,\
        sql_connection\
    )\
\
    print("\\nQuery Result:")\
    print(query_output)\
\
\
# ==========================================\
# MAIN ETL PROCESS\
# ==========================================\
\
if __name__ == "__main__":\
\
    # Define initial variables\
\
    url = (\
        "https://web.archive.org/web/20230908091635/"\
        "https://en.wikipedia.org/wiki/List_of_largest_banks"\
    )\
\
    table_attribs = ["Name", "MC_USD_Billion"]\
\
    csv_path = "/home/project/exchange_rate.csv"\
    output_path = "/home/project/Largest_banks_data.csv"\
\
    database_path = "/home/project/Banks.db"\
    table_name = "Largest_banks"\
\
    # TASK 1: Initialize ETL process\
\
    log_progress(\
        "Preliminaries complete. Initiating ETL process"\
    )\
\
    # TASK 2: Extract data\
\
    df = extract(url, table_attribs)\
\
    log_progress(\
        "Data extraction complete. Initiating Transformation process"\
    )\
\
    # TASK 3: Transform data\
\
    df = transform(df, csv_path)\
\
    log_progress(\
        "Data transformation complete. Initiating Loading process"\
    )\
\
    # TASK 4: Load data to CSV\
\
    load_to_csv(df, output_path)\
\
    log_progress(\
        "Data saved to CSV file"\
    )\
\
    # TASK 5: Connect to SQLite database\
\
    sql_connection = sqlite3.connect(database_path)\
\
    log_progress(\
        "SQL connection initiated"\
    )\
\
    # Load data into database\
\
    load_to_db(df, sql_connection, table_name)\
\
    log_progress(\
        "Data loaded into the database as a table. Executing queries"\
    )\
\
    # TASK 6: Run SQL queries\
\
    # Query 1: Display the entire table\
\
    run_query(\
        "SELECT * FROM Largest_banks",\
        sql_connection\
    )\
\
    # Query 2: Calculate average market capitalization in GBP\
\
    run_query(\
        "SELECT AVG(MC_GBP_Billion) FROM Largest_banks",\
        sql_connection\
    )\
\
    # Query 3: Display the first five bank names\
\
    run_query(\
        "SELECT Name FROM Largest_banks LIMIT 5",\
        sql_connection\
    )\
\
    log_progress(\
        "Process Complete"\
    )\
\
    # Close SQL connection\
\
    sql_connection.close()\
\
    log_progress(\
        "Server connection closed"\
    )\
}