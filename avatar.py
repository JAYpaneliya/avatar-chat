from db import get_connection
from models import AvatarCreate


def create_avatar(user_id: str, data: AvatarCreate) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO avatars 
        (user_id, name, age, location, relationship, situation, occupation,
         interests, behaviour, communication_style, slangs, language)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, data.name, data.age, data.location, data.relationship,
        data.situation, data.occupation, data.interests, data.behaviour,
        data.communication_style, data.slangs, data.language
    ))

    conn.commit()
    avatar_id = cursor.lastrowid
    conn.close()
    return get_avatar_by_id(avatar_id)


def get_avatar_by_id(avatar_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM avatars WHERE id = ?", (avatar_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_avatars_by_user(user_id: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, name, relationship, created_at 
        FROM avatars WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_avatar(avatar_id: int, user_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM avatars WHERE id = ? AND user_id = ?", (avatar_id, user_id))
    deleted = cursor.rowcount > 0
    if deleted:
        cursor.execute(
            "DELETE FROM messages WHERE avatar_id = ? AND user_id = ?",
            (avatar_id, user_id)
        )
    conn.commit()
    conn.close()
    return deleted