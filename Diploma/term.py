import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
import re

session = requests.Session()
URL = 'https://www.wikidata.org/w/api.php'


def get_terminology_annotation(dict):
    text = ''
    pdf_document = f"math.pdf"
    with open(pdf_document, "rb") as filehandle:
        pdf = PdfFileReader(filehandle)

        pages = pdf.getNumPages()
        for i in range(pages):
            page = pdf.getPage(i)
            text += str(page.extractText())

        # lemmatization and tokenization document
        clean_word = []
        arr_of_word = text.split(" ")
        for word in arr_of_word:
            tokenized_word = re.sub("[^0-9а-яА-Яa-zA-Z]+", "", word).lower()
            if tokenized_word != " ":
                clean_word.append(tokenized_word)

        # terminology annotation based on ontology
        duplicate_word = []
        data = []
        for word in clean_word:
            if word in dict:
                if word not in duplicate_word:
                    duplicate_word.append(word)
                    helper_dict = word, get_url_from_wiki(word)
                    data.append(helper_dict)

        for i in range(len(clean_word) - 1):
            word = clean_word[i] + " " + clean_word[i + 1]
            if word in dict:
                if word not in duplicate_word:
                    duplicate_word.append(word)
                    helper_dict = word, get_url_from_wiki(word)
                    data.append(helper_dict)

        for entity in data:
            print(entity)


def get_url_from_wiki(word):
    response = session.post(URL, data={
        'action': 'wbsearchentities',
        'search': word,
        'language': 'en',
        'format': 'json',
    })
    try:
        res_json = response.json()['search'][0]['id']
    except:
        res_json = None
    url = "https://www.wikidata.org/wiki/" + res_json
    return url


def processing_term(term):
    return term.replace("' ", "").replace("'", "").replace("$", "").replace("n-", "").lower()

def main ():
    get_term_annotation_based_on_ontology()

def get_term_annotation_based_on_ontology():
    link = "http://ontomathpro.org/ontology/"
    link2 = "https://sciencewise.info/ontology/"
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('a', href=True)

    terms = []
    dictionary = []

    for result in results:
        terms.append(str(result.text))

    for term in terms:
        dictionary.append(processing_term(term))

    get_terminology_annotation(dictionary)


if __name__ == "__main__":
   main()
