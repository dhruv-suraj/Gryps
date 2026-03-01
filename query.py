import argparse
import json
import sys
from typing import List, Dict, Any

from tabulate import tabulate

import db


def query_films_by_character(conn, character_name: str) -> List[Dict[str, Any]]:
    """Get all films that a character appears in."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT f.title, f.episode_id, f.release_date
        FROM films f
        JOIN people_films pf ON f.id = pf.film_id
        JOIN people p ON pf.person_id = p.id
        WHERE LOWER(p.name) LIKE LOWER(?)
        ORDER BY f.episode_id
    """, (f'%{character_name}%',))

    return [dict(row) for row in cursor.fetchall()]


def query_characters_by_film(conn, film_title: str) -> List[Dict[str, Any]]:
    """Get all characters who appear in a film."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT p.name, p.gender, p.birth_year
        FROM people p
        JOIN people_films pf ON p.id = pf.person_id
        JOIN films f ON pf.film_id = f.id
        WHERE LOWER(f.title) LIKE LOWER(?)
        ORDER BY p.name
    """, (f'%{film_title}%',))

    return [dict(row) for row in cursor.fetchall()]


def query_homeworld_by_character(conn, character_name: str) -> List[Dict[str, Any]]:
    """Get the homeworld of a character."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name AS character, pl.name AS homeworld, pl.climate, pl.terrain, pl.population
        FROM people p
        LEFT JOIN planets pl ON p.homeworld_id = pl.id
        WHERE LOWER(p.name) LIKE LOWER(?)
    """, (f'%{character_name}%',))

    return [dict(row) for row in cursor.fetchall()]


def query_characters_by_homeworld(conn, planet_name: str) -> List[Dict[str, Any]]:
    """Get all characters from a specific planet."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.gender, p.birth_year
        FROM people p
        JOIN planets pl ON p.homeworld_id = pl.id
        WHERE LOWER(pl.name) LIKE LOWER(?)
        ORDER BY p.name
    """, (f'%{planet_name}%',))

    return [dict(row) for row in cursor.fetchall()]


def query_starships_by_character(conn, character_name: str) -> List[Dict[str, Any]]:
    """Get all starships piloted by a character."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT s.name, s.model, s.manufacturer, s.starship_class
        FROM starships s
        JOIN people_starships ps ON s.id = ps.starship_id
        JOIN people p ON ps.person_id = p.id
        WHERE LOWER(p.name) LIKE LOWER(?)
        ORDER BY s.name
    """, (f'%{character_name}%',))

    return [dict(row) for row in cursor.fetchall()]


def get_stats(conn) -> Dict[str, int]:
    """Get database statistics."""
    cursor = conn.cursor()

    stats = {}
    for table in ['people', 'films', 'planets', 'starships']:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        stats[table] = cursor.fetchone()['count']

    # Get last ingestion time if available
    cursor.execute("SELECT value FROM metadata WHERE key = 'last_ingestion'")
    row = cursor.fetchone()
    if row:
        stats['last_ingestion'] = row['value']

    return stats


def search_query(conn, search_term: str) -> str:
    """Simple natural language search dispatcher."""
    search_lower = search_term.lower()

    # Character names to search for
    character_names = ['luke skywalker', 'han solo', 'leia organa', 'leia', 'darth vader', 'vader',
                      'yoda', 'obi-wan kenobi', 'obi-wan', 'anakin skywalker', 'anakin']

    # Film names to search for
    film_names = ['new hope', 'a new hope', 'empire strikes back', 'empire strikes',
                  'return of the jedi', 'return', 'phantom menace', 'attack of the clones',
                  'revenge of the sith']

    # Check for films by character queries
    if any(word in search_lower for word in ['film', 'movie']) and any(word in search_lower for word in ['appear', 'in', 'feature', 'star', 'does', 'did']):
        for name in character_names:
            if name in search_lower:
                results = query_films_by_character(conn, name)
                return f"Films featuring {name.title()}:\n" + format_results(results, as_json=False)

    # Check for characters by film queries
    if any(word in search_lower for word in ['who', 'character', 'people', 'person']) and any(word in search_lower for word in ['appear', 'in', 'from', 'feature', 'star']):
        for film in film_names:
            if film in search_lower:
                results = query_characters_by_film(conn, film)
                return f"Characters in '{film.title()}':\n" + format_results(results, as_json=False)

    # Check for homeworld queries
    if 'homeworld' in search_lower or 'home planet' in search_lower or 'from where' in search_lower:
        for name in character_names:
            if name in search_lower:
                results = query_homeworld_by_character(conn, name)
                return f"Homeworld of {name.title()}:\n" + format_results(results, as_json=False)

    # Check for starship queries
    if any(word in search_lower for word in ['starship', 'ship', 'pilot', 'fly', 'flies']):
        for name in character_names:
            if name in search_lower:
                results = query_starships_by_character(conn, name)
                return f"Starships piloted by {name.title()}:\n" + format_results(results, as_json=False)

    return "Sorry, I couldn't understand that query. Try being more specific or use one of the direct commands."


