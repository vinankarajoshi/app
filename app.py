import streamlit as st
import time
if 'order_started' not in st.session_state:
    st.session_state.order_started = False

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

st.set_page_config(page_title="O2D Simulation", layout="wide")

# Initialization of session state
if "simulation_started" not in st.session_state:
    st.session_state.simulation_started = False
if "current_stage" not in st.session_state:
    st.session_state.current_stage = 0
if "delays" not in st.session_state:
    st.session_state.delays = {}
if "fixes" not in st.session_state:
    st.session_state.fixes = []
if "delay_index" not in st.session_state:
    st.session_state.delay_index = 0
if "all_delays_encountered" not in st.session_state:
    st.session_state.all_delays_encountered = []
if "delivered" not in st.session_state:
    st.session_state.delivered = False
if "order_complete" not in st.session_state:
    st.session_state.order_complete = False
if "fixed_delays" not in st.session_state:
    st.session_state.fixed_delays = set()
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "stage_start_time" not in st.session_state:
    st.session_state.stage_start_time = time.time()
if "time_per_stage" not in st.session_state:
    st.session_state.time_per_stage = {}
if "actions_per_stage" not in st.session_state:
    st.session_state.actions_per_stage = {}
if "current_delay" not in st.session_state:
    st.session_state.current_delay = None
if "show_fix_ui" not in st.session_state:
    st.session_state.show_fix_ui = False

# Define simulation stages and delay reasons
stages = ["Order processing", "FO and vehicle placement", "In Transit", "Reached Customer"]
delay_reasons_per_stage = {
    "Order processing": ["Customer funds unavailable", "Stock shortage", "Incorrect Material"],
    "FO and vehicle placement": ["Vehicle Unavailable", "Dock waiting", "Underload"],
    "In Transit": ["No entry window", "Traffic/Road blocks"],
    "Reached Customer": ["CD weekly off", "Unloading Delayed", "POD entry delayed"]
}
delay_action_messages = {
    "Customer funds unavailable": "Contact customer to confirm fund availability.",
    "Stock shortage": "Check alternate warehouses or postpone order.",
    "Incorrect Material": "Raise return request and reinitiate FO.",
    "Vehicle Unavailable": "Engage with alternate transporter.",
    "Dock waiting": "Contact CD manager to free up dock slot.",
    "Underload": "Fill with additional load or reschedule delivery.",
    "No entry window": "Wait for next entry slot or apply for special pass.",
    "Traffic/Road blocks": "Reroute shipment using GPS alternatives.",
    "CD weekly off": "Reschedule delivery to next working day.",
    "Unloading Delayed": "Call unloading team to prioritize.",
    "POD entry delayed": "Push for manual POD entry in system."
}

# Start screen
if not st.session_state.simulation_started:
    st.markdown("<h1 style='text-align: center;'>Welcome to Nestlé</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 22px;'>Would you like to place an order?</p>", unsafe_allow_html=True)
    if st.button("🚀 PLACE ORDER", use_container_width=True):
        st.session_state.simulation_started = True
        st.session_state.current_stage = 0
        st.session_state.delays = {stage: [] for stage in stages}
        st.session_state.time_per_stage = {stage: 0 for stage in stages}
        st.session_state.actions_per_stage = {stage: 0 for stage in stages}
        st.rerun()
    st.stop()

# Main simulation UI starts here
st.title("🚚 Order to Delivery (O2D) Simulation Interface")

# Top metrics
total_time = int(time.time() - st.session_state.start_time)
total_actions = sum(st.session_state.actions_per_stage.values())

st.markdown("### 📉 Simulation Summary")
col_total_time, col_total_actions = st.columns(2)
col_total_time.metric("⏱️ Total Time Elapsed (s)", total_time)
col_total_actions.metric("🛠️ Total Actions Taken", total_actions)

