import os
import pandas as pd
import streamlit as st
import plotly.express as px
from textblob import TextBlob

# Load the dataset
file_path = r'C:\Users\User\Downloads\New folder (4)\McDonald_s_Reviews.csv'
if os.path.exists(file_path):
    mcdonalds_data = pd.read_csv(file_path, encoding='ISO-8859-1')
else:
    st.error("Dataset not found. Please make sure the file 'McDonald_s_Reviews.csv' is in the specified directory.")
    st.stop()

# Sentiment Analysis
mcdonalds_data['sentiment'] = mcdonalds_data['review'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

# Convert 'latitude', 'longitude'to numeric, replacing non-numeric values with NaN
mcdonalds_data['latitude'] = pd.to_numeric(mcdonalds_data['latitude'], errors='coerce')
mcdonalds_data['longitude'] = pd.to_numeric(mcdonalds_data['longitude'], errors='coerce')




# Streamlit app
def main():
    st.title("McDonald's Reviews Dashboard")

    st.header("Select a Store")

    # Dropdown for selecting store addresses
    all_option = 'Select All'
    selected_store_address = st.sidebar.selectbox('Select a Store Address:', [all_option] + mcdonalds_data['store_address'].unique().tolist())

    if selected_store_address == all_option:
        map_data = mcdonalds_data  # Select all stores
    else:
        map_data = mcdonalds_data[mcdonalds_data['store_address'] == selected_store_address]


    # Map showing store locations
    st.subheader(f"{selected_store_address} - Ratings Map")
    map_data = mcdonalds_data[mcdonalds_data['store_address'] == selected_store_address]

    if not map_data[['latitude', 'longitude']].empty and map_data['latitude'].notna().all() and map_data['longitude'].notna().all():
        fig = px.scatter_mapbox(map_data,
                                lat='latitude',
                                lon='longitude',
                                color='rating',
                                size_max=10,  # Set a constant max size value (adjust as needed)
                                hover_name='store_name',
                                mapbox_style='carto-positron',
                                zoom=10)
        st.plotly_chart(fig)
    else:
        st.warning("No valid geospatial data available for the selected store.")

    
    # Clean the 'rating' column by extracting the numerical part
    map_data['numeric_rating'] = map_data['rating'].str.extract(r'(\d+)')

    # Display the unique values in the 'numeric_rating' column
    unique_ratings = map_data['numeric_rating'].unique()
    st.write("Unique values in 'numeric_rating' column:", unique_ratings)

    # Rating Distribution
    st.subheader(f"{selected_store_address} - Rating Distribution")

    # Remove NaN values before counting
    filtered_data = map_data.dropna(subset=['numeric_rating'])

    # Count the occurrences of each rating
    rating_counts = filtered_data['numeric_rating'].value_counts().sort_index()

    # Check if rating_counts is not empty
    if not rating_counts.empty:
        # Create a pie chart for the rating distribution
        fig = px.pie(rating_counts, names=rating_counts.index, values=rating_counts.values, title='Rating Distribution')
        st.plotly_chart(fig)
    else:
        st.warning("No data available for the Rating Distribution.")




    # Positive and Negative Graphs based on Sentiment
    st.subheader(f"{selected_store_address} - Positive and Negative Sentiments")
    positive_reviews = map_data[map_data['sentiment'] > 0]
    negative_reviews = map_data[map_data['sentiment'] < 0]

    # Positive Sentiment Graph
    positive_figure = px.histogram(positive_reviews, x='sentiment', nbins=50, title='Positive Sentiments Distribution')
    st.plotly_chart(positive_figure)

    # Negative Sentiment Graph
    negative_figure = px.histogram(negative_reviews, x='sentiment', nbins=50, title='Negative Sentiments Distribution')
    st.plotly_chart(negative_figure)

if __name__ == '__main__':
    main()
