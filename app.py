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
if 'all_delays_encountered' not in st.session_state:
    st.session_state.all_delays_encountered = []
if 'delivered' not in st.session_state:
    st.session_state.delivered = False

cols = st.columns(len(stages))

for i, stage in enumerate(stages):
    with cols[i]:
        if i < st.session_state.current_stage:
            st.success(stage)
            for reason in delay_reasons_per_stage[stage]:
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

    if st.button("🚀 Move to Next Stage / Fix Delay"):
        if st.session_state.delay_index < len(stage_reasons):
            next_reason = stage_reasons[st.session_state.delay_index]
            st.session_state.delays[current_stage_name].append(next_reason)
            st.session_state.all_delays_encountered.append((current_stage_name, next_reason))
            st.session_state.delay_index += 1
        elif st.session_state.delays[current_stage_name]:
            fixed_reason = st.session_state.delays[current_stage_name].pop(0)
            st.session_state.fixes.append(f"Fix applied for: {fixed_reason} at {current_stage_name}")
        else:
            st.session_state.current_stage += 1
            st.session_state.delay_index = 0
            if st.session_state.current_stage == len(stages):
                st.session_state.delivered = True
else:
    if st.session_state.delivered:
        st.success("✅ Order Successfully Delivered!")
        st.toast("🎉 Order has been delivered!")

if st.session_state.delivered:
    if st.button("🔄 Reset Simulation"):
        st.session_state.current_stage = 0
        st.session_state.delays = {stage: [] for stage in stages}
        st.session_state.fixes = []
        st.session_state.delay_index = 0
        st.session_state.all_delays_encountered = []
        st.session_state.delivered = False
        st.rerun()

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("❌ Delays Encountered")
    if st.session_state.all_delays_encountered:
        for stage, reason in st.session_state.all_delays_encountered:
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
