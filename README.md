# Relational Database Management with SQLAlchemy

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLAlchemy](https://img.shields.io/badge/SQLALCHEMY-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-000?style=for-the-badge&logo=sqlite&logoColor=07405E)

**Author:** Kathy Booth (with assistance from Claude)                
**Course:** Coding Temple — Database Module  
**Assignment:** Relational Database Practice with Python and SQLAlchemy

---

## Overview

This project demonstrates how to create and manage a relational database using Python and SQLAlchemy's ORM (Object Relational Mapper). It covers defining tables as Python classes, setting up relationships between them, and performing full CRUD (Create, Read, Update, Delete) operations — all using SQLite as the database backend.

---

## Project Structure

```
RelationalDBwSQLAlchemy/
├── relational_db_sqla.py   # Main script — all assignment code
├── shop.db                 # SQLite database (auto-created on first run)
└── README.md               # This file
```

---

## Requirements

- Python 3.x
- SQLAlchemy

### Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate      # Windows
   source venv/bin/activate     # Mac/Linux
   ```

2. Install SQLAlchemy:
   ```bash
   pip install sqlalchemy
   ```

---

## How to Run

```bash
python relational_db_sqla.py
```

The script will:
1. Create the `shop.db` SQLite database file automatically if it doesn't exist
2. Insert sample data on the first run only (subsequent runs skip the insert to prevent duplicates)
3. Print the results of all queries to the terminal

To start fresh, simply delete `shop.db` and rerun the script.

---

## Database Schema

### `users`
| Column | Type    | Constraints         |
|--------|---------|---------------------|
| id     | Integer | Primary Key         |
| name   | String  |                     |
| email  | String  | Unique              |

### `products`
| Column | Type    | Constraints |
|--------|---------|-------------|
| id     | Integer | Primary Key |
| name   | String  |             |
| price  | Integer |             |

### `orders`
| Column     | Type    | Constraints                    |
|------------|---------|--------------------------------|
| id         | Integer | Primary Key                    |
| user_id    | Integer | Foreign Key → users.id         |
| product_id | Integer | Foreign Key → products.id      |
| quantity   | Integer |                                |
| status     | Boolean | Default False (not shipped)    |

### Relationships
- A `User` can have many `Orders` (one-to-many)
- A `Product` can appear in many `Orders` (one-to-many)
- Cascade delete is configured on `User` → `Orders`, so deleting a user automatically removes their orders

---

## Assignment Parts

| Part | Description |
|------|-------------|
| Part 1 | Setup — engine, base, session |
| Part 2 | Define `User`, `Product`, and `Order` tables with relationships |
| Part 3 | Create tables using `Base.metadata.create_all(engine)` |
| Part 4 | Insert 5 users, 5 products, and 5 orders |
| Part 5 | Query all users, products, and orders; update a price; delete a user |
| Part 6 | Bonus — `status` column, unshipped orders query, order count per user |

---

## Sample Data

### Users (5 total)
| Name    | Note                                      |
|---------|-------------------------------------------|
| Kathy   | 2 orders (Laptop, Mouse)                  |
| Andrea  | 1 order (Headphones)                      |
| Brendan | 1 order (Keyboard)                        |
| LuLu    | 1 order (Webcam)                          |
| Marcus  | No orders — used to demonstrate deletion  |

### Products (5 total)
| Name        | Price  |
|-------------|--------|
| Laptop      | $1,200 |
| Headphones  | $150   |
| Mouse       | $40    |
| Keyboard    | $80    |
| Webcam      | $100   |

---

## Design Decisions

**Duplicate prevention:** The insert function checks whether any users already exist before inserting, so re-running the script does not create duplicate rows.

**Intentional orderless user:** Marcus is created with no orders so that the delete operation in Part 5 demonstrates a clean, dependency-free deletion without needing to handle cascades.

**Cascade delete:** `cascade="all, delete-orphan"` is set on `User.orders` so that if a user who *does* have orders is deleted, their orders are automatically removed — preventing foreign key constraint errors.

**`if __name__ == "__main__":`** All executable code is wrapped in this guard so the models and functions can be safely imported by other scripts without triggering the insert/query/delete operations.

**Pylint suppressions:** Three inline `# pylint: disable` comments are used for known SQLAlchemy false positives (`func.count`, `== False` comparisons, and the `Session` naming convention). These are intentional and do not affect runtime behavior.

---

## Viewing the Database

To inspect `shop.db` visually:
- **VS Code:** Install the [SQLite Viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer) extension and click on `shop.db` in the Explorer panel
- **Standalone:** Use [DB Browser for SQLite](https://sqlitebrowser.org/) (free download)