# Stage-wise metrics
st.markdown("### 📊 Stage-wise Progress")
stage_cols = st.columns(len(stages))
for i, stage in enumerate(stages):
    with stage_cols[i]:
        st.markdown(f"**{stage}**")
        st.metric("Time (s)", int(st.session_state.time_per_stage[stage]))
        st.metric("Actions", st.session_state.actions_per_stage[stage])

st.divider()

# Order status
st.subheader("📦 Current Order Status")
cols = st.columns(len(stages))
for i, stage in enumerate(stages):
    with cols[i]:
        if i < st.session_state.current_stage:
            st.success(stage)
        elif i == st.session_state.current_stage:
            st.warning(stage)
        else:
            st.info(stage)

        for reason in delay_reasons_per_stage[stage]:
            if (stage, reason) in st.session_state.fixed_delays:
                st.warning(f"✅ Fixed: {reason}")
            elif (stage, reason) in st.session_state.all_delays_encountered:
                st.error(f"⏱️ Delay: {reason}")

progress_value = min((st.session_state.current_stage + 1) / len(stages), 0.999)
st.progress(progress_value)

# Fix UI
if st.session_state.show_fix_ui and st.session_state.current_delay:
    stage, reason = st.session_state.current_delay
    st.error(f"""
    ### ⏱️ Delay encountered: {reason}
    #### 🛠 TAKE ACTION
    {delay_action_messages[reason]}
    """)
    if st.button("✅ Fix this"):
        st.session_state.fixes.append(f"Fix applied for: {reason} at {stage}")
        st.session_state.fixed_delays.add((stage, reason))
        st.session_state.actions_per_stage[stage] += 1
        st.session_state.show_fix_ui = False
        st.session_state.current_delay = None

        # Move to next delay or stage
        stage_reasons = delay_reasons_per_stage[stage]
        if st.session_state.delay_index < len(stage_reasons):
            next_reason = stage_reasons[st.session_state.delay_index]
            st.session_state.delays[stage].append(next_reason)
            st.session_state.all_delays_encountered.append((stage, next_reason))
            st.session_state.current_delay = (stage, next_reason)
            st.session_state.show_fix_ui = True
            st.session_state.delay_index += 1
        else:
            st.session_state.delay_index = 0
            st.session_state.current_stage += 1
            if st.session_state.current_stage < len(stages):
                st.session_state.stage_start_time = time.time()
            else:
                st.session_state.delivered = True
                st.session_state.order_complete = True
                st.success("✅ Order Successfully Delivered!")
                st.toast("🎉 Order has been delivered! Click button again to reset.", icon="✅")

        st.rerun()

# Proceed button
if not st.session_state.order_complete and not st.session_state.show_fix_ui:
    if st.button("➡️ PROCEED TO NEXT EVENT"):
        current_stage_name = stages[st.session_state.current_stage]
        stage_reasons = delay_reasons_per_stage[current_stage_name]

        if st.session_state.delay_index < len(stage_reasons):
            next_reason = stage_reasons[st.session_state.delay_index]
            st.session_state.delays[current_stage_name].append(next_reason)
            st.session_state.all_delays_encountered.append((current_stage_name, next_reason))
            st.session_state.current_delay = (current_stage_name, next_reason)
            st.session_state.show_fix_ui = True
            st.session_state.delay_index += 1

            # Record time
            elapsed = time.time() - st.session_state.stage_start_time
            st.session_state.time_per_stage[current_stage_name] += elapsed
            st.session_state.stage_start_time = time.time()
            st.rerun()

# Reset button
if st.session_state.order_complete:
    if st.button("🔄 Reset Simulation"):
        for var in [
            "simulation_started", "current_stage", "delays", "fixes", "delay_index",
            "all_delays_encountered", "delivered", "order_complete", "fixed_delays",
            "start_time", "stage_start_time", "time_per_stage", "actions_per_stage",
            "current_delay", "show_fix_ui"
        ]:
            if var in st.session_state:
                del st.session_state[var]
        st.rerun()

st.divider()
