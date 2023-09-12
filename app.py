import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from collections import Counter
from pyresparser import ResumeParser
import base64

# Set page configuration and title
st.set_page_config(page_title="ResuMate - Aryans", page_icon=":bar_chart:", layout="wide")

# Title and styling
st.title("ResuMate Miner")
st.markdown('<style>div.block-container{padding-top: 1rem;}</style>', unsafe_allow_html=True)

# Sidebar for navigation
sidebar_options = ['Resume Parser', 'Analytics', 'Ranking']
selected_option = st.sidebar.radio("Select a Page", sidebar_options)

# ----------------------------- #
# Resume Parser

if selected_option == 'Resume Parser':
    st.subheader("Resume Parser")

    # Load JSON data from files
    with open("data1.json", "r") as json_file1:
        data1 = json.load(json_file1)


    # Divide the screen into two columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload Your Resume")
        uploaded_file = st.file_uploader("Drag and drop a file here", type=["pdf", "docx"])

        if uploaded_file:
            st.write("Uploaded file:", uploaded_file.name)

            base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
            pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000px" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

            data1 = ResumeParser(uploaded_file).get_extracted_data()
            print(data1)

    with col2:
        st.subheader("Resume")
        # Prepare data for the table
        for key, value in data1.items():
            if isinstance(value, list):
                st.subheader(f"**{key.capitalize()}**")
                for item in value:
                    st.table([(item,)])
            else:
                st.write(f"**{key.capitalize()}:**", value)

# ----------------------------- #
# Analytics

elif selected_option == 'Analytics':
    st.subheader("Analytics Page")

    # Sidebar for analytics options
    analytics_options = ['CPI Comparison', 'Top Mentioned Skills', 'Most Projects or Experience']
    selected_analytics_option = st.sidebar.radio("Select a Chart", analytics_options)

    # Load JSON data and create DataFrame for analytics
    with open('applicants_data.json') as json_file:
        data = json.load(json_file)
    applicants_df = pd.DataFrame(data['applicants'])

    if selected_analytics_option == 'CPI Comparison':
        st.header("Applicants' CPI Comparison")
        st.write("Comparison of Cumulative Performance Index (CPI) among applicants")

        # Filter by CPI range
        min_cpi, max_cpi = st.slider("CPI Range", min_value=min(applicants_df['cpi']), max_value=max(applicants_df['cpi']),
                                     value=(min(applicants_df['cpi']), max(applicants_df['cpi'])))
        filtered_applicants_df = applicants_df[(applicants_df['cpi'] >= min_cpi) & (applicants_df['cpi'] <= max_cpi)]

        # Calculate median and average CPI
        median_cpi = np.median(filtered_applicants_df['cpi'])
        average_cpi = np.mean(filtered_applicants_df['cpi'])

        # Create a bar chart to compare CPIs
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(filtered_applicants_df['name'], filtered_applicants_df['cpi'], color='skyblue', label='CPI')
        ax.set_xlabel('CPI (Cumulative Performance Index)')
        ax.set_title('CPI Comparison')

        # Display the exact CPI value on hovering over the chart
        for bar in bars:
            yval = bar.get_y() + bar.get_height() / 2
            ax.text(bar.get_width(), yval, f'{bar.get_width():.2f}', va='center')

        # Display median and average CPI lines
        ax.axvline(median_cpi, color='red', linestyle='dashed', linewidth=1, label=f'Median CPI: {median_cpi:.2f}')
        ax.axvline(average_cpi, color='green', linestyle='dashed', linewidth=1, label=f'Average CPI: {average_cpi:.2f}')
        ax.legend()

        # Display the bar chart using matplotlib
        st.pyplot(fig)

    elif selected_analytics_option == 'Top Mentioned Skills':
        st.header("Top Mentioned Skills")
        st.write("Chart showing the frequency of top mentioned skills among applicants")

        # Search bar for skills
        st.markdown('<style>div.css-1v4eu6x{font-weight:bold;}div.st-dd{width:50%;}</style>', unsafe_allow_html=True)
        skill_search = st.text_input("Search for a skill:", value="", key="skill_search")
        st.markdown('<div style="font-style: italic; color: gray; margin-top: 0.2rem;">Press Enter to Apply</div>', unsafe_allow_html=True)

        if skill_search:
            matching_people = applicants_df[applicants_df['skills'].apply(lambda skills: skill_search.lower() in [skill.lower() for skill in skills])]
            if not matching_people.empty:
                st.subheader("People with Matching Skill:")
                st.dataframe(matching_people[['name', 'skills']])
            else:
                st.subheader("No matching skills found.")

        # Combine all skills into a single list
        all_skills = []
        for skills_list in applicants_df['skills']:
            all_skills.extend(skills_list)

        # Count the frequency of each skill
        skills_counter = Counter(all_skills)

        # Get the top mentioned skills and their frequencies
        top_skills = skills_counter.most_common(10)  # Change the number as needed

        # Extract skill names and frequencies
        skill_names = [skill[0] for skill in top_skills]
        skill_frequencies = [skill[1] for skill in top_skills]

        # Create a smaller bar chart to show skill frequencies
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(skill_names, skill_frequencies, color='lightblue')
        ax.set_xlabel('Skills')
        ax.set_ylabel('Frequency')
        ax.set_title('Top Mentioned Skills')

        # Rotate x-axis labels, adjust spacing, and set font size
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.tight_layout()

        # Display the smaller bar chart using matplotlib
        st.pyplot(fig)

    elif selected_analytics_option == 'Most Projects or Experience':
        st.header("Most Projects or Experience")
        st.write("Applicants with the most number of projects or experience")

        # Search bar for projects and experience keywords
        keyword_search = st.text_input("Search for keywords in projects or experience:")

        # Filter applicants based on keyword search
        if keyword_search:
            matching_applicants = applicants_df[applicants_df['experience'].apply(lambda exp: any(keyword_search.lower() in project.lower() for project in exp))]

            if not matching_applicants.empty:
                st.subheader("Applicants with Matching Keywords in Projects or Experience:")
                st.dataframe(matching_applicants[['name', 'experience']])
            else:
                st.subheader("No matching applicants found.")

        # If no keyword is provided, show the default graph
        else:
            # Count the number of projects or experiences
            applicants_df['experience'] = applicants_df['experience'].apply(lambda x: len(x))
            applicants_df = applicants_df.sort_values(by='experience', ascending=False)

            # Create a smaller bar chart to show most projects or experience
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(applicants_df['name'], applicants_df['experience'], color='salmon')
            ax.set_xlabel('Number of Projects or Experience')
            ax.set_title('Most Projects or Experience')

            # Display the smaller bar chart using matplotlib
            st.pyplot(fig)

