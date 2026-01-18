import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Smart Water Usage Advisor",
    page_icon="💧",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom right, #eff6ff, #ecfeff);
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #3b82f6;
        color: white;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #f3f4f6;
        color: #1f2937;
        margin-right: 20%;
    }
    .quick-btn {
        background-color: white;
        border: 1px solid #93c5fd;
        color: #2563eb;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"type": "bot", "text": "Hello! I'm your Smart Water Usage Advisor. I can help you understand water conservation, calculate your usage, and provide personalized tips. Ask me anything about saving water!"}
    ]

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'household_size': 4,
        'region': 'urban'
    }

# Knowledge base for RAG
knowledge_base = [
    {
        'topic': 'daily_water_usage',
        'content': 'Average daily water usage per person varies: Urban areas: 135-150 liters, Rural areas: 70-90 liters. Activities breakdown: Toilet flushing (30%), Bathing (25%), Laundry (20%), Kitchen (15%), Other (10%).'
    },
    {
        'topic': 'water_conservation_tips',
        'content': 'Effective water conservation tips: Fix leaky taps (saves 20L/day), Install low-flow showerheads (saves 40L/day), Use bucket instead of shower (saves 60L/day), Turn off tap while brushing (saves 6L/min), Reuse RO waste water for plants, Collect rainwater, Run washing machine only with full loads.'
    },
    {
        'topic': 'bathroom_tips',
        'content': 'Bathroom water saving: Install dual-flush toilets, Take shorter showers (5 mins max), Use bucket for bathing, Fix dripping taps immediately, Install aerators on taps, Don\'t let water run while brushing or shaving.'
    },
    {
        'topic': 'kitchen_tips',
        'content': 'Kitchen water conservation: Wash vegetables in a bowl not running water, Reuse water from washing vegetables for plants, Run dishwasher only when full, Use minimal water for cooking, Thaw frozen food in fridge not under running water.'
    },
    {
        'topic': 'garden_tips',
        'content': 'Garden watering tips: Water plants early morning or evening, Use drip irrigation, Mulch soil to retain moisture, Collect and use rainwater, Choose native drought-resistant plants, Use greywater from kitchen for non-edible plants.'
    },
    {
        'topic': 'water_crisis',
        'content': 'Global water crisis facts: Only 0.3% of Earth\'s water is accessible freshwater. By 2025, half the world will face water scarcity. Agriculture uses 70% of freshwater. 2 billion people lack safe drinking water. Water conservation is critical for sustainability.'
    },
    {
        'topic': 'sdg_6',
        'content': 'SDG 6 targets: Ensure universal access to safe drinking water, Achieve adequate sanitation for all, Improve water quality, Increase water-use efficiency, Implement integrated water resource management, Protect water-related ecosystems.'
    },
    {
        'topic': 'rainwater_harvesting',
        'content': 'Rainwater harvesting benefits: Free water source, Reduces water bills, Decreases groundwater depletion, Prevents urban flooding, Simple to implement. A 100 sq.m roof can collect 100,000 liters annually in areas with 1000mm rainfall.'
    },
    {
        'topic': 'water_footprint',
        'content': 'Water footprint understanding: Direct water (drinking, bathing, cooking), Indirect water (food production, products). 1 kg beef requires 15,000L water, 1 kg rice requires 2,500L, 1 cotton shirt requires 2,700L. Reducing meat consumption significantly lowers water footprint.'
    },
    {
        'topic': 'greywater_reuse',
        'content': 'Greywater reuse: Water from washing machines, showers, sinks can be reused. Safe for: Toilet flushing, Garden watering, Car washing, Floor cleaning. Not safe for: Drinking, Cooking, Vegetable gardens. Can save 30-40% of household water.'
    }
]

# Simple RAG retrieval function
def retrieve_relevant_info(query):
    lower_query = query.lower()
    relevant_docs = []
    
    for doc in knowledge_base:
        topic_words = doc['topic'].split('_')
        topic_match = any(word in lower_query for word in topic_words)
        
        content_words = [word for word in doc['content'].lower().split() if len(word) > 4]
        content_match = any(word in lower_query for word in content_words)
        
        if topic_match or content_match:
            relevant_docs.append(doc)
    
    return relevant_docs if relevant_docs else [knowledge_base[1]]

