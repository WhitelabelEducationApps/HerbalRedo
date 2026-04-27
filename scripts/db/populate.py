"""SQLite database population for plants.db."""

import sqlite3
import os
from config import DB_PATH, DB_COLUMNS, MEDICINAL_CATEGORIES


def init_db():
    """Ensure database schema has ar/hi columns. Creates if doesn't exist."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(museum_item)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    # Add missing ar/hi columns
    columns_to_add = [
        ('description_ar', 'TEXT'),
        ('paintingname_ar', 'TEXT'),
        ('style_ar', 'TEXT'),
        ('description_hi', 'TEXT'),
        ('paintingname_hi', 'TEXT'),
        ('style_hi', 'TEXT'),
    ]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE museum_item ADD COLUMN {col_name} {col_type}")
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Column may already exist

    # Same for authors table
    cursor.execute("PRAGMA table_info(authors)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    authors_cols = [
        ('name_ar', 'TEXT'),
        ('name_hi', 'TEXT'),
        ('description_ar', 'TEXT'),
        ('description_hi', 'TEXT'),
    ]

    for col_name, col_type in authors_cols:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE authors ADD COLUMN {col_name} {col_type}")
                conn.commit()
            except sqlite3.OperationalError:
                pass

    conn.close()


def get_next_plant_id():
    """Get the next available plant ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM museum_item")
    result = cursor.fetchone()
    conn.close()

    max_id = result[0] if result and result[0] else -1
    return max_id + 1


def get_existing_plant_ids():
    """Get all existing plant IDs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM museum_item ORDER BY id")
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids


def insert_plant(plant_data):
    """
    Insert or update a plant in the database.
    plant_data should be dict with keys: id, author, descriptions, images, colors, etc.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    plant_id = plant_data.get('id')
    descriptions = plant_data.get('descriptions', {})
    names = plant_data.get('names', {})
    colors = plant_data.get('colors', [0xFF808080] * 4)
    image_url = plant_data.get('image_url')
    author = plant_data.get('author', 'tonic')

    # Build column list and values
    columns = ['id', 'author', 'location', 'isFavourite', 'viewed', 'visited', 'prim_color', 'sec_color', 'detail_color', 'background_color', 'full_image_uri']
    values = [plant_id, author, '0,0', 'false', 'false', 'false', colors[0], colors[1], colors[2], colors[3], image_url or '']

    # Add language columns
    for lang in ['en', 'ro', 'es', 'de', 'fr', 'it', 'ru', 'pt', 'zh', 'ja', 'ar', 'hi']:
        name_col, desc_col, style_col = DB_COLUMNS.get(lang, (None, None, None))

        if name_col:
            columns.append(name_col)
            values.append(names.get(lang, ''))

        if desc_col:
            columns.append(desc_col)
            values.append(descriptions.get(lang, ''))

        if style_col:
            columns.append(style_col)
            values.append(author)  # Style = category name

    # Check if plant exists
    cursor.execute("SELECT id FROM museum_item WHERE id = ?", (plant_id,))
    exists = cursor.fetchone() is not None

    if exists:
        # Update
        set_clause = ', '.join([f"{col} = ?" for col in columns if col != 'id'])
        update_vals = values[1:] + [plant_id]
        cursor.execute(f"UPDATE museum_item SET {set_clause} WHERE id = ?", update_vals)
    else:
        # Insert
        placeholders = ', '.join(['?' for _ in columns])
        cursor.execute(f"INSERT INTO museum_item ({', '.join(columns)}) VALUES ({placeholders})", values)

    conn.commit()
    conn.close()


def populate_categories():
    """Populate the authors table with medicinal categories."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing categories (keep any manually added, except our predefined ones)
    # Actually, let's just clear and re-insert to be clean
    cursor.execute("DELETE FROM authors")

    for category_id, category_data in MEDICINAL_CATEGORIES.items():
        columns = ['id', 'name', 'description', 'name_ro', 'description_ro', 'name_es', 'description_es',
                   'name_de', 'description_de', 'name_fr', 'description_fr', 'name_it', 'description_it',
                   'name_ru', 'description_ru', 'name_pt', 'description_pt', 'name_zh', 'description_zh',
                   'name_ja', 'description_ja', 'name_ar', 'description_ar', 'name_hi', 'description_hi']

        values = [
            category_id,
            category_data['name'],
            category_data['description'],
            category_data['name_ro'],
            category_data['description'],
            category_data['name_es'],
            category_data['description'],
            category_data['name_de'],
            category_data['description'],
            category_data['name_fr'],
            category_data['description'],
            category_data['name_it'],
            category_data['description'],
            category_data['name_ru'],
            category_data['description'],
            category_data['name_pt'],
            category_data['description'],
            category_data['name_zh'],
            category_data['description'],
            category_data['name_ja'],
            category_data['description'],
            category_data['name_ar'],
            category_data['description'],
            category_data['name_hi'],
            category_data['description'],
        ]

        placeholders = ', '.join(['?' for _ in columns])
        cursor.execute(f"INSERT INTO authors ({', '.join(columns)}) VALUES ({placeholders})", values)

    conn.commit()
    conn.close()
