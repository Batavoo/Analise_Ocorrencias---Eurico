import pandas as pd

# Read the CSV file
df = pd.read_csv('planilha_ocorrencias_tratadas_as_csv.csv', encoding='utf-8')


# Display the first few rows
print(df.head())
