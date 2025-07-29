# LitMiner

LitMiner is a Text Technology project designed to extract, store, and search literary metadata from the OpenLibrary website. It queries author and book data via an external API, processes it, and stores it in a structured relational database. A lightweight application is included for querying the data.

## GitHub Project

[Link of code](https://github.com/nataliapalomares/LitMiner/tree/main)

## Project structure
```bash
LitMiner/
├── sample_scripts/
│   ├── createDB_scripts/
│   │   └── LitMinerDB.sql
│   ├── insert_scripts/
│   │   ├── insert_authors.sql
│   │   ├── insert_books.sql
│   │   ├── insert_bookAuthors.sql
│   │   ├── insert_bookCover.sql
│   │   ├── insert_covers.sql
│   │   ├── insert_subjects.sql
│   │   └── insert_subjectXBook.sql
├── src/
│   ├── .env
│   ├── CleanSubjectList.py
│   └── ExtractData.py
├── LitMinerDB.png
├── requirements.txt
├── app.py
├── db_query_trial.py
└── search_result.xml
```

## 🧠 Project Overview
- **ExtractData.py:** Fetches authors and their works from the OpenLibrary API
- **CleanSubjectList.py:** Cleans up subject strings (e.g., special characters, apostrophes).
- **app.py:** Search application to query the existing database.
- **LitMinerDB.sql:** Contains the schema used to create the database.
- **search_result.xml:** Shows a sample output.

	> Sample data is already inserted into the database using the provided SQL scripts.

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

## 🛠️ How It Works

 1. Database Setup:
 - We run sample_scripts/createDB_scripts/LitMinerDB.sql to create the database schema and set up foreign key constraints.
	> See LitMinerDB.png for visual diagram of the database schema

 2. Data Insertion:
 - Used ExtractData.py to dynamically retrieve author and book data via the API and generate sql script (check sample_scripts/insert_scripts/) to populate the tables with sample data.

 3. Database conection:
 - Use the parameters in .env file inside the src/ directory to establish connection with the DB

 4. Querying and Search:

- Use **app.py** to search the database by author, book title, or subject.
- db_query_trial.py includes example query logic.
![-](https://raw.githubusercontent.com/nataliapalomares/LitMiner/refs/heads/main/app_images/appy_search.jpeg)
![-](https://raw.githubusercontent.com/nataliapalomares/LitMiner/refs/heads/main/app_images/appy_trial.jpeg)
- A sample XML output (search_result.xml) is provided to illustrate how the data might be returned or exported.

## 👩‍💻 Authors & Acknowledgments
Natalia Palomares & Trinita Roy

Master students in Computational Linguistics

University of Stuttgart

This project was developed as part of the Text Technology course SS2025.

## 📜 License
This project is for educational purposes. Please cite appropriately if reused or referenced.