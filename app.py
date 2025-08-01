import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="wide")

# Initialize session state
if 'order_placed' not in st.session_state:
    st.session_state.order_placed = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 0
if 'delays' not in st.session_state:
    st.session_state.delays = {}
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
if 'stage_messages' not in st.session_state:
    st.session_state.stage_messages = {}
if 'actions_per_stage' not in st.session_state:
    st.session_state.actions_per_stage = {}

stages = ["Order processing", "FO and vehicle placement", "In Transit", "Reached Customer"]

for stage in stages:
    if stage not in st.session_state.delays:
        st.session_state.delays[stage] = []
    if stage not in st.session_state.actions_per_stage:
        st.session_state.actions_per_stage[stage] = 0


if not st.session_state.order_placed:
    st.markdown("""
        <div style='text-align: center; padding-top: 100px;'>
            <h1 style='font-size: 48px;'>Welcome to Nestlé</h1>
            <p style='font-size: 20px;'>Would you like to place an order?</p>
            <form action="" method="post">
                <button style='padding: 15px 30px; font-size: 20px; background-color: #ff4b4b; color: white; border: none; border-radius: 8px; cursor: pointer;' type='submit' name='place_order'>PLACE ORDER</button>
            </form>
        </div>
    """, unsafe_allow_html=True)

    if st.form_submit_button("place_order"):
        st.session_state.order_placed = True
        st.experimental_rerun()

else:
    st.title("🚚 Order to Delivery (O2D) Simulation Interface")
    st.markdown("""
    Simulate an order as it moves through the supply chain stages. Encounter delays and apply fixes to ensure timely delivery.
    """)

    st.divider()

    st.markdown("### 🚦 Stagewise Progress")
    cols = st.columns(len(stages))

    for i, stage in enumerate(stages):
        with cols[i]:
            box_style = "font-size:13px; padding: 6px; margin-bottom: 4px;"
            if i < st.session_state.current_stage:
                st.markdown(f'<div style="background-color:#d4edda; border:1px solid #c3e6cb; border-radius:5px; {box_style}"><strong>{stage}</strong></div>', unsafe_allow_html=True)
            elif i == st.session_state.current_stage:
                st.markdown(f'<div style="background-color:#fff3cd; border:1px solid #ffeeba; border-radius:5px; {box_style}"><strong>{stage}</strong></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background-color:#d1ecf1; border:1px solid #bee5eb; border-radius:5px; {box_style}"><strong>{stage}</strong></div>', unsafe_allow_html=True)

            if stage in st.session_state.stage_messages:
                st.info(st.session_state.stage_messages[stage])

            for reason in st.session_state.delays[stage]:
                st.error(f"⏱️ Delay: {reason}")
            for reason in st.session_state.fixed_delays:
                if reason[0] == stage:
                    st.warning(f"✅ Fixed: {reason[1]}")

    st.divider()

    st.markdown("### 📉 Simulation Summary")
    total_time = int(time.time() - st.session_state.start_time)
    total_actions = sum(st.session_state.actions_per_stage.values())

    st.markdown(f"""
        <div style="border: 1.5px solid #4CAF50; border-radius: 8px; padding: 10px 15px; background-color: #f9fff9;">
            <div style="display: flex; justify-content: space-between; font-size: 14px;">
                <div><strong>⏱️ Time:</strong> {total_time}s</div>
                <div><strong>🛠️ Actions:</strong> {total_actions}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    if not st.session_state.order_complete:
        if st.session_state.current_stage < len(stages):
            current_stage_name = stages[st.session_state.current_stage]
            stage_reasons = {
                "Order processing": ["Customer funds unavailable", "Stock shortage", "Incorrect Material"],
                "FO and vehicle placement": ["Vehicle Unavailable", "Dock waiting", "Underload"],
                "In Transit": ["No entry window", "Traffic/Road blocks"],
                "Reached Customer": ["CD weekly off", "Unloading Delayed", "POD entry delayed"]
            }[current_stage_name]

            if st.button("🚀 PROCEED"):
                st.session_state.actions_per_stage[current_stage_name] += 1

                if st.session_state.delay_index < len(stage_reasons):
                    next_reason = stage_reasons[st.session_state.delay_index]
                    st.session_state.delays[current_stage_name].append(next_reason)
                    st.session_state.all_delays_encountered.append((current_stage_name, next_reason))
                    st.session_state.delay_index += 1
                elif st.session_state.delays[current_stage_name]:
                    fixed_reason = st.session_state.delays[current_stage_name].pop(0)
                    st.session_state.fixes.append(f"Fix applied for: {fixed_reason} at {current_stage_name}")
                    st.session_state.fixed_delays.add((current_stage_name, fixed_reason))
                else:
                    st.session_state.stage_messages[current_stage_name] = {
                        0: "📄 OBD Created",
                        1: "🚛 Vehicle Dispatched",
                        2: "📍 Reached Location",
                        3: "📦 Delivery Completed"
                    }[st.session_state.current_stage]
                    st.session_state.current_stage += 1
                    st.session_state.delay_index = 0

                    if st.session_state.current_stage == len(stages):
                        st.session_state.delivered = True
                        st.session_state.order_complete = True
                        st.success("✅ Order Successfully Delivered!")

    else:
        if st.button("🔄 Reset Simulation"):
            for key in st.session_state.keys():
                del st.session_state[key]
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
