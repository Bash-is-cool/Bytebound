# Bytebound

A game in which you must write commands to move your character through the various levels. Check Core Command API section to see commands.

---

## Installation:
1. Install exe from github releases page
2. Download ZIP and extract to folder. Run `python main.py` to run the file while in the same directory as it.

---

## Language Specifications & Precedence

The scripting engine breaks raw instruction streams down into individual token sequences via regular expressions. Boolean evaluations are parsed using a recursive descent matching model matching standard structural precedence operators:

1. **Level 1 (Lowest Precedence):** `or` Logic Splits
2. **Level 2:** `and` Logic Gates
3. **Level 3 (Highest Precedence):** Binary Relational Injections (`==`, `!=`, `<`, `>`, `<=`, `>=`)

### Environment State Snapshot Keys
When writing code scripts, the runtime engine exposes these state values from the live game board directly to your variables:
* `north` / `south` / `east` / `west`: Returns `"wall"` or `"sand"` depending on adjacent tile conditions.

---

## Core Command API

Commands can be executed raw on their own line, or conditionally trailing a structured divider colon (`:`).

| Command syntax                 | Arguments | Description |
|:-------------------------------| :--- | :--- |
| `walk [direction] [distance]`  | `direction` (up/down/left/right), `distance` (frames) | Appends a positional move sequence to the action queue. |
| `if [condition] : [command]`   | `condition` is any standard condition. `command` is any walk | The conditions use the cardinal directions to see if you can walk there or if there is a wall i.e `if west == wall : walk up 20` |
| `elif [condition] : [command]` | `condition` same as if | same as if but must be preceeded by an if statement |
| `else : [command]`             | | Same as if but must have either a `elif` or `if` before it|

---

## Code Script Examples: How to Play

Below are functional examples demonstrating how to use the single-line conditional architecture, `elif` chains, and fallback `else` logic scopes to control your entity on the grid.

### 1. Basic Obstacle Navigation
Safely inspect adjacent tile types before queuing a movement sequence.
```
if north == sand : walk up 10
if north == wall : walk right 15
```

---

### AI Usage
AI was used to create the tokenizer. This tokenizer uses Lexer and parsers (such as the boolean parser) to make a single file for all special types of conditions that are used in game.