# ----------------------------- #
# Ranking of Applicants
else:
    # Load JSON data and create DataFrame for ranking
    with open('applicants_data.json') as json_file:
        data = json.load(json_file)
    applicants_df = pd.DataFrame(data['applicants'])

    # Calculate the ranking score based on criteria
    applicants_df['score'] = (applicants_df['cpi'] * 0.5) + (applicants_df['experience'].apply(len) * 0.1) + \
                             (applicants_df['skills'].apply(len) * 0.2)

    # Add points if designation matches a skill or experience
    for index, row in applicants_df.iterrows():
        if row['designation'] in row['skills']:
            applicants_df.at[index, 'score'] += 0.3
        if row['designation'] in row['experience']:
            applicants_df.at[index, 'score'] += 0.3

    st.subheader("Ranking Page")
    st.write("Ranking applicants based on the provided criteria")

    # Sort applicants by score in descending order
    ranked_applicants_df = applicants_df.sort_values(by='score', ascending=False)

    # Display the ranked applicants
    st.dataframe(ranked_applicants_df[['name', 'score', 'cpi', 'experience', 'skills', 'designation']])

    # Additional ranking visualization: Bar chart of top ranked applicants
    top_ranked_applicants = ranked_applicants_df.head(10)  # Change the number as needed
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(top_ranked_applicants['name'], top_ranked_applicants['score'], color='green')
    ax.set_xlabel('Applicant Name')
    ax.set_ylabel('Ranking Score')
    ax.set_title('Top Ranked Applicants')

    # Rotate x-axis labels, adjust spacing, and set font size
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    # Display the bar chart using matplotlib
    st.pyplot(fig)
