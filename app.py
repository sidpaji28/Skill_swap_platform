import streamlit as st
from database import SupabaseClient
from schema_definitions import UserProfile
from matching import match_users
from spam_filter import is_spammy
import base64
import uuid

# Advanced Dark 3D CSS with stunning effects
st.markdown("""
<style>
    /* Import futuristic fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    /* Global dark theme with 3D perspective */
    .stApp {
        font-family: 'Rajdhani', sans-serif;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Futuristic Sidebar with cyberpunk styling */
    .stSidebar {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.85) 0%, rgba(26, 26, 46, 0.95) 100%);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transform: perspective(1000px) rotateY(-5deg);
        transition: all 0.3s ease;
        z-index: 2;
    }

    /* Hover effect for sidebar */
    .stSidebar:hover {
        transform: perspective(1000px) rotateY(0deg) translateZ(10px);
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.7),
            inset 0 1px 0 rgba(255, 255, 255, 0.2),
            0 0 30px rgba(0, 245, 255, 0.3);
    }

    /* Sidebar radio button container */
    .stSidebar .stRadio > div {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.15) 0%, rgba(255, 0, 255, 0.15) 100%);
        border: 1px solid rgba(0, 245, 255, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        transform: translateZ(0);
    }

    /* Hover effect for radio button container */
    .stSidebar .stRadio > div:hover {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.25) 0%, rgba(255, 0, 255, 0.25) 100%);
        transform: translateZ(10px) scale(1.05);
        box-shadow: 0 10px 25px rgba(0, 245, 255, 0.3);
    }

    /* Radio button labels */
    .stSidebar .stRadio > label {
        color: #00f5ff;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        font-size: 1.3rem;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
        padding: 0.5rem;
        transition: all 0.3s ease;
    }

    /* Radio button selected state */
    .stSidebar .stRadio > div input[type="radio"]:checked + label {
        color: #ff00ff;
        text-shadow: 0 0 15px rgba(255, 0, 255, 0.7);
        transform: scale(1.05);
    }

    /* Sidebar title */
    .stSidebar h3 {
        font-family: 'Orbitron', monospace;
        color: #00f5ff;
        font-weight: 900;
        font-size: 1.8rem;
        text-shadow: 0 0 15px rgba(0, 245, 255, 0.7);
        margin-bottom: 1.5rem;
        text-align: center;
    }

    /* Responsive design for sidebar */
    @media (max-width: 768px) {
        .stSidebar {
            padding: 1.5rem;
            margin: 0.5rem;
            border-radius: 15px;
            transform: perspective(1000px) rotateY(0deg);
        }
        
        .stSidebar .stRadio > label {
            font-size: 1.1rem;
        }
        
        .stSidebar .stRadio > div {
            padding: 0.75rem;
        }
    }
    
    /* Floating particles effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(255, 255, 255, 0.3), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255, 255, 255, 0.2), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(255, 255, 255, 0.4), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(255, 255, 255, 0.2), transparent);
        background-repeat: repeat;
        background-size: 75px 100px;
        animation: sparkle 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes sparkle {
        0% { transform: translateY(0px); }
        100% { transform: translateY(-100px); }
    }
    
    /* Main container with 3D glass effect */
    .main .block-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 3rem;
        margin: 2rem auto;
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            0 0 100px rgba(83, 52, 131, 0.3);
        position: relative;
        z-index: 1;
        transform-style: preserve-3d;
        transition: all 0.3s ease;
    }
    
    .main .block-container:hover {
        transform: translateY(-5px) rotateX(2deg);
        box-shadow: 
            0 35px 70px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.2),
            0 0 120px rgba(83, 52, 131, 0.4);
    }
    
    /* Cinematic title with entrance animation and clean neon glow */
    .main h1 {
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 5rem;
        color: transparent;
        background: linear-gradient(45deg, #00f5ff, #ff00ff, #00ff00, #ffff00, #ff0000, #00f5ff);
        -webkit-background-clip: text;
        background-clip: text;
        text-align: center;
        margin: 2rem 0 4rem 0;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.8);
        animation: slideIn 2s ease-out forwards;
        transform: perspective(1500px) rotateX(25deg) translateZ(50px);
        filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.8));
        position: relative;
        z-index: 3;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Entrance animation for title */
    @keyframes slideIn {
        0% {
            opacity: 0;
            transform: perspective(1500px) rotateX(25deg) translateZ(50px) translateY(-100px);
            text-shadow: 0 0 0 rgba(0, 245, 255, 0);
        }
        100% {
            opacity: 1;
            transform: perspective(1500px) rotateX(25deg) translateZ(50px) translateY(0);
            text-shadow: 0 0 20px rgba(0, 245, 255, 0.8);
        }
    }

    /* Lens flare effect behind the title */
    .main h1::before {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: radial-gradient(circle, rgba(0, 245, 255, 0.3) 0%, transparent 60%);
        opacity: 0;
        animation: lensFlareEntrance 2s ease-out forwards;
        z-index: -1;
        pointer-events: none;
    }

    @keyframes lensFlareEntrance {
        0% { opacity: 0; transform: scale(0.5); }
        50% { opacity: 0.6; transform: scale(1.3); }
        100% { opacity: 0.4; transform: scale(1); }
    }

    /* Fallback for Streamlit title */
    [data-testid="stAppViewContainer"] h1 {
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 5rem;
        color: transparent;
        background: linear-gradient(45deg, #00f5ff, #ff00ff, #00ff00, #ffff00, #ff0000, #00f5ff);
        -webkit-background-clip: text;
        background-clip: text;
        text-align: center;
        margin: 2rem 0 4rem 0;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.8);
        animation: slideIn 2s ease-out forwards;
        transform: perspective(1500px) rotateX(25deg) translateZ(50px);
        filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.8));
        position: relative;
        z-index: 3;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Futuristic form styling */
    .stForm {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(26, 26, 46, 0.7) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 3rem;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transform: perspective(1000px) rotateX(5deg);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stForm::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(0, 245, 255, 0.05), transparent);
        animation: shimmer 3s infinite;
        pointer-events: none;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .stForm:hover {
        transform: perspective(1000px) rotateX(0deg) translateY(-5px);
        box-shadow: 
            0 30px 60px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.2),
            0 0 50px rgba(0, 245, 255, 0.2);
    }
    
    /* Cyberpunk input fields */
    .stTextInput > div > div > input {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid rgba(0, 245, 255, 0.3);
        border-radius: 15px;
        padding: 1rem;
        font-size: 1.1rem;
        color: #ffffff;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.5);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00f5ff;
        box-shadow: 
            0 0 20px rgba(0, 245, 255, 0.5),
            inset 0 2px 10px rgba(0, 0, 0, 0.7);
        outline: none;
        transform: scale(1.02);
    }
    
    .stSelectbox > div > div > select {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid rgba(0, 245, 255, 0.3);
        border-radius: 15px;
        padding: 1rem;
        font-size: 1.1rem;
        color: #ffffff;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.5);
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #00f5ff;
        box-shadow: 
            0 0 20px rgba(0, 245, 255, 0.5),
            inset 0 2px 10px rgba(0, 0, 0, 0.7);
        outline: none;
        transform: scale(1.02);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div > div > label {
        color: #00f5ff;
        font-family: 'Orbitron', monospace;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }

    .stFileUploader > div > div > div > button {
        background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 50%, #00ff00 100%);
        color: #000000;
        border: none;
        border-radius: 15px;
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        font-family: 'Orbitron', monospace;
        transition: all 0.3s ease;
        box-shadow: 
            0 5px 15px rgba(0, 245, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    .stFileUploader > div > div > div > button:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 8px 20px rgba(0, 245, 255, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
    }
    
    /* Holographic buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 50%, #00ff00 100%);
        color: #000000;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 700;
        font-family: 'Orbitron', monospace;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 
            0 10px 30px rgba(0, 245, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transform: perspective(1000px) rotateX(10deg);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: buttonShimmer 2s infinite;
        pointer-events: none;
    }
    
    @keyframes buttonShimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .stButton > button:hover {
        transform: perspective(1000px) rotateX(0deg) translateY(-5px) scale(1.05);
        box-shadow: 
            0 15px 40px rgba(0, 245, 255, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.4),
            0 0 50px rgba(255, 0, 240, 0.3);
    }
    
    /* Neon subheaders */
    .main h2 {
        font-family: 'Orbitron', monospace;
        color: #00f5ff;
        font-weight: 700;
        font-size: 2rem;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(0, 245, 255, 0.5);
        text-shadow: 0 0 15px rgba(0, 245, 255, 0.7);
        position: relative;
        overflow: hidden;
    }
    
    .main h2::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00f5ff, transparent);
        animation: scanline 2s infinite;
    }
    
    @keyframes scanline {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Holographic alerts */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 255, 0, 0.1) 0%, rgba(0, 255, 127, 0.1) 100%);
        border: 1px solid rgba(0, 255, 0, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0, 255, 0, 0.2);
        color: #00ff00;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(255, 0, 0, 0.1) 0%, rgba(255, 0, 127, 0.1) 100%);
        border: 1px solid rgba(255, 0, 0, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(255, 0, 0, 0.2);
        color: #ff0066;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 255, 0, 0.1) 0%, rgba(255, 165, 0, 0.1) 100%);
        border: 1px solid rgba(255, 255, 0, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(255, 255, 0, 0.2);
        color: #ffff00;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.1) 0%, rgba(0, 127, 255, 0.1) 100%);
        border: 1px solid rgba(0, 245, 255, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0, 245, 255, 0.2);
        color: #00f5ff;
    }
    
    /* 3D Profile cards with holographic effects */
    .profile-card {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.8) 0%, rgba(26, 26, 46, 0.9) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        transform: perspective(1000px) rotateX(5deg);
        position: relative;
        overflow: hidden;
    }
    
    .profile-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #00f5ff, #ff00ff, #00ff00, #ffff00);
        border-radius: 25px;
        z-index: -1;
        animation: borderGlow 3s infinite;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .profile-card:hover::before {
        opacity: 1;
    }
    
    @keyframes borderGlow {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.8; }
    }
    
    .profile-card:hover {
        transform: perspective(1000px) rotateX(0deg) translateY(-10px) scale(1.02);
        box-shadow: 
            0 30px 60px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.2),
            0 0 50px rgba(0, 245, 255, 0.3);
    }
    
    /* Profile photo styling */
    .profile-photo {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid rgba(0, 245, 255, 0.5);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
        margin: 0 auto 1.5rem;
        display: block;
        transition: all 0.3s ease;
    }

    .profile-photo:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.7);
    }
    
    /* Epic match cards */
    .match-card {
        background: linear-gradient(135deg, rgba(0, 255, 0, 0.1) 0%, rgba(0, 255, 127, 0.1) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 255, 0, 0.3);
        border-radius: 25px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            0 0 30px rgba(0, 255, 0, 0.2);
        transition: all 0.3s ease;
        transform: perspective(1000px) rotateX(5deg);
        position: relative;
        overflow: hidden;
    }
    
    .match-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.2), transparent);
        animation: matchScan 3s infinite;
        pointer-events: none;
    }
    
    @keyframes matchScan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .match-card:hover {
        transform: perspective(1000px) rotateX(0deg) translateY(-10px) scale(1.03);
        box-shadow: 
            0 30px 60px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.2),
            0 0 50px rgba(0, 255, 0, 0.4);
    }
    
    /* Neon skill tags */
    .skill-tag {
        display: inline-block;
        background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 100%);
        color: #000000;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.3rem;
        box-shadow: 
            0 5px 15px rgba(0, 245, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
        transform: perspective(1000px) rotateX(10deg);
    }
    
    .skill-tag:hover {
        transform: perspective(1000px) rotateX(0deg) translateY(-3px) scale(1.1);
        box-shadow: 
            0 8px 25px rgba(0, 245, 255, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
    }
    
    /* Holographic match score */
    .match-score {
        background: linear-gradient(135deg, #00ff00 0%, #00ffff 100%);
        color: #000000;
        padding: 1rem 2rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1.3rem;
        font-family: 'Orbitron', monospace;
        display: inline-block;
        box-shadow: 
            0 10px 30px rgba(0, 255, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transform: perspective(1000px) rotateX(10deg);
    }
    
    /* Neon dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00f5ff, #ff00ff, #00f5ff, transparent);
        margin: 3rem 0;
        border-radius: 2px;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
    
    /* Form labels with neon styling */
    .stForm label {
        font-weight: 600;
        color: #00f5ff;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: #00f5ff;
        font-weight: 500;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 2rem;
            margin: 1rem;
        }
        
        .main h1 {
            font-size: 3.2rem;
            margin: 1.5rem 0 3rem 0;
        }
        
        .profile-card, .match-card {
            padding: 1.5rem;
            transform: perspective(1000px) rotateX(2deg);
        }

        .profile-photo {
            width: 100px;
            height: 100px;
        }
    }
</style>
""", unsafe_allow_html=True)

