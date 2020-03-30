from bs4 import BeautifulSoup
import csv
import datetime
import pdfplumber
import re
import requests

url = 'https://govstatus.egov.com/coronavirus'


def get_pdf_link():
    response = requests.get(url)
    parser = BeautifulSoup(response.content, 'html.parser')
    pdf_link = parser.find('a', text = re.compile('(COVID-19 Public Update)'))
    
    return pdf_link['href']

def download_pdf(link):
    response = requests.get(link)
    with open('pdf/{}.pdf'.format(datetime.date.today()), 'wb') as f:
        f.write(response.content)

def parse_pdf():
    pdf_path = 'pdf/{}.pdf'.format(datetime.date.today())
    reader = pdfplumber.open(pdf_path)
    page = sanitize(reader.pages[0].extract_text())
    table = [chunk(row.strip().split(' ')) for row in page.split('County Number ')[-1].split('\n') if valid(row)]

    return flatten_and_sort(table)

def write_table_to_csv(table):
    with open('cases.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        for row in table:
            writer.writerow(row)

def sanitize(page):
    return re.sub(re.compile(r' +'), ' ', page)

def chunk(lst):
    return [list(chunk) for chunk in zip(*[iter(lst)]*2)]

def flatten_and_sort(lst):
    flat_list = []
    for sublist in lst:
        for item in sublist:
            item.append(datetime.date.today().strftime('%x'))
            flat_list.append(item)

    flat_list.sort(key=lambda entry: entry[0])

    return flat_list

def valid(row):
    try:
        if row.strip() == '':
            return False

        for entry in chunk(row.strip().split(' ')):
            if str(int(entry[1])) != entry[1]:
                return False

        return True
    except:
        return False

if __name__ == '__main__':
    pdf_link = get_pdf_link()
    download_pdf(pdf_link)
    table = parse_pdf()
    write_table_to_csv(table)