import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="wide")

st.title("🚚 Order to Delivery (O2D) Simulation Interface")

# Stage info
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

# Session states
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
if 'order_complete' not in st.session_state:
    st.session_state.order_complete = False
if 'fixed_delays' not in st.session_state:
    st.session_state.fixed_delays = set()
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'stage_start_time' not in st.session_state:
    st.session_state.stage_start_time = time.time()
if 'time_per_stage' not in st.session_state:
    st.session_state.time_per_stage = {stage: 0 for stage in stages}
if 'actions_per_stage' not in st.session_state:
    st.session_state.actions_per_stage = {stage: 0 for stage in stages}
if 'current_delay' not in st.session_state:
    st.session_state.current_delay = None
if 'show_fix_ui' not in st.session_state:
    st.session_state.show_fix_ui = False

# Top Metrics
total_time = int(time.time() - st.session_state.start_time)
total_actions = sum(st.session_state.actions_per_stage.values())

st.markdown("### 🔢 Simulation Summary")
col_total_time, col_total_actions = st.columns(2)
col_total_time.metric("⏱️ Total Time Elapsed (s)", total_time)
col_total_actions.metric("🛠️ Total Actions Taken", total_actions)

# Section-wise summary
st.markdown("### 📊 Stage-wise Progress")
stage_cols = st.columns(len(stages))
for i, stage in enumerate(stages):
    with stage_cols[i]:
        st.markdown(f"**{stage}**")
        st.metric("Time (s)", int(st.session_state.time_per_stage[stage]))
        st.metric("Actions", st.session_state.actions_per_stage[stage])

st.divider()

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
        st.session_state.actions_per_stage[stage] += 1  # increment only on fix
        st.session_state.show_fix_ui = False
        st.session_state.current_delay = None

        # Check if all delays are fixed
        if not st.session_state.delays[stage]:
            st.session_state.current_stage += 1
            if st.session_state.current_stage < len(stages):
                st.session_state.stage_start_time = time.time()
            else:
                st.session_state.delivered = True
                st.session_state.order_complete = True
                st.success("✅ Order Successfully Delivered!")
                st.toast("🎉 Order has been delivered! Click button again to reset.", icon="✅")

        st.rerun()

# Proceed Button
if not st.session_state.order_complete and not st.session_state.show_fix_ui:
    if st.button("🚀 PROCEED"):
        current_stage_name = stages[st.session_state.current_stage]
        stage_reasons = delay_reasons_per_stage[current_stage_name]

        if st.session_state.delay_index < len(stage_reasons):
            next_reason = stage_reasons[st.session_state.delay_index]
            st.session_state.delays[current_stage_name].append(next_reason)
            st.session_state.all_delays_encountered.append((current_stage_name, next_reason))
            st.session_state.current_delay = (current_stage_name, next_reason)
            st.session_state.show_fix_ui = True
            st.session_state.delay_index += 1

            # Record time for stage so far
            elapsed = time.time() - st.session_state.stage_start_time
            st.session_state.time_per_stage[current_stage_name] += elapsed
            st.session_state.stage_start_time = time.time()
            st.rerun()

# Reset Button
if st.session_state.order_complete:
    if st.button("🔄 Reset Simulation"):
        st.session_state.current_stage = 0
        st.session_state.delays = {stage: [] for stage in stages}
        st.session_state.fixes = []
        st.session_state.delay_index = 0
        st.session_state.all_delays_encountered = []
        st.session_state.delivered = False
        st.session_state.order_complete = False
        st.session_state.fixed_delays = set()
        st.session_state.start_time = time.time()
        st.session_state.stage_start_time = time.time()
        st.session_state.time_per_stage = {stage: 0 for stage in stages}
        st.session_state.actions_per_stage = {stage: 0 for stage in stages}
        st.session_state.current_delay = None
        st.session_state.show_fix_ui = False
        st.rerun()

st.divider()
