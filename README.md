# LitMiner

LitMiner is a Text Technology project designed to extract, store, and search literary metadata from the OpenLibrary website. It queries author and book data via an external API, processes it, and stores it in a structured relational database. A lightweight application is included for querying the data.

## Project structure
```bash
LitMiner/
├── sample_scripts/
│   ├── createDB_scripts/
│   │   └── LitMinerDB.sql             # SQL script to create DB schema and constraints
│   ├── insert_scripts/
│   │   ├── insert_authors.sql         # SQL script to insert author data
│   │   ├── insert_books.sql           # SQL script to insert book data
│   │   ├── insert_bookAuthors.sql     # SQL script to insert book author
│   │   ├── insert_bookCover.sql       # SQL script to insert book cover image
│   │   ├── insert_covers.sql          # SQL script to insert cover data
│   │   ├── insert_subjects.sql        # SQL script to insert subject terms
│   │   └── insert_subjectXBook.sql    # SQL script to insert subject-book associations
├── src/
│   ├── .env                           # Environment variables for DB connection
│   ├── CleanSubjectList.py           # Cleans and normalizes subject list (handles special characters, apostrophes, etc.)
│   └── ExtractData.py                # Main data extraction script using OpenLibrary API
├── LitMinerDB.png                    # Database ER diagram
├── app.py                            # Simple search interface to query stored data
├── db_query_trial.py                 # Script to test database queries
└── search_result.xml                 # Sample XML output of search results
```

## 🚀 Getting Started
Prerequisites
- Python 3.8+
- PostgreSQL (or compatible SQL DB)
- OpenLibrary API
- psycopg2 or another PostgreSQL adapter for Python
- Install Python dependencies using:

```bash
pip install -r requirements.txt
```
	> Note: You’ll need to set up a .env file with your DB connection credentials.

## 🛠️ How It Works

 1. Database Setup (Optional):
 - Run sample_scripts/createDB_scripts/LitMinerDB.sql to create the database schema and set up foreign key constraints.
	> See LitMinerDB.png for visual diagram of the database schema

 2. Data Insertion (Optional):
 - Use scripts in sample_scripts/insert_scripts/ to populate the tables with sample data.
 - Alternatively, use ExtractData.py to dynamically retrieve author and book data via the API.

 3. Database conection (Optional):

Create a .env file inside the src/ directory with the following structure:
DB_HOST=localhost
DB_NAME=your_db_name
DB_USER=your_username
DB_PASSWORD=your_password


 4. Querying and Search:

- Use **app.py** to search the database by author, book title, or subject.
- db_query_trial.py includes example query logic.
![-](https://raw.githubusercontent.com/nataliapalomares/LitMiner/refs/heads/main/app_images/appy_search.jpeg)
![-](https://raw.githubusercontent.com/nataliapalomares/LitMiner/refs/heads/main/app_images/appy_trial.jpeg)
- search_result.xml shows a sample output in XML format.

## 🔎 Sample Output
A sample XML output (search_result.xml) is provided to illustrate how the data might be returned or exported.

## 👩‍💻 Authors & Acknowledgments
Natalia Palomares & Trinita Roy

Master students in Computational Linguistics

University of Stuttgart

This project was developed as part of the Text Technology course SS2025.

## 📜 License
This project is for educational purposes. Please cite appropriately if reused or referenced.