"""
FitFlow — Health & Workout Recommendation App
==============================================
A personalized health app powered by Gemini AI, Supabase, and Streamlit.
"""

import streamlit as st
from db import (
    get_all_user_names,
    get_physical_profile,
    upsert_physical_profile,
    rename_user,
    update_weight,
    get_equipment,
    add_equipment,
    delete_equipment,
    get_food_preferences,
    add_food_preference,
    delete_food_preference,
    get_recommendation_history,
    save_recommendation,
)
from ai import get_workout_recommendation, get_dinner_recommendation, get_recipe_details


# ─── Page Config ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="FitFlow",
    page_icon="💪",
    layout="wide",
)


# ─── User Avatars — Each user gets a unique fitness-themed identity ───

AVATARS = {
    "Ashley": {
        "emoji": "🔥",
        "label": "Blaze",
        "color": "#FF6B6B",
        "gradient": "linear-gradient(135deg, #FF6B6B, #FF8E53)",
        "bg": "#FFF5F3",
    },
    "User A": {
        "emoji": "⚡",
        "label": "Bolt",
        "color": "#7C3AED",
        "gradient": "linear-gradient(135deg, #7C3AED, #A855F7)",
        "bg": "#F5F0FF",
    },
    "User B": {
        "emoji": "🌊",
        "label": "Wave",
        "color": "#0891B2",
        "gradient": "linear-gradient(135deg, #0891B2, #22D3EE)",
        "bg": "#F0FDFF",
    },
    "User C": {
        "emoji": "🏔️",
        "label": "Summit",
        "color": "#D97706",
        "gradient": "linear-gradient(135deg, #D97706, #FBBF24)",
        "bg": "#FFFBEB",
    },
    "User D": {
        "emoji": "🌿",
        "label": "Zen",
        "color": "#059669",
        "gradient": "linear-gradient(135deg, #059669, #34D399)",
        "bg": "#ECFDF5",
    },
}

DEFAULT_AVATAR = {
    "emoji": "🌟",
    "label": "Star",
    "color": "#FF6B6B",
    "gradient": "linear-gradient(135deg, #FF6B6B, #FF8E53)",
    "bg": "#FFF5F3",
}


def get_avatar(user_name: str) -> dict:
    """Get avatar for a user."""
    if user_name in AVATARS:
        return AVATARS[user_name]
    return DEFAULT_AVATAR


# ─── FitFlow Theme Styling ───────────────────────────────────────────

