# SWAPI Data & Query Tool

A tool for fetching, storing, and querying Star Wars data from the [SWAPI](https://swapi.info/documentation).

Includes both a **command-line interface** and a **web-based UI** for easy exploration.

## Features

- Fetches complete dataset from SWAPI with progress tracking
- Stores data in a normalized SQLite database with proper relationships
- **Modern web interface** with beautiful UI for easy querying
- Command-line interface for programmatic access
- Fast, case-insensitive queries with clean table output
- Support for JSON output format
- Database statistics and metadata tracking
- Natural language search capability

## Setup

### Requirements

- Python 3.8 or higher

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

That's it. No additional setup required.

## Usage

You can interact with the data in two ways: **Web Interface** (recommended for exploration) or **Command Line** (for scripting).

### 1. Fetch and Store Data

**Important:** You must fetch the data first before using either interface.

Run the ingestion script to download all SWAPI data and populate the database:

```bash
python ingest.py
```

This will:
- Fetch all people, films, planets, and starships from SWAPI
- Create a normalized SQLite database (`swapi.db`)
- Show progress bars for each data type
- Display a summary of fetched records

Expected output:
```
Initializing database...

Fetching and storing SWAPI data...
This may take a minute or two...

Fetching planets: 100%|██████████| 6/6 [00:02<00:00]
Inserting planets: 100%|██████████| 60/60 [00:00<00:00]
Fetching films: 100%|██████████| 1/1 [00:01<00:00]
Inserting films: 100%|██████████| 6/6 [00:00<00:00]
...

==================================================
Ingestion complete!
==================================================
Characters: 82
Films: 6
Planets: 60
Starships: 36

Database saved to: swapi.db
```

**Options:**

- `--force`: Delete existing database and re-fetch all data
- `--refresh`: Update existing database with fresh data

```bash
python ingest.py --force    # Complete refresh
python ingest.py --refresh  # Update existing data
```

### 2. Web Interface (Recommended)

Launch the web interface for an easy, visual way to explore the data:

```bash
python3 app.py
```

Then open your browser to **http://localhost:5000**

**Features:**
- Beautiful, modern UI with gradient design
- Live database statistics dashboard
- 5 query types with example buttons for quick testing
- Interactive result tables
- Real-time search with visual feedback
- Responsive design that works on all screen sizes

**Query Types Available:**
1. Films by Character - Find all films a character appears in
2. Characters by Film - See all characters in a specific film
3. Character Homeworld - Discover where a character is from
4. Characters by Planet - Find all characters from a specific planet
5. Starships by Character - See which starships a character pilots

Each query type includes helpful examples you can click to try instantly!

### 3. Command Line Interface

The query tool provides several commands to retrieve data:

#### Test Query 1: Films by Character

**Question:** What are the names of all the films that Luke Skywalker appears in?

```bash
python query.py films --character "Luke Skywalker"
```

**Output:**
```
+------------------------------------+---------------+-----------------+
| title                              | episode_id    | release_date    |
+====================================+===============+=================+
| A New Hope                         | 4             | 1977-05-25      |
| The Empire Strikes Back            | 5             | 1980-05-17      |
| Return of the Jedi                 | 6             | 1983-05-25      |
| Revenge of the Sith                | 3             | 2005-05-19      |
+------------------------------------+---------------+-----------------+
```

#### Test Query 2: Characters by Film

**Question:** What are the names of all characters who appear in "A New Hope" (Episode IV)?

```bash
python query.py characters --film "A New Hope"
```

**Output:**
```
+----------------------+----------+--------------+
| name                 | gender   | birth_year   |
+======================+==========+==============+
| Biggs Darklighter    | male     | 24BBY        |
| C-3PO                | n/a      | 112BBY       |
| Darth Vader          | male     | 41.9BBY      |
| Greedo               | male     | 44BBY        |
| Han Solo             | male     | 29BBY        |
| Jabba Desilijic Tiure| hermaphrodite | 600BBY  |
| Leia Organa          | female   | 19BBY        |
| Luke Skywalker       | male     | 19BBY        |
| Obi-Wan Kenobi       | male     | 57BBY        |
| R2-D2                | n/a      | 33BBY        |
| R5-D4                | n/a      | unknown      |
| Wilhuff Tarkin       | male     | 64BBY        |
| ... (continues)
+----------------------+----------+--------------+
```

#### Test Query 3: Homeworld by Character

**Question:** What is the name of the homeworld of Luke Skywalker?

```bash
python query.py homeworld --character "Luke Skywalker"
```

**Output:**
```
+------------------+------------+----------+-------------+--------------+
| character        | homeworld  | climate  | terrain     | population   |
+==================+============+==========+=============+==============+
| Luke Skywalker   | Tatooine   | arid     | desert      | 200000       |
+------------------+------------+----------+-------------+--------------+
```

#### Test Query 4: Characters by Homeworld

**Question:** What are the names of all characters who are from the planet Tatooine?

```bash
python query.py characters --homeworld "Tatooine"
```

**Output:**
```
+----------------------------+----------+--------------+
| name                       | gender   | birth_year   |
+============================+==========+==============+
| Anakin Skywalker           | male     | 41.9BBY      |
| Beru Whitesun lars         | female   | 47BBY        |
| Biggs Darklighter          | male     | 24BBY        |
| C-3PO                      | n/a      | 112BBY       |
| Cliegg Lars                | male     | 82BBY        |
| Luke Skywalker             | male     | 19BBY        |
| Owen Lars                  | male     | 52BBY        |
| R5-D4                      | n/a      | unknown      |
| Shmi Skywalker             | female   | 72BBY        |
+----------------------------+----------+--------------+
```

#### Test Query 5: Starships by Character

**Question:** What are the names of all starships piloted by Han Solo?

```bash
python query.py starships --character "Han Solo"
```

**Output:**
```
+---------------------+---------------------+-----------------------------+------------------+
| name                | model               | manufacturer                | starship_class   |
+=====================+=====================+=============================+==================+
| Imperial shuttle    | Lambda-class T-4a   | Sienar Fleet Systems        | Armed transport  |
| Millennium Falcon   | YT-1300 light       | Corellian Engineering       | Light freighter  |
|                     | freighter           | Corporation                 |                  |
+---------------------+---------------------+-----------------------------+------------------+
```

### Additional Commands

#### Database Statistics

View a summary of the database contents:

```bash
python query.py stats
```

**Output:**
```
========================================
SWAPI Database Statistics
========================================
Characters: 82
Films: 6
Planets: 60
Starships: 36

Last updated: 2024-01-15T10:30:45.123456
========================================
```

#### Natural Language Search

Try a free-form search query:

```bash
python query.py search "What films does Luke appear in?"
python query.py search "Who appears in A New Hope?"
```

#### JSON Output

Add `--json` flag to any query for machine-readable output:

```bash
python query.py films --character "Luke Skywalker" --json
```

**Output:**
```json
[
  {
    "title": "A New Hope",
    "episode_id": 4,
    "release_date": "1977-05-25"
  },
  {
    "title": "The Empire Strikes Back",
    "episode_id": 5,
    "release_date": "1980-05-17"
  }
]
```

### Query Features

- **Case-insensitive matching**: "luke skywalker", "Luke Skywalker", and "LUKE SKYWALKER" all work
- **Partial matching**: "Luke" will match "Luke Skywalker"
- **Clean error messages**: Helpful feedback when no results are found
- **Fast lookups**: Database indexes on all searchable fields

## Architecture & Design

### Database Schema

The tool uses a normalized SQLite schema that mirrors SWAPI's relational structure:

**Core Tables:**
- `people` (characters with homeworld reference)
- `films` (movies with metadata)
- `planets` (locations)
- `starships` (vehicles)

**Junction Tables:**
- `people_films` (many-to-many: characters ↔ films)
- `people_starships` (many-to-many: characters ↔ starships)
- `films_planets` (many-to-many: films ↔ planets)

This design allows efficient SQL joins for all query types without string parsing or post-processing.

### Why SQLite?

- No server setup required
- File-based persistence
- Full SQL support including complex joins
- Included in Python's standard library
- Perfect for datasets of this size

### File Structure

```
swapi_tool/
├── db.py              # Database schema and connection helpers
├── ingest.py          # SWAPI data fetching and population
├── query.py           # CLI query interface
├── app.py             # Flask web application
├── templates/
│   └── index.html     # Web interface UI
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── swapi.db          # SQLite database (created after ingestion)
```

## Troubleshooting

**Database not found error:**
```
Error: Database not found at swapi.db
Please run 'python ingest.py' first to fetch and store the data.
```
**Solution:** Run `python ingest.py` to create the database.

**No results found:**
```
No films found for character matching 'Luke'
Try a different spelling or check if the character exists.
```
**Solution:** Check spelling or try a more specific search term. Use `python query.py stats` to verify data exists.

**Connection timeout during ingestion:**
The script includes automatic retry logic and rate limiting. If ingestion fails, simply run `python ingest.py --refresh` to continue.

## Requirements

See `requirements.txt` for specific versions. Core dependencies:

- `requests` - HTTP client for SWAPI
- `tabulate` - Pretty table formatting
- `tqdm` - Progress bars
- `flask` - Web framework for the UI

All dependencies are lightweight and well-maintained.

## License

This is a coding test project. Use freely for evaluation purposes.
