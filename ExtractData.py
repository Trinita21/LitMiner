import requests
import time
import json
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



# Step 1: Call the API to get list of authors
url = "https://openlibrary.org/search/authors.json?q=*&limit=100"
response = requests.get(url)
data = response.json()

# Step 2: Generate SQL INSERT statements
sql_statements = []
count = 0

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

        birth_date = author_data.get('birth_date', None)
        if birth_date:
            try:
                birth_date = datetime.strptime(birth_date, "%d %B %Y").date()
            except:
                birth_date = None

        death_date = author_data.get('death_date', None)
        if death_date:
            try:
                death_date = datetime.strptime(death_date, "%d %B %Y").date()
            except:
                death_date = None

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

        birth_date_sql = "NULL" if birth_date is None else f"'{birth_date}'"
        death_date_sql = "NULL" if death_date is None else f"'{death_date}'"

        created_sql = f"'{created.isoformat(sep=' ')}'" if created else "NULL"
        last_modified_sql = f"'{last_modified.isoformat(sep=' ')}'" if last_modified else "NULL"

        title_sql = f"'{sql_escape(title)}'" if title else "NULL"
        personal_name_sql = f"'{sql_escape(personal_name)}'" if personal_name else "NULL"
        alternate_names_sql = safe_sql_value(json.dumps(alternate_names) if alternate_names else None)
        key_sql = f"'{sql_escape(key)}'" if key else "NULL"

        sql = f"""INSERT INTO Author (
            AuthorID, name, bio, entity_type, birth_date,
            personal_name, death_date, title, alternate_names,
            keyVal, created, last_modified
        ) VALUES (
            '{author_id}', {name_sql}, {bio_sql}, {entity_type_sql},
            {birth_date_sql}, {personal_name_sql}, {death_date_sql},
            {title_sql}, {alternate_names_sql}, {key_sql}, {created_sql},
            {last_modified_sql}
        );"""
        sql_statements.append(sql)
        count = count + 1
        if count > 1000:
            break

    except Exception as e:
        print(f"Failed to fetch data for author {author_id}: {e}")

    time.sleep(0.5)  # Be nice to the API by not spamming requests

# Step 3: Save to a .sql file (optional)
with open('insert_authors.sql', 'w', encoding='utf-8') as f:
    for statement in sql_statements:
        f.write(statement + '\n')

print("Generated SQL statements saved to insert_authors.sql")