import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="wide")

# Session states for controlling welcome screen
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

    # Stage info
    stages = ["Order processing", "FO and vehicle placement", "In Transit", "Reached Customer"]
    stage_completion_messages = ["OBD Created", "Vehicle Dispatched", "Reached Location", "Delivery Completed"]

    delay_reasons_per_stage = {
        "Order processing": ["Customer funds unavailable", "Stock shortage", "Incorrect Material code", "Large order qty"],
        "FO and vehicle placement": ["Vehicle Unavailable", "Dock waiting", "Underload"],
        "In Transit": ["No entry window", "Traffic/Road blocks"],
        "Reached Customer": ["CD weekly off", "Unloading Delayed", "POD entry delayed"]
    }
    delay_action_messages = {
        "Customer funds unavailable": "NEED TO WAIT UNTIL FUNDS REFLECT/CREATE MANUAL OBD LATER",
        "Stock shortage": "ORDER QTY CHANGE- CSA",
        "Incorrect Material code": "VB11 TO BE PERFORMED/ MANUALLY CHANGE CODE",
        "Vehicle Unavailable": "NEED TO WAIT/ CALL UP FOR VEHICLE MANUALLY",
        "Dock waiting": "WAITING TILL DOCK IS FREE",
        "Underload": "WAITING TILL CLUB LOAD/ MANUALLY DROP QTY IF LESS",
        "No entry window": "NEED TO WAIT AT CITY ENTRY POINT (IDLING)",
        "Traffic/Road blocks": "DELAY ENCOUNTERED",
        "CD weekly off": "WAIT FOR ANOTHER DAY",
        "Unloading Delayed": "WAIT TILL CD UNLOADS",
        "POD entry delayed": "ENTER POD MANUALLY (TPO OR SDS)",
        "Large order qty": "SOOC TO BE PERFORMED"
    }
    action_taken = {
        "Customer funds unavailable": "Wait complete and funds got reflected",
        "Stock shortage": "CSA changed the order quantity in SAP",
        "Incorrect Material code": "VB11 completed",
        "Vehicle Unavailable": "vehicle called and and vehicle made available after waiting",
        "Dock waiting": "Dock free and dock in complete for the vehicle",
        "Underload": "waiting complete, Order qty dropped/ Club load created for the same route",
        "No entry window": "Waited at entry",
        "Traffic/Road blocks": "Waiting complete",
        "CD weekly off": "One day vehicle detention taken",
        "Unloading Delayed": "Unloading completion delayed",
        "POD entry delayed": "POD captured from a manual entry in SDS or TPO",
        "Large order qty": "SOO completed and order split"
    }
    touch_count = {
        "Customer funds unavailable": 1,
        "Stock shortage": 1,
        "Incorrect Material code": 1,
        "Vehicle Unavailable": 1,
        "Dock waiting": 0,
        "Underload": 1,
        "No entry window": 0,
        "Traffic/Road blocks": 0,
        "CD weekly off": 0,
        "Unloading Delayed": 0,
        "POD entry delayed": 1,
        "Large order qty": 1
    }
    delay_times = {
        "Customer funds unavailable": 3,
        "Stock shortage": 2,
        "Incorrect Material code": 2,
        "Vehicle Unavailable": 4,
        "Dock waiting": 2,
        "Underload": 4,
        "No entry window": 8,
        "Traffic/Road blocks": 3,
        "CD weekly off": 24,
        "Unloading Delayed": 4,
        "POD entry delayed": 4,
        "Large order qty": 1
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
    if 'stage_milestones' not in st.session_state:
        st.session_state.stage_milestones = {}
    if 'cumulative_time' not in st.session_state:
        st.session_state.cumulative_time = 0

    st.divider()

    st.subheader("📦 Current Order Status")
    cols = st.columns(len(stages))
    for i, stage in enumerate(stages):
        with cols[i]:
            # Stage box (spanning full width)
            if i < st.session_state.current_stage:
                st.success(stage)
                if i in st.session_state.stage_milestones:
                    st.markdown(
                        f"<div style='text-align:center; font-weight:bold; color:green;'>{st.session_state.stage_milestones[i]}</div>",
                        unsafe_allow_html=True
                    )
            elif i == st.session_state.current_stage:
                st.warning(stage)
            else:
                st.info(stage)
        
            # Paired display of reason and delay info
            for reason in delay_reasons_per_stage[stage]:
                encountered = (stage, reason) in st.session_state.all_delays_encountered
                fixed = (stage, reason) in st.session_state.fixed_delays
        
                left, right = st.columns([2, 1])  # side-by-side row per delay reason
        
                with left:
                    if encountered:
                        action = action_taken.get(reason, "")
                        issue_html = f"""
                        <div style='padding:10px; background-color:#fff3cd; border-radius:8px; border:1px solid #ffeeba;'>
                            <div style='color:red; font-weight:bold;'>⚠️ ISSUE: {reason}</div>
                        """
                        if fixed:
                            issue_html += f"""
                            <div style='color:green; font-weight:bold;'>✅ Fixed: {action}</div>
                            """
                        issue_html += "</div>"
                        st.markdown(issue_html, unsafe_allow_html=True)


        
                with right:
                    if encountered:
                        delay = delay_times.get(reason, "-")
                        touches = touch_count.get(reason, "-")
                        st.markdown(
                            f"""
                            <div style='padding:8px; background-color:#f0f2f6; border-radius:8px; text-align:center;'>
                                <div><b>Delay:</b> {delay} hrs</div>
                                <div><b>Touches:</b> {touches}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )



    progress_value = min((st.session_state.current_stage + 1) / len(stages), 0.999)
    st.progress(progress_value)

    if st.session_state.show_fix_ui and st.session_state.current_delay:
        stage, reason = st.session_state.current_delay
        col1, col2 = st.columns(2)

        with col1:
            st.error(f"""
            ### ⏱️ Delay encountered: {reason}
            #### 🛠 TAKE ACTION
            {delay_action_messages[reason]}
            """)
    
        with col2:
            st.info(f"""
            ### ⏱️ Delay         :     {delay_times[reason]} hrs  
        
            ### 👤 Touchpoints   :     {touch_count[reason]}
            """)

           
        if st.button("✅ Fix the issue and take required action"):
            st.session_state.fixes.append(f"Fix applied for: {reason} at {stage}")
            st.session_state.fixed_delays.add((stage, reason))
            st.session_state.actions_per_stage[stage] += touch_count[reason]
            st.session_state.time_per_stage[stage] += delay_times[reason]
            st.session_state.cumulative_time += delay_times[reason]
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
                st.session_state.stage_milestones[st.session_state.current_stage] = stage_completion_messages[st.session_state.current_stage]
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
            stage_reasons = delay_reasons_per_stage[current_stage_name]

            if st.session_state.delay_index < len(stage_reasons):
                next_reason = stage_reasons[st.session_state.delay_index]
                st.session_state.delays[current_stage_name].append(next_reason)
                st.session_state.all_delays_encountered.append((current_stage_name, next_reason))
                st.session_state.current_delay = (current_stage_name, next_reason)
                st.session_state.show_fix_ui = True
                st.session_state.delay_index += 1
                st.rerun()

    if st.session_state.order_complete:
        if st.button("🔄 Reset Simulation"):
            st.session_state.order_started = False
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
            st.session_state.stage_milestones = {}
            st.session_state.cumulative_time = 0
            st.rerun()

    st.divider()
    total_time = int(time.time() - st.session_state.start_time)
    total_actions = sum(st.session_state.actions_per_stage.values())

    st.markdown("""
        <div style='border:2px solid #4CAF50; border-radius:10px; padding:15px; background-color:#f9f9f9;'>
            <h4>📊 Simulation Summary</h4>
            <div style='display:flex; justify-content:space-between;'>
                <div style='flex:1; text-align:center;'>
                    <h5>⏱️ Total Time Elapsed (HRS)</h5>
                    <p style='font-size:24px; font-weight:bold;'>""" + str(st.session_state.cumulative_time) + """</p>
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
            st.metric("Time (HRS)", int(st.session_state.time_per_stage[stage]))
            st.metric("Actions", st.session_state.actions_per_stage[stage])
    st.divider()
