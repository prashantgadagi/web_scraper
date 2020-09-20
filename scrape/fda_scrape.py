import requests
import csv
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

fda_url = "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm"

# opening a connection
uClient = uReq(fda_url)
page_html = uClient.read();
uClient.close()

filename = "fds_records.csv"
with open(filename, 'w') as csv_file:
    csvwriter = csv.writer(csv_file)
    # html parsing to get all CFR title options
    page_soup = soup(page_html, "html.parser")
    options = page_soup.find("select")
    option = options.contents[1]
    # contains all the child pages
    post_list = []
    while option is not None:
        val = int(option.attrs['value'])
        if val != 0:
            post_list.append(val)
        if len(option.contents) > 1:
            option = option.contents[1]
        else:
            option = None

    # Iterate for each post
    for part in post_list:
        post_url = "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm"
        data = {"CFRPart": part, "Search": "search"}
        response = requests.post(post_url, data)
        page_soup = soup(response.text, "html.parser")
        column1 = page_soup.table.tr.td.table.findAll("tr")[3].div.find("a").text
        items = page_soup.table.tr.td.table.findAll("tr")[3].findAll("td")[0].findAll("strong")
        for item in items:
            if item.a is not None:
                data = item.a['href'].split('?')[1]
                response = requests.get(post_url, data)
                page_soup = soup(response.text, "html.parser")
                # all_rows = page_soup.table.tr.td.table.findAll("tr")
                all_rows = list(page_soup.table.tr.td.table.children)
                row_counter = 0
                while row_counter < len(all_rows):
                    if all_rows[row_counter] == '\n':
                        row_counter += 1
                        continue
                    if all_rows[row_counter].strong is not None:
                        break
                    row_counter += 1
                column2 = all_rows[row_counter].strong.text.strip().split('--')[1]
                for row_num in range(row_counter, len(all_rows)):
                    row = all_rows[row_num]
                    if row is not None and row != '\n' and len(row.findAll("table")) >= 2:
                        table1 = row.findAll("table")[0]
                        text_arr = table1.tr.td.text.strip().split(' ')
                        column3 = text_arr[1:][0]
                        column4 = " ".join(text_arr[1:][1:])
                        column5 = " ".join(list(row.findAll("table")[1].strings)).strip().replace("\n", "")
                        fields = [column1, column2, column3, column4, column5]
                        csvwriter.writerow(fields)