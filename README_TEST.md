# Coding Test: SWAPI Data and Query Tool

## Overview

Build a system that pulls data from the Star Wars API (SWAPI), stores it, and provides a way to retrieve or query that data.

## Requirements

- **Python 3.8+** (required)
- **`requirements.txt`** listing any dependencies
- **`README.md`** with run instructions (see Deliverables)

Your solution must:

1. **Get data from the SWAPI API**  
   Use [SWAPI](https://swapi.info/documentation) (base URL: `https://swapi.info/api`). No authentication. Use whatever resources and endpoints you find relevant.

2. **Store the data**  
   Persist the fetched data in some form so it can be queried later. How you store it and where is up to you.

3. **Retrieval / query tool**  
   Provide a way to query or retrieve the stored data (e.g. by criteria, filters, or a simple query language). The interface is your choice (CLI, script, library, etc.).

## Deliverables

- Code that implements the above
- A `requirements.txt` for a Python 3.8+ environment
- A `README.md` with instructions on how to run ingestion and how to run or use the query/retrieval tool

Zip your project files and email the archive to kyle@gryps.io and alyssa@gryps.io.

## Test queries

Your system should be able to answer questions like these (using your query/retrieval tool):

1. What are the names of all the films that Luke Skywalker appears in?
2. What are the names of all characters who appear in "A New Hope" (Episode IV)?
3. What is the name of the homeworld of Luke Skywalker?
4. What are the names of all characters who are from the planet Tatooine?
5. What are the names of all starships piloted by Han Solo?

## Getting started

- Read the API docs: https://swapi.info/documentation  
- Set up a Python 3.8+ environment and install from `requirements.txt`  
- Design how you’ll fetch, store, and query the data; then implement.

Good luck.
