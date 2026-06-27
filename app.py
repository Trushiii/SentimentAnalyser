import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sentiment_analyzer import SentimentAnalyzer
from social_scraper import SocialMediaScraper
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Social Media Sentiment Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1F77B4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = SentimentAnalyzer()
if 'scraper' not in st.session_state:
    st.session_state.scraper = SocialMediaScraper()
if 'results' not in st.session_state:
    st.session_state.results = None

# Header
st.markdown('<h1 class="main-header">📊 Social Media Sentiment Analyzer</h1>', unsafe_allow_html=True)
st.markdown("### Analyze public opinion about products and brands from Reddit")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    analysis_mode = st.radio(
        "Choose Analysis Mode:",
        ["🔍 Search Reddit", "📝 Manual Input", "📁 Upload File"]
    )
    
    st.markdown("---")
    st.info("💡 Tip: Search for product names, brands, or topics to analyze public sentiment!")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This tool uses AI to analyze sentiment from social media posts.")
    st.markdown("Built with: Python, Streamlit, TextBlob, Reddit API")

# Main Content
if analysis_mode == "🔍 Search Reddit":
    st.header("🔍 Search & Analyze Reddit Posts")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Enter product name or topic to search:",
            placeholder="e.g., iPhone 15, Tesla Model 3, PlayStation 5"
        )
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("🔍 Search & Analyze", type="primary", use_container_width=True)
    
    # Settings
    col3, col4, col5 = st.columns(3)
    with col3:
        max_posts = st.slider("Maximum posts to fetch", 10, 200, 50)
    with col4:
        subreddit = st.text_input("Subreddit (optional)", value="all", placeholder="all")
    with col5:
        st.write("")
        st.info(f"Will fetch up to {max_posts} posts")
    
    if search_button and search_query:
        with st.spinner(f'🔄 Searching Reddit for "{search_query}"...'):
            # Collect posts from Reddit
            posts = st.session_state.scraper.search_reddit(search_query, subreddit, max_posts)
            
            if posts:
                st.success(f"✅ Found {len(posts)} Reddit posts! Analyzing sentiment...")
                
                # Analyze sentiment
                with st.spinner('🤖 AI is analyzing sentiment...'):
                    st.session_state.results = st.session_state.analyzer.analyze_multiple(posts)
                st.rerun()
            else:
                st.error("❌ No Reddit posts found. Please check your API keys in config.py or try a different search term.")
                st.info("Troubleshooting:\n- Verify Reddit API keys are correct\n- Make sure your Reddit account credentials are valid\n- Try a more popular search term or different subreddit")

elif analysis_mode == "📝 Manual Input":
    st.header("📝 Manual Text Input")
    
    st.write("Paste reviews or comments below (one per line):")
    
    manual_text = st.text_area(
        "Enter text to analyze:",
        height=200,
        placeholder="Example:\nThis product is amazing!\nTerrible customer service\nDelivered on time\nLove the quality!\nWay too expensive"
        )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        analyze_button = st.button("🤖 Analyze Text", type="primary", use_container_width=True)
    
    with col2:
        if st.button("📋 Load Sample Data", use_container_width=True):
            sample_text = """This product exceeded my expectations!
Worst purchase I've ever made
Arrived on time, good packaging
Amazing quality for the price
Customer support was unhelpful
Great design and features
Too expensive for what you get
Fast shipping, very satisfied
Product stopped working after one week
Highly recommend to everyone"""
            manual_text = sample_text
            st.rerun()
    
    if analyze_button:
        if manual_text.strip():
            texts = [line.strip() for line in manual_text.split('\n') if line.strip()]
            with st.spinner('🤖 Analyzing sentiment...'):
                st.session_state.results = st.session_state.analyzer.analyze_multiple(texts)
                st.rerun()
        else:
            st.warning("⚠️ Please enter some text to analyze")

