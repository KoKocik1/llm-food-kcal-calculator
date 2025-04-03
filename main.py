import streamlit as st
from datetime import datetime
from db.meal_service import get_meals_by_day, delete_meal
from backend.core import run_llm
from backend.utils import get_formatted_response
from db.settings_service import get_user_settings, update_user_settings
import time


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "chat_answers_history" not in st.session_state:
        st.session_state.chat_answers_history = []
    if "user_prompt_history" not in st.session_state:
        st.session_state.user_prompt_history = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "sources_history" not in st.session_state:
        st.session_state.sources_history = []
    if "user_settings" not in st.session_state:
        st.session_state.user_settings = get_user_settings()


def main():
    initialize_session_state()

    with st.sidebar:
        st.title("Todays Meals")
        today = datetime.now().strftime("%Y-%m-%d")
        todays_meals = get_meals_by_day(today)

        if todays_meals:
            for meal in todays_meals:
                st.write(f"**{meal.name}** ({meal.calories} kcal)")
                st.write(f"_{meal.category}_")
                st.write(meal.description)
                st.write("---")
        else:
            st.write("No meals recorded today")

        total_calories = sum(meal.calories for meal in todays_meals)
        st.markdown("---")
        st.markdown(f"**Total calories today:** {total_calories} kcal")

        st.markdown("---")

        st.markdown("### App Information")
        st.markdown("**Version:** 1.0.0")
        st.markdown("**Last Updated:** 31.03.2025")

    st.header("Food Kcal Calculator")

    # Tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Chat", "View Meals", "Statistics", "Settings"])

    with tab1:
        st.subheader("Ask about nutrition")
        prompt = st.text_input(
            "Prompt", placeholder="What did you just eat?", key="prompt_input"
        )

        if prompt:
            if not prompt.strip():
                st.write("Please enter a prompt")
                return

            with st.spinner("Processing your request..."):
                generated_response = run_llm(
                    query=prompt, chat_history=st.session_state.chat_history
                )

                formatted_response, sources = get_formatted_response(
                    generated_response)

                # Update session state
                st.session_state.user_prompt_history.append(prompt)
                st.session_state.chat_answers_history.append(
                    formatted_response)
                st.session_state.sources_history.append(sources)
                st.session_state.chat_history.extend(
                    [("human", prompt), ("ai", generated_response["result"])]
                )

        # Display chat history
        if st.session_state.chat_answers_history:
            for response, user_query, sources in zip(
                st.session_state.chat_answers_history,
                st.session_state.user_prompt_history,
                st.session_state.sources_history,
            ):
                st.chat_message("user").write(user_query)
                with st.chat_message("assistant"):
                    st.markdown(response)
                    cols = st.columns(len(sources))
                    for i, (col, source) in enumerate(zip(cols, sources)):
                        with col:
                            st.link_button(
                                f"Source {i + 1}", source, use_container_width=True
                            )
    with tab2:
        st.subheader("View and Manage Meals")
        view_date = st.date_input("Select Date", key="view_date")
        view_date = view_date.strftime("%Y-%m-%d")
        meals = get_meals_by_day(view_date)

        if meals:
            for meal in meals:
                with st.expander(f"{meal.name} - {meal.date.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2, col3 = st.columns([6, 1, 1])
                    with col1:
                        st.write(f"Category: {meal.category}")
                        st.write(f"Calories: {meal.calories}")
                        st.write(f"Description: {meal.description}")
                    with col2:
                        if st.button("Edit", key=f"edit_{meal._id}"):
                            st.session_state.editing_meal = meal._id
                    with col3:
                        if st.button("Delete", key=f"delete_{meal._id}"):
                            result = delete_meal(str(meal._id))
                            if result:
                                st.success(
                                    f"Successfully deleted {meal.name}")
                                st.rerun()
                            else:
                                st.error(
                                    f"Failed to delete meal: {meal.name}")

    with tab3:
        st.subheader("Statistics")
        st.write("Statistics will be added soon")
    with tab4:
        st.subheader("Settings")

        # Settings form
        with st.form("settings_form"):
            st.write("Personal Information")
            col1, col2 = st.columns(2)

            with col1:
                sex = st.selectbox(
                    "Sex",
                    options=["Male", "Female"],
                    key="settings_sex",
                    index=0 if st.session_state.user_settings["sex"] == "Male" else 1
                )
                age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=120,
                    value=st.session_state.user_settings["age"],
                    key="settings_age"
                )

            with col2:
                height = st.number_input(
                    "Height (cm)",
                    min_value=1,
                    max_value=300,
                    value=st.session_state.user_settings["height"],
                    key="settings_height"
                )
                weight = st.number_input(
                    "Weight (kg)",
                    min_value=1,
                    max_value=500,
                    value=st.session_state.user_settings["weight"],
                    key="settings_weight"
                )

            target_calories = st.number_input(
                "Daily Calorie Target",
                min_value=500,
                max_value=10000,
                value=st.session_state.user_settings["target_calories"],
                key="settings_calories",
                step=100
            )

            if st.form_submit_button("Save Settings"):
                new_settings = {
                    "sex": sex,
                    "age": age,
                    "height": height,
                    "weight": weight,
                    "target_calories": target_calories
                }
                result = update_user_settings(new_settings)
                if result:
                    st.session_state.user_settings = new_settings
                    st.success("Settings saved successfully!", icon="✅")
                else:
                    st.error("Failed to save settings", icon="❌")
                time.sleep(2)
                st.rerun()


if __name__ == "__main__":
    main()
