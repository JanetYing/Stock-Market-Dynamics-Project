import re
import csv
import pandas as pd
import numpy as np
import os
import PyPDF2
output_directory  = r'C:\Users\Janet\OneDrive - The University of Chicago\Data_policy\final-project-janet'
input_directory = r'C:\Users\Janet\OneDrive - The University of Chicago\Data_policy\final-project-janet\data\pdf_raw_data'



def convert_pdfs_to_texts(file_names):
    for file_name in file_names:
        file_name = file_name + ".pdf"

        path = os.path.join(input_directory, file_name)

        output_file_name = os.path.splitext(file_name)[0] + '.txt'
        output_path = os.path.join(input_directory, output_file_name)

        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            with open(output_path, 'w', encoding='utf-8') as text_file:
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text_file.write(page.extract_text() + '\n')

def clean_data(file_names):
    for file_name in file_names:
        txt_file_name = file_name + ".txt"
        output_path = os.path.join(input_directory, txt_file_name)

        with open(output_path, "r", encoding='utf-8') as file:
            lines = file.readlines()

        #remove rows without parathesis or ending with capital letter
        with open(output_path, "w", encoding='utf-8') as file:
            for line in lines:
                if "(" in line or ")" in line:
                    if line.strip() and line.strip()[-1].isupper():
                        file.write(line)

        df = pd.read_csv(output_path, header=None)
        df_filtered = df[df.apply(lambda row: 'United States' in row[0], axis=1)]
        df_filtered.to_csv(output_path, index=False, header=False)

file_names = ['businessServices','computer_services','consumer_services','diversified_holding','general_services' ,'shell_companies', #sector -- business/consumer services
              'computer_consumerElectronics', 'emerging_technologies','internet_online','networking','semiconductors','software' ]#sector -- technology
convert_pdfs_to_texts(file_names)
clean_data(file_names)



def extract_data_to_dataframe(file_path, input_directory):
    txt_file_name = file_path + ".txt"
    path = os.path.join(input_directory, txt_file_name)
    data = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.search(r'\((.*?)\).*?United States\s+([A-Z]+\s*[A-Z]+)', line)
            if match:
                ticker = match.group(1)
                exchange = match.group(2).replace(' ', '')
                data.append({'ticker': ticker, 'exchange': exchange})

    df = pd.DataFrame(data)
    df['industry'] = file_path
    return df

def process_files(file_names, input_directory):
    dfs = []
    for file_name in file_names:
        df = extract_data_to_dataframe(file_name, input_directory)
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


final_df = process_files(file_names, input_directory)

business_consumer_services = ['businessServices', 'computer_services', 'consumer_services', 'diversified_holding', 'general_services', 'shell_companies']
technology = ['computer_consumerElectronics', 'emerging_technologies', 'internet_online', 'networking', 'semiconductors', 'software']

# Use numpy.select to assign the new sector values
conditions = [
    final_df['industry'].isin(business_consumer_services),
    final_df['industry'].isin(technology)
]
choices = ['businessConsumer_services', 'technology']

final_df['sector'] = np.select(conditions, choices, default='Other')

output_path = os.path.join(output_directory, 'output.csv')

final_df.to_csv(output_path, index=False)

