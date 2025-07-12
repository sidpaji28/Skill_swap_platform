import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import uuid
from datetime import datetime

# Import our modules
from matching import match_users, get_skill_similarity
from moderation import is_spammy, moderate_content
from database import SupabaseClient
from schemas import UserProfile, SwapRequest, FeedbackData
from utils.helpers import format_availability, validate_email, sanitize_input

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'db' not in st.session_state:
    st.session_state.db = SupabaseClient()

# Page config
st.set_page_config(
    page_title="SkillSync - AI-Powered Skill Swap",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🤝 SkillSync: AI-Powered Skill Swap Platform")
    st.markdown("*Find the perfect skill match and grow together!*")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        if st.session_state.user_id:
            st.success(f"Welcome, {st.session_state.user_name}!")
            page = st.selectbox(
                "Go to:",
                ["🏠 Dashboard", "🔍 Find Matches", "📝 My Profile", "💬 My Swaps", "⭐ Feedback", "🚪 Logout"]
            )
        else:
            page = st.selectbox(
                "Choose:",
                ["🔐 Login", "📝 Sign Up", "ℹ️ About"]
            )
    
    # Route to different pages
    if not st.session_state.user_id:
        if page == "🔐 Login":
            login_page()
        elif page == "📝 Sign Up":
            signup_page()
        else:
            about_page()
    else:
        if page == "🏠 Dashboard":
            dashboard_page()
        elif page == "🔍 Find Matches":
            find_matches_page()
        elif page == "📝 My Profile":
            profile_page()
        elif page == "💬 My Swaps":
            swaps_page()
        elif page == "⭐ Feedback":
            feedback_page()
        elif page == "🚪 Logout":
            logout()

def login_page():
    st.header("🔐 Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not validate_email(email):
                st.error("Please enter a valid email address")
                return
            
            # Simulate login (in real app, use Supabase auth)
            user = st.session_state.db.authenticate_user(email, password)
            if user:
                st.session_state.user_id = user['id']
                st.session_state.user_name = user['name']
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

def signup_page():
    st.header("📝 Sign Up")
    
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        location = st.text_input("Location (optional)")
        
        st.subheader("Skills")
        skills_offered = st.text_area("Skills you can offer (comma-separated)", 
                                     placeholder="e.g., Photoshop, Web Design, Python")
        skills_wanted = st.text_area("Skills you want to learn (comma-separated)",
                                    placeholder="e.g., Excel, Marketing, Guitar")
        
        availability = st.multiselect(
            "When are you available?",
            ["Morning", "Afternoon", "Evening", "Weekends", "Weekdays"]
        )
        
        is_public = st.checkbox("Make my profile public", value=True)
        
        submit = st.form_submit_button("Create Account")
        
        if submit:
            # Validate inputs
            if not name or not email or not password:
                st.error("Please fill in all required fields")
                return
            
            if not validate_email(email):
                st.error("Please enter a valid email address")
                return
            
            # Check for spam/toxicity
            if is_spammy(skills_offered) or is_spammy(skills_wanted):
                st.error("⚠️ Inappropriate or spammy content detected. Please revise your skills.")
                return
            
            # Create user profile
            user_profile = UserProfile(
                name=sanitize_input(name),
                email=email,
                location=sanitize_input(location) if location else None,
                skills_offered=[s.strip() for s in skills_offered.split(",") if s.strip()],
                skills_wanted=[s.strip() for s in skills_wanted.split(",") if s.strip()],
                availability=format_availability(availability),
                is_public=is_public
            )
            
            # Save to database
            user_id = st.session_state.db.create_user(user_profile)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.user_name = name
                st.success("Account created successfully!")
                st.rerun()
            else:
                st.error("Failed to create account. Email might already exist.")

def dashboard_page():
    st.header("🏠 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Swaps", "3", "1")
    
    with col2:
        st.metric("Completed Swaps", "12", "2")
    
    with col3:
        st.metric("Rating", "4.8⭐", "0.1")
    
    st.subheader("🔥 Recent Activity")
    
    # Get recent swaps
    recent_swaps = st.session_state.db.get_user_swaps(st.session_state.user_id, limit=5)
    
    if recent_swaps:
        for swap in recent_swaps:
            with st.expander(f"Swap: {swap['skill_offered']} ↔ {swap['skill_requested']}"):
                st.write(f"Status: {swap['status'].title()}")
                st.write(f"Partner: {swap['partner_name']}")
                st.write(f"Created: {swap['created_at']}")
    else:
        st.info("No recent activity. Start by finding matches!")
    
    st.subheader("💡 Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Find New Matches", use_container_width=True):
            st.switch_page("find_matches")
    
    with col2:
        if st.button("📝 Update Profile", use_container_width=True):
            st.switch_page("profile")

def find_matches_page():
    st.header("🔍 Find Perfect Matches")
    
    # Get current user's profile
    user_profile = st.session_state.db.get_user_profile(st.session_state.user_id)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Search Filters")
        
        skill_filter = st.selectbox(
            "Looking for:",
            ["All Skills"] + user_profile['skills_wanted']
        )
        
        location_filter = st.text_input("Location (optional)")
        
        availability_filter = st.multiselect(
            "Availability:",
            ["Morning", "Afternoon", "Evening", "Weekends", "Weekdays"]
        )
        
        min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)
        
        search_button = st.button("🔍 Search Matches", use_container_width=True)
    
    with col2:
        st.subheader("✨ AI-Powered Matches")
        
        if search_button or 'matches' not in st.session_state:
            with st.spinner("Finding your perfect matches..."):
                # Get all users
                all_users = st.session_state.db.get_all_users(exclude_id=st.session_state.user_id)
                
                # Apply filters
                filtered_users = []
                for user in all_users:
                    if not user['is_public']:
                        continue
                    
                    if skill_filter != "All Skills":
                        if skill_filter not in user['skills_offered']:
                            continue
                    
                    if location_filter:
                        if location_filter.lower() not in user['location'].lower():
                            continue
                    
                    filtered_users.append(user)
                
                # Get AI matches
                matches = match_users(user_profile['skills_wanted'], filtered_users)
                st.session_state.matches = matches
        
        # Display matches
        if 'matches' in st.session_state:
            for user, score in st.session_state.matches:
                with st.container():
                    st.markdown("---")
                    
                    col_avatar, col_info, col_action = st.columns([1, 3, 1])
                    
                    with col_avatar:
                        st.markdown(f"### 👤")
                        st.markdown(f"**{score:.0%}** match")
                    
                    with col_info:
                        st.markdown(f"**{user['name']}**")
                        st.markdown(f"📍 {user['location']}")
                        st.markdown(f"🕒 {user['availability']}")
                        
                        # Show matching skills
                        matching_skills = []
                        for wanted in user_profile['skills_wanted']:
                            for offered in user['skills_offered']:
                                similarity = get_skill_similarity(wanted, offered)
                                if similarity > 0.5:
                                    matching_skills.append(f"{wanted} ↔ {offered}")
                        
                        if matching_skills:
                            st.markdown("🎯 **Matching Skills:**")
                            for skill in matching_skills[:3]:
                                st.markdown(f"• {skill}")
                    
                    with col_action:
                        if st.button(f"💬 Request Swap", key=f"swap_{user['id']}"):
                            st.session_state.selected_user = user
                            st.session_state.show_swap_modal = True
        
        # Swap request modal
        if st.session_state.get('show_swap_modal', False):
            show_swap_request_modal()

def show_swap_request_modal():
    st.subheader("📩 Send Swap Request")
    
    user = st.session_state.selected_user
    user_profile = st.session_state.db.get_user_profile(st.session_state.user_id)
    
    with st.form("swap_request_form"):
        st.write(f"Requesting swap with: **{user['name']}**")
        
        my_skill = st.selectbox(
            "Your skill to offer:",
            user_profile['skills_offered']
        )
        
        their_skill = st.selectbox(
            "Skill you want to learn:",
            user['skills_offered']
        )
        
        message = st.text_area(
            "Message (optional):",
            placeholder="Hi! I'd love to learn from you..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Send Request", use_container_width=True):
                if is_spammy(message):
                    st.error("⚠️ Inappropriate message detected")
                else:
                    swap_request = SwapRequest(
                        from_user_id=st.session_state.user_id,
                        to_user_id=user['id'],
                        skill_offered=my_skill,
                        skill_requested=their_skill,
                        message=message
                    )
                    
                    if st.session_state.db.create_swap_request(swap_request):
                        st.success("Swap request sent!")
                        st.session_state.show_swap_modal = False
                        st.rerun()
                    else:
                        st.error("Failed to send request")
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.show_swap_modal = False
                st.rerun()

def profile_page():
    st.header("📝 My Profile")
    
    user_profile = st.session_state.db.get_user_profile(st.session_state.user_id)
    
    with st.form("profile_form"):
        name = st.text_input("Name", value=user_profile['name'])
        location = st.text_input("Location", value=user_profile['location'] or "")
        
        skills_offered = st.text_area(
            "Skills I can offer:",
            value=", ".join(user_profile['skills_offered'])
        )
        
        skills_wanted = st.text_area(
            "Skills I want to learn:",
            value=", ".join(user_profile['skills_wanted'])
        )
        
        availability = st.multiselect(
            "Availability:",
            ["Morning", "Afternoon", "Evening", "Weekends", "Weekdays"],
            default=user_profile['availability'].split(", ") if user_profile['availability'] else []
        )
        
        is_public = st.checkbox("Make profile public", value=user_profile['is_public'])
        
        if st.form_submit_button("Update Profile"):
            # Validate content
            if is_spammy(skills_offered) or is_spammy(skills_wanted):
                st.error("⚠️ Inappropriate content detected")
                return
            
            updated_profile = UserProfile(
                name=sanitize_input(name),
                email=user_profile['email'],
                location=sanitize_input(location) if location else None,
                skills_offered=[s.strip() for s in skills_offered.split(",") if s.strip()],
                skills_wanted=[s.strip() for s in skills_wanted.split(",") if s.strip()],
                availability=format_availability(availability),
                is_public=is_public
            )
            
            if st.session_state.db.update_user_profile(st.session_state.user_id, updated_profile):
                st.success("Profile updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update profile")

def swaps_page():
    st.header("💬 My Swaps")
    
    tab1, tab2, tab3 = st.tabs(["📥 Received", "📤 Sent", "✅ Completed"])
    
    with tab1:
        st.subheader("Requests received")
        received_swaps = st.session_state.db.get_received_swaps(st.session_state.user_id)
        
        for swap in received_swaps:
            if swap['status'] == 'pending':
                with st.expander(f"From {swap['from_user_name']}: {swap['skill_offered']} ↔ {swap['skill_requested']}"):
                    st.write(f"Message: {swap.get('message', 'No message')}")
                    st.write(f"Received: {swap['created_at']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"✅ Accept", key=f"accept_{swap['id']}"):
                            st.session_state.db.update_swap_status(swap['id'], 'accepted')
                            st.success("Swap accepted!")
                            st.rerun()
                    
                    with col2:
                        if st.button(f"❌ Reject", key=f"reject_{swap['id']}"):
                            st.session_state.db.update_swap_status(swap['id'], 'rejected')
                            st.info("Swap rejected")
                            st.rerun()
    
    with tab2:
        st.subheader("Requests sent")
        sent_swaps = st.session_state.db.get_sent_swaps(st.session_state.user_id)
        
        for swap in sent_swaps:
            status_emoji = {"pending": "⏳", "accepted": "✅", "rejected": "❌"}
            st.write(f"{status_emoji[swap['status']]} **{swap['to_user_name']}** - {swap['skill_offered']} ↔ {swap['skill_requested']}")
    
    with tab3:
        st.subheader("Completed swaps")
        completed_swaps = st.session_state.db.get_completed_swaps(st.session_state.user_id)
        
        for swap in completed_swaps:
            st.write(f"✅ **{swap['partner_name']}** - {swap['skill_offered']} ↔ {swap['skill_requested']}")

def feedback_page():
    st.header("⭐ Feedback")
    
    st.subheader("Leave Feedback")
    
    completed_swaps = st.session_state.db.get_completed_swaps(st.session_state.user_id)
    unfeedback_swaps = [s for s in completed_swaps if not s.get('feedback_given')]
    
    if unfeedback_swaps:
        selected_swap = st.selectbox(
            "Select swap to review:",
            unfeedback_swaps,
            format_func=lambda x: f"{x['partner_name']} - {x['skill_offered']} ↔ {x['skill_requested']}"
        )
        
        with st.form("feedback_form"):
            rating = st.slider("Rating", 1, 5, 5)
            comment = st.text_area("Comment (optional)")
            
            if st.form_submit_button("Submit Feedback"):
                if is_spammy(comment):
                    st.error("⚠️ Inappropriate comment detected")
                else:
                    feedback = FeedbackData(
                        swap_id=selected_swap['id'],
                        from_user_id=st.session_state.user_id,
                        to_user_id=selected_swap['partner_id'],
                        rating=rating,
                        comment=comment
                    )
                    
                    if st.session_state.db.create_feedback(feedback):
                        st.success("Feedback submitted!")
                        st.rerun()
                    else:
                        st.error("Failed to submit feedback")
    else:
        st.info("No completed swaps to review")
    
    st.subheader("Received Feedback")
    
    feedback_received = st.session_state.db.get_user_feedback(st.session_state.user_id)
    
    if feedback_received:
        for feedback in feedback_received:
            st.write(f"⭐ **{feedback['rating']}/5** from {feedback['from_user_name']}")
            if feedback['comment']:
                st.write(f"*{feedback['comment']}*")
            st.write("---")
    else:
        st.info("No feedback received yet")

def about_page():
    st.header("ℹ️ About SkillSync")
    
    st.markdown("""
    **SkillSync** is an AI-powered platform that helps you exchange skills with others in your community.
    
    ### 🎯 How it works:
    1. **Sign up** and list your skills
    2. **Browse** other users' profiles
    3. **Match** with compatible skill partners using AI
    4. **Exchange** skills and learn together
    5. **Rate** your experience and build reputation
    
    ### 🤖 AI Features:
    - **Smart Matching**: Our AI finds the best skill matches for you
    - **Spam Detection**: Automatic content moderation keeps the platform safe
    - **Skill Similarity**: Advanced algorithms understand skill relationships
    
    ### 🔒 Privacy & Safety:
    - Control your profile visibility
    - Report inappropriate content
    - Secure authentication
    
    Ready to start swapping skills? Sign up now!
    """)

def logout():
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.clear()
    st.rerun()

if __name__ == "__main__":
    main()