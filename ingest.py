import argparse
import requests
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from tqdm import tqdm

import db


BASE_URL = "https://swapi.info/api"


def extract_id_from_url(url: str) -> Optional[int]:
    """Extract the numeric ID from a SWAPI URL."""
    if not url:
        return None
    match = re.search(r'/(\d+)/?$', url)
    return int(match.group(1)) if match else None


def fetch_all_pages(endpoint: str) -> List[Dict[str, Any]]:
    """Fetch all data from a SWAPI endpoint."""
    url = f"{BASE_URL}/{endpoint}/"

    try:
        with tqdm(desc=f"Fetching {endpoint}", unit=" records") as pbar:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Handle both list responses (swapi.info) and paginated responses
            if isinstance(data, list):
                pbar.update(len(data))
                return data
            elif isinstance(data, dict):
                # Handle paginated response
                all_results = []
                while url:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    page_data = response.json()

                    results = page_data.get('results', [])
                    all_results.extend(results)
                    pbar.update(len(results))

                    url = page_data.get('next')
                    time.sleep(0.1)  # Be nice to the API

                return all_results
            else:
                return []

    except requests.RequestException as e:
        print(f"\nError fetching {url}: {e}")
        return []


def ingest_planets(conn) -> None:
    """Fetch and insert all planets."""
    planets = fetch_all_pages('planets')

    cursor = conn.cursor()
    for planet in tqdm(planets, desc="Inserting planets", unit=" planets"):
        planet_id = extract_id_from_url(planet['url'])
        if planet_id:
            cursor.execute("""
                INSERT OR REPLACE INTO planets (id, name, climate, terrain, population)
                VALUES (?, ?, ?, ?, ?)
            """, (
                planet_id,
                planet['name'],
                planet.get('climate'),
                planet.get('terrain'),
                planet.get('population')
            ))
    conn.commit()


def ingest_films(conn) -> None:
    """Fetch and insert all films."""
    films = fetch_all_pages('films')

    cursor = conn.cursor()
    for film in tqdm(films, desc="Inserting films", unit=" films"):
        film_id = extract_id_from_url(film['url'])
        if film_id:
            cursor.execute("""
                INSERT OR REPLACE INTO films (id, title, episode_id, release_date, director)
                VALUES (?, ?, ?, ?, ?)
            """, (
                film_id,
                film['title'],
                film.get('episode_id'),
                film.get('release_date'),
                film.get('director')
            ))

            # Insert film-planet relationships
            for planet_url in film.get('planets', []):
                planet_id = extract_id_from_url(planet_url)
                if planet_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO films_planets (film_id, planet_id)
                        VALUES (?, ?)
                    """, (film_id, planet_id))

    conn.commit()


def ingest_starships(conn) -> None:
    """Fetch and insert all starships."""
    starships = fetch_all_pages('starships')

    cursor = conn.cursor()
    for starship in tqdm(starships, desc="Inserting starships", unit=" starships"):
        starship_id = extract_id_from_url(starship['url'])
        if starship_id:
            cursor.execute("""
                INSERT OR REPLACE INTO starships (id, name, model, manufacturer, starship_class)
                VALUES (?, ?, ?, ?, ?)
            """, (
                starship_id,
                starship['name'],
                starship.get('model'),
                starship.get('manufacturer'),
                starship.get('starship_class')
            ))
    conn.commit()


def ingest_people(conn) -> None:
    """Fetch and insert all people with their relationships."""
    people = fetch_all_pages('people')

    cursor = conn.cursor()
    for person in tqdm(people, desc="Inserting people", unit=" people"):
        person_id = extract_id_from_url(person['url'])
        if person_id:
            homeworld_id = extract_id_from_url(person.get('homeworld'))

            cursor.execute("""
                INSERT OR REPLACE INTO people (id, name, birth_year, gender, homeworld_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                person_id,
                person['name'],
                person.get('birth_year'),
                person.get('gender'),
                homeworld_id
            ))

            # Insert person-film relationships
            for film_url in person.get('films', []):
                film_id = extract_id_from_url(film_url)
                if film_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO people_films (person_id, film_id)
                        VALUES (?, ?)
                    """, (person_id, film_id))

            # Insert person-starship relationships
            for starship_url in person.get('starships', []):
                starship_id = extract_id_from_url(starship_url)
                if starship_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO people_starships (person_id, starship_id)
                        VALUES (?, ?)
                    """, (person_id, starship_id))

    conn.commit()


def update_metadata(conn) -> None:
    """Update metadata with ingestion timestamp."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value)
        VALUES ('last_ingestion', ?)
    """, (datetime.now().isoformat(),))
    conn.commit()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch data from SWAPI and populate the SQLite database"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-ingestion by deleting existing database'
    )
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Refresh data in existing database'
    )
    args = parser.parse_args()

    if db.db_exists() and not (args.force or args.refresh):
        print(f"Database already exists at {db.DB_FILE}")
        print("Use --force to recreate or --refresh to update")
        return

    print("Initializing database...")
    conn = db.initialize_db(force=args.force)

    print("\nFetching and storing SWAPI data...")
    print("This may take a minute or two...\n")

    try:
        # Order matters: planets first (no dependencies)
        ingest_planets(conn)

        # Then films and starships (no dependencies on people)
        ingest_films(conn)
        ingest_starships(conn)

        # Finally people (depends on planets, and creates relationships)
        ingest_people(conn)

        update_metadata(conn)

        # Print summary
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM people")
        people_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM films")
        films_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM planets")
        planets_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM starships")
        starships_count = cursor.fetchone()[0]

        print("\n" + "=" * 50)
        print("Ingestion complete!")
        print("=" * 50)
        print(f"Characters: {people_count}")
        print(f"Films: {films_count}")
        print(f"Planets: {planets_count}")
        print(f"Starships: {starships_count}")
        print(f"\nDatabase saved to: {db.DB_FILE}")

    except Exception as e:
        print(f"\nError during ingestion: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
