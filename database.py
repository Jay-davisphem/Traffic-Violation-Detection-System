import sqlite3
import threading
from logger import logger

class ViolationDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._local = threading.local()
        self.connect()
        self.create_tables()

    def _get_connection(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            try:
                self._local.conn = sqlite3.connect(self.db_path)
                logger.info(f"Thread {threading.get_ident()}: Database connected.")
            except sqlite3.Error as e:
                logger.error(f"Thread {threading.get_ident()}: Error connecting to database: {e}")
                raise
        return self._local.conn

    def _get_cursor(self):
        if not hasattr(self._local, 'cursor') or self._local.cursor is None:
            try:
                conn = self._get_connection()
                self._local.cursor = conn.cursor()
            except sqlite3.Error as e:
                logger.error(f"Thread {threading.get_ident()}: Error getting cursor: {e}")
                raise
        return self._local.cursor

    def connect(self):
        self._get_connection()

    def create_tables(self):
        try:
            cursor = self._get_cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    image_hash TEXT NOT NULL,
                    violation_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    bbox TEXT NOT NULL,
                    position_description TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_images (
                    image_hash TEXT PRIMARY KEY NOT NULL
                )
            """)
            self._get_connection().commit()
            logger.info(f"Thread {threading.get_ident()}: Violation and processed_images tables ensured.")
        except sqlite3.Error as e:
            logger.error(f"Thread {threading.get_ident()}: Error creating tables: {e}")
            raise

    def insert_violation(self, timestamp, image_path, image_hash, violation_type, confidence, bbox, position_description, latitude=None, longitude=None):
        try:
            cursor = self._get_cursor()
            cursor.execute("""
                INSERT INTO violations (timestamp, image_path, image_hash, violation_type, confidence, bbox, position_description, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, image_path, image_hash, violation_type, confidence, bbox, position_description, latitude, longitude))
            self._get_connection().commit()
            logger.info(f"Thread {threading.get_ident()}: Violation inserted at {timestamp} with type {violation_type}.")
        except sqlite3.Error as e:
            logger.error(f"Thread {threading.get_ident()}: Error inserting violation: {e}")
            raise

    def check_image_hash(self, image_hash):
        try:
            cursor = self._get_cursor()
            cursor.execute("SELECT 1 FROM processed_images WHERE image_hash = ?", (image_hash,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Thread {threading.get_ident()}: Error checking image hash: {e}")
            return False

    def insert_image_hash(self, image_hash):
        try:
            cursor = self._get_cursor()
            cursor.execute("INSERT INTO processed_images (image_hash) VALUES (?)", (image_hash,))
            self._get_connection().commit()
            logger.info(f"Thread {threading.get_ident()}: Image hash {image_hash} inserted into processed_images table.")
        except sqlite3.Error as e:
            logger.error(f"Thread {threading.get_ident()}: Error inserting image hash: {e}")
            raise

    def close(self):
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            try:
                self._local.conn.close()
                logger.info(f"Thread {threading.get_ident()}: Database connection closed.")
            except sqlite3.Error as e:
                logger.error(f"Thread {threading.get_ident()}: Error closing database connection: {e}")
            finally:
                self._local.conn = None
                self._local.cursor = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()