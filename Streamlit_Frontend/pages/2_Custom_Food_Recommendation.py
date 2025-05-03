
import streamlit as st
import pandas as pd
import warnings
import contextlib
from Generate_Recommendations import Generator
from ImageFinder.ImageFinder import get_images_links as find_image
from streamlit_echarts import st_echarts

# ======================= WARNINGS AND EXCEPTION HANDLING =======================
warnings.filterwarnings("ignore")

@contextlib.contextmanager
def suppress_all_exceptions():
    try:
        yield
    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")  # Optional: Log error details if needed

# ======================= SESSION GUARD =======================
if "user_email" not in st.session_state:
    st.warning("🔐 Please log in to access this page.")
    st.stop()

# ======================= PAGE CONFIG =======================
st.set_page_config(page_title="Custom Food Recommendation", page_icon="🍽️", layout="wide")

# ======================= SIDEBAR =======================
st.sidebar.image(st.session_state.get("user_picture", ""), width=80)
st.sidebar.write(f"**{st.session_state.get('user_name', '')}**")
st.sidebar.write(f"`{st.session_state.get('user_email', '')}`")
st.sidebar.markdown("---")
# Logout button
if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# ======================= NUTRITIONAL FIELDS =======================
nutrition_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent',
                    'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']

# ======================= STATE INITIALIZATION =======================
if 'generated' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations = None

# ======================= RECOMMENDATION CLASS =======================
class Recommendation:
    def __init__(self, nutrition_list, nb_recommendations, ingredient_txt):
        self.nutrition_list = nutrition_list
        self.nb_recommendations = nb_recommendations
        self.ingredient_txt = ingredient_txt

    def generate(self):
        params = {'n_neighbors': self.nb_recommendations, 'return_distance': False}
        ingredients = self.ingredient_txt.split(';')
        generator = Generator(self.nutrition_list, ingredients, params)
        recommendations = generator.generate()
        recommendations = recommendations.json().get('output', [])
        for recipe in recommendations:
            with suppress_all_exceptions():
                recipe['image_link'] = find_image(recipe['Name'])
        return recommendations

# ======================= DISPLAY CLASS =======================
class Display:
    def __init__(self):
        self.nutrition_values = nutrition_values

    def display_recommendation(self, recommendations):
        st.subheader('🍽️ Recommended Recipes')
        if recommendations:
            columns = st.columns(5)
            chunks = [recommendations[i::5] for i in range(5)]
            for col, chunk in zip(columns, chunks):
                with col:
                    for recipe in chunk:
                        expander = st.expander(recipe['Name'])
                        with suppress_all_exceptions():
                            expander.markdown(
                                f'<center><img src="{recipe.get("image_link", "")}" width="200"></center>',
                                unsafe_allow_html=True
                            )
                            expander.markdown("#### Nutritional Values (g):")
                            df = pd.DataFrame({v: [recipe[v]] for v in self.nutrition_values})
                            expander.dataframe(df)

                            expander.markdown("#### Ingredients:")
                            for ing in recipe.get('RecipeIngredientParts', []):
                                expander.markdown(f"- {ing}")

                            expander.markdown("#### Instructions:")
                            for step in recipe.get('RecipeInstructions', []):
                                expander.markdown(f"- {step}")

                            expander.markdown("#### Times:")
                            expander.markdown(f"""
                                - Cook Time: {recipe.get('CookTime', 'N/A')} min  
                                - Prep Time: {recipe.get('PrepTime', 'N/A')} min  
                                - Total Time: {recipe.get('TotalTime', 'N/A')} min
                            """)
        else:
            st.info('No recipes found for the provided ingredients.', icon="❌")

    def display_overview(self, recommendations):
        if recommendations:
            st.subheader("📊 Nutritional Overview")
            selected_recipe_name = st.selectbox("Select a recipe to view overview:", [r['Name'] for r in recommendations])
            recipe = next((r for r in recommendations if r['Name'] == selected_recipe_name), None)
            if recipe:
                options = {
                    "title": {"text": "Nutrition Overview", "subtext": recipe['Name'], "left": "center"},
                    "tooltip": {"trigger": "item"},
                    "legend": {"orient": "vertical", "left": "left"},
                    "series": [{
                        "name": "Nutritional Value",
                        "type": "pie",
                        "radius": "50%",
                        "data": [{"value": recipe[n], "name": n} for n in self.nutrition_values],
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.5)",
                            }
                        },
                    }],
                }
                with suppress_all_exceptions():
                    st_echarts(options=options, height="600px")

# ======================= UI - HEADER =======================
st.markdown("<h1 style='text-align: center;'>🍲 Custom Food Recommendation</h1>", unsafe_allow_html=True)

# ======================= UI - FORM =======================
with st.form("input_form"):
    st.header("Select Your Desired Nutrition Range:")
    nutrition_input = [
        st.slider(label, 0, max_val, default)
        for label, max_val, default in zip(nutrition_values,
                                           [2000, 100, 13, 300, 2300, 325, 50, 40, 40],
                                           [500, 50, 0, 0, 400, 100, 10, 10, 10])
    ]

    st.header("Recommendation Options (Optional):")
    nb_recommendations = st.slider("Number of Recommendations", 5, 20, 10, step=5)
    ingredient_txt = st.text_input("Ingredients (separated by `;`):", placeholder="e.g., Milk;Eggs;Chicken")

    submit = st.form_submit_button("Generate")

# ======================= PROCESSING =======================
if submit:
    with st.spinner("🔄 Generating your personalized recommendations..."):
        with suppress_all_exceptions():
            rec = Recommendation(nutrition_input, nb_recommendations, ingredient_txt)
            st.session_state.recommendations = rec.generate()
            st.session_state.generated = True

# ======================= OUTPUT DISPLAY =======================
if st.session_state.generated:
    display = Display()
    with suppress_all_exceptions():
        display.display_recommendation(st.session_state.recommendations)
    with suppress_all_exceptions():
        display.display_overview(st.session_state.recommendations)