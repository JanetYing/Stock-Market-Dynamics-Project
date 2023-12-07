import os
import re
import pandas as pd
import numpy as np
import PyPDF2

# Global Constants
OUTPUT_DIRECTORY = r'C:\Users\Janet\OneDrive - The University of Chicago\Data_policy\final-project-janet\data'
INPUT_DIRECTORY = r'C:\Users\Janet\OneDrive - The University of Chicago\Data_policy\final-project-janet\data\pdf_raw_data'
FILE_NAMES = ['business_services', 'computer_services', 'consumer_services', 'diversified_holding', 'general_services', 'shell_companies',
              'consumer_electronics', 'emerging_technologies', 'internet_online', 'networking', 'semiconductors', 'software']

def convert_pdfs_to_texts(file_names, input_directory):
    """Converts a list of PDF files to text files."""
    for file_name in file_names:
        path = os.path.join(input_directory, f"{file_name}.pdf")
        output_path = os.path.join(input_directory, f"{os.path.splitext(file_name)[0]}.txt")

        with open(path, 'rb') as file, open(output_path, 'w', encoding='utf-8') as text_file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text_file.write(page.extract_text() + '\n')

def clean_data(file_names, input_directory):
    """Cleans text data in specified files."""
    for file_name in file_names:
        path = os.path.join(input_directory, f"{file_name}.txt")

        with open(path, "r", encoding='utf-8') as file:
            lines = [line for line in file if "(" in line or ")" in line and line.strip()[-1].isupper()]

        df = pd.DataFrame(lines)
        df_filtered = df[df[0].str.contains('United States')]
        df_filtered.to_csv(path, index=False, header=False)

def extract_data_to_dataframe(file_path, input_directory):
    """Extracts data from a text file and returns a DataFrame."""
    path = os.path.join(input_directory, f"{file_path}.txt")
    data = []

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.search(r'\((.*?)\).*?United States\s+([A-Z]+\s*[A-Z]+)', line)
            if match:
                data.append({'ticker': match.group(1), 'exchange': match.group(2).replace(' ', ''), 'industry': file_path})

    return pd.DataFrame(data)

def process_files(file_names, input_directory):
    """Processes a list of files and concatenates their data into a single DataFrame."""
    return pd.concat([extract_data_to_dataframe(file_name, input_directory) for file_name in file_names], ignore_index=True)

def assign_sectors(df):
    """Assigns sectors to the DataFrame based on industry."""
    business_consumer_services = ['business_services', 'computer_services', 'consumer_services', 'diversified_holding', 'general_services', 'shell_companies']
    technology = ['consumer_electronics', 'emerging_technologies', 'internet_online', 'networking', 'semiconductors', 'software']

    conditions = [df['industry'].isin(business_consumer_services), df['industry'].isin(technology)]
    choices = ['businessConsumer_services', 'technology']
    df['sector'] = np.select(conditions, choices, default='Other')

def main():
    """Main function to execute the data processing workflow."""
    convert_pdfs_to_texts(FILE_NAMES, INPUT_DIRECTORY)
    clean_data(FILE_NAMES, INPUT_DIRECTORY)
    final_df = process_files(FILE_NAMES, INPUT_DIRECTORY)
    assign_sectors(final_df)

    output_path = os.path.join(OUTPUT_DIRECTORY, 'processed_text.csv')
    final_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()
