from flask import Flask, render_template, request, jsonify
import db
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


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("SWAPI Query Tool - Web Interface")
    print("=" * 60)
    print("\nStarting server at http://localhost:8000")
    print("Also accessible at http://127.0.0.1:8000")
    print("Press CTRL+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=8000)
