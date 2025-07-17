import psycopg2
import xml.etree.ElementTree as ET
from lxml import etree
import streamlit as st
import re

# --- DB Connection ---
@st.cache_resource
def connect_db():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres.pihlfdrrtlaldotjllez",
        password="K+#.2tdxRE8L27h",
        host="aws-0-eu-central-1.pooler.supabase.com",
        port="6543"
    )

conn = connect_db()
cursor = conn.cursor()

# --- XML Conversion ---

def clean_text(text):
    if text:
        return text.replace('\r\n', '\n').replace('\r', '\n').strip()
    return ""

def clean_description(text):
    # Remove leading/trailing whitespace
    text = text.strip()
    # Replace multiple newlines and spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Optional: wrap long text if you want formatting (for terminal or basic HTML)
    return text

def books_to_xml(books):
    root = etree.Element("Books")
    for book in books:
        book_elem = etree.SubElement(root, "Book")
        etree.SubElement(book_elem, "BookID").text = book[0]
        etree.SubElement(book_elem, "Title").text = clean_text(book[1])
        etree.SubElement(book_elem, "Description").text = clean_description(clean_text(book[2]))
    return etree.tostring(root, pretty_print=True, encoding="unicode")

# --- Streamlit UI ---
st.title("📚 OpenLibrary Full-Text Book Search")

search_term = st.text_input("Enter a search term for book descriptions", "love")

if "results" not in st.session_state:
    st.session_state.results = None
if "xml_output" not in st.session_state:
    st.session_state.xml_output = None

if st.button("Search"):
    query = search_term.replace(" ", " & ")
    cursor.execute("""
        SELECT "BookID", "title", "description"
        FROM "Book"
        WHERE to_tsvector('english', "description") @@ to_tsquery(%s)
    """, (query,))
    results = cursor.fetchall()

    if results:
        st.success(f"✅ Found {len(results)} matching books")
        st.session_state.results = results
        st.session_state.xml_output = books_to_xml(results)
    else:
        st.warning("No matching books found.")
        st.session_state.results = None
        st.session_state.xml_output = None

# --- Display Results ---
if st.session_state.results:
    st.subheader("🔍 Search Results")
    for book in st.session_state.results:
        st.markdown(f"**{book[1]}** (`{book[0]}`)")
        st.text(book[2])
        st.markdown("---")

    # XML Output
    st.subheader("🧾 XML Output")
    st.code(st.session_state.xml_output, language="xml")

    # XPath Search
    st.subheader("🔎 XPath Query")
    xpath_query = st.text_input("Enter an XPath (e.g., //Book[contains(Description, 'robot')]/Title/text())")

    if xpath_query:
        try:
            tree = etree.fromstring(st.session_state.xml_output)
            xpath_results = tree.xpath(xpath_query)
            st.success("XPath Results:")
            st.write(xpath_results)
        except Exception as e:
            st.error(f"XPath Error: {e}")

    # Save to file
    with open("search_results.xml", "w", encoding="utf-8") as f:
        f.write(st.session_state.xml_output)
