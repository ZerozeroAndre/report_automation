#
import pandas as pd
import re
from itertools import cycle
from itertools import tee
from PyPDF2 import PdfFileReader
from pdfreader import SimplePDFViewer
import pandas as pd



pdf_file_name = "7035  AS FRANZISKA.pdf"


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

# Load the pdf to the PdfFileReader object with default settings
with open(pdf_file_name, "rb") as pdf_file:
    pdf_reader = PdfFileReader(pdf_file)
    pdf_pages = pdf_reader.numPages
    
fd = open(pdf_file_name, "rb")
viewer = SimplePDFViewer(fd)
viewer.render()
    
# extract text from pdf
sum_text = []
for i in range(pdf_pages):
    viewer.navigate(i + 1)
    viewer.render()
    sum_text  += viewer.canvas.strings
    

# CLEAN    
    
# Remove KPP numbers

r = re.compile('(INN|KPP|TRRC)', re.IGNORECASE)
words_counter_0 = 0

for line in sum_text:
    #print(line)
    if r.match(line) is not None:
        #print(sum_text[words_counter_0])
        #print(sum_text[words_counter_0 + 1])
        #print(words_counter)
        del sum_text[words_counter_0 + 1]

    words_counter_0 += 1
    
words_counter_1 = 0



words_counter_3 = 0

for line in sum_text:
    #print(line)
    if line.find('INN') > -1:
        
        #print(sum_text[words_counter - 1])
        #print(sum_text[words_counter])
        #print(" ", sum_text[words_counter + 1])
        #print(" ", sum_text[words_counter + 2])
        #print(words_counter)
        del sum_text[words_counter_3]
        del sum_text[words_counter_3 + 1]

    
    words_counter_3 += 1

    
words_counter_1 = 0

for line in sum_text:

    if line.find('KPP') > -1:

        del sum_text[words_counter_1]
        del sum_text[words_counter_1 + 1]
        #print(sum_text[words_counter_1])
    
    words_counter_1 += 1    
    

# OGRN
words_counter_2 = 0

for line in sum_text:
    #print(line)
    if line.find('OGRN') > -1:
        
        #print(sum_text[words_counter - 1])
        #print(sum_text[words_counter])
        #print(" ", sum_text[words_counter + 1])
        #print(" ", sum_text[words_counter + 2])
        #print(words_counter)
        del sum_text[words_counter_2]
        del sum_text[words_counter_2 + 1]
        del sum_text[words_counter_2 + 2]
        #print("--------------")
    
    words_counter_2 += 1    
    
# Remove garbage words    
r = re.compile('Страница|Количество|В том числе')
words_counter = 0

for line in sum_text:
    if r.match(line) is not None:
        del sum_text[words_counter]

    words_counter += 1
    
# Vessel
document_end = len(sum_text)
vessel_border = []
vessel_names = []
bill_names = []
bill_border = []
container_border = []
container_type_border = []
description_border = []


#print("END", document_end)

# VESSEL 
vessel_counter = 0
r = re.compile('VESSEL')
for line in sum_text:
    if r.match(line) is not None:
        #print(sum_text[vessel_counter + 1])
        vessel_names.append(sum_text[vessel_counter + 1])
        vessel_border.append(vessel_counter + 1)

    vessel_counter += 1

    if vessel_counter == document_end:
        vessel_border.append(document_end)
        
#print("Vessel Border: ", vessel_border)


# BILL OF LADING
bill_counter = 0
for line_2 in sum_text:

    r = re.compile('(^\d{9}$|^[a-zA-Z]{3}\d{6}$|^[a-zA-Z]{6}\d{3}$|\d{8}[a-zA-Z]{1})')


    if r.match(line_2) is not None:
        #print("Bill of Lading:", sum_text[bill_counter])
        bill_border.append(bill_counter)
        bill_names.append(sum_text[bill_counter])

    bill_counter += 1
    
    if bill_counter == document_end:
        bill_border.append(document_end)
        
#print("Bill Border: ", bill_border)    

# CONTAINER
container_counter = 0
for line_3 in sum_text:

        r = re.compile('^[a-zA-Z]{3}[uUjJzZ]{1}[0-9]{7}$')

        if r.match(line_3) is not None:
            #print(sum_text[container_counter])
            container_border.append(container_counter)

        container_counter += 1
        
        if container_counter == document_end:
            container_border.append(document_end)
            
#print("Bill Border: ", container_border)


# DESCRIPTION
description_counter = 0
for line_4 in sum_text:

        r = re.compile('[ЁёА-я]')

        if r.match(line_4) is not None:
            #print(sum_text[description_counter])
            description_border.append(description_counter)

        description_counter += 1
        
        if description_counter == document_end:
            description_border.append(document_end)
            
#print("Description Border: ", description_border)
result = {'Type/Size': [],
        'Description': [],
        'Vessel': [],
        'Container Number': [],
        'Bill of Lading': [],
        }

df_result = pd.DataFrame(result, columns= ['Type/Size', 'Description', 'Vessel', 'Container Number', 'Bill of Lading'])


for i, nextelem in pairwise(vessel_border):
    #print("Vessel Bording ---", i, "+++", nextelem)
    print("Vessel: ", sum_text[i])
    for i_1, nextelem_1 in pairwise(bill_border):
        #print("Bill Bording---", i_1, "+++", nextelem_1)
        if i < i_1 < nextelem:
            bill_name = sum_text[i_1]
            print("Bill of Lading: ",bill_name)
            for i_3, nextelem_3 in pairwise(description_border):
                        if i_2 < i_3 < nextelem_2:
                            descriptoin_name = sum_text[i_3]
                            print("Description: ", descriptoin_name)
                            for i_2, nextelem_2 in pairwise(container_border):
                                if i_1 < i_2 < nextelem_1:
                                    container_name = sum_text[i_2]
                                    container_type = sum_text[i_2 + 1]
                                    print("Container: ",container_name, "Container type: ", container_type)
                    
                            
                                    result = {'Type/Size': container_type,
                                            'Description': descriptoin_name,
                                            'Vessel': sum_text[i],
                                            'Container Number': container_name,
                                            'Bill of Lading': bill_name,
                                            }
                                    df_result = df_result.append(result, ignore_index=True)