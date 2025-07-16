import re
import psycopg2
from dotenv import load_dotenv
import os

def remove_duplicateSubjects(input_subjects,input_bookSubjects):
    # Step 1: Deduplicate Subjects
    output_subjects = "deduplicated_subjects.sql"
    output_bookSubjects = "updated_bookSubjects.sql"

    seen_descriptions = {}
    deduplicated_lines = []
    subject_id = 9933

    # Build mapping from (type, description) to new subject_id
    with open(input_subjects, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r"VALUES\s*\(\d+,\s*'([^']+)',\s*'(.+)'\);", line)
            if match:
                subj_type = match.group(1)
                description = match.group(2)
                key = (subj_type, description)
                if key not in seen_descriptions:
                    seen_descriptions[key] = subject_id
                    subj_type_sql = "'" + subj_type.replace("'", "''") + "'"
                    description_sql = "'" + description.replace("'", "''") + "'"
                    new_line = (
                        f'INSERT INTO public."Subjects" ("SubjectID", subj_type, description) '
                        f"VALUES ({subject_id}, {subj_type_sql}, {description_sql});\n"
                    )
                    deduplicated_lines.append(new_line)
                    subject_id += 1

    # Save new insert_subjects.sql
    with open(output_subjects, "w", encoding="utf-8") as f:
        f.writelines(deduplicated_lines)

    # Step 2: Update insert_bookSubjects.sql
    # But first, reverse the map: old_id → new_id

    # To do this, we need the original mapping from (type, description) → old_id
    # So we parse the original file again
    old_id_map = {}
    with open(input_subjects, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r"VALUES\s*\((\d+),\s*'([^']+)',\s*'(.+)'\);", line)
            if match:
                old_id = int(match.group(1))
                subj_type = match.group(2)
                description = match.group(3)
                key = (subj_type, description)
                old_id_map[old_id] = seen_descriptions.get(key)

    # Now update the BookSubjects file
    updated_lines = []
    with open(input_bookSubjects, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r"VALUES\s*\('([^']+)',\s*(\d+)\);", line)
            if match:
                book_id = match.group(1)
                old_subject_id = int(match.group(2))
                new_subject_id = old_id_map.get(old_subject_id)

                if new_subject_id:  # only keep valid ones
                    new_line = f"INSERT INTO BookSubjects (BookID, SubjectID) VALUES ('{book_id}', {new_subject_id});\n"
                    updated_lines.append(new_line)

    # Save the updated insert_bookSubjects.sql
    with open(output_bookSubjects, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"Updated Subjects saved to {output_subjects}")
    print(f"Updated BookSubjects saved to {output_bookSubjects}")

def clean_books_authors_sql(input_file, output_file):
    triplets = set()

    # Step 1: Read and extract triplets
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(
                r"VALUES\s*\('([^']+)',\s*'([^']+)',\s*'([^']+)'\);", line)
            if match:
                author_id, book_id, role = match.groups()
                triplets.add((author_id, book_id, role))

    # Step 2: Sort by AuthorID, then BookID
    sorted_triplets = sorted(triplets, key=lambda x: (x[0], x[1]))

    # Step 3: Write to new .sql file
    with open(output_file, "w", encoding="utf-8") as f:
        for author_id, book_id, role in sorted_triplets:
            line = (
                f'INSERT INTO public."BooksAuthors" (AuthorID, BookID, rol_type) '
                f"VALUES ('{author_id}', '{book_id}', '{role}');\n"
            )
            f.write(line)

    print(f"Cleaned file written to {output_file} with {len(sorted_triplets)} entries.")

