# DataSoluTech — Healthcare data migration to MongoDB

Migrates a public healthcare dataset from Kaggle into a MongoDB collection with a
server-side schema validator, then verifies that what landed in the database matches
the source.

The dataset is **not** stored in this repository. It is downloaded at runtime, so a
fresh clone always works from the published source rather than from a stale copy.

## What it does

The work is split into three steps that run in order. Each one only starts if the
previous one exited successfully, so invalid source data can never reach the database.

```
mongodb (healthy)
    │
    ├─ 1. unit_tests        check the source data          (no database needed)
    │        exit 0
    ├─ 2. migrate           download, transform, insert
    │        exit 0
    └─ 3. integrity_tests   check what landed in MongoDB
```

| Step | What it checks or does |
|---|---|
| `unit_tests` | 5 checks on the downloaded DataFrame: not empty, 15 columns, no duplicates, no nulls, correct types and allowed values |
| `migrate` | Drops and recreates `healthcare_db.patients` with its validator, converts dates, normalises names, inserts 54 966 documents |
| `integrity_tests` | 6 checks against the live database: collection exists, has documents, field count, document count matches the source, stored types |

## Requirements

- Docker with Compose v2 (the only requirement for the standard workflow)
- Python 3.11 and MongoDB, only if you want to run outside Docker

## Quick start

```bash
# 1. Provide credentials
cp .env.example .env
#    then edit .env and change MONGO_ROOT_PASSWORD

# 2. Run the whole pipeline
docker compose --profile pipeline up -d

# 3. Read the results of each step
docker compose logs unit_tests
docker compose logs migrate
docker compose logs integrity_tests
```

Expected output from step 2 and 3:

```
migrate           | imported 54966 documents into healthcare_db.patients
integrity_tests   | 6 passed
```

## Commands

| Command | What it does |
|---|---|
| `docker compose --profile pipeline up -d` | Runs all three steps in order |
| `docker compose up -d mongodb` | Starts only the database |
| `docker compose --profile pipeline run --rm unit_tests` | Runs one step on its own |
| `docker compose --profile pipeline run --rm migrate` | Same, for the migration |
| `docker compose --profile pipeline run --rm integrity_tests` | Same, for the integrity tests |
| `docker compose ps -a` | Shows each step and its exit code |
| `docker compose logs -f <service>` | Follows the logs of one service |
| `docker compose down` | Stops everything, keeps the data |
| `docker compose down -v` | Stops everything and deletes the data volume |

`mongodb` has no profile, so a plain `docker compose up -d` starts the database
alone. The three pipeline steps are one-shot jobs and stay hidden until you pass
`--profile pipeline`.

Running a step with `run` also runs the steps it depends on: asking for
`integrity_tests` runs `unit_tests`, then `migrate`, then the integrity tests. Add
`--no-deps` to run a step strictly on its own.

Inspecting the data by hand:

```bash
mongosh "mongodb://admin:<password>@localhost:27017/healthcare_db?authSource=admin"

db.patients.countDocuments()
db.patients.findOne()
```

## Project structure

| File | Role |
|---|---|
| `healthcare.py` | Migration script. Builds the connection string, creates the validated collection, transforms and inserts the data |
| `dataset.py` | Downloads the dataset from Kaggle into a DataFrame and removes duplicate rows |
| `conftest.py` | Shared pytest fixtures: MongoDB client, database, collection, source DataFrame |
| `df_integrity_test.py` | Checks the source data, before migration |
| `collection_integrity_test.py` | Checks the migrated data, in MongoDB |
| `docker-compose.yml` | The database service plus the three pipeline steps |
| `Dockerfile` | `python:3.11` image with the project dependencies |
| `requirements.txt` | Pinned dependencies |
| `.env.example` | Template for the credentials, copy to `.env` |
| `.dockerignore` | Keeps the local virtualenv and `.env` out of the image |
| `SCHEMA.md` | Database schema: fields, types, constraints, transformations |

## Configuration

All configuration goes through environment variables. Real values live in `.env`,
which is gitignored; `.env.example` documents them.

| Variable | Purpose | Default |
|---|---|---|
| `MONGO_ROOT_USERNAME` | MongoDB root account | `admin` |
| `MONGO_ROOT_PASSWORD` | Password for that account | none, must be set |
| `MONGO_HOST` | `host:port` of the server | `localhost:27017` |
| `MDB_URI` | Full connection string. Overrides the three variables above when set | unset |

Docker Compose sets `MONGO_HOST=mongodb:27017` inside the containers, because
`mongodb` is the service name and resolves over the project's Docker network.

## Authentication

The database is never exposed without credentials.

- Passing `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` to the
  MongoDB image creates a root account and starts the server with `--auth`.
  Unauthenticated commands are refused.
- `healthcare.py` builds its connection string from the environment. The credentials
  are URL-escaped, and `authSource=admin` is set because MongoDB stores accounts in
  the `admin` database rather than in `healthcare_db`.
- Passwords are never written in the source or in `docker-compose.yml`. They are read
  from `.env`, which is excluded from both git and the Docker image. A secret copied
  into an image layer cannot be removed later, so it must never be copied in.
- MongoDB does not store passwords in clear text. It keeps SCRAM-SHA-256 credentials,
  a salted hash with an iteration count, and the password is never sent in clear
  during the handshake.
- The services communicate over a named Docker network, `healthcare_net`. Only
  containers attached to it can reach the database.

## Data source

[`prasad22/healthcare-dataset`](https://www.kaggle.com/datasets/prasad22/healthcare-dataset)
on Kaggle, version 2. Downloaded by `dataset.py` through `kagglehub`; no Kaggle
account is required.

| | |
|---|---|
| Rows published | 55 500 |
| Exact duplicates removed | 534 |
| Documents inserted | 54 966 |

The download is cached in a Docker volume, so it happens once and is then shared by
all three pipeline steps.

## Database schema

See [SCHEMA.md](SCHEMA.md) for the collection's fields, types, constraints and the
transformations applied before insertion.

## Running without Docker

You need a MongoDB server reachable at `MONGO_HOST` and, if it enforces
authentication, matching credentials in `.env`.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python healthcare.py     # run the migration
pytest                   # run all 11 tests
```

`pytest` reads `.env` automatically, so there is nothing to export by hand. The
integrity tests inspect the collection produced by the migration rather than building
their own, so run `healthcare.py` first — otherwise they fail with a message telling
you to.

## Troubleshooting

**Authentication fails after changing the password.** The MongoDB image only creates
the root account when its data directory is empty. Changing `.env` has no effect on an
existing volume. Recreate it:

```bash
docker compose down -v
docker compose --profile pipeline up -d
```

**A step did not run.** Each step depends on the previous one exiting 0. Check where
the chain stopped:

```bash
docker compose ps -a
```

**The dataset is downloaded on every run.** The cache volume was removed. Recreate it
by bringing the pipeline up again; the first run repopulates it.
