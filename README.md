# tic-tac-toe

# Tic-Tac-Toe

A full-stack Tic-Tac-Toe web app with user accounts, real-time multiplayer,
and a perfect-play minimax bot. Built with Flask, PostgreSQL, and plain
JavaScript — no frontend framework.

Play against the computer, or sign in from two browsers and play a
live human-vs-human match.

---

## Features

- **Accounts** — signup, login, session-based auth for the UI,
  HTTP Basic Auth for the JSON API. Passwords hashed with Werkzeug
  (`pbkdf2:sha256` / `scrypt`).
- **Play vs Computer** — unbeatable minimax bot (never loses, only draws).
- **Play vs Human** — create a game, share the room, opponent joins from
  another browser. The board updates automatically via polling.
- **Game states** — `waiting`, `in_progress`, `draw`, `win`. Moves are
  rejected when it's not your turn, when the game is over, or when the
  cell is occupied.
- **Scoreboard** — per-user history of finished games, filtered by the
  current session. Shows who won, "Bot", or "Draw".
- **REST API** — JSON endpoints for every operation. Usable from Postman
  or any HTTP client, independent of the browser UI.
- **Persistent storage** — games and users survive server restarts;
  PostgreSQL holds all state.

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Web framework | Flask 3 |
| ORM | SQLAlchemy 2 (Flask-SQLAlchemy) |
| Database | PostgreSQL 15+ |
| Auth | Werkzeug password hashing, Flask sessions, HTTP Basic Auth |
| Frontend | Jinja2 templates, Bootstrap 5, vanilla JavaScript (polling) |
| Testing | Postman collection (manual + runner) |

No JS framework. No ORM migrations tool. No build step. Deliberately small.

## Architecture

The project is layered, with dependencies pointing inward:
web/ HTTP: routes, auth decorators, JSON serialization
↓
domain/ Business rules: GameService (rules + minimax), UserService
↓
datasource/ Persistence: SQLAlchemy models, repositories, DTO mappers


- **`domain/`** knows nothing about Flask, HTTP, or SQL. `Game` and `Board`
  are plain Python objects; `GameService` and `UserService` implement the
  rules and have no side effects beyond what they're told to persist.
- **`datasource/`** translates between domain objects and database rows.
  `GameRepository` owns the SQL; the domain never sees a `GameRow`.
- **`web/`** handles HTTP only. Controllers parse the request, call the
  container, and serialize the response. They don't implement rules.
- **`di/container.py`** wires everything together. Swapping the in-memory
  storage for Postgres (which happened during development) touched only
  this layer and the repository — nothing above it changed.

### Data flow: making a move
Browser POST /game/<id> (form: cell=4)  
│  
▼  
main.py reads request.form, calls container  
│  
▼  
Container play_turn(game_id, row, col, user_id)  
├─ loads game from DB via repository (GameRow → GameDTO → Game)  
├─ GameService.make_move (domain logic)  
├─ if vs bot and it's O's turn:  
│ GameService.get_next_move (minimax, clone-based)  
│ GameService.make_move  
├─ saves game back (Game → GameDTO → GameRow)  
└─ if game over: writes to completed_games  
│  
▼  
Redirect 302 → GET /game/<id> → renders template  

For a human-vs-human game, the opponent's browser polls
`GET /game/<id>/state` every 2 seconds and reloads when the board
differs from what it last rendered.

## Quick start

### 1. Requirements

- Python 3.11 or newer
- PostgreSQL 15+ running locally
- `git`

### 2. Clone and set up

```bash
git clone https://github.com/<your-username>/tic-tac-toe.git
cd tic-tac-toe

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt  
```

### 3. Create the database
In psql (or pgAdmin):
``` sql
CREATE DATABASE tic_tac_toe
    WITH ENCODING 'UTF8'
        TEMPLATE = template0;  
```
The application will create its tables on first start via db.create_all().  

### 4. Configure environment  

Create .env in the project root:  
``` dotenv
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/tic_tac_toe
SECRET_KEY=change-me-in-production
```
On Windows, additionally set:  

``` dotenv
PYTHONUTF8=1
PGCLIENTENCODING=UTF8
```
to avoid a known psycopg2 + Windows Unicode pitfall.

5. Run

``` bash
python main.py
```
Open http://127.0.0.1:5000. Sign up, then:

Click Play vs Computer for a bot game.

Click Play vs Human → open a second browser (or incognito) →
log in as a different user → Join the game by room id.
