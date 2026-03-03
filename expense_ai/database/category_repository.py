class CategoryRepository:

    def __init__(self, connection):
        self.conn = connection

    def get_by_id(self, category_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM categories
            WHERE id = ? AND is_active = 1
        """, (category_id,))
        return cursor.fetchone()

    def get_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM categories
            WHERE LOWER(name) = LOWER(?) AND is_active = 1
        """, (name,))
        return cursor.fetchone()

    def list_by_type(self, category_type):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM categories
            WHERE type = ? AND is_active = 1
            ORDER BY name ASC
        """, (category_type,))
        return cursor.fetchall()