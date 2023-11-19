import csv
import string

input_file = 'cleaned_dataset.csv'
output_file = 'data_lower.csv'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        lowered = [x.lower() for x in row]
        writer.writerow(lowered)