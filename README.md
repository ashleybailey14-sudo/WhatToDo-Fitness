# 🚀 Galactic Gains — Health & Workout App

A personalized workout and dinner recommendation app powered by **Gemini AI**, **Supabase**, and **Streamlit**.

![Galactic Gains](assets/background.png)

## Features

- **User Profiles** — Select from a dropdown; new users fill out their info on first visit
- **AI Workouts** — Gemini generates a unique 45-minute workout tailored to your goals, limitations, and available equipment
- **AI Dinner Ideas** — Get a flavorful dinner suggestion based on your food preferences and nutritional goals
- **Recipe on Demand** — Ask for the full recipe if the dinner sounds good
- **Equipment Inventory** — Track what gear you have so workouts match your setup
- **Food Preferences** — Record staples, allergies, dislikes, and nutritional goals
- **History Tracking** — Past recommendations are reviewed so you never get the same thing twice

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| AI | Google Gemini 2.0 Flash |
| Database | Supabase (PostgreSQL) |
| Hosting | Streamlit Community Cloud |

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/galactic-gains.git
cd galactic-gains
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure secrets

Copy the example and fill in your keys:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
GEMINI_API_KEY = "your-gemini-api-key"
```

### 4. Add your background image

Place your background image at `assets/background.png`.

### 5. Run locally

```bash
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and select `app.py`
4. Add your secrets in the Streamlit Cloud dashboard under **Settings → Secrets**

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
GEMINI_API_KEY = "your-gemini-api-key"
```

## Database Schema (Supabase)

### `physical_profile`
| Column | Type |
|--------|------|
| id | int (PK, serial) |
| updated_at | timestamptz |
| age | int |
| height_in | int |
| weight_lbs | int |
| medical_notes | text |
| user_name | text |

### `equipment_inventory`
| Column | Type |
|--------|------|
| id | int (PK, serial) |
| name | text |
| category | text |
| notes | text |
| user_name | text |

### `food_preferences`
| Column | Type |
|--------|------|
| id | int (PK, serial) |
| item_name | text |
| preference_type | text |
| nutritional_goal | text |
| user_name | text |

### `recommendation_history` (optional)
| Column | Type |
|--------|------|
| id | int (PK, serial) |
| created_at | timestamptz (default now()) |
| user_name | text |
| workout | text |
| dinner | text |

## License

MIT