def format_results(results: List[Dict[str, Any]], as_json: bool = False) -> str:
    """Format query results as table or JSON."""
    if not results:
        return "No results found."

    if as_json:
        return json.dumps(results, indent=2)

    return tabulate(results, headers="keys", tablefmt="grid")


def main():
    parser = argparse.ArgumentParser(
        description="Query the SWAPI database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query.py films --character "Luke Skywalker"
  python query.py characters --film "A New Hope"
  python query.py homeworld --character "Luke Skywalker"
  python query.py characters --homeworld "Tatooine"
  python query.py starships --character "Han Solo"
  python query.py stats
  python query.py search "What films does Luke appear in?"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Query command')

    # Films command
    films_parser = subparsers.add_parser('films', help='Get films by character')
    films_parser.add_argument('--character', required=True, help='Character name')
    films_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Characters command (two modes: by film or by homeworld)
    characters_parser = subparsers.add_parser('characters', help='Get characters by film or homeworld')
    characters_group = characters_parser.add_mutually_exclusive_group(required=True)
    characters_group.add_argument('--film', help='Film title')
    characters_group.add_argument('--homeworld', help='Planet name')
    characters_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Homeworld command
    homeworld_parser = subparsers.add_parser('homeworld', help='Get homeworld by character')
    homeworld_parser.add_argument('--character', required=True, help='Character name')
    homeworld_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Starships command
    starships_parser = subparsers.add_parser('starships', help='Get starships by character')
    starships_parser.add_argument('--character', required=True, help='Character name')
    starships_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')

    # Search command (natural language-ish)
    search_parser = subparsers.add_parser('search', help='Natural language search')
    search_parser.add_argument('query', help='Search query')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Check database exists
    if not db.db_exists():
        print(f"Error: Database not found at {db.DB_FILE}")
        print("Please run 'python ingest.py' first to fetch and store the data.")
        sys.exit(1)

    conn = db.get_connection()

    try:
        if args.command == 'films':
            results = query_films_by_character(conn, args.character)
            if not results:
                print(f"No films found for character matching '{args.character}'")
                print("Try a different spelling or check if the character exists.")
                sys.exit(1)
            print(format_results(results, args.json))

        elif args.command == 'characters':
            if args.film:
                results = query_characters_by_film(conn, args.film)
                if not results:
                    print(f"No characters found for film matching '{args.film}'")
                    print("Try a different spelling or check if the film exists.")
                    sys.exit(1)
            else:  # args.homeworld
                results = query_characters_by_homeworld(conn, args.homeworld)
                if not results:
                    print(f"No characters found from homeworld matching '{args.homeworld}'")
                    print("Try a different spelling or check if the planet exists.")
                    sys.exit(1)
            print(format_results(results, args.json))

        elif args.command == 'homeworld':
            results = query_homeworld_by_character(conn, args.character)
            if not results:
                print(f"No homeworld found for character matching '{args.character}'")
                print("Try a different spelling or check if the character exists.")
                sys.exit(1)
            print(format_results(results, args.json))

        elif args.command == 'starships':
            results = query_starships_by_character(conn, args.character)
            if not results:
                print(f"No starships found for character matching '{args.character}'")
                print("This character may not pilot any starships, or try a different spelling.")
                sys.exit(1)
            print(format_results(results, args.json))

        elif args.command == 'stats':
            stats = get_stats(conn)
            print("\n" + "=" * 40)
            print("SWAPI Database Statistics")
            print("=" * 40)
            print(f"Characters: {stats['people']}")
            print(f"Films: {stats['films']}")
            print(f"Planets: {stats['planets']}")
            print(f"Starships: {stats['starships']}")
            if 'last_ingestion' in stats:
                print(f"\nLast updated: {stats['last_ingestion']}")
            print("=" * 40 + "\n")

        elif args.command == 'search':
            print(search_query(conn, args.query))

    except Exception as e:
        print(f"Error executing query: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
