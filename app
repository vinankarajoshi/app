import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="wide")

st.title("🚚 Order to Delivery (O2D) Simulation Interface")

st.markdown("""
Simulate an order as it moves through the supply chain stages. Encounter delays and apply fixes to ensure timely delivery.
""")

st.divider()

st.subheader("📦 Current Stage")
stages = ["Order Placed", "Processing", "FO Created", "Dispatched", "In Transit", "Delivered"]
delay_reasons = [
    "Customer funds unavailable",
    "Manual truncation required",
    "Dock unavailable",
    "Truck mismatch",
    "GPS lost",
    "POD delay"
]

if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 0
if 'delays' not in st.session_state:
    st.session_state.delays = []
if 'fixes' not in st.session_state:
    st.session_state.fixes = []

stage = stages[st.session_state.current_stage]
st.progress((st.session_state.current_stage + 1) / len(stages))
st.info(f"Stage: {stage}")

if st.session_state.current_stage < len(stages) - 1:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Advance to Next Stage"):
            from random import random
            if random() < 0.4:
                delay = delay_reasons[st.session_state.current_stage]
                st.session_state.delays.append((stage, delay))
                st.warning(f"⏱️ Delay at {stage}: {delay}")
            else:
                st.session_state.current_stage += 1

    with col2:
        if st.button("Apply Fix & Proceed"):
            st.session_state.fixes.append(f"Fix applied at {stage}")
            st.session_state.current_stage += 1

else:
    st.success("✅ Order Successfully Delivered!")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("❌ Delays Encountered")
    if st.session_state.delays:
        for stage, reason in st.session_state.delays:
            st.write(f"- **{stage}**: {reason}")
    else:
        st.write("No delays so far.")

with col2:
    st.subheader("🔧 Fixes Applied")
    if st.session_state.fixes:
        for fix in st.session_state.fixes:
            st.write(f"- {fix}")
    else:
        st.write("No fixes applied yet.")
