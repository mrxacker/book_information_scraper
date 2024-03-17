import requests
from bs4 import BeautifulSoup
import xlsxwriter
import pandas as pd

MAIN_URL = 'https://gnbookstore.com.tm/'

def get_sections(url):
    section_links = []
    all_data = BeautifulSoup(requests.get(url).content,'html.parser')
    navbar_div = all_data.find('div',class_='row row-cols-2 row-cols-md-3 row-cols-xl-4 g-1')
    for section_link in navbar_div.find_all('a'):
        section_links.append(section_link.get('href'))
        
    return section_links

def get_books_url(url):
    books_urls = []
    try:
        books_data = BeautifulSoup(requests.get(url).content,'html.parser')
        books_div = books_data.find('div', class_="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6 g-4")
        
        books= books_div.find_all('div', class_='col')
        
        for book in books:
            books_urls.append(book.find_all('a')[-1].get('href'))
    except:
        print(f'Some error with {url} link')
        
    return books_urls

def get_book_info(url):
    book_info = {}
    book_data = BeautifulSoup(requests.get(url).content,'html.parser')
    
    book_title = book_data.find('div', class_='h4 mb-2 mb-sm-3').text.strip()
    book_info['title']=book_title
    
    book_image = book_data.find('a', class_='btn btn-light btn-sm').get('href').split('/')[-1]
    book_info['image']=book_image
    
    
    # get all information DIVs
    all_h6 = book_data.find('div', class_='row g-4 mb-2 mb-sm-3').find_all('div', class_='h6')
    
    
    # split information inside H6 class DIVs
    for info in all_h6:
        try:
            book_info_key = info.find('span').text.strip()
            
            if len(info.find_all('a')) > 0:
                for i in info.find_all('a'):
                    if book_info_key in book_info:
                        book_info[book_info_key]+=', '+(i.text.strip())
                    else:
                        book_info[book_info_key]=(i.text.strip())
            else:
                if len(info.contents[2].text.strip()) > 0:
                    book_info[book_info_key]=(info.contents[2].text.strip())
        except:
            pass  
        
         
    return book_info


all_info=[]
num = 1
total = len( get_sections(MAIN_URL))
for section_url in get_sections(MAIN_URL):
    print(f'{num} of {total}')
    for book_url in get_books_url(section_url):
        all_info.append(get_book_info(book_url))
    num+=1
    
def convert_to_df(data):
    book_df = pd.DataFrame(data)

    book_df.loc[book_df["Awtorlar:"].isna(),"Awtorlar:"] = book_df["Awtor:"]
    book_df.loc[book_df["Kategoriýalar:"].isna(),"Kategoriýalar:"] = book_df["Kategoriýa:"]

    book_df.drop('Awtor:',axis=1, inplace=True)
    book_df.drop('Kategoriýa:',axis=1, inplace=True) 
    
    return book_df
    
convert_to_df(all_info).to_excel('All_inf.xlsx')


    

