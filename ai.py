"""
Gemini AI module for the Galactic Gains Health App.
Generates personalized workout and dinner recommendations.
"""

import time
import streamlit as st
import google.generativeai as genai


def _get_model():
    """Configure and return the Gemini model."""
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-2.0-flash")


def _generate_with_retry(model, prompt, max_retries=3):
    """Call Gemini with automatic retry on 429 rate-limit errors."""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "quota" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 15  # 15s, 30s, 45s
                    st.toast(f"⏳ Rate limited — waiting {wait_time}s before retrying...")
                    time.sleep(wait_time)
                else:
                    return (
                        f"**⚠️ Gemini rate limit reached after {max_retries} attempts.**\n\n"
                        f"Full error: `{e}`\n\n"
                        "The free tier allows only a few requests per minute. "
                        "Please wait about 60 seconds and try again."
                    )
            else:
                return f"**Error:** {e}"
    return f"**Error after {max_retries} retries:** {last_error}"


def build_workout_prompt(profile: dict, equipment: list[dict], history: list[dict]) -> str:
    """Build the workout recommendation prompt."""
    # Format equipment list
    if equipment:
        equip_str = "\n".join(
            f"  - {e['name']} ({e['category']}){' — ' + e['notes'] if e.get('notes') else ''}"
            for e in equipment
        )
    else:
        equip_str = "  No equipment listed — suggest bodyweight exercises only."

    # Format history
    if history:
        hist_str = "\n".join(
            f"  - {h.get('workout', 'N/A')[:120]}"
            for h in history[:7]
        )
    else:
        hist_str = "  No previous workouts on record."

    height_ft = profile.get("height_in", 0) // 12
    height_remaining = profile.get("height_in", 0) % 12

    prompt = f"""You are a certified personal trainer creating a personalized 45-minute workout.

USER PROFILE:
  Name: {profile.get('user_name', 'Unknown')}
  Age: {profile.get('age', 'Unknown')}
  Height: {height_ft}'{height_remaining}"
  Weight: {profile.get('weight_lbs', 'Unknown')} lbs
  Medical notes / limitations: {profile.get('medical_notes', 'None')}

AVAILABLE EQUIPMENT:
{equip_str}

RECENT PAST WORKOUTS (avoid repeating these):
{hist_str}

INSTRUCTIONS:
- Design a 45-minute workout that is DIFFERENT from the recent past workouts listed above.
- The workout should be interesting and varied. Acceptable formats include:
    • 15 minutes each of three different workout types (e.g., strength, cardio, mobility)
    • 5-minute warm-up + 35-minute main workout + 5-minute cooldown
    • Any other creative 45-minute structure
- Respect ALL medical notes and limitations. If a limitation is listed, do NOT suggest exercises that could aggravate it.
- Only suggest exercises that use the available equipment or bodyweight.
- Include sets, reps (or duration), and brief form cues for each exercise.
- Keep the tone encouraging and fun — this is Galactic Gains!

Format the response in clean markdown with clear sections."""

    return prompt


def build_dinner_prompt(profile: dict, food_prefs: list[dict], history: list[dict]) -> str:
    """Build the dinner recommendation prompt."""
    # Format food preferences
    if food_prefs:
        pref_str = "\n".join(
            f"  - {f['item_name']} (type: {f['preference_type']})"
            f"{' — goal: ' + f['nutritional_goal'] if f.get('nutritional_goal') else ''}"
            for f in food_prefs
        )
    else:
        pref_str = "  No food preferences recorded."

    # Format past dinners
    if history:
        dinner_hist = "\n".join(
            f"  - {h.get('dinner', 'N/A')[:120]}"
            for h in history[:7]
        )
    else:
        dinner_hist = "  No previous dinner suggestions on record."

    prompt = f"""You are a nutrition-savvy personal chef creating a personalized dinner suggestion.

USER PROFILE:
  Name: {profile.get('user_name', 'Unknown')}
  Age: {profile.get('age', 'Unknown')}
  Weight: {profile.get('weight_lbs', 'Unknown')} lbs
  Medical notes: {profile.get('medical_notes', 'None')}

FOOD PREFERENCES & DIETARY NEEDS:
{pref_str}

RECENT PAST DINNER SUGGESTIONS (suggest something different):
{dinner_hist}

INSTRUCTIONS:
- Suggest ONE dinner that aligns with the user's food preferences and nutritional goals.
- Make it DIFFERENT from past suggestions.
- Respect any allergies or items marked "avoid."
- Be descriptive and flavorful in your suggestion but do NOT include the full recipe.
  Example good answer: "Lemon pepper grilled chicken with cilantro lime rice and roasted garlic asparagus."
- After the suggestion, ask: "Would you like the full recipe?"
- Keep the tone fun and appetizing — this is Galactic Gains fuel!

Format the response in clean markdown."""

    return prompt


def get_workout_recommendation(profile: dict, equipment: list[dict], history: list[dict]) -> str:
    """Generate a workout recommendation using Gemini."""
    model = _get_model()
    prompt = build_workout_prompt(profile, equipment, history)
    return _generate_with_retry(model, prompt)


def get_dinner_recommendation(profile: dict, food_prefs: list[dict], history: list[dict]) -> str:
    """Generate a dinner recommendation using Gemini."""
    model = _get_model()
    prompt = build_dinner_prompt(profile, food_prefs, history)
    return _generate_with_retry(model, prompt)


def get_recipe_details(dinner_description: str, food_prefs: list[dict]) -> str:
    """When the user asks for the full recipe, generate it."""
    model = _get_model()

    if food_prefs:
        pref_str = ", ".join(
            f"{f['item_name']} ({f['preference_type']})" for f in food_prefs
        )
    else:
        pref_str = "No specific preferences."

    prompt = f"""The user wants the full recipe for this dinner:

"{dinner_description}"

User's food preferences: {pref_str}

Please provide:
1. Ingredients list with quantities
2. Step-by-step cooking instructions
3. Approximate cook time
4. Any helpful tips

Keep the tone fun and format in clean markdown."""

    return _generate_with_retry(model, prompt)
