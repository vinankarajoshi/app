import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="centered")

# Session state initialization
if "current_stage" not in st.session_state:
    st.session_state.current_stage = 0
    st.session_state.delays = {}
    st.session_state.fixed_delays = set()
    st.session_state.actions_per_stage = {}
    st.session_state.stage_start_time = time.time()
    st.session_state.total_actions = 0
    st.session_state.total_time = 0
    st.session_state.delivered = False
    st.session_state.show_fix_ui = False
    st.session_state.current_delay = None

# Define stages and sample delays
stages = ["Order Received", "Packed", "Shipped", "Delivered"]
delay_data = {
    "Order Received": ["Incorrect SKU code", "Out of stock"],
    "Packed": ["Missing labels"],
    "Shipped": ["Vehicle breakdown", "Address not found"],
    "Delivered": []
}

# Initialize delay and action data per stage
for stage in stages:
    st.session_state.delays.setdefault(stage, delay_data.get(stage, []))
    st.session_state.actions_per_stage.setdefault(stage, 0)

# Stats tracker
with st.container():
    cols = st.columns(len(stages) + 1)
    total_actions = sum(st.session_state.actions_per_stage.values())
    total_time = int(time.time() - st.session_state.stage_start_time)
    cols[0].metric("Total Actions", total_actions)
    for i, stage in enumerate(stages):
        actions = st.session_state.actions_per_stage[stage]
        cols[i+1].metric(f"{stage}", actions)

# Get current stage
if st.session_state.current_stage < len(stages):
    stage = stages[st.session_state.current_stage]
else:
    stage = "Completed"

# Show delay block with fix button if delay exists and hasn't been fixed
if st.session_state.current_stage < len(stages):
    st.subheader(f"Current Stage: {stage}")
    if st.session_state.show_fix_ui:
        reason = st.session_state.current_delay
        with st.container():
            st.markdown("""
                <div style='background-color: #ffe6e6; padding: 20px; border-radius: 10px; border-left: 6px solid red;'>
                    <h4>🚨 Delay Encountered</h4>
                    <b>Reason:</b> {reason}<br><br>
                    <b>Take Action:</b> Please resolve the issue before proceeding.
                </div>
            """.format(reason=reason), unsafe_allow_html=True)
            if st.button("✅ Fix this"):
                st.session_state.fixed_delays.add((stage, reason))
                st.session_state.actions_per_stage[stage] += 1
                st.session_state.show_fix_ui = False
                st.session_state.current_delay = None
                st.rerun()
    else:
        # Show delay notice one-by-one
        for reason in st.session_state.delays[stage]:
            if (stage, reason) not in st.session_state.fixed_delays:
                st.session_state.current_delay = reason
                st.session_state.show_fix_ui = True
                st.rerun()
                break
        else:
            # All delays are fixed for this stage
            if st.button("🚀 Proceed to next stage"):
                st.session_state.current_stage += 1
                st.session_state.stage_start_time = time.time()
                st.rerun()
else:
    st.success("🎉 Order Delivered Successfully!")
    if st.button("🔁 Restart Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
