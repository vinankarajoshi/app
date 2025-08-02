import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="wide")

# Define delays and actions per stage
delays_per_stage = {
    0: [
        {"message": "SOH not available", "lag": 10, "touchpoints": 1, "solved_message": "SOH updated in system"},
        {"message": "ATP mismatch", "lag": 15, "touchpoints": 2, "solved_message": "ATP manually aligned"},
    ],
    1: [
        {"message": "Truck not available", "lag": 20, "touchpoints": 1, "solved_message": "Vehicle arranged via alternate vendor"},
        {"message": "Order not prioritized", "lag": 12, "touchpoints": 1, "solved_message": "Customer requested urgent dispatch"},
    ],
    2: [
        {"message": "Vehicle breakdown", "lag": 30, "touchpoints": 2, "solved_message": "Backup vehicle deployed"},
        {"message": "Driver not reachable", "lag": 10, "touchpoints": 1, "solved_message": "Driver contacted via vendor"},
    ],
    3: [
        {"message": "Gate entry delay", "lag": 8, "touchpoints": 1, "solved_message": "Gate pass pre-approved"},
        {"message": "Unloading resource not available", "lag": 14, "touchpoints": 1, "solved_message": "Customer arranged additional manpower"},
    ]
}

stages = ["Order processing", "FO and vehicle placement", "In Transit", "Reached Customer"]
stage_completion_messages = ["OBD Created", "Vehicle dispatched", "Reached location", "Delivery completed"]

# Initialize session states
for key in ['current_stage', 'delays', 'fixes', 'delay_index', 'all_delays_encountered', 'delivered',
            'order_complete', 'fixed_delays', 'start_time', 'stage_start_time', 'time_per_stage',
            'actions_per_stage', 'current_delay', 'show_fix_ui', 'stage_milestones']:
    if key not in st.session_state:
        if key in ['delays', 'time_per_stage', 'actions_per_stage']:
            st.session_state[key] = {stage: [] if key == 'delays' else 0 for stage in stages}
        elif key in ['fixes', 'all_delays_encountered']:
            st.session_state[key] = []
        elif key == 'fixed_delays':
            st.session_state[key] = set()
        elif key in ['start_time', 'stage_start_time']:
            st.session_state[key] = time.time()
        elif key == 'stage_milestones':
            st.session_state[key] = {}
        else:
            st.session_state[key] = 0 if key in ['current_stage', 'delay_index'] else False

if 'order_started' not in st.session_state:
    st.session_state.order_started = False

if not st.session_state.order_started:
    st.title("Welcome to O2D Simulation")
    st.write("This simulation will walk you through the order-to-delivery process with delays and actions.")
    if st.button("Start Simulation"):
        st.session_state.order_started = True
        st.rerun()
else:
    current_stage = st.session_state.current_stage
    if current_stage >= len(stages):
        st.success("✅ Order has been delivered successfully!")
        total_time = int(time.time() - st.session_state.start_time)
        st.write(f"Total simulation time: {total_time} seconds")

        st.write("\n---\n")
        st.subheader("Stage-wise Summary")
        for i, stage in enumerate(stages):
            st.markdown(f"**{stage}:**")
            st.write(f"Time Taken: {st.session_state.time_per_stage[stage]} sec")
            for action in st.session_state.actions_per_stage[stage]:
                st.markdown(f"- {action}")
        st.stop()

    stage_name = stages[current_stage]
    st.header(f"🚚 Stage {current_stage + 1}: {stage_name}")

    cols = st.columns(len(stages))
    for i, col in enumerate(cols):
        if i < current_stage:
            col.success(stage_completion_messages[i])
        elif i == current_stage:
            col.warning("In Progress")
        else:
            col.info("Pending")

    if 'current_delay' not in st.session_state or st.session_state.current_delay == "":
        if st.session_state.delay_index < len(delays_per_stage[current_stage]):
            current_delay_obj = delays_per_stage[current_stage][st.session_state.delay_index]
            st.session_state.current_delay = current_delay_obj["message"]
            st.session_state.current_delay_lag = current_delay_obj["lag"]
            st.session_state.current_touchpoints = current_delay_obj["touchpoints"]
            st.session_state.current_solved_message = current_delay_obj["solved_message"]
            st.session_state.show_fix_ui = True
        else:
            st.session_state.current_delay = ""
            st.session_state.current_delay_lag = 0
            st.session_state.current_touchpoints = 0
            st.session_state.current_solved_message = ""
            st.session_state.show_fix_ui = False

    if st.session_state.show_fix_ui:
        with st.expander("⚠️ Delay Encountered"):
            st.markdown(f"**Delay:** {st.session_state.current_delay}")
            st.markdown(f"**Lag:** {st.session_state.current_delay_lag} min")
            st.markdown(f"**Touchpoints:** {st.session_state.current_touchpoints}")
            if st.button("Fix this"):
                st.session_state.actions_per_stage[stage_name].append(f"✅ {st.session_state.current_solved_message}")
                st.session_state.delay_index += 1
                st.session_state.current_delay = ""
                st.rerun()
    else:
        if st.button("Proceed to next stage"):
            end_time = time.time()
            st.session_state.time_per_stage[stage_name] = int(end_time - st.session_state.stage_start_time)
            st.session_state.stage_start_time = end_time
            st.session_state.stage_milestones[st.session_state.current_stage] = stage_completion_messages[st.session_state.current_stage]
            st.session_state.delay_index = 0
            st.session_state.current_stage += 1
            st.rerun()