else:  # Upload File
    st.header("📁 Upload File")
    
    st.write("Upload a text file (.txt) or CSV file (.csv) with reviews:")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'csv']
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.txt'):
                content = uploaded_file.read().decode('utf-8')
                texts = [line.strip() for line in content.split('\n') if line.strip()]
                
                st.success(f"✅ Loaded {len(texts)} lines from file")
                st.write("Preview:")
                st.text("\n".join(texts[:5]))
                if len(texts) > 5:
                    st.write(f"... and {len(texts) - 5} more")
                
            else:  # CSV
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded CSV with {len(df)} rows")
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                column = st.selectbox("Select column containing text:", df.columns)
                texts = df[column].dropna().astype(str).tolist()
            
            if st.button("🤖 Analyze Uploaded Data", type="primary"):
                with st.spinner('🤖 Analyzing sentiment...'):
                    st.session_state.results = st.session_state.analyzer.analyze_multiple(texts)
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("Make sure your file is properly formatted (UTF-8 encoding)")

# Display Results
if st.session_state.results:
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    # Get statistics
    stats = st.session_state.analyzer.get_statistics()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Total Posts", stats['total'])
    with col2:
        st.metric("😊 Positive", f"{stats['positive']} ({stats['positive_pct']}%)", 
                 delta=None if stats['positive_pct'] < 50 else "Majority")
    with col3:
        st.metric("😞 Negative", f"{stats['negative']} ({stats['negative_pct']}%)",
                 delta=None if stats['negative_pct'] < 30 else "High")
    with col4:
        st.metric("😐 Neutral", f"{stats['neutral']} ({stats['neutral_pct']}%)")
    
    # Overall Sentiment
    st.markdown("---")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if stats['positive_pct'] > 50:
            st.success(f"### 🎉 Overall Sentiment: POSITIVE ({stats['positive_pct']}%)")
        elif stats['negative_pct'] > 50:
            st.error(f"### ⚠️ Overall Sentiment: NEGATIVE ({stats['negative_pct']}%)")
        else :
            st.info(f"### 🤔 Overall Sentiment: MIXED")
    
    st.markdown("---")
    
    # Charts Row
    col5, col6 = st.columns(2)
    
    with col5:
        # Pie Chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Positive', 'Negative', 'Neutral'],
            values=[stats['positive'], stats['negative'], stats['neutral']],
            marker=dict(colors=['#00CC96', '#EF553B', '#636EFA']),
            hole=0.4,
            textinfo='label+percent',
            textfont_size=14
        )])
        fig_pie.update_layout(
            title="Sentiment Distribution",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col6:
        # Bar Chart
        fig_bar = go.Figure(data=[
            go.Bar(
                x=['Positive', 'Negative', 'Neutral'],
                y=[stats['positive'], stats['negative'], stats['neutral']],
                marker_color=['#00CC96', '#EF553B', '#636EFA'],
                text=[stats['positive'], stats['negative'], stats['neutral']],
                textposition='auto',
            )
        ])
        fig_bar.update_layout(
            title="Sentiment Count Comparison",
            xaxis_title="Sentiment Type",
            yaxis_title="Number of Posts",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Word Clouds
    st.markdown("---")
    st.subheader("☁️ Word Clouds - Most Common Words")
    
    col7, col8 = st.columns(2)
    
    with col7:
        st.write("🟢 Positive Words")
        pos_words = st.session_state.analyzer.get_top_words('Positive', 50)
        if pos_words:
            wordcloud = WordCloud(
                width=400, 
                height=300, 
                background_color='white',
                colormap='Greens',
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(dict(pos_words))
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("No positive words found")
    
    with col8:
        st.write("🔴 Negative Words")
        neg_words = st.session_state.analyzer.get_top_words('Negative', 50)
        if neg_words:
            wordcloud = WordCloud(
                width=400, 
                height=300, 
                background_color='white',
                colormap='Reds',
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(dict(neg_words))
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("No negative words found")
    
    # Top Words Lists
    st.markdown("---")
    st.subheader("🔤 Top Keywords by Sentiment")
    
    col9, col10, col11 = st.columns(3)
    
    with col9:
        st.write("Top Positive Words:")
        pos_words_list = st.session_state.analyzer.get_top_words('Positive', 10)
        if pos_words_list:
            for word, count in pos_words_list:
                st.write(f"✅ {word}: {count}")
        else:
            st.write("None found")
    
    with col10:
        st.write("Top Negative Words:")
        neg_words_list = st.session_state.analyzer.get_top_words('Negative', 10)
        if neg_words_list:
            for word, count in neg_words_list:
                st.write(f"❌ {word}: {count}")
        else:
            st.write("None found")
    
    with col11:
        st.write("Top Neutral Words:")
        neu_words_list = st.session_state.analyzer.get_top_words('Neutral', 10)
        if neu_words_list:
            for word, count in neu_words_list:
                st.write(f"➖ {word}: {count}")
        else:
            st.write("None found")
    
    # Detailed Results Table
    st.markdown("---")
    st.subheader("📋 Detailed Results")
    
    # Filter options
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        filter_sentiment = st.multiselect(
            "Filter by sentiment:",
            ['Positive', 'Negative', 'Neutral'],
            default=['Positive', 'Negative', 'Neutral']
        )
    
    # Create DataFrame
    df_results = pd.DataFrame(st.session_state.results)
    
    # Apply filter
    if filter_sentiment:
        df_filtered = df_results[df_results['sentiment'].isin(filter_sentiment)]
    else:
        df_filtered = df_results
    
    st.write(f"Showing {len(df_filtered)} of {len(df_results)} posts")
    
    # Add color coding function
    def highlight_sentiment(row):
        if row['sentiment'] == 'Positive':
            return ['background-color: #d4edda'] * len(row)
        elif row['sentiment'] == 'Negative':
            return ['background-color: #f8d7da'] * len(row)
        else:
            return ['background-color: #d1ecf1'] * len(row)
    
    # Display table
    styled_df = df_filtered[['text', 'sentiment', 'polarity']].style.apply(highlight_sentiment, axis=1)
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Export Options
    st.markdown("---")
    st.subheader("💾 Export Results")
    
    col12, col13 = st.columns(2)
    
    with col12:
        # CSV Export
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Results as CSV",
            data=csv,
            file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col13:
        # Summary Export
        summary = f"""SENTIMENT ANALYSIS SUMMARY
=========================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW
--------
Total Posts Analyzed: {stats['total']}

SENTIMENT BREAKDOWN
------------------
Positive: {stats['positive']} ({stats['positive_pct']}%)
Negative: {stats['negative']} ({stats['negative_pct']}%)
Neutral: {stats['neutral']} ({stats['neutral_pct']}%)

METRICS
-------
Average Polarity: {stats['avg_polarity']}
Average Subjectivity: {stats['avg_subjectivity']}

OVERALL SENTIMENT
----------------
{"POSITIVE ✅" if stats['positive_pct'] > 50 else "NEGATIVE ❌" if stats['negative_pct'] > 50 else "MIXED ➖"}

TOP POSITIVE WORDS
-----------------
{chr(10).join([f"- {word}: {count}" for word, count in st.session_state.analyzer.get_top_words('Positive', 10)])}

TOP NEGATIVE WORDS
-----------------
{chr(10).join([f"- {word}: {count}" for word, count in st.session_state.analyzer.get_top_words('Negative', 10)])}

---
Generated by Social Media Sentiment Analyzer
"""
        
        st.download_button(
            label="📥 Download Summary Report",
            data=summary,
            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Social Media Sentiment Analysis Dashboard</strong></p>
        <p>Built with ❤️ using Python, Streamlit, TextBlob & Reddit API</p>
        <p style='font-size: 0.9em;'>Developed by Information Systems Students</p>
        <p style='font-size: 0.9em;'>Developed by Supun Tharushi Sachintha</p>
    </div>
""", unsafe_allow_html=True)