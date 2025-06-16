-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/uhrGXc
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.

-- Modify this code to update the DB schema diagram.
-- To reset the sample schema, replace everything with
-- two dots ('..' - without quotes).

CREATE TABLE "Author" (
    "AuthorID" string   NOT NULL,
    "name" string   NOT NULL,
    "bio" text   NULL,
    "entity_type" string   NULL,
    "birth_date" date   NULL,
    "personal_name" string   NULL,
    "death_date" date   NULL,
    "title" string   NULL,
    "alternate_names" json   NULL,
    "keyVal" string   NOT NULL,
    "created" datetime   NOT NULL,
    "last_modified" datetime   NULL,
    CONSTRAINT "pk_Author" PRIMARY KEY (
        "AuthorID"
     )
);

CREATE TABLE "Book" (
    "BookID" string   NOT NULL,
    "title" string   NOT NULL,
    "description" text   NULL,
    "first_publish_date" date   NULL,
    -- subject_places json
    -- subjects json
    -- subject_people json
    -- subject_times json
    -- covers json
    "created" datetime   NOT NULL,
    "last_modified" datetime   NULL,
    CONSTRAINT "pk_Book" PRIMARY KEY (
        "BookID"
     )
);

CREATE TABLE "BooksAuthors" (
    "BookID" string   NOT NULL,
    "AuthorID" string   NOT NULL,
    "rol_type" string   NOT NULL
);

CREATE TABLE "Cover" (
    "CoverID" int   NOT NULL,
    CONSTRAINT "pk_Cover" PRIMARY KEY (
        "CoverID"
     )
);

CREATE TABLE "BooksCover" (
    "BookID" string   NOT NULL,
    "CoverID" int   NOT NULL
);

CREATE TABLE "Subjects" (
    "SubjectID" int   NOT NULL,
    -- places,people,times,topic
    "type" string   NOT NULL,
    "description" string   NOT NULL,
    CONSTRAINT "pk_Subjects" PRIMARY KEY (
        "SubjectID"
     )
);

CREATE TABLE "BookSubjects" (
    "BookID" string   NOT NULL,
    "SubjectID" int   NOT NULL
);

ALTER TABLE "BooksAuthors" ADD CONSTRAINT "fk_BooksAuthors_BookID" FOREIGN KEY("BookID")
REFERENCES "Book" ("BookID");

ALTER TABLE "BooksAuthors" ADD CONSTRAINT "fk_BooksAuthors_AuthorID" FOREIGN KEY("AuthorID")
REFERENCES "Author" ("AuthorID");

ALTER TABLE "BooksCover" ADD CONSTRAINT "fk_BooksCover_BookID" FOREIGN KEY("BookID")
REFERENCES "Book" ("BookID");

ALTER TABLE "BooksCover" ADD CONSTRAINT "fk_BooksCover_CoverID" FOREIGN KEY("CoverID")
REFERENCES "Cover" ("CoverID");

ALTER TABLE "BookSubjects" ADD CONSTRAINT "fk_BookSubjects_BookID" FOREIGN KEY("BookID")
REFERENCES "Book" ("BookID");

ALTER TABLE "BookSubjects" ADD CONSTRAINT "fk_BookSubjects_SubjectID" FOREIGN KEY("SubjectID")
REFERENCES "Subjects" ("SubjectID");

CREATE INDEX "idx_Author_name"
ON "Author" ("name");

