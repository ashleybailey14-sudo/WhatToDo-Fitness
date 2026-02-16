"""
Supabase database helper for the Galactic Gains Health App.
Handles all reads/writes to physical_profile, equipment_inventory, and food_preferences.
"""

import streamlit as st
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """Create and return a Supabase client using Streamlit secrets."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ─── Physical Profile ────────────────────────────────────────────────

def get_all_user_names() -> list[str]:
    """Return a list of all distinct user_name values from physical_profile."""
    sb = get_supabase_client()
    resp = sb.table("physical_profile").select("user_name").execute()
    names = sorted(set(row["user_name"] for row in resp.data)) if resp.data else []
    return names


def get_physical_profile(user_name: str) -> dict | None:
    """Return the physical profile row for a given user, or None."""
    sb = get_supabase_client()
    resp = (
        sb.table("physical_profile")
        .select("*")
        .eq("user_name", user_name)
        .execute()
    )
    if resp.data:
        return resp.data[0]
    return None


def upsert_physical_profile(
    user_name: str,
    age: int,
    height_in: int,
    weight_lbs: int,
    medical_notes: str,
) -> dict:
    """Insert or update a physical profile row. Returns the upserted row."""
    sb = get_supabase_client()
    existing = get_physical_profile(user_name)
    if existing:
        resp = (
            sb.table("physical_profile")
            .update(
                {
                    "age": age,
                    "height_in": height_in,
                    "weight_lbs": weight_lbs,
                    "medical_notes": medical_notes,
                    "updated_at": "now()",
                }
            )
            .eq("user_name", user_name)
            .execute()
        )
    else:
        resp = (
            sb.table("physical_profile")
            .insert(
                {
                    "user_name": user_name,
                    "age": age,
                    "height_in": height_in,
                    "weight_lbs": weight_lbs,
                    "medical_notes": medical_notes,
                }
            )
            .execute()
        )
    return resp.data[0] if resp.data else {}


def rename_user(old_name: str, new_name: str):
    """Rename a user across all three tables."""
    sb = get_supabase_client()
    sb.table("physical_profile").update({"user_name": new_name}).eq("user_name", old_name).execute()
    sb.table("equipment_inventory").update({"user_name": new_name}).eq("user_name", old_name).execute()
    sb.table("food_preferences").update({"user_name": new_name}).eq("user_name", old_name).execute()


def update_weight(user_name: str, weight_lbs: int):
    """Quick-update just the weight for a user."""
    sb = get_supabase_client()
    sb.table("physical_profile").update(
        {"weight_lbs": weight_lbs, "updated_at": "now()"}
    ).eq("user_name", user_name).execute()


# ─── Equipment Inventory ─────────────────────────────────────────────

def get_equipment(user_name: str) -> list[dict]:
    """Return all equipment rows for a user."""
    sb = get_supabase_client()
    resp = (
        sb.table("equipment_inventory")
        .select("*")
        .eq("user_name", user_name)
        .order("id")
        .execute()
    )
    return resp.data or []


def add_equipment(user_name: str, name: str, category: str, notes: str = "") -> dict:
    """Add an equipment item for a user."""
    sb = get_supabase_client()
    resp = (
        sb.table("equipment_inventory")
        .insert(
            {
                "user_name": user_name,
                "name": name,
                "category": category,
                "notes": notes,
            }
        )
        .execute()
    )
    return resp.data[0] if resp.data else {}


def delete_equipment(row_id: int):
    """Delete an equipment row by its primary key."""
    sb = get_supabase_client()
    sb.table("equipment_inventory").delete().eq("id", row_id).execute()


# ─── Food Preferences ────────────────────────────────────────────────

def get_food_preferences(user_name: str) -> list[dict]:
    """Return all food preference rows for a user."""
    sb = get_supabase_client()
    resp = (
        sb.table("food_preferences")
        .select("*")
        .eq("user_name", user_name)
        .order("id")
        .execute()
    )
    return resp.data or []


def add_food_preference(
    user_name: str, item_name: str, preference_type: str, nutritional_goal: str = ""
) -> dict:
    """Add a food preference for a user."""
    sb = get_supabase_client()
    resp = (
        sb.table("food_preferences")
        .insert(
            {
                "user_name": user_name,
                "item_name": item_name,
                "preference_type": preference_type,
                "nutritional_goal": nutritional_goal,
            }
        )
        .execute()
    )
    return resp.data[0] if resp.data else {}


def delete_food_preference(row_id: int):
    """Delete a food preference row by its primary key."""
    sb = get_supabase_client()
    sb.table("food_preferences").delete().eq("id", row_id).execute()


# ─── Recommendation History ──────────────────────────────────────────

def get_recommendation_history(user_name: str, limit: int = 10) -> list[dict]:
    """Return recent recommendation history for a user (newest first).

    This reads from a 'recommendation_history' table if it exists.
    If the table doesn't exist yet, returns an empty list gracefully.
    """
    sb = get_supabase_client()
    try:
        resp = (
            sb.table("recommendation_history")
            .select("*")
            .eq("user_name", user_name)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


def save_recommendation(
    user_name: str, workout: str, dinner: str
):
    """Save a recommendation to history. Silently fails if table doesn't exist."""
    sb = get_supabase_client()
    try:
        sb.table("recommendation_history").insert(
            {
                "user_name": user_name,
                "workout": workout,
                "dinner": dinner,
            }
        ).execute()
    except Exception:
        pass  # Table may not exist yet — that's okay
