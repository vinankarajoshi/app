import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="wide")

# Initialize session state
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 0
    st.session_state.stage_start_time = time.time()
    st.session_state.total_actions = 0
    st.session_state.total_start_time = time.time()
    st.session_state.stage_stats = [
        {'name': 'Order Placement', 'time': 0, 'actions': 0},
        {'name': 'Warehouse Processing', 'time': 0, 'actions': 0},
        {'name': 'In-Transit', 'time': 0, 'actions': 0},
        {'name': 'Delivery', 'time': 0, 'actions': 0},
    ]
    st.session_state.delays = [
        {'reason': 'Order verification failed', 'action': 'Verify order details with customer'},
        {'reason': 'Stock not available', 'action': 'Initiate stock transfer from nearby warehouse'},
        {'reason': 'Vehicle breakdown', 'action': 'Arrange alternate transport'},
        {'reason': 'Customer unavailable at delivery', 'action': 'Reschedule delivery'},
    ]
    st.session_state.delay_index = 0
    st.session_state.simulation_complete = False

# Track time and actions
current_time = time.time()
elapsed_total = int(current_time - st.session_state.total_start_time)

# Header stats
st.markdown("## 📦 Order to Delivery Simulation")

cols = st.columns([2, 2, 6])
cols[0].metric("Total Time Elapsed (s)", elapsed_total)
cols[1].metric("Total Actions Taken", st.session_state.total_actions)

# Section-wise stats
col_stats = st.columns(4)
for i, stats in enumerate(st.session_state.stage_stats):
    col_stats[i].markdown(f"### {stats['name']}")
    col_stats[i].metric("Time (s)", int(stats['time']))
    col_stats[i].metric("Actions", stats['actions'])

# Current stage display
if not st.session_state.simulation_complete:
    stage = st.session_state.current_stage
    st.markdown(f"## ▶️ Stage {stage+1}: {st.session_state.stage_stats[stage]['name']}")

    # Simulate delay for this stage if any left
    if st.session_state.delay_index < len(st.session_state.delays):
        delay = st.session_state.delays[st.session_state.delay_index]
        with st.container(border=True):
            st.markdown("## ❗ Delay Encountered:")
            st.markdown(f"**Reason:** {delay['reason']}")
            st.markdown("### 🛠️ TAKE ACTION")
            st.markdown(f"{delay['action']}")

            fix = st.button("Fix Issue", key=f"fix_{st.session_state.delay_index}")
            if fix:
                # Update time for current stage
                now = time.time()
                elapsed = now - st.session_state.stage_start_time
                st.session_state.stage_stats[stage]['time'] += elapsed
                st.session_state.stage_stats[stage]['actions'] += 1
                st.session_state.total_actions += 1
                st.session_state.stage_start_time = now

                # Move to next delay (and possibly next stage)
                st.session_state.delay_index += 1
                if st.session_state.delay_index % 1 == 0 and st.session_state.delay_index // 1 > stage:
                    st.session_state.current_stage += 1
                    st.session_state.stage_start_time = now

                # Complete simulation
                if st.session_state.current_stage >= len(st.session_state.stage_stats):
                    st.session_state.simulation_complete = True
                st.experimental_rerun()
    else:
        st.session_state.simulation_complete = True
        st.experimental_rerun()

else:
    st.success("✅ Simulation Complete!")
    total_elapsed = int(time.time() - st.session_state.total_start_time)
    st.markdown(f"### ⏱️ Total Time: {total_elapsed} seconds")
    st.markdown(f"### 🔢 Total Actions Taken: {st.session_state.total_actions}")
