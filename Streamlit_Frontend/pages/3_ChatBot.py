import streamlit as st
import openai
import os

# ----------------- Page Config -----------------
st.set_page_config(page_title="🩺 Health Advice Chatbot", layout="centered")

# ----------------- Sidebar -----------------

if "user_email" not in st.session_state:
    st.sidebar.warning("🔐 Please log in to access this page.")
    st.stop()

# Display user email

# Optional profile image (fallback to placeholder)
st.sidebar.image(st.session_state.get("user_picture", ""), width=80)
st.sidebar.write(f"**{st.session_state.get('user_name', '')}**")
st.sidebar.write(f"`{st.session_state.get('user_email', '')}`")
st.sidebar.markdown("---")
# Logout button
if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()



# ----------------- Main Interface -----------------
st.title("🩺 Health Advice Chatbot")
st.markdown("### 🤖 Your AI Health Consultant")
st.info("Get preliminary health advice based on your queries. **Note:** This is not a substitute for professional medical advice.")

# ----------------- API Key -----------------
api_key = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ **API Key is missing! Please set OPENAI_API_KEY in Streamlit Secrets or Environment Variables.**")
    st.stop()

# ----------------- Query Form -----------------
query_type = st.selectbox("📌 **Select Query Type**", 
                          ["Symptom Checker", "Preventive Measures", "General Health Advice", "Medical Terms", "First Aid"])

user_input = st.text_area("✍️ **Enter your query here:**", max_chars=300, help="Keep your query brief (max 300 characters).")

max_tokens = st.slider("🔢 **Max Response Length (Tokens)**", min_value=50, max_value=300, value=150)

if st.button("🚀 **Get Advice**"):
    if not user_input:
        st.warning("⚠️ **Please enter a query before submitting.**")
    else:
        query_mapping = {
            "Symptom Checker": f"User has described the following symptoms: {user_input}. What could be the potential conditions?",
            "Preventive Measures": f"Provide preventive measures for: {user_input}.",
            "General Health Advice": f"Give general health advice on the topic: {user_input}.",
            "Medical Terms": f"Explain the following medical term: {user_input}.",
            "First Aid": f"Provide first aid tips for: {user_input}."
        }
        user_message = query_mapping[query_type]

        # Initialize OpenAI API
        client = openai.OpenAI(api_key=api_key)
        with st.spinner("⏳ **Fetching response...**"):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": (
                            "You are a highly knowledgeable, empathetic, and professional health assistant specializing in delivering accurate, evidence-based, and easily understandable guidance. "
                            "Your core responsibilities are to assist users with health-related topics, specifically focusing on symptoms assessment, preventive care advice, nutrition and diet optimization, fitness and exercise recommendations, mental health support strategies, and first aid instructions. "
                            "Maintain a tone that is friendly, supportive, clear, and strictly professional. Always provide answers that are factually correct, concise, and directly relevant to the user’s inquiry, without offering personal opinions or speculative advice. "
                            "It is mandatory to conclude every response with a clear disclaimer stating: "
                            "'Disclaimer: This information is for educational purposes only and does not substitute professional medical advice, diagnosis, or treatment. "
                            "Please consult a qualified healthcare provider for personalized medical guidance.' "
                            "Do not deviate into unrelated topics. Do not provide diagnosis, prescriptions, or emergency interventions. Prioritize user safety, accuracy, and clarity in every response."
                        )},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=max_tokens
                )

                # 🚨 Correct way to extract the result (new SDK uses dot notation, not dictionary lookup)
                advice = response.choices[0].message.content.strip()
                st.success("✅ **Response Received**")
                st.markdown(f'<div class="response-box">{advice}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ **Unexpected Error:** {e}")