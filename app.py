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

delay_reasons_per_stage = {
    "Order Placed": ["Customer funds unavailable", "Incorrect order format"],
    "Processing": ["Manual truncation required", "System error"],
    "FO Created": ["Dock unavailable", "FO approval pending"],
    "Dispatched": ["Truck mismatch", "Underload detected"],
    "In Transit": ["GPS lost", "Route blocked", "No entry window"],
    "Delivered": ["POD delay", "Customer unavailable", "CD weekly off"]
}

if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 0
if 'delays' not in st.session_state:
    st.session_state.delays = {stage: [] for stage in stages}
if 'fixes' not in st.session_state:
    st.session_state.fixes = []
if 'delay_index' not in st.session_state:
    st.session_state.delay_index = 0

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

if st.session_state.current_stage < len(stages):
    current_stage_name = stages[st.session_state.current_stage]
    stage_reasons = delay_reasons_per_stage[current_stage_name]

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Next Delay / Initialize Delay"):
            if st.session_state.delay_index < len(stage_reasons):
                next_reason = stage_reasons[st.session_state.delay_index]
                st.session_state.delays[current_stage_name].append(next_reason)
                st.session_state.delay_index += 1

    with col2:
        if st.button("Apply Fix"):
            if st.session_state.delay_index > 0:
                last_reason = stage_reasons[st.session_state.delay_index - 1]
                st.session_state.fixes.append(f"Fix applied for: {last_reason} at {current_stage_name}")
                st.session_state.delays[current_stage_name].remove(last_reason)
                st.session_state.delay_index -= 1

            if st.session_state.delay_index == 0:
                st.session_state.current_stage += 1
                st.session_state.delay_index = 0
else:
    st.success("✅ Order Successfully Delivered!")

if st.button("🔄 Reset Simulation"):
    st.session_state.current_stage = 0
    st.session_state.delays = {stage: [] for stage in stages}
    st.session_state.fixes = []
    st.session_state.delay_index = 0
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
