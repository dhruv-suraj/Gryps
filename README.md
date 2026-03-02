# Star Wars Data Explorer

Okay so basically this grabs all the Star Wars data from SWAPI and lets you search through it. I built both a web interface (looks pretty cool with the space theme) and a command-line tool if you're into that.

## What it does

You know how SWAPI has all this Star Wars data scattered around? This pulls everything down, dumps it into a SQLite database, and gives you a few ways to search through it. You can find stuff like "what movies was Luke in" or "who's from Tatooine" - that kind of thing.

## Getting started

Make sure you've got Python 3.8+ installed. Then:

```bash
pip install -r requirements.txt
```

That's it for setup.

## Running it

### Step 1: Get the data

First time you need to pull all the data from SWAPI:

```bash
python3 ingest.py
```

This takes maybe a minute or two. You'll see progress bars as it downloads characters, films, planets, and starships. When it's done you'll have a `swapi.db` file with everything in it.

If you mess something up and want to start fresh, just run:
```bash
python3 ingest.py --force
```

### Step 2: Search the data

Two ways to do this:

#### Option A: Web interface (easier)

```bash
python3 app.py
```

Then open http://localhost:8000 in your browser.

There's a "Ask a Question" tab where you can literally just type questions like:
- "What films does Luke Skywalker appear in?"
- "Who appears in A New Hope?"
- "What is Luke's homeworld?"

The other tabs let you search by specific categories if you prefer that. I added some example buttons too so you can click around and see what it does.

#### Option B: Command line

For when you want to script stuff or just prefer the terminal:

**Films by character:**
```bash
python3 query.py films --character "Luke Skywalker"
```

**Characters in a film:**
```bash
python3 query.py characters --film "A New Hope"
```

**Character's homeworld:**
```bash
python3 query.py homeworld --character "Luke Skywalker"
```

**Everyone from a planet:**
```bash
python3 query.py characters --homeworld "Tatooine"
```

**Starships someone pilots:**
```bash
python3 query.py starships --character "Han Solo"
```

Add `--json` to any of these if you want JSON instead of a table.

## What's in here

```
├── app.py              # Flask web app
├── db.py               # Database stuff (schema, connections)
├── ingest.py           # Fetches data from SWAPI
├── query.py            # CLI search tool
├── templates/
│   └── index.html      # Web UI (has a cool space theme)
├── requirements.txt    # Python packages you need
└── swapi.db           # Database (created after you run ingest.py)
```

## The 5 test queries

These were the requirements, and yeah they all work:

1. **What are the names of all the films that Luke Skywalker appears in?**
   ```bash
   python3 query.py films --character "Luke Skywalker"
   ```
   Or on web: Type that question in the "Ask a Question" tab

2. **What are the names of all characters who appear in "A New Hope"?**
   ```bash
   python3 query.py characters --film "A New Hope"
   ```

3. **What is the name of the homeworld of Luke Skywalker?**
   ```bash
   python3 query.py homeworld --character "Luke Skywalker"
   ```

4. **What are the names of all characters who are from the planet Tatooine?**
   ```bash
   python3 query.py characters --homeworld "Tatooine"
   ```

5. **What are the names of all starships piloted by Han Solo?**
   ```bash
   python3 query.py starships --character "Han Solo"
   ```

## Technical stuff

I used SQLite because it's simple and doesn't need a server running. The schema is normalized with proper foreign keys and junction tables for the many-to-many relationships (like characters appearing in multiple films).

The web app is Flask - nothing fancy, just works. I threw in some CSS to make it look like a Star Wars interface because why not.

For the natural language search, it's not using any ML or anything. Just pattern matching on common question formats. Works pretty well though.

## If something breaks

**"Database not found" error:**
Run `python3 ingest.py` first. You need to fetch the data before you can search it.

**Can't find a character:**
Make sure the spelling is right. The search is case-insensitive and does partial matching, so "luke" will find "Luke Skywalker" but you need at least part of the name correct.

**Ingestion fails halfway:**
Just run it again with `python3 ingest.py --refresh`. It won't duplicate data.

## Deploying to Render

If you want to put this online, it's set up for Render already:

1. Push to GitHub
2. Connect your repo to Render
3. It'll auto-detect the `render.yaml` and deploy

The build command runs `ingest.py` automatically so the database gets created on deployment.

---

That's pretty much it. The code should be straightforward if you want to poke around.
