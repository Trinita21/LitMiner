import re

def remove_duplicateSubjects(input_subjects,input_bookSubjects):
    # Step 1: Deduplicate Subjects
    output_subjects = "deduplicated_subjects.sql"
    output_bookSubjects = "updated_bookSubjects.sql"

    seen_descriptions = {}
    deduplicated_lines = []
    subject_id = 1

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
                    new_line = re.sub(r"\(\d+,", f"({subject_id},", line)
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


input_subjects = "insert_subjects.sql"
input_bookSubjects = "insert_subjectXBook.sql"
remove_duplicateSubjects(input_subjects,input_bookSubjects)

input_bookAuthorfile  = "insert_bookAuthors.sql"
output_bookAuthorfile = "deduplicated_bookAuthors.sql"
clean_books_authors_sql(input_bookAuthorfile,output_bookAuthorfile)