db = SupabaseClient()
st.set_page_config(page_title="SkillSwap", layout="centered")

# Add a sidebar title for better UX
st.sidebar.header("SkillSwap Menu")

# Main title
st.title("🔁 SkillSwap Platform")

# Add a cinematic subtitle
st.markdown(
    '<h2 style="font-family: \'Orbitron\', monospace; color: #00f5ff; text-align: center; text-shadow: 0 0 15px rgba(0, 245, 255, 0.7); font-size: 1.8rem; margin-top: -2rem;">Connect. Learn. Swap Skills.</h2>',
    unsafe_allow_html=True
)

menu = st.sidebar.radio("Navigate", ["Dashboard", "Register", "Login", "Explore Matches", "Browse Skills"])

# ----------------------------
# DASHBOARD PAGE
# ----------------------------
if menu == "Dashboard":
    st.subheader("Your SkillSwap Dashboard")
    if "user" not in st.session_state:
        st.warning("Please log in to view your dashboard.")
    else:
        user = st.session_state["user"]

        # Display profile photo
        profile_photo_url = user.get("profile_photo_url", None)
        if profile_photo_url:
            st.markdown(
                f'<img src="{profile_photo_url}" class="profile-photo" alt="Profile Photo">',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="width: 150px; height: 150px; border-radius: 50%; background: rgba(0, 245, 255, 0.2); margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center; color: #00f5ff; font-family: \'Orbitron\', monospace; text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);">No Photo</div>',
                unsafe_allow_html=True
            )

        # Display user credentials
        st.markdown(f"""
        <div class="profile-card">
            <h3 style="color: #00f5ff; margin-bottom: 1.5rem; font-family: 'Orbitron', monospace; text-shadow: 0 0 15px rgba(0, 245, 255, 0.7);">🎯 {user.get('name', 'Unnamed')}</h3>
            <p style="color: #ffffff; margin-bottom: 1rem; font-size: 1.1rem;"><strong>📧 Email:</strong> <span style="color: #00ffff;">{user.get('email', 'N/A')}</span></p>
            <p style="color: #ffffff; margin-bottom: 1rem; font-size: 1.1rem;"><strong>📍 Location:</strong> <span style="color: #00ffff;">{user.get('location', 'Unknown')}</span></p>
            <p style="color: #ffffff; margin-bottom: 1rem; font-size: 1.1rem;"><strong>🕒 Availability:</strong> <span style="color: #00ffff;">{user.get('availability', 'N/A')}</span></p>
            <p style="margin-bottom: 1rem; color: #ffffff; font-size: 1.1rem;"><strong>🛠️ Skills Offered:</strong><br>
                {' '.join([f'<span class="skill-tag">{skill}</span>' for skill in user.get('skills_offered', [])])}
            </p>
            <p style="margin-bottom: 1rem; color: #ffffff; font-size: 1.1rem;"><strong>🎯 Skills Wanted:</strong><br>
                {' '.join([f'<span class="skill-tag">{skill}</span>' for skill in user.get('skills_wanted', [])])}
            </p>
            <p style="color: #00ff00; font-weight: 600; text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);"><strong>🌐 Profile Visibility:</strong> {'Public' if user.get('is_public', False) else 'Private'}</p>
        </div>
        """, unsafe_allow_html=True)

        # Profile photo upload
        st.subheader("Update Profile Photo")
        with st.form("photo_upload_form"):
            uploaded_file = st.file_uploader("Upload Profile Photo (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
            submit_photo = st.form_submit_button("Upload Photo")

        if submit_photo and uploaded_file is not None:
            try:
                # Check if storage bucket exists
                bucket = "profile_photos"
                try:
                    db.client.storage.from_(bucket).list()
                except Exception as e:
                    if "Bucket not found" in str(e):
                        st.error("Storage bucket 'profile_photos' not found. Please create it in Supabase Storage.")
                    else:
                        st.error(f"Error accessing storage bucket: {str(e)}")
                    raise Exception("Bucket check failed")

                # Generate a unique filename
                file_extension = uploaded_file.name.split('.')[-1]
                file_name = f"{uuid.uuid4()}.{file_extension}"
                
                # Read file bytes
                file_bytes = uploaded_file.read()
                
                # Upload to Supabase Storage
                db.client.storage.from_(bucket).upload(file_name, file_bytes, file_options={"content-type": f"image/{file_extension}"})
                
                # Get public URL
                photo_url = db.client.storage.from_(bucket).get_public_url(file_name)
                
                # Update user profile with photo URL
                updated_profile = UserProfile(
                    name=user.get('name'),
                    email=user.get('email'),
                    password="",  # Password not needed for update
                    location=user.get('location', ''),
                    availability=user.get('availability', ''),
                    is_public=user.get('is_public', False),
                    skills_offered=user.get('skills_offered', []),
                    skills_wanted=user.get('skills_wanted', []),
                    profile_photo_url=photo_url
                )
                success = db.update_user(user.get('id'), updated_profile)
                
                if success:
                    # Update session state
                    user['profile_photo_url'] = photo_url
                    st.session_state["user"] = user
                    st.success("Profile photo updated successfully!")
                    st.rerun()  # Rerun to refresh the displayed photo
                else:
                    st.error("Failed to update profile photo.")
            except Exception as e:
                st.error(f"Error uploading photo: {str(e)}")

        # Add skills form
        st.subheader("Add New Skills")
        with st.form("add_skills_form"):
            new_skills_offered = st.text_input("Add Skills You Offer (comma-separated, e.g., Python, Design)")
            new_skills_wanted = st.text_input("Add Skills You Want to Learn (comma-separated, e.g., JavaScript, Cooking)")
            submit_skills = st.form_submit_button("Add Skills")

        if submit_skills:
            if not new_skills_offered and not new_skills_wanted:
                st.error("Please enter at least one skill to add.")
            else:
                try:
                    # Get current skills from user_skills table
                    user_id = user.get('id')
                    response = db.client.table('user_skills').select('skill, type').eq('user_id', user_id).execute()
                    current_skills = response.data if response.data else []
                    current_skills_offered = [s['skill'] for s in current_skills if s['type'] == 'offered']
                    current_skills_wanted = [s['skill'] for s in current_skills if s['type'] == 'wanted']
                    
                    # Parse and clean new skills
                    new_offered = [s.strip() for s in new_skills_offered.split(",") if s.strip()] if new_skills_offered else []
                    new_wanted = [s.strip() for s in new_skills_wanted.split(",") if s.strip()] if new_skills_wanted else []
                    
                    # Check for spam
                    if is_spammy(" ".join(new_offered + new_wanted)):
                        st.error("Skills content seems spammy. Please revise.")
                    else:
                        # Filter out duplicates (case-insensitive)
                        new_offered = [s for s in new_offered if s.lower() not in [x.lower() for x in current_skills_offered]]
                        new_wanted = [s for s in new_wanted if s.lower() not in [x.lower() for x in current_skills_wanted]]
                        
                        # Prepare records for insertion
                        skills_to_insert = []
                        for skill in new_offered:
                            skills_to_insert.append({
                                'user_id': user_id,
                                'type': 'offered',
                                'skill': skill
                            })
                        for skill in new_wanted:
                            skills_to_insert.append({
                                'user_id': user_id,
                                'type': 'wanted',
                                'skill': skill
                            })
                        
                        # Insert new skills into user_skills table
                        if skills_to_insert:
                            response = db.client.table('user_skills').insert(skills_to_insert).execute()
                            if response.data:
                                # Update session state
                                user['skills_offered'] = current_skills_offered + new_offered
                                user['skills_wanted'] = current_skills_wanted + new_wanted
                                st.session_state["user"] = user
                                st.success("Skills added successfully!")
                                st.rerun()  # Rerun to refresh the displayed skills
                            else:
                                st.error("Failed to add skills to the database.")
                        else:
                            st.info("No new skills to add (all entered skills already exist).")
                except Exception as e:
                    st.error(f"Error adding skills: {str(e)}")

# ----------------------------
# REGISTER PAGE
# ----------------------------
elif menu == "Register":
    st.subheader("Create a New Profile")
    with st.form("register_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        location = st.text_input("Location (Optional)")
        availability = st.selectbox("Availability", ["Mornings", "Evenings", "Weekends"])
        skills_offered = st.text_input("Skills You Offer (comma-separated)")
        skills_wanted = st.text_input("Skills You Want to Learn (comma-separated)")
        is_public = st.checkbox("Make profile public", value=True)
        submit = st.form_submit_button("Register")

    if submit:
        if is_spammy(name + " " + email + " " + skills_offered + " " + skills_wanted):
            st.error("Profile content seems spammy. Please revise.")
        else:
            profile = UserProfile(
                name=name,
                password=password,
                email=email,
                location=location,
                availability=availability,
                is_public=is_public,
                skills_offered=[s.strip() for s in skills_offered.split(",") if s.strip()],
                skills_wanted=[s.strip() for s in skills_wanted.split(",") if s.strip()],
                profile_photo_url=""
            )
            user_id = db.create_user(profile, password)
            if user_id:
                st.success(f"User created with ID: {user_id}")
            else:
                st.error("Registration failed. Try again.")

# ----------------------------
# LOGIN PAGE
# ----------------------------
elif menu == "Login":
    st.subheader("Login to SkillSwap")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")

    if login:
        user = db.authenticate_user(email, password)
        if user:
            st.success(f"Welcome, {user.get('name', 'User')}!")
            st.session_state["user"] = user
        else:
            st.error("Login failed. Check credentials.")

# ----------------------------
# EXPLORE MATCHES
# ----------------------------
elif menu == "Explore Matches":
    st.subheader("Find Skill Matches")
    if "user" not in st.session_state:
        st.warning("Please log in first.")
    else:
        current_user = st.session_state["user"]

        # Safely get skills_wanted
        skills_wanted = current_user.get("skills_wanted", [])
        if not isinstance(skills_wanted, list):
            skills_wanted = []

        all_users = db.get_all_users(exclude_id=current_user.get("id"))
        matches = match_users(skills_wanted, all_users)

        if not matches:
            st.info("No good matches found yet. Try updating your profile.")
        else:
            for match, score in matches:
                st.markdown(f"""
                <div class="match-card">
                    <h3 style="color: #00f5ff; margin-bottom: 1.5rem; font-family: 'Orbitron', monospace; text-shadow: 0 0 15px rgba(0, 245, 255, 0.7);">⚡ {match.get('name', 'Unnamed')}</h3>
                    <p style="color: #ffffff; margin-bottom: 1rem; font-size: 1.1rem;"><strong>📍 Location:</strong> <span style="color: #00ffff;">{match.get('location', 'Unknown')}</span></p>
                    <p style="margin-bottom: 1rem; color: #ffffff; font-size: 1.1rem;"><strong>🛠️ Offers:</strong><br>
                        {' '.join([f'<span class="skill-tag">{skill}</span>' for skill in match.get('skills_offered', [])])}
                    </p>
                    <p style="margin-bottom: 2rem; color: #ffffff; font-size: 1.1rem;"><strong>🎯 Wants:</strong><br>
                        {' '.join([f'<span class="skill-tag">{skill}</span>' for skill in match.get('skills_wanted', [])])}
                    </p>
                    <div style="text-align: center;">
                        <span class="match-score">🚀 Match Score: {round(score * 100, 2)}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ----------------------------
# BROWSE ALL PUBLIC PROFILES
# ----------------------------
elif menu == "Browse Skills":
    st.subheader("🌍 Explore Public Skill Profiles")
    search_query = st.text_input("Search by Skills (comma-separated, e.g., Python, Design)")
    users = db.get_all_users()
    public_users = [u for u in users if u.get("is_public", False)]

    # Filter users based on search query
    if search_query:
        search_terms = [term.strip().lower() for term in search_query.split(",") if term.strip()]
        filtered_users = []
        for user in public_users:
            skills_offered = [s.lower() for s in user.get("skills_offered", [])]
            skills_wanted = [s.lower() for s in user.get("skills_wanted", [])]
            if any(term in skills_offered or term in skills_wanted for term in search_terms):
                filtered_users.append(user)
        public_users = filtered_users

    if not public_users:
        st.info("No public profiles match your search.")
    else:
        for user in public_users:
            profile_photo_url = user.get("profile_photo_url", None)
            photo_html = f'<img src="{profile_photo_url}" class="profile-photo" alt="Profile Photo">' if profile_photo_url else '<div style="width: 150px; height: 150px; border-radius: 50%; background: rgba(0, 245, 255, 0.2); margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center; color: #00f5ff; font-family: \'Orbitron\', monospace; text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);">No Photo</div>'
            st.markdown(f"""
            <div class="profile-card">
                {photo_html}
                <h3 style="color: #00f5ff; margin-bottom: 1.5rem; font-family: 'Orbitron', monospace; text-shadow: 0 0 15px rgba(0, 245, 255, 0.7);">🎯 {user.get('name', 'Unnamed')}</h3>
                <p style="color: #ffffff; margin-bottom: 1rem; font-size: 1.1rem;"><strong>📍 Location:</strong> <span style="color: #00ffff;">{user.get('location', 'Unknown')}</span></p>
                <p style="margin-bottom: 1rem; color: #ffffff; font-size: 1.1rem;"><strong>🛠️ Offers:</strong><br>
                    {' '.join([f'<span class="skill-tag">{skill}</span>' for skill in user.get('skills_offered', [])])}
                </p>
                <p style="margin-bottom: 1rem; color: #ffffff; font-size: 1.1rem;"><strong>🎯 Wants:</strong><br>
                    {' '.join([f'<span class="skill-tag">{skill}</span>' for skill in user.get('skills_wanted', [])])}
                </p>
                <p style="color: #00ff00; font-weight: 600; text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);"><strong>🕒 Availability:</strong> {user.get('availability', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)