import streamlit as st
import google_auth_oauthlib.flow
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req
import logging
import sys

# --------------------
# Suppress Streamlit Error Traces
# --------------------
def suppress_tracebacks():
    logger = logging.getLogger("streamlit")
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(logging.CRITICAL)
    logger.handlers = [handler]
    logger.setLevel(logging.CRITICAL)

suppress_tracebacks()

# --------------------
# Load Credentials
# --------------------
def load_credentials():
    try:
        return (
            st.secrets["google"]["client_id"],
            st.secrets["google"]["client_secret"],
            st.secrets["google"]["redirect_uri"],
        )
    except KeyError:
        st.error("⚠️ Google OAuth credentials missing in `secrets.toml`.")
        st.stop()

CLIENT_ID, CLIENT_SECRET, REDIRECT_URI = load_credentials()

# --------------------
# Handle Login
# --------------------
def handle_login():
    query_params = st.experimental_get_query_params()
    if "code" in query_params and "user_email" not in st.session_state:
        auth_code = query_params["code"][0]

        try:
            token_response = req.post("https://oauth2.googleapis.com/token", data={
                "code": auth_code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code"
            })

            if token_response.status_code == 200:
                token_info = token_response.json()
                user_info = id_token.verify_oauth2_token(
                    token_info["id_token"],
                    requests.Request(),
                    CLIENT_ID
                )

                st.session_state["user_email"] = user_info["email"]
                st.session_state["user_name"] = user_info.get("name", "User")
                st.session_state["user_picture"] = user_info.get("picture", "")

                # Clear query parameters after successful login
                st.experimental_set_query_params()

        except Exception:
            st.error("⚠️ Login failed or token verification issue occurred.")

# --------------------
# Login UI
# --------------------
def render_login_ui():
    st.title("🍽️ Welcome to Food Recommendation System")
    st.markdown("#### Your smart companion for healthier food choices")

    auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline&prompt=select_account"
    )

    st.markdown(f"""
    <div style="text-align: center; margin-top: 50px;">
        <a href="{auth_url}">
            <button style="padding: 0.7rem 2rem; border-radius: 8px; font-size: 1rem; border: none;">
                🔒 Login with Google
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

# --------------------
# Post-Login UI
# --------------------
def render_logged_in_ui():
    st.sidebar.write(f"**{st.session_state.get('user_name', '')}**")
    st.sidebar.write(f"`{st.session_state.get('user_email', '')}`")
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_set_query_params()
        st.experimental_rerun()


    st.markdown("""
# 🍽️ Welcome to Food Recommendation System!

Your health, your body, your goals — all powered by advanced Artificial Intelligence.  
Our system is more than a meal planner — it’s a **smart nutrition coach**, **a virtual dietician**, and **a personal health advisor**, all working together to guide you toward better living.

---

## 🔍 What Is This System?

This intelligent dietary platform analyzes your:
- **Body parameters** (like BMI, BMR, weight, height, and age)
- **Personal health goals** (weight loss, muscle gain, maintenance)
- **Dietary restrictions** (vegan, diabetic-friendly, hypertensive-safe)
- **Food preferences and dislikes**
- **Daily caloric and macronutrient needs**

Based on these factors, it generates **daily personalized food recommendations** that evolve with your progress.

---

## 🧠 How It Works: AI That Learns With You

- ✅ **Behavioral Analysis**: Learns from your food logging and adapts recommendations based on your eating history.
- 🔄 **Real-Time Customization**: Adapts instantly when you change your diet, fitness routine, or goals.
- 📊 **Data-Driven Insights**: Provides nutritional breakdowns, calorie tracking, and meal compositions — all backed by scientific data.
- 🧬 **Predictive Intelligence**: Suggests foods that match your current lifestyle while forecasting future needs (e.g., seasonal changes, activity level spikes).

---

## 🍛 Personalized Meal Plans Made Simple

- 🎯 **Goal-Based Recommendations**: Whether you're aiming to burn fat, build muscle, or manage a health condition, this system tailors your food like a precision tool.
- 🥗 **Macro-Optimized Meals**: Balances protein, carbohydrates, and fats to align with your exact nutritional profile.
- 🌍 **Cultural & Local Adaptability**: Includes food suggestions based on your regional cuisine and available ingredients.

---

## 🩺 Smart Enough to Care for Your Health

- 💉 Diabetic? Low glycemic meals to manage blood sugar.
- ❤️ Heart conditions? Sodium-controlled, heart-healthy recipes.
- 🧂 Hypertension? Low-salt, nutrient-dense foods.
- 🌱 Vegan, Vegetarian, Keto? Customized to your dietary type.

Your health condition is **not a limitation**, but a parameter our AI takes seriously.

---

## 🌐 Seamless Experience, Anytime. Anywhere.

- 📱 **Accessible 24/7** via desktop, tablet, or mobile.
- 🧭 **Instant Recommendations** for breakfast, lunch, snacks, or dinner.
- 📝 **Track what you eat**, get feedback, and keep progressing daily.
- ☁️ **Cloud-backed user sessions** so your profile stays updated across devices.

---

## 🚀 Why Choose the AI Food Recommendation System?

| Feature | Benefit |
|--------|---------|
| 🤖 AI-Driven Engine | Intelligent decisions based on your history, needs, and progress |
| 🧬 Personalized Diet Plans | No generic diets — everything is custom to YOU |
| 📈 Progress-Oriented | Get daily and weekly reports, improvements, and tips |
| 🏥 Medical-Condition Awareness | Food that’s not just good — but right for your condition |
| 🧑‍🍳 Built-in Meal Ideas | Never wonder “what to eat” again — we’ll tell you, based on science |
| 🌍 Global Cuisine Support | Indian thalis? Mediterranean bowls? All supported! |
| 🗣️ Multilingual Support *(coming soon)* | Speak your food language — literally |

---

## ✨ Let AI Be Your Nutrition Partner

Achieving your fitness and health goals should be **simple**, **science-based**, and **sustainable**.  
This system transforms your dietary journey into a personalized experience powered by the latest in health tech.

---

""")

# --------------------
# Main
# --------------------
def main():
    st.set_page_config(page_title="NutriAI", layout="wide", initial_sidebar_state="expanded")
    handle_login()

    if "user_email" in st.session_state:
        render_logged_in_ui()
    else:
        render_login_ui()

if __name__ == "__main__":
    main()
