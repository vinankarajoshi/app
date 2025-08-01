import streamlit as st
import time
import random

st.set_page_config(page_title="O2D Simulation", layout="wide")

st.title("🚚 Order to Delivery (O2D) Simulation Interface")

st.markdown("""
Simulate an order as it moves through the supply chain stages. Encounter delays and apply fixes to ensure timely delivery.
""")

st.divider()

st.subheader("📦 Current Order Status")
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
    st.session_state.delays = {stage: [] for stage in stages}
if 'fixes' not in st.session_state:
    st.session_state.fixes = []

cols = st.columns(len(stages))

for i, stage in enumerate(stages):
    with cols[i]:
        if i < st.session_state.current_stage:
            st.success(stage)
            for reason in st.session_state.delays[stage]:
                st.error(f"⏱️ Delay: {reason}")
        elif i == st.session_state.current_stage:
            st.warning(stage)
            for reason in st.session_state.delays[stage]:
                st.error(f"⏱️ Delay: {reason}")
        else:
            st.info(stage)

st.progress((st.session_state.current_stage + 1) / len(stages))

if st.session_state.current_stage < len(stages) - 1:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Advance to Next Stage"):
            reasons = random.sample(delay_reasons, k=min(2, len(delay_reasons)))  # multiple reasons per stage
            for reason in reasons:
                st.session_state.delays[stages[st.session_state.current_stage]].append(reason)

    with col2:
        if st.button("Apply Fix & Proceed"):
            st.session_state.fixes.append(f"Fix applied at {stages[st.session_state.current_stage]}")
            st.session_state.current_stage += 1
else:
    st.success("✅ Order Successfully Delivered!")

if st.button("🔄 Reset Simulation"):
    st.session_state.current_stage = 0
    st.session_state.delays = {stage: [] for stage in stages}
    st.session_state.fixes = []
    st.rerun()

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("❌ Delays Encountered")
    any_delay = any(st.session_state.delays[stage] for stage in stages)
    if any_delay:
        for stage in stages:
            for reason in st.session_state.delays[stage]:
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
