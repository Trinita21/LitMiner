import requests
import time
import json
import re
from datetime import datetime

def sql_escape(s):
    return s.replace("'", "''")  # Escape single quotes for SQL

def safe_sql_value(value):
    if value is None:
        return "NULL"
    elif isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"  # Escape single quotes for SQL
    else:
        return f"'{value}'"

def generate_authorInsert():

    # Step 1: Call the API to get list of authors
    url = "https://openlibrary.org/search/authors.json?q=*&limit=100"
    response = requests.get(url)
    data = response.json()

    # Step 2: Generate SQL INSERT statements
    sql_statements = []
    coversFullList = []
    count = 0
    author_book_roles = set()

    # Step 2: Loop through author IDs and call the detailed API
    for author in data.get('docs', []):
        author_id = author.get('key')  # Format: OL12345A
        if not author_id:
            continue

        # Extract ID and build the detailed URL
        author_url = f"https://openlibrary.org/authors/{author_id}.json"

        # Request detailed author data
        try:
            author_response = requests.get(author_url)
            author_data = author_response.json()

            # Example: Print or process detailed fields
            name = author_data.get('name', 'Unknown')
            entity_type = author_data.get('entity_type',None)
            personal_name = author_data.get('personal_name',None)
            title = author_data.get('title',None)

            birth_date_raw = author_data.get('birth_date', None)
            birth_year = None
            if birth_date_raw:
                match = re.search(r'(\d{4})', birth_date_raw)
                if match:
                    birth_year = int(match.group(1))

            death_date_raw = author_data.get('death_date', None)
            death_year = None
            if death_date_raw:
                match = re.search(r'(\d{4})', death_date_raw)
                if match:
                    death_year = int(match.group(1))

            bio = author_data.get('bio')
            if isinstance(bio, dict):  # bio can sometimes be a dict with a 'value'
                bio = bio.get('value', None)
            elif not isinstance(bio, str):
                bio = None

            key = author_data.get('key',None)
            alternate_names = author_data.get('alternate_names',[])
            if not isinstance(alternate_names,list):
                alternate_names = []

            created = author_data.get('created')
            if isinstance(created,dict):
                created = created.get('value',None)
                created = datetime.fromisoformat(created)
            else:
                created = None

            last_modified = author_data.get('last_modified')
            if isinstance(last_modified,dict):
                last_modified = last_modified.get('value',None)
                last_modified = datetime.fromisoformat(last_modified)
            else:
                last_modified = None


            name_sql = f"'{sql_escape(name)}'" if name else "NULL"
            bio_sql = safe_sql_value(bio)
            entity_type_sql = safe_sql_value(entity_type)

            birth_date_raw_sql = f"'{sql_escape(birth_date_raw)}'" if birth_date_raw else "NULL"
            birth_year_sql = str(birth_year) if birth_year is not None else "NULL"
            death_date_raw_sql = f"'{sql_escape(death_date_raw)}'" if death_date_raw else "NULL"
            death_year_sql = str(death_year) if death_year is not None else "NULL"

            created_sql = f"'{created.isoformat(sep=' ')}'" if created else "NULL"
            last_modified_sql = f"'{last_modified.isoformat(sep=' ')}'" if last_modified else "NULL"

            title_sql = f"'{sql_escape(title)}'" if title else "NULL"
            personal_name_sql = f"'{sql_escape(personal_name)}'" if personal_name else "NULL"
            alternate_names_sql = safe_sql_value(json.dumps(alternate_names) if alternate_names else None)
            key_sql = f"'{sql_escape(key)}'" if key else "NULL"

            sql = f"""INSERT INTO Author (
                AuthorID, name, bio, entity_type, birth_date, birth_year,
                personal_name, death_date, death_year, title, alternate_names,
                keyVal, created, last_modified
            ) VALUES (
                '{author_id}', {name_sql}, {bio_sql}, {entity_type_sql},
                {birth_date_raw_sql}, {birth_year_sql}, {personal_name_sql}, {death_date_raw_sql}, 
                {death_year_sql}, {title_sql}, {alternate_names_sql}, {key_sql}, {created_sql},
                {last_modified_sql}
            );"""
            sql_statements.append(sql)

            url_authorWorks = f"https://openlibrary.org/authors/{author_id}/works.json"
            
            authorWorks_response = requests.get(url_authorWorks)
            authorWorks_data = authorWorks_response.json()
            
            for workOfAuthor in authorWorks_data.get('entries', []):
                key = workOfAuthor.get('key',None)
                work_id = key.split('/')[-1]

                title = workOfAuthor.get('title',None)
                description = workOfAuthor.get('description',None)
                if isinstance(description, dict):  # bio can sometimes be a dict with a 'value'
                    description = description.get('value', None)
                elif not isinstance(description, str):
                    description = None

                createdB = workOfAuthor.get('created')
                if isinstance(createdB,dict):
                    createdB = createdB.get('value',None)
                    createdB = datetime.fromisoformat(createdB)
                else:
                    createdB = None

                last_modifiedB = workOfAuthor.get('last_modified')
                if isinstance(last_modifiedB,dict):
                    last_modifiedB = last_modifiedB.get('value',None)
                    last_modifiedB = datetime.fromisoformat(last_modifiedB)
                else:
                    last_modifiedB = None

                first_publish_date = workOfAuthor.get('first_publish_date',None)
                fPublish_year = None
                if first_publish_date:
                    match = re.search(r'(\d{4})', first_publish_date)
                    if match:
                        fPublish_year = int(match.group(1))

                #Cover Data
                coverList = workOfAuthor.get('covers',None)
                if not isinstance(coverList,list):
                    coverList = None

                for cover in coverList:
                    coversFullList.append(cover)
                    coversFullList
                    sql_CoverBook = f"""INSERT INTO BooksCover (BookID, CoverID) 
                                        VALUES ('{work_id}',{cover});"""

                #Book's author data
                authorsxBookL = workOfAuthor.get('authors',None)
                if not isinstance(authorsxBookL,list):
                    authorsxBookL = None
                
                for authorxBook in authorsxBookL:
                    authorFull = authorxBook.get('author',None)
                    authorV = authorFull.split('/')[-1]
                    typeRole = authorxBook.get('type',None)
                    typeV = typeRole.split('/')[-1]

                    if authorV is not None:
                        triplet = (authorV,work_id,typeV)

                        if triplet not in author_book_roles:
                            author_book_roles.add(triplet)


            count = count + 1
            #if count > 1000:
            break

        except Exception as e:
            print(f"Failed to fetch data for author {author_id}: {e}")

        time.sleep(0.5)  # Be nice to the API by not spamming requests

    # Step 3: Save to a .sql file (optional)
    with open('insert_authors.sql', 'w', encoding='utf-8') as f:
        for statement in sql_statements:
            f.write(statement + '\n')

    generate_coverScript(coversFullList)
    print("Generated SQL statements saved to insert_authors.sql")

def generate_coverScript(coversFullList):
    coversFullList = list(set(coversFullList))
    
    with open('insert_authors.sql', 'w', encoding='utf-8') as f:
        for cover in coversFullList:
            sql_CoverBook = f"""INSERT INTO Cover (CoverID) VALUES ('{cover}');"""
            f.write(sql_CoverBook + '\n')

    

