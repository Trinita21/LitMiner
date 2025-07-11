import psycopg2
import xml.etree.ElementTree as ET
from lxml import etree

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres.pihlfdrrtlaldotjllez",
    password="K+#.2tdxRE8L27h",
    host="aws-0-eu-central-1.pooler.supabase.com",
    port="6543"
)

cursor = conn.cursor()

## Extract & Encode Result into XML

def books_to_xml(books):
    root = ET.Element("Books")
    for book in books:
        book_elem = ET.SubElement(root, "Book")
        ET.SubElement(book_elem, "BookID").text = book[0]
        ET.SubElement(book_elem, "Title").text = book[1]
        ET.SubElement(book_elem, "Description").text = book[2]
    return ET.tostring(root, encoding="unicode")


search_term ='love'    #input("Enter search term: ")

cursor.execute("""
    SELECT "BookID", "title", "description"
    FROM "Book"
    WHERE to_tsvector('english', "description") @@ to_tsquery(%s)
""", (search_term.replace(' ', ' & '),))
results = cursor.fetchall()
xml_output = books_to_xml(results)
print('results', results)
print('xml_output', xml_output)

## Query the XML using XPath

tree = etree.fromstring(xml_output)

# Find all book titles
titles = tree.xpath('//Book/Title/text()')
print(titles)

# Find book descriptions containing “robot”
robot_books = tree.xpath('//Book[contains(Description, "robot")]/Title/text()')

with open("search_results.xml", "w", encoding="utf-8") as f:
    f.write(xml_output)