import streamlit as st
import time
from collections import defaultdict

st.set_page_config(page_title="O2D Simulation", layout="wide")

# Data-driven delay configuration
delays_per_stage = {
    "Order processing": [
        {
            "reason": "Customer funds unavailable",
            "action": "Contact customer to confirm fund availability.",
            "lag": 5,
            "touchpoints": 1,
            "solved_message": "Funds confirmed"
        },
        {
            "reason": "Stock shortage",
            "action": "Check alternate warehouses or postpone order.",
            "lag": 8,
            "touchpoints": 2,
            "solved_message": "Stock arranged"
        }
    ],
    "FO and vehicle placement": [
        {
            "reason": "Vehicle Unavailable",
            "action": "Engage with alternate transporter.",
            "lag": 6,
            "touchpoints": 1,
            "solved_message": "Vehicle arranged"
        },
        {
            "reason": "Dock waiting",
            "action": "Contact CD manager to free up dock slot.",
            "lag": 4,
            "touchpoints": 1,
            "solved_message": "Dock cleared"
        }
    ],
    "In Transit": [
        {
            "reason": "Traffic/Road blocks",
            "action": "Reroute shipment using GPS alternatives.",
            "lag": 10,
            "touchpoints": 1,
            "solved_message": "Route cleared"
        }
    ],
    "Reached Customer": [
        {
            "reason": "CD weekly off",
            "action": "Reschedule delivery to next working day.",
            "lag": 4,
            "touchpoints": 1,
            "solved_message": "Delivery rescheduled"
        }
    ]
}

# Session states
if 'order_started' not in st.session_state:
    st.session_state.order_started = False
if not st.session_state.order_started:
    st.markdown("""
        <div style='text-align:center;'>
            <h1 style='font-size:60px;'>👋 Welcome to Nestlé's O2D Simulation</h1>
            <p style='font-size:48px;'>Would you like to place an order?</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("📦 PLACE ORDER"):
        st.session_state.order_started = True
        st.rerun()
else:
    st.title("🚚 Order to Delivery (O2D) Simulation Interface")

    stages = list(delays_per_stage.keys())
    stage_completion_messages = ["OBD Created", "Vehicle Dispatched", "Reached Location", "Delivery Completed"]

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
            else:
                st.session_state[key] = 0 if key == 'current_stage' or key == 'delay_index' else False
                
    st.divider()
    st.subheader("📦 Current Order Status")
    cols = st.columns(len(stages))
    for i, stage in enumerate(stages):
        with cols[i]:
            if i < st.session_state.current_stage:
                st.success(stage)
                if i in st.session_state.stage_milestones:
                    st.markdown(f"<div style='text-align:center; font-weight:bold; color:green;'>"
                                f"{st.session_state.stage_milestones[i]}</div>", unsafe_allow_html=True)
            elif i == st.session_state.current_stage:
                st.warning(stage)
            else:
                st.info(stage)

            for delay in delays_per_stage[stage]:
                encountered = (stage, delay["reason"]) in st.session_state.all_delays_encountered
                fixed = (stage, delay["reason"]) in st.session_state.fixed_delays
                if encountered and fixed:
                    st.warning(f"⏱️ Delay: {delay['reason']}\n\n✅ Fixed: {delay['solved_message']}")
                elif encountered:
                    st.error(f"⏱️ Delay: {delay['reason']}")

    progress_value = min((st.session_state.current_stage + 1) / len(stages), 0.999)
    st.progress(progress_value)

    if st.session_state.show_fix_ui and st.session_state.current_delay:
        stage, reason = st.session_state.current_delay
        delay_info = next((d for d in delays_per_stage[stage] if d["reason"] == reason), None)
        if delay_info:
            st.error(f"""
            ### ⏱️ Delay encountered: {reason}
            #### 🛠 TAKE ACTION
            {delay_info['action']}
            (⏱️ Expected delay: {delay_info['lag']}s, 👥 Touchpoints: {delay_info['touchpoints']})
            """)
            if st.button("✅ Fix the issue and take required action"):
                st.session_state.fixes.append(f"Fix applied for: {reason} at {stage}")
                st.session_state.fixed_delays.add((stage, reason))
                st.session_state.actions_per_stage[stage] += 1
                st.session_state.show_fix_ui = False
                st.session_state.current_delay = None

                stage_delays = delays_per_stage[stage]
                if st.session_state.delay_index < len(stage_delays):
                    next_reason = stage_delays[st.session_state.delay_index]["reason"]
                    st.session_state.delays[stage].append(next_reason)
                    st.session_state.all_delays_encountered.append((stage, next_reason))
                    st.session_state.current_delay = (stage, next_reason)
                    st.session_state.show_fix_ui = True
                    st.session_state.delay_index += 1
                else:
                    st.session_state.delay_index = 0
                    st.session_state.stage_milestones[st.session_state.current_stage] = \
                        stage_completion_messages[st.session_state.current_stage]
                    st.session_state.current_stage += 1
                    if st.session_state.current_stage < len(stages):
                        st.session_state.stage_start_time = time.time()
                    else:
                        st.session_state.delivered = True
                        st.session_state.order_complete = True
                        st.success("✅ Order Successfully Delivered!")
                st.rerun()

    if not st.session_state.order_complete and not st.session_state.show_fix_ui:
        if st.button("🚀 PROCEED"):
            current_stage_name = stages[st.session_state.current_stage]
            stage_delays = delays_per_stage[current_stage_name]

            if st.session_state.delay_index < len(stage_delays):
                next_reason = stage_delays[st.session_state.delay_index]["reason"]
                st.session_state.delays[current_stage_name].append(next_reason)
                st.session_state.all_delays_encountered.append((current_stage_name, next_reason))
                st.session_state.current_delay = (current_stage_name, next_reason)
                st.session_state.show_fix_ui = True
                st.session_state.delay_index += 1

                elapsed = time.time() - st.session_state.stage_start_time
                st.session_state.time_per_stage[current_stage_name] += elapsed
                st.session_state.stage_start_time = time.time()
                st.rerun()

    if st.session_state.order_complete:
        if st.button("🔄 Reset Simulation"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.divider()

    total_time = int(time.time() - st.session_state.start_time)
    total_actions = sum(st.session_state.actions_per_stage.values())

    st.markdown("""
        <div style='border:2px solid #4CAF50; border-radius:10px; padding:15px; background-color:#f9f9f9;'>
            <h4>📊 Simulation Summary</h4>
            <div style='display:flex; justify-content:space-between;'>
                <div style='flex:1; text-align:center;'>
                    <h5>⏱️ Total Time Elapsed (s)</h5>
                    <p style='font-size:24px; font-weight:bold;'>""" + str(total_time) + """</p>
                </div>
                <div style='flex:1; text-align:center;'>
                    <h5>🛠️ Total Actions Taken</h5>
                    <p style='font-size:24px; font-weight:bold;'>""" + str(total_actions) + """</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 Stage-wise Progress")
    stage_cols = st.columns(len(stages))
    for i, stage in enumerate(stages):
        with stage_cols[i]:
            st.markdown(f"**{stage}**")
            st.metric("Time (s)", int(st.session_state.time_per_stage[stage]))
            st.metric("Actions", st.session_state.actions_per_stage[stage])

    st.divider()
