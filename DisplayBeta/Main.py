import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import warnings
import time

pages = {
    "Your account": [
        st.Page("stockcompare.py", title="Compare Stocks"),
        st.Page("Test.py", title="Manage your account"),
    ],
    "Resources": [
    ],
}

pg = st.navigation(pages)
pg.run()
