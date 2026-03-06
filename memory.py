from db import get_connection

WINDOW_SIZE = 15


def get_recent_messages(user_id: str, avatar_id: int, limit: int = WINDOW_SIZE) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content FROM messages
        WHERE user_id = ? AND avatar_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, avatar_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]


def get_all_messages(user_id: str, avatar_id: int) -> list:
    """Get every message in the session — used for end-of-chat analysis."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content FROM messages
        WHERE user_id = ? AND avatar_id = ?
        ORDER BY timestamp ASC
    """, (user_id, avatar_id))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


def save_message(user_id: str, avatar_id: int, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (user_id, avatar_id, role, content)
        VALUES (?, ?, ?, ?)
    """, (user_id, avatar_id, role, content))
    conn.commit()
    conn.close()


def clear_messages(user_id: str, avatar_id: int):
    """Clear chat history after analysis so next session starts fresh."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM messages WHERE user_id = ? AND avatar_id = ?
    """, (user_id, avatar_id))
    conn.commit()
    conn.close()