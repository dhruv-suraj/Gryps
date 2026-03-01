from flask import Flask, render_template, request, jsonify
import db
import os
import re
from query import (
    query_films_by_character,
    query_characters_by_film,
    query_homeworld_by_character,
    query_characters_by_homeworld,
    query_starships_by_character,
    get_stats
)

app = Flask(__name__)


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def api_query():
    """Handle query requests from the frontend."""
    data = request.json
    query_type = data.get('type')
    param = data.get('param', '')

    if not db.db_exists():
        return jsonify({
            'error': 'Database not found. Please run "python3 ingest.py" first.'
        }), 404

    conn = db.get_connection()

    try:
        results = []

        if query_type == 'films_by_character':
            results = query_films_by_character(conn, param)
            if not results:
                return jsonify({'error': f'No films found for character "{param}"'}), 404

        elif query_type == 'characters_by_film':
            results = query_characters_by_film(conn, param)
            if not results:
                return jsonify({'error': f'No characters found for film "{param}"'}), 404

        elif query_type == 'homeworld_by_character':
            results = query_homeworld_by_character(conn, param)
            if not results:
                return jsonify({'error': f'No homeworld found for character "{param}"'}), 404

        elif query_type == 'characters_by_homeworld':
            results = query_characters_by_homeworld(conn, param)
            if not results:
                return jsonify({'error': f'No characters found from homeworld "{param}"'}), 404

        elif query_type == 'starships_by_character':
            results = query_starships_by_character(conn, param)
            if not results:
                return jsonify({'error': f'No starships found for character "{param}"'}), 404

        else:
            return jsonify({'error': 'Invalid query type'}), 400

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get database statistics."""
    if not db.db_exists():
        return jsonify({
            'error': 'Database not found. Please run "python3 ingest.py" first.'
        }), 404

    conn = db.get_connection()

    try:
        stats = get_stats(conn)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/search', methods=['POST'])
def api_search():
    """Handle natural language search queries."""
    data = request.json
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'error': 'Please provide a question'}), 400

    if not db.db_exists():
        return jsonify({
            'error': 'Database not found. Please run "python3 ingest.py" first.'
        }), 404

    conn = db.get_connection()

    try:
        # Parse the natural language query
        question_lower = question.lower()

        # Extract names using regex patterns
        # Common character names
        characters = {
            'luke skywalker': ['luke skywalker', 'luke'],
            'han solo': ['han solo', 'han'],
            'leia organa': ['leia organa', 'leia', 'princess leia'],
            'darth vader': ['darth vader', 'vader', 'anakin skywalker', 'anakin'],
            'yoda': ['yoda'],
            'obi-wan kenobi': ['obi-wan kenobi', 'obi-wan', 'kenobi'],
            'chewbacca': ['chewbacca', 'chewie'],
            'r2-d2': ['r2-d2', 'r2d2', 'artoo'],
            'c-3po': ['c-3po', 'c3po', 'threepio'],
            'padmé amidala': ['padmé amidala', 'padme amidala', 'padme', 'padmé']
        }

        films = {
            'a new hope': ['a new hope', 'new hope', 'episode iv', 'episode 4'],
            'the empire strikes back': ['empire strikes back', 'empire strikes', 'episode v', 'episode 5'],
            'return of the jedi': ['return of the jedi', 'return', 'episode vi', 'episode 6'],
            'the phantom menace': ['phantom menace', 'episode i', 'episode 1'],
            'attack of the clones': ['attack of the clones', 'episode ii', 'episode 2'],
            'revenge of the sith': ['revenge of the sith', 'episode iii', 'episode 3']
        }

        planets = {
            'tatooine': ['tatooine'],
            'alderaan': ['alderaan'],
            'naboo': ['naboo'],
            'coruscant': ['coruscant'],
            'dagobah': ['dagobah'],
            'hoth': ['hoth'],
            'endor': ['endor']
        }

        # Determine query type and parameters
        results = []
        query_type = None

        # Check for films by character
        if any(word in question_lower for word in ['film', 'movie', 'appear', 'feature', 'in what']):
            for canonical_name, aliases in characters.items():
                if any(alias in question_lower for alias in aliases):
                    results = query_films_by_character(conn, canonical_name)
                    query_type = 'films_by_character'
                    if results:
                        return jsonify({
                            'results': results,
                            'interpretation': f'Films featuring {canonical_name.title()}'
                        })
                    break

        # Check for characters by film
        if any(word in question_lower for word in ['character', 'who', 'people', 'person', 'cast']):
            for canonical_title, aliases in films.items():
                if any(alias in question_lower for alias in aliases):
                    results = query_characters_by_film(conn, canonical_title)
                    query_type = 'characters_by_film'
                    if results:
                        return jsonify({
                            'results': results,
                            'interpretation': f'Characters in "{canonical_title.title()}"'
                        })
                    break

        # Check for homeworld queries
        if any(word in question_lower for word in ['homeworld', 'home world', 'home planet', 'from where', 'where is', 'planet of']):
            for canonical_name, aliases in characters.items():
                if any(alias in question_lower for alias in aliases):
                    results = query_homeworld_by_character(conn, canonical_name)
                    query_type = 'homeworld'
                    if results:
                        return jsonify({
                            'results': results,
                            'interpretation': f'Homeworld of {canonical_name.title()}'
                        })
                    break

        # Check for characters by planet
        if any(word in question_lower for word in ['from', 'planet', 'homeworld']):
            for canonical_planet, aliases in planets.items():
                if any(alias in question_lower for alias in aliases):
                    results = query_characters_by_homeworld(conn, canonical_planet)
                    query_type = 'characters_by_planet'
                    if results:
                        return jsonify({
                            'results': results,
                            'interpretation': f'Characters from {canonical_planet.title()}'
                        })
                    break

        # Check for starship queries
        if any(word in question_lower for word in ['starship', 'ship', 'pilot', 'fly', 'flies', 'vessel']):
            for canonical_name, aliases in characters.items():
                if any(alias in question_lower for alias in aliases):
                    results = query_starships_by_character(conn, canonical_name)
                    query_type = 'starships'
                    if results:
                        return jsonify({
                            'results': results,
                            'interpretation': f'Starships piloted by {canonical_name.title()}'
                        })
                    break

        # If no results found
        return jsonify({
            'error': 'I couldn\'t understand your question. Try asking about films, characters, homeworlds, or starships.',
            'suggestions': [
                'What films does Luke Skywalker appear in?',
                'Who appears in A New Hope?',
                'What is the homeworld of Luke Skywalker?',
                'What characters are from Tatooine?',
                'What starships does Han Solo pilot?'
            ]
        }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print("\n" + "=" * 60)
    print("SWAPI Query Tool - Web Interface")
    print("=" * 60)
    print(f"\nStarting server at http://localhost:{port}")
    print(f"Also accessible at http://127.0.0.1:{port}")
    print("Press CTRL+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=port)