st.markdown(
    """
    <style>
    /* ── Base: force light theme regardless of device dark mode ── */
    .stApp {
        background: #FAFAFA;
        color-scheme: light;
    }

    /* Force MAIN AREA text to be dark — fixes iPhone dark mode */
    /* Scoped to stMainBlockContainer so it does NOT touch the sidebar */
    [data-testid="stMainBlockContainer"],
    [data-testid="stMainBlockContainer"] * {
        color: #1A1A2E;
    }
    [data-testid="stMainBlockContainer"] p,
    [data-testid="stMainBlockContainer"] span,
    [data-testid="stMainBlockContainer"] li,
    [data-testid="stMainBlockContainer"] h1,
    [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3,
    [data-testid="stMainBlockContainer"] h4,
    [data-testid="stMainBlockContainer"] h5,
    [data-testid="stMainBlockContainer"] h6,
    [data-testid="stMainBlockContainer"] strong,
    [data-testid="stMainBlockContainer"] em,
    [data-testid="stMainBlockContainer"] code,
    [data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"],
    [data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] * {
        color: #1A1A2E !important;
    }

    /* Keep buttons white text */
    .stButton > button, .stButton > button *,
    .stFormSubmitButton > button, .stFormSubmitButton > button * {
        color: white !important;
    }

    /* ── Sidebar: dark charcoal with coral accents ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1A2E 0%, #16213E 100%);
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] * {
        color: #F0F0F0 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
        color: #F0F0F0 !important;
    }

    /* Sidebar dropdown/select: dark text on white background */
    [data-testid="stSidebar"] [data-baseweb="select"],
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #1A1A2E !important;
        background-color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: #1A1A2E !important;
    }
    [data-testid="stSidebar"] [data-baseweb="popover"],
    [data-testid="stSidebar"] [data-baseweb="popover"] *,
    [data-testid="stSidebar"] [role="listbox"],
    [data-testid="stSidebar"] [role="listbox"] *,
    [data-testid="stSidebar"] [role="option"],
    [data-testid="stSidebar"] [role="option"] * {
        color: #1A1A2E !important;
        background-color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [role="option"]:hover {
        background-color: #F3F4F6 !important;
    }

    [data-testid="stSidebar"] .stMetric label {
        color: #94A3B8 !important;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #FF8E53 !important;
        font-size: 1.05rem;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .sidebar-notes {
        color: #94A3B8 !important;
        font-size: 0.8rem;
    }

    /* ── Avatar Banner ── */
    .avatar-banner {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 28px 36px;
        border-radius: 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .avatar-circle {
        width: 76px;
        height: 76px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 36px;
        flex-shrink: 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    .avatar-name {
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
    }
    .avatar-subtitle {
        font-size: 0.95rem;
        margin: 4px 0 0 0;
        opacity: 0.6;
        font-weight: 500;
    }

    /* ── Title (for setup screens) ── */
    .app-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B, #0891B2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .app-tagline {
        text-align: center;
        color: #6B7280;
        font-size: 1rem;
        margin-top: 4px;
        font-weight: 500;
    }

    /* ── Buttons: coral-to-orange gradient, big & bold ── */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.85rem 2rem;
        font-weight: 800;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF8E53, #FF6B6B);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.35);
        transform: translateY(-2px);
        color: white;
    }

    /* ── Form submit buttons: teal variant ── */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #0891B2, #22D3EE) !important;
        color: white !important;
        border-radius: 12px;
        font-weight: 700;
    }
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #22D3EE, #0891B2) !important;
        box-shadow: 0 6px 20px rgba(8, 145, 178, 0.35);
        transform: translateY(-2px);
        color: white !important;
    }

    /* ── Tabs: big, bold, gradient when active ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #F3F4F6;
        border-radius: 16px;
        padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 800;
        font-size: 1.05rem;
        letter-spacing: 0.01em;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 107, 107, 0.08);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.35);
    }
    .stTabs [aria-selected="true"] *,
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {
        color: white !important;
    }

    /* Info/success/warning box text stays readable */
    .stAlert, .stAlert * {
        color: inherit !important;
    }

    /* Caption/muted text */
    .stApp .stCaption, .stApp .stCaption * {
        color: #6B7280 !important;
    }

    /* ── Section headers ── */
    h3 {
        color: #1A1A2E !important;
        font-weight: 700 !important;
    }
    h4 {
        color: #374151 !important;
        font-weight: 600 !important;
    }

    /* ── All input fields: force white bg + dark text (fixes iPhone dark mode) ── */
    input, textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="input"],
    [data-baseweb="textarea"],
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #1A1A2E !important;
        -webkit-text-fill-color: #1A1A2E !important;
        border: 1px solid #D1D5DB !important;
    }
    /* Placeholder text */
    input::placeholder, textarea::placeholder {
        color: #9CA3AF !important;
        -webkit-text-fill-color: #9CA3AF !important;
    }
    /* Select/dropdown in main area: white bg + dark text */
    [data-testid="stMainBlockContainer"] [data-baseweb="select"],
    [data-testid="stMainBlockContainer"] [data-baseweb="select"] * {
        background-color: #FFFFFF !important;
        color: #1A1A2E !important;
    }
    /* Number input +/- buttons */
    [data-testid="stNumberInput"] button {
        background-color: #F3F4F6 !important;
        color: #1A1A2E !important;
    }
    /* Form labels */
    .stTextInput label, .stTextArea label,
    .stNumberInput label, .stSelectbox label {
        color: #1A1A2E !important;
    }

    /* ── Dividers ── */
    hr {
        border-color: #E5E7EB;
    }

    /* ── Metric styling in main area ── */
    [data-testid="stMetricValue"] {
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Initialize Session State ────────────────────────────────────────

DEFAULT_USERS = ["Ashley", "User A", "User B", "User C", "User D"]

if "selected_user" not in st.session_state:
    st.session_state.selected_user = None
if "setup_mode" not in st.session_state:
    st.session_state.setup_mode = False
if "last_workout" not in st.session_state:
    st.session_state.last_workout = None
if "last_dinner" not in st.session_state:
    st.session_state.last_dinner = None


# ─── Ensure Default Users Exist in DB ────────────────────────────────

def ensure_default_users():
    """Make sure the five default user slots exist in physical_profile."""
    existing = get_all_user_names()
    for u in DEFAULT_USERS:
        if u not in existing:
            upsert_physical_profile(
                user_name=u,
                age=0,
                height_in=0,
                weight_lbs=0,
                medical_notes="",
            )


ensure_default_users()


# ─── Helper: Check if user is set up ─────────────────────────────────

def user_is_configured(profile: dict | None) -> bool:
    """A user is configured if they have height, weight, and age filled in."""
    if not profile:
        return False
    return all([
        profile.get("height_in", 0) > 0,
        profile.get("weight_lbs", 0) > 0,
        profile.get("age", 0) > 0,
    ])


# ─── Get current state ───────────────────────────────────────────────

all_users = get_all_user_names()
display_users = list(dict.fromkeys(DEFAULT_USERS + all_users))


# ─── Sidebar — User Selection + Profile Details ──────────────────────

with st.sidebar:
    st.markdown(
        "<p style='text-align:center; font-size:1.4rem; font-weight:800; "
        "background: linear-gradient(135deg, #FF6B6B, #FF8E53); "
        "-webkit-background-clip: text; -webkit-text-fill-color: transparent; "
        "margin-bottom:0;'>💪 FitFlow</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("##### Select Your Profile")

    selected = st.selectbox(
        "Who are you?",
        options=["— Select your profile —"] + display_users,
        index=0,
        key="user_dropdown",
        label_visibility="collapsed",
    )
    st.session_state.selected_user = selected

    # Show profile details in sidebar if user is configured
    profile = get_physical_profile(selected) if selected != "— Select your profile —" else None
    if profile and user_is_configured(profile):
        st.divider()
        avatar = get_avatar(selected)

        # Avatar + name in sidebar
        st.markdown(
            f"<div style='text-align:center;'>"
            f"<div style='display:inline-flex; align-items:center; justify-content:center; "
            f"width:64px; height:64px; border-radius:50%; font-size:30px; "
            f"background:{avatar['gradient']}; margin-bottom:8px; "
            f"box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>{avatar['emoji']}</div>"
            f"<p style='font-weight:700; font-size:1.1rem; margin:0; color:#F0F0F0;'>"
            f"{profile['user_name']}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("")  # spacer

        height_ft = profile["height_in"] // 12
        height_in_val = profile["height_in"] % 12

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Age", f"{profile.get('age', '—')}")
        with col2:
            st.metric("Height", f"{height_ft}'{height_in_val}\"")
        with col3:
            st.metric("Weight", f"{profile['weight_lbs']}")

        if profile.get("medical_notes"):
            st.divider()
            st.markdown(
                f"<p class='sidebar-notes'>📋 {profile['medical_notes']}</p>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown(
        "<p style='font-size:0.7rem; text-align:center; opacity:0.35;'>"
        "FitFlow v1.0 &middot; Gemini AI &middot; Supabase"
        "</p>",
        unsafe_allow_html=True,
    )


# ─── Main Content ────────────────────────────────────────────────────

user = st.session_state.selected_user

# ─── HOME PAGE — No user selected yet ────────────────────────────────

if user == "— Select your profile —":
    st.markdown("")
    st.markdown(
        "<p class='app-title'>💪 FitFlow</p>"
        "<p class='app-tagline'>Your personalized workout & dinner recommendations — powered by AI</p>",
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown("")
    st.markdown(
        "<div style='text-align:center; padding: 60px 20px;'>"
        "<p style='font-size: 4rem; margin-bottom: 16px;'>👈</p>"
        "<p style='font-size: 1.3rem; font-weight: 600; color: #6B7280;'>"
        "Select your profile from the sidebar to get started!"
        "</p>"
        "<p style='font-size: 1rem; color: #9CA3AF; margin-top: 8px;'>"
        "Pick your name from the dropdown, or choose an open slot to create a new profile."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

profile = get_physical_profile(user)
is_placeholder = user in ["User A", "User B", "User C", "User D"]

# ─── FIRST-TIME SETUP for placeholder users ──────────────────────────

if is_placeholder and not user_is_configured(profile):
    st.markdown(
        "<p class='app-title'>💪 FitFlow</p>"
        "<p class='app-tagline'>Your personalized workout & dinner recommendations — powered by AI</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(f"### 🆕 Welcome! Let's set up your profile.")
    st.info(f"You selected **{user}**. Fill in your details below to get started.")

    with st.form("new_user_form"):
        new_name = st.text_input("Your Name", placeholder="Enter your name")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_age = st.number_input("Age", min_value=10, max_value=120, value=30)
        with col2:
            feet = st.number_input("Height (feet)", min_value=3, max_value=8, value=5)
        with col3:
            inches = st.number_input("Height (inches)", min_value=0, max_value=11, value=6)
        new_weight = st.number_input("Weight (lbs)", min_value=50, max_value=600, value=150)
        new_medical = st.text_area(
            "Goals & Medical Notes / Limitations",
            placeholder="e.g., Weight loss, bad knees, Harrington rods — avoid high-impact spinal compression",
        )
        submitted = st.form_submit_button("🚀 Save Profile")

        if submitted:
            if not new_name.strip():
                st.error("Please enter your name!")
            else:
                height_in = (feet * 12) + inches
                upsert_physical_profile(
                    user_name=user,
                    age=new_age,
                    height_in=height_in,
                    weight_lbs=new_weight,
                    medical_notes=new_medical,
                )
                rename_user(user, new_name.strip())
                st.success(f"✅ Profile saved! Welcome, **{new_name.strip()}**!")
                st.rerun()

# ─── CONFIGURED USER VIEW ────────────────────────────────────────────

elif user_is_configured(profile):
    # Avatar banner at top
    avatar = get_avatar(user)
    st.markdown(
        f"""
        <div class="avatar-banner" style="background: {avatar['bg']}; border-left: 5px solid {avatar['color']};">
            <div class="avatar-circle" style="background: {avatar['gradient']}; color: white;">
                {avatar['emoji']}
            </div>
            <div>
                <p class="avatar-name" style="color: #1A1A2E;">
                    Welcome back, {profile['user_name']}!
                </p>
                <p class="avatar-subtitle" style="color: #6B7280;">
                    Let's make today count 💪
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ─── TABS ─────────────────────────────────────────────────────────

    tab_recs, tab_equip, tab_food, tab_profile = st.tabs(
        ["🏋️ Recommendations", "🔧 My Equipment", "🍽️ Food Preferences", "⚙️ Edit Profile"]
    )

    # ── Recommendations Tab ───────────────────────────────────────────
    with tab_recs:
        st.markdown("### 💡 Today's Recommendations")

        equipment = get_equipment(profile["user_name"])
        food_prefs = get_food_preferences(profile["user_name"])
        history = get_recommendation_history(profile["user_name"])

        rcol1, rcol2 = st.columns(2)

        with rcol1:
            st.markdown("#### 🏋️ Workout")
            if st.button("🎲 Generate Workout", use_container_width=True):
                with st.spinner("Building your workout..."):
                    workout = get_workout_recommendation(profile, equipment, history)
                    st.session_state.last_workout = workout

            if st.session_state.last_workout:
                st.markdown(st.session_state.last_workout)

        with rcol2:
            st.markdown("#### 🍽️ Dinner")
            if st.button("🎲 Generate Dinner Idea", use_container_width=True):
                with st.spinner("Cooking up ideas..."):
                    dinner = get_dinner_recommendation(profile, food_prefs, history)
                    st.session_state.last_dinner = dinner

            if st.session_state.last_dinner:
                st.markdown(st.session_state.last_dinner)

                if st.button("📜 Yes, give me the recipe!"):
                    with st.spinner("Writing up the recipe..."):
                        recipe = get_recipe_details(
                            st.session_state.last_dinner, food_prefs
                        )
                        st.markdown(recipe)

        # Save both if generated
        if st.session_state.last_workout and st.session_state.last_dinner:
            if st.button("💾 Save today's recommendations to history"):
                save_recommendation(
                    profile["user_name"],
                    st.session_state.last_workout[:500],
                    st.session_state.last_dinner[:500],
                )
                st.success("Saved to your history!")

    # ── Equipment Tab ─────────────────────────────────────────────────
    with tab_equip:
        st.markdown("### 🔧 My Equipment")
        st.caption("Tell us what you have available so we can tailor workouts.")

        equipment = get_equipment(profile["user_name"])

        if equipment:
            for item in equipment:
                ecol1, ecol2, ecol3 = st.columns([3, 2, 1])
                with ecol1:
                    st.write(f"**{item['name']}**")
                with ecol2:
                    st.caption(item.get("category", ""))
                with ecol3:
                    if st.button("🗑️", key=f"del_eq_{item['id']}"):
                        delete_equipment(item["id"])
                        st.rerun()
                if item.get("notes"):
                    st.caption(f"  _{item['notes']}_")
        else:
            st.info("No equipment added yet. Add some below!")

        st.divider()
        st.markdown("#### ➕ Add Equipment")
        with st.form("add_equipment_form"):
            eq_name = st.text_input("Equipment Name", placeholder="e.g., Kettlebell")
            eq_category = st.selectbox(
                "Category",
                ["strength", "cardio", "mobility", "other"],
            )
            eq_notes = st.text_input("Notes (optional)", placeholder="e.g., 16kg single")
            eq_submit = st.form_submit_button("Add Equipment")

            if eq_submit and eq_name.strip():
                add_equipment(profile["user_name"], eq_name.strip(), eq_category, eq_notes)
                st.success(f"Added **{eq_name.strip()}**!")
                st.rerun()

    # ── Food Preferences Tab ──────────────────────────────────────────
    with tab_food:
        st.markdown("### 🍽️ Food Preferences")
        st.caption("Help us suggest meals you'll actually enjoy.")

        food_prefs = get_food_preferences(profile["user_name"])

        if food_prefs:
            for fp in food_prefs:
                fcol1, fcol2, fcol3 = st.columns([3, 2, 1])
                with fcol1:
                    st.write(f"**{fp['item_name']}**")
                with fcol2:
                    badge_colors = {
                        "staple": "🟢", "avoid": "🔴", "allergy": "⛔",
                        "like": "👍", "dislike": "👎",
                    }
                    icon = badge_colors.get(fp.get("preference_type", ""), "⚪")
                    st.caption(f"{icon} {fp.get('preference_type', '')}")
                with fcol3:
                    if st.button("🗑️", key=f"del_fp_{fp['id']}"):
                        delete_food_preference(fp["id"])
                        st.rerun()
                if fp.get("nutritional_goal"):
                    st.caption(f"  _Goal: {fp['nutritional_goal']}_")
        else:
            st.info("No food preferences added yet. Add some below!")

        st.divider()
        st.markdown("#### ➕ Add Food Preference")
        with st.form("add_food_form"):
            fp_item = st.text_input(
                "Food Item or Category",
                placeholder="e.g., High Protein, Shellfish, Mexican food",
            )
            fp_type = st.selectbox(
                "Preference Type",
                ["staple", "like", "dislike", "avoid", "allergy"],
            )
            fp_goal = st.text_input(
                "Nutritional Goal (optional)",
                placeholder="e.g., Support muscle recovery",
            )
            fp_submit = st.form_submit_button("Add Preference")

            if fp_submit and fp_item.strip():
                add_food_preference(
                    profile["user_name"], fp_item.strip(), fp_type, fp_goal
                )
                st.success(f"Added **{fp_item.strip()}**!")
                st.rerun()

    # ── Edit Profile Tab ──────────────────────────────────────────────
    with tab_profile:
        st.markdown("### ⚙️ Edit Profile")

        with st.form("edit_profile_form"):
            edit_name = st.text_input(
                "Profile Name",
                value=profile.get("user_name", user),
            )
            edit_age = st.number_input(
                "Age", min_value=10, max_value=120, value=profile.get("age", 30)
            )
            ecol1, ecol2 = st.columns(2)
            with ecol1:
                edit_feet = st.number_input(
                    "Height (feet)",
                    min_value=3,
                    max_value=8,
                    value=profile["height_in"] // 12,
                )
            with ecol2:
                edit_inches = st.number_input(
                    "Height (inches)",
                    min_value=0,
                    max_value=11,
                    value=profile["height_in"] % 12,
                )
            edit_weight = st.number_input(
                "Weight (lbs)",
                min_value=50,
                max_value=600,
                value=profile.get("weight_lbs", 150),
            )
            edit_medical = st.text_area(
                "Goals & Medical Notes / Limitations",
                value=profile.get("medical_notes", ""),
            )
            edit_submit = st.form_submit_button("💾 Update Profile")

            if edit_submit:
                new_height = (edit_feet * 12) + edit_inches
                final_name = edit_name.strip() if edit_name.strip() else profile["user_name"]

                upsert_physical_profile(
                    user_name=profile["user_name"],
                    age=edit_age,
                    height_in=new_height,
                    weight_lbs=edit_weight,
                    medical_notes=edit_medical,
                )

                # If name changed, rename the user in the database
                if final_name != profile["user_name"]:
                    rename_user(profile["user_name"], final_name)
                    st.success(f"Profile updated! Name changed to **{final_name}**.")
                else:
                    st.success("Profile updated!")
                st.rerun()

# ─── User exists but not configured (edge case) ──────────────────────
else:
    st.markdown(
        "<p class='app-title'>💪 FitFlow</p>"
        "<p class='app-tagline'>Your personalized workout & dinner recommendations — powered by AI</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.warning(
        f"**{user}** has a profile but it's incomplete. "
        "Please fill in the details below."
    )
    with st.form("fix_profile_form"):
        fix_name = st.text_input("Your Name", value=user if not is_placeholder else "")
        col1, col2, col3 = st.columns(3)
        with col1:
            fix_age = st.number_input("Age", min_value=10, max_value=120, value=30)
        with col2:
            fix_feet = st.number_input("Height (feet)", min_value=3, max_value=8, value=5)
        with col3:
            fix_inches = st.number_input("Height (inches)", min_value=0, max_value=11, value=6)
        fix_weight = st.number_input("Weight (lbs)", min_value=50, max_value=600, value=150)
        fix_medical = st.text_area(
            "Goals & Medical Notes / Limitations",
            placeholder="e.g., Muscle gain, no limitations",
        )
        fix_submit = st.form_submit_button("🚀 Save Profile")

        if fix_submit:
            final_name = fix_name.strip() if fix_name.strip() else user
            height_in = (fix_feet * 12) + fix_inches
            upsert_physical_profile(
                user_name=user,
                age=fix_age,
                height_in=height_in,
                weight_lbs=fix_weight,
                medical_notes=fix_medical,
            )
            if final_name != user:
                rename_user(user, final_name)
            st.success(f"Profile saved for **{final_name}**!")
            st.rerun()
