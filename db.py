import sqlite3
import os
from typing import Optional

DB_FILE = "swapi.db"


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def db_exists() -> bool:
    """Check if the database file exists."""
    return os.path.exists(DB_FILE)


def create_schema(conn: sqlite3.Connection) -> None:
    """Create the database schema with normalized tables."""
    cursor = conn.cursor()

    # Metadata table to track ingestion
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Core tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            climate TEXT,
            terrain TEXT,
            population TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            birth_year TEXT,
            gender TEXT,
            homeworld_id INTEGER,
            FOREIGN KEY (homeworld_id) REFERENCES planets(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            episode_id INTEGER,
            release_date TEXT,
            director TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS starships (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            model TEXT,
            manufacturer TEXT,
            starship_class TEXT
        )
    """)

    # Junction tables for many-to-many relationships
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people_films (
            person_id INTEGER,
            film_id INTEGER,
            PRIMARY KEY (person_id, film_id),
            FOREIGN KEY (person_id) REFERENCES people(id),
            FOREIGN KEY (film_id) REFERENCES films(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people_starships (
            person_id INTEGER,
            starship_id INTEGER,
            PRIMARY KEY (person_id, starship_id),
            FOREIGN KEY (person_id) REFERENCES people(id),
            FOREIGN KEY (starship_id) REFERENCES starships(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS films_planets (
            film_id INTEGER,
            planet_id INTEGER,
            PRIMARY KEY (film_id, planet_id),
            FOREIGN KEY (film_id) REFERENCES films(id),
            FOREIGN KEY (planet_id) REFERENCES planets(id)
        )
    """)

    # Indexes for common queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_people_name ON people(LOWER(name))")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_films_title ON films(LOWER(title))")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_planets_name ON planets(LOWER(name))")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_starships_name ON starships(LOWER(name))")

    conn.commit()


def initialize_db(force: bool = False) -> sqlite3.Connection:
    """Initialize the database, optionally forcing recreation."""
    if force and db_exists():
        os.remove(DB_FILE)

    conn = get_connection()
    create_schema(conn)
    return conn
