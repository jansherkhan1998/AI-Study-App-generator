"""UI Components and CSS layout styling module."""

import streamlit as st


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
            color: #e0e0e0;
        }
        .card-container {
            background-color: #1a1f2c;
            border: 1px solid #2d3748;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .metric-card {
            background-color: #242c3d;
            border-left: 4px solid #63b3ed;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }
        section[data-testid="stSidebar"] {
            background-color: #131722;
            border-right: 1px solid #2d3748;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str):
    st.markdown(
        f"""
        <div class="metric-card">
            <h4 style="margin:0; color:#a0aec0;">{label}</h4>
            <h2 style="margin:5px 0 0 0; color:#63b3ed;">{value}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