def reconcile_subjects_against_db(
    subjects_sql,
    booksubjects_sql,
    output_subjects,
    output_booksubjects
):
    """
    For each (SubjectID, subj_type, description) in Subjects.sql:
        - If exists in DB, get canonical SubjectID.
        - If not, assign MAX+1.
    Then updates BookSubjects.sql to use canonical SubjectIDs.
    """

    # 1. Load Subjects.sql and prepare mapping
    subjects_data = []  # List of (old_id, subj_type, description)
    with open(subjects_sql, "r", encoding="utf-8") as f:
        for line in f:
            m = re.search(r"VALUES\s*\(\s*(\d+),\s*'([^']+)',\s*'(.+)'\);", line)
            if m:
                old_id = int(m.group(1))
                subj_type = m.group(2)
                description = m.group(3)
                subjects_data.append((old_id, subj_type, description))

    print(f"Loaded {len(subjects_data)} subjects.")

    # 2. Connect to the DB
    conn = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        gssencmode = GSSENCMODE,
    )
    cur = conn.cursor()

    # 3. Build a map of canonical subjects from DB
    cur.execute('SELECT "SubjectID", subj_type, description FROM public."Subjects";')
    canonical_rows = cur.fetchall()
    canonical_map = {(r[1], r[2]): r[0] for r in canonical_rows}
    canonical_subject_ids = set(row[0] for row in canonical_rows)

    # 4. Find MAX SubjectID in DB
    cur.execute('SELECT COALESCE(MAX("SubjectID"),0) FROM public."Subjects";')
    max_subject_id = cur.fetchone()[0]

    print(f"Database has {len(canonical_map)} subjects. Max SubjectID: {max_subject_id}")

    # 5. Build mapping from old SubjectID -> canonical or new SubjectID
    id_remap = {}
    new_subject_inserts = []
    for old_id, subj_type, description in subjects_data:
        key = (subj_type, description)
        if key in canonical_map:
            canonical_id = canonical_map[key]
        else:
            max_subject_id += 1
            canonical_id = max_subject_id
            canonical_map[key] = canonical_id  # So future lookups use this
            # Generate INSERT
            subj_type_sql = "'" + subj_type.replace("'", "''") + "'"
            desc_sql = "'" + description.replace("'", "''") + "'"
            insert_line = (
                f'INSERT INTO public."Subjects" ("SubjectID", subj_type, description) '
                f"VALUES ({canonical_id}, {subj_type_sql}, {desc_sql});\n"
            )
            new_subject_inserts.append(insert_line)

        id_remap[old_id] = canonical_id

    # 6. Update BookSubjects.sql
    updated_booksubjects_lines = []
    with open(booksubjects_sql, "r", encoding="utf-8") as f:
        for line in f:
            m = re.search(r"VALUES\s*\('([^']+)',\s*(\d+)\);", line)
            if m:
                book_id = m.group(1)
                old_subj_id = int(m.group(2))
                if old_subj_id not in id_remap:
                    raise ValueError(f"SubjectID {old_subj_id} not found in mapping.")
                new_subj_id = id_remap[old_subj_id]
                new_line = (
                    f"INSERT INTO BookSubjects (BookID, SubjectID) "
                    f"VALUES ('{book_id}', {new_subj_id});\n"
                )
                updated_booksubjects_lines.append(new_line)

    # 7. Save reconciled Subjects.sql (original + new inserts)
    with open(output_subjects, "w", encoding="utf-8") as f:
        with open(subjects_sql, "r", encoding="utf-8") as orig:
            f.writelines(orig.readlines())
        f.writelines(new_subject_inserts)

    # 8. Save updated BookSubjects.sql
    with open(output_booksubjects, "w", encoding="utf-8") as f:
        f.writelines(updated_booksubjects_lines)

    cur.close()
    conn.close()

    print(f" Reconciled Subjects saved to {output_subjects}")
    print(f" Updated BookSubjects saved to {output_booksubjects}")


#input_subjects = "insert_subjects2.sql"
#input_bookSubjects = "insert_subjectXBook2.sql"
#remove_duplicateSubjects(input_subjects,input_bookSubjects)


input_subjects = "deduplicated_subjects.sql"
input_bookSubjects = "updated_bookSubjects.sql"
output_subjects = "final_subjects.sql"
output_booksubjects = "final_bookSubjects.sql"

load_dotenv()
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
GSSENCMODE = os.getenv("gssencmode")

reconcile_subjects_against_db(input_subjects,input_bookSubjects,output_subjects,output_booksubjects)
#input_bookAuthorfile  = "insert_bookAuthors.sql"
#output_bookAuthorfile = "deduplicated_bookAuthors.sql"
#clean_books_authors_sql(input_bookAuthorfile,output_bookAuthorfile)