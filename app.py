import streamlit as st
import datetime

st.set_page_config(page_title="O2D Simulation", layout="wide")

# Initialize session state
if 'order_started' not in st.session_state:
    st.session_state.order_started = False
if 'stage' not in st.session_state:
    st.session_state.stage = 0
if 'fix_log' not in st.session_state:
    st.session_state.fix_log = []
if 'current_time' not in st.session_state:
    st.session_state.current_time = datetime.datetime(2025, 8, 1, 9, 0)  # Start time: 9:00 AM

# Delay mapping in hours
delay_mapping = {
    "Customer funds unavailable": 3,
    "Stock shortage": 1,
    "Incorrect Material": 2,
    "Vehicle Unavailable": 4,
    "Dock waiting": 2,
    "Underload": 12,
    "No entry window": 8,
    "Traffic/Road blocks": 3,
    "CD weekly off": 12,
    "Unloading Delayed": 2,
    "POD entry delayed": 5
}

# Welcome screen
if not st.session_state.order_started:
    st.markdown(
        """
        <div style='text-align: center; padding-top: 100px;'>
            <h1 style='font-size: 50px; color: #005F7F;'>👋 Welcome to Nestlé's O2D Simulator</h1>
            <p style='font-size: 20px; color: #333;'>Experience how customer orders are delivered step-by-step</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_space, col_button, col_space2 = st.columns([2, 1, 2])
    with col_button:
        if st.button("📦 PLACE ORDER", use_container_width=True):
            st.session_state.order_started = True
            st.rerun()

    st.stop()

# Define stages and their issues
stages = [
    ("Order Processing", ["Customer funds unavailable", "Stock shortage", "Incorrect Material"]),
    ("FO and Vehicle Placement", ["Vehicle Unavailable", "Dock waiting", "Underload"]),
    ("In Transit", ["No entry window", "Traffic/Road blocks", "CD weekly off"]),
    ("Delivery", ["Unloading Delayed", "POD entry delayed"])
]

st.title("🚚 Order to Delivery (O2D) Simulation Interface")

# Display current simulation time
st.markdown(f"**🕒 Current Simulation Time:** {st.session_state.current_time.strftime('%d-%b-%Y %I:%M %p')}")

# Display stages
for i, (stage_name, issues) in enumerate(stages):
    col = st.columns(1)[0]
    with col:
        st.subheader(f"Step {i+1}: {stage_name}")
        if st.session_state.stage == i:
            for issue in issues:
                if st.button(f"Fix: {issue}", key=f"fix_{i}_{issue}"):
                    delay = delay_mapping.get(issue, 0)
                    st.session_state.current_time += datetime.timedelta(hours=delay)
                    st.session_state.fix_log.append((stage_name, issue, delay))
                    st.rerun()
            if st.button("✅ All Issues Fixed – Proceed", key=f"next_{i}"):
                st.session_state.stage += 1
                st.rerun()
        elif st.session_state.stage > i:
            st.success(f"✅ {stage_name} Completed at {st.session_state.current_time.strftime('%I:%M %p')}")

# Display fix log
if st.session_state.fix_log:
    with st.expander("🛠️ View Fix Log"):
        for stage, issue, delay in st.session_state.fix_log:
            st.write(f"🔧 {issue} in {stage} → +{delay} hrs")

# Final message
if st.session_state.stage >= len(stages):
    st.balloons()
    st.success(f"🎉 Delivery Completed at {st.session_state.current_time.strftime('%d-%b-%Y %I:%M %p')}")
