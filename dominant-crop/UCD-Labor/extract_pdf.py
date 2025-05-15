import os
import re
import pdfplumber
import pandas as pd

def extract_total_cultural_costs(pdf_filename, product):
    extracted_data = []
    table_pattern = re.compile(
        r".*UC COOPERATIVE EXTENSION.*\n.*TABLE\s*\d+\.\s*COSTS PER ACRE\s*(.*)", 
        re.IGNORECASE
    )
    
    pdf_path = pdf_filename

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                if "COSTS PER ACRE" in text:
                    lines = text.split("\n")  # Split text into lines
                    purpose = "Unknown"
                    if len(lines) >= 2:
                        second_line = lines[1].strip()
                        purpose_match = re.search(r"COSTS PER ACRE\s*(.*)", second_line, re.IGNORECASE)
                        if purpose_match:
                            purpose = purpose_match.group(1).strip()
                    region, year = "Unknown", "Unknown"
                    if len(lines) >= 3:
                        third_line = lines[2].strip()
                        year_match = re.search(r"(\d{4})", third_line)
                        if year_match:
                            year = year_match.group(1)
                        region = third_line.replace(year, "").strip(" -,")
                    for line in lines:
                        
                        if "TOTAL CULTURAL COSTS" in line:
                            print(f"Page {page.page_number} matched TOTAL CULTURAL COSTS row")
                            numbers_str = line.replace("TOTAL CULTURAL COSTS", "").strip()
                            numbers_str = numbers_str.replace(",", "")

                            print(numbers_str)
                            numbers = list(map(float, numbers_str.split()[:7]))

                            if len(numbers) >= 7: 
                                extracted_data.append({
                                    "Region": region,
                                    "Year": year,
                                    "Product": product,
                                    "Purpose": purpose,
                                    "Time (Hrs./Ac)": numbers[0],
                                    "Labor Cost": numbers[1],
                                    "Fuel": numbers[2],
                                    "Lube & Repairs": numbers[3],
                                    "Material Cost": numbers[4],
                                    "Custom/Rent": numbers[5],
                                    "Total Cost": numbers[6]
                                })

    df = pd.DataFrame(extracted_data)
    if df.empty:
        print("\n⚠️ No data extracted! Check table formatting or text extraction output.\n")
    return df

df = pd.DataFrame()

for item in os.listdir('pdf-files'):
    if item != ".DS_Store":
        print(item)
        item_path = os.path.join('pdf-files', item)
        print(item_path)
        for pdffile in os.listdir(item_path):
            print(os.path.join(item_path, pdffile))
            curr = extract_total_cultural_costs(os.path.join(item_path, pdffile), item)
        
            df = pd.concat([df, curr], ignore_index=True)
            print(curr)
            df.to_csv("UCD-data.csv")