# Generate response based on retrieved context
def generate_response(query, context):
    lower_query = query.lower()
    profile = st.session_state.user_profile
    
    # Calculate water usage
    if any(word in lower_query for word in ['calculate', 'usage', 'how much']):
        per_person_usage = 140 if profile['region'] == 'urban' else 80
        total_usage = profile['household_size'] * per_person_usage
        comparison = 135 * profile['household_size']
        
        response = f"Based on your household of {profile['household_size']} people in an {profile['region']} area, your estimated daily water usage is approximately {total_usage} liters ({per_person_usage}L per person). The national average is 135L per person. "
        
        if total_usage > comparison:
            response += "You're using more than average - here are ways to reduce:\n\n"
        else:
            response += "Good job! Here are ways to conserve even more:\n\n"
        
        response += '. '.join(context[0]['content'].split('.')[:3]) + '.'
        return response
    
    # Specific topic responses
    topic_keywords = {
        'bathroom_tips': ['bathroom', 'shower', 'toilet'],
        'kitchen_tips': ['kitchen', 'cooking', 'dish'],
        'garden_tips': ['garden', 'plant', 'watering'],
        'rainwater_harvesting': ['rain', 'harvest'],
        'water_crisis': ['crisis', 'scarcity', 'global'],
        'sdg_6': ['sdg', 'sustainable', 'goal'],
        'greywater_reuse': ['grey', 'reuse', 'recycle'],
        'water_footprint': ['footprint', 'indirect']
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in lower_query for keyword in keywords):
            matching_doc = next((doc for doc in context if doc['topic'] == topic), None)
            if matching_doc:
                topic_name = topic.replace('_', ' ').title()
                return f"{topic_name}:\n\n{matching_doc['content']}"
    
    # Default response
    return f"Here's what I found about water conservation:\n\n{context[0]['content']}\n\nWould you like specific tips for bathroom, kitchen, or garden?"

# Header
st.markdown("# 💧 Smart Water Usage Advisor")
st.markdown("### AI-Powered Water Conservation Assistant (SDG 6)")

# Stats section
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 30px;">👥</div>
        <div style="color: #6b7280; font-size: 14px;">Household Size</div>
        <div style="font-size: 28px; font-weight: bold;">{st.session_state.user_profile['household_size']}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 30px;">🏠</div>
        <div style="color: #6b7280; font-size: 14px;">Area Type</div>
        <div style="font-size: 24px; font-weight: bold;">{st.session_state.user_profile['region'].capitalize()}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_usage = 140 if st.session_state.user_profile['region'] == 'urban' else 80
    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 30px;">📉</div>
        <div style="color: #6b7280; font-size: 14px;">Avg. Usage</div>
        <div style="font-size: 28px; font-weight: bold;">{avg_usage}L</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 30px;">🌿</div>
        <div style="color: #6b7280; font-size: 14px;">SDG Target</div>
        <div style="font-size: 24px; font-weight: bold;">SDG 6</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Settings section
st.markdown("### Settings")
col_settings1, col_settings2 = st.columns(2)

with col_settings1:
    household_size = st.number_input(
        "Household Size:",
        min_value=1,
        max_value=20,
        value=st.session_state.user_profile['household_size'],
        key='household_input'
    )
    st.session_state.user_profile['household_size'] = household_size

with col_settings2:
    region = st.selectbox(
        "Region:",
        options=['urban', 'rural'],
        index=0 if st.session_state.user_profile['region'] == 'urban' else 1,
        key='region_input'
    )
    st.session_state.user_profile['region'] = region

st.markdown("<br>", unsafe_allow_html=True)

# Chat Interface
st.markdown("### 💬 Chat with Water Advisor")
st.markdown("Ask about water conservation, tips, and calculations")

# Display messages
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        msg_class = "user-message" if msg['type'] == 'user' else "bot-message"
        st.markdown(f'<div class="chat-message {msg_class}">{msg["text"]}</div>', unsafe_allow_html=True)

# Quick questions
st.markdown("#### Quick questions:")
quick_questions = [
    "Calculate my water usage",
    "Bathroom water saving tips",
    "How to harvest rainwater?",
    "Kitchen conservation tips",
    "Tell me about SDG 6"
]

cols = st.columns(len(quick_questions))
for idx, (col, question) in enumerate(zip(cols, quick_questions)):
    with col:
        if st.button(question, key=f'quick_{idx}'):
            # Add user message
            st.session_state.messages.append({"type": "user", "text": question})
            
            # Generate response using RAG
            relevant_context = retrieve_relevant_info(question)
            response = generate_response(question, relevant_context)
            
            # Add bot response
            st.session_state.messages.append({"type": "bot", "text": response})
            st.rerun()

# Input section
user_input = st.text_input("Ask about water conservation...", key='user_input', label_visibility='collapsed', placeholder="Ask about water conservation...")

if st.button("Send", type="primary") or (user_input and user_input != ""):
    if user_input and user_input.strip():
        # Add user message
        st.session_state.messages.append({"type": "user", "text": user_input})
        
        # RAG pipeline: Retrieve + Generate
        relevant_context = retrieve_relevant_info(user_input)
        response = generate_response(user_input, relevant_context)
        
        # Add bot response
        st.session_state.messages.append({"type": "bot", "text": response})
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Project Information
st.markdown("---")
st.markdown("### 📋 Project Information")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("**SDG Alignment:** SDG 6: Clean Water and Sanitation")
    st.markdown("**Technology Used:** RAG (Retrieval-Augmented Generation)")

with col_info2:
    st.markdown("**Target Users:** Households, Communities, Educational Institutions")
    st.markdown("**Impact:** Promotes water conservation awareness & reduction")

st.markdown("#### Responsible AI Considerations:")
st.success("""
- ✅ Provides evidence-based water conservation information
- ✅ Transparent calculations based on regional standards
- ✅ No collection of personal or sensitive data
- ✅ Promotes sustainable behavior change
""")