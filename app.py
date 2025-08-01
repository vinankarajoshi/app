import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="wide")

if 'order_started' not in st.session_state:
    st.session_state.order_started = False

if not st.session_state.order_started:
    st.title("👋 Welcome to Nestlé's O2D Simulator")
    st.markdown("""
        This simulation helps you visualize the journey of an order through Nestlé's supply chain.
    """)
    if st.button("📦 PLACE ORDER"):
        st.session_state.order_started = True
        st.rerun()
else:
    st.title("🚚 Order to Delivery (O2D) Simulation Interface")

    st.markdown("""
    Simulate an order as it moves through the supply chain stages. Encounter delays and apply fixes to ensure timely delivery.
    """)

    st.divider()

    st.subheader("📦 Current Order Status")
    stages = ["Order processing", "FO and vehicle placement", "In Transit", "Reached Customer"]

    delay_reasons_per_stage = {
        "Order processing": ["Customer funds unavailable", "Stock shortage", "Incorrect Material"],
        "FO and vehicle placement": ["Vehicle Unavailable", "Dock waiting", "Underload"],
        "In Transit": ["No entry window", "Traffic/Road blocks"],
        "Reached Customer": ["CD weekly off", "Unloading Delayed", "POD entry delayed"]
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

    # Progress bar
    progress_value = min((st.session_state.current_stage + 1) / len(stages), 0.999)
    st.progress(progress_value)

    if not st.session_state.order_complete:
        if st.session_state.current_stage < len(stages):
            current_stage_name = stages[st.session_state.current_stage]
            stage_reasons = delay_reasons_per_stage[current_stage_name]

            if st.button("🚀 PROCEED"):
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
                    st.session_state.current_stage += 1
                    st.session_state.delay_index = 0
                    if st.session_state.current_stage == len(stages):
                        st.session_state.delivered = True
                        st.session_state.order_complete = True
                        st.success("✅ Order Successfully Delivered!")
    else:
        if st.button("🔄 Reset Simulation"):
            st.session_state.current_stage = 0
            st.session_state.delays = {stage: [] for stage in stages}
            st.session_state.fixes = []
            st.session_state.delay_index = 0
            st.session_state.all_delays_encountered = []
            st.session_state.delivered = False
            st.session_state.order_complete = False
            st.session_state.fixed_delays = set()
            st.session_state.order_started = False
            st.rerun()

    st.divider()
