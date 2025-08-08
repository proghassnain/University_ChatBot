import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import praw
import os

# ======================
# Load environment variables
# ======================
load_dotenv()

# Google API Setup
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Reddit API Setup
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# ======================
# Function to get reviews from Reddit
# ======================
def fetch_university_reviews(university_name, limit=10):
    subreddit_list = ["pakistan", "college", "AskAcademia", university_name.replace(" ", "")]
    reviews = []

    for sub in subreddit_list:
        try:
            subreddit = reddit.subreddit(sub)
            for post in subreddit.search(university_name, sort="relevance", limit=limit):
                reviews.append(post.title + " " + (post.selftext or ""))
        except Exception:
            pass

    return reviews
# ======================
# Streamlit UI
# ======================
st.set_page_config(page_title="University Comparison Bot", page_icon="🎓")
st.title("🎓 University Comparison Bot (Pakistan)")
st.write("Compare Universities based on **live Reddit student reviews**!")

# Input for first university
selected_uni1 = st.text_input("Enter the first university name:")

# Compare mode
compare_mode = st.checkbox("Compare with another University")
selected_uni2 = None
if compare_mode:
    selected_uni2 = st.text_input("Enter the second university name:")

# When button is clicked
if st.button("Get Insights"):
    if not selected_uni1:
        st.warning("Please enter at least one university name.")
    else:
        with st.spinner("Fetching reviews from Reddit..."):
            if not compare_mode:
                uni1_reviews = fetch_university_reviews(selected_uni1)
                reviews_text = " ".join(uni1_reviews)
                prompt = f"""
                Based on the following Reddit student reviews of {selected_uni1}, 
                provide 3 pros and 3 cons in bullet points:
                {reviews_text}
                """
            else:
                uni1_reviews = fetch_university_reviews(selected_uni1)
                uni2_reviews = fetch_university_reviews(selected_uni2)
                reviews1_text = " ".join(uni1_reviews)
                reviews2_text = " ".join(uni2_reviews)

                prompt = f"""
                Compare these two universities based on Reddit student reviews.

                University 1: {selected_uni1}
                Reviews: {reviews1_text}

                University 2: {selected_uni2}
                Reviews: {reviews2_text}

                Provide a short summary of strengths and weaknesses of each, and 
                who each university is better suited for.
                """

        # Send to Gemini
        with st.spinner("Analyzing reviews..."):
            response = model.generate_content(prompt)
            st.subheader("🎯 Recommendation:")
            st.write(response.text)
