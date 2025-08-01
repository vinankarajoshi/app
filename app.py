import streamlit as st
import time

st.set_page_config(page_title="O2D Simulation", layout="wide")

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
if 'show_fix_prompt' not in st.session_state:
    st.session_state.show_fix_prompt = False
if 'last_delay_reason' not in st.session_state:
    st.session_state.last_delay_reason = ""

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

# Feedback placeholder
feedback_placeholder = st.empty()

if not st.session_state.order_complete:
    if st.session_state.current_stage < len(stages):
        current_stage_name = stages[st.session_state.current_stage]
        stage_reasons = delay_reasons_per_stage[current_stage_name]

        if st.session_state.show_fix_prompt:
            with st.container():
                st.markdown("""
                    <div style='padding: 2rem; margin: 2rem auto; background-color: #fff3f3; border: 2px solid red; border-radius: 10px; text-align: center; width: 60%;'>
                        <h2>⏱️ Delay Encountered</h2>
                        <p style='font-size: 1.2rem;'>""" + st.session_state.last_delay_reason + """</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button("✅ FIX THIS"):
                    fixed_reason = st.session_state.delays[current_stage_name].pop(0)
                    st.session_state.fixes.append(f"Fix applied for: {fixed_reason} at {current_stage_name}")
                    st.session_state.fixed_delays.add((current_stage_name, fixed_reason))
                    feedback_placeholder.success(f"🔧 Fix applied: {fixed_reason}")
                    st.session_state.show_fix_prompt = False

        elif st.button("🚀 PROCEED"):
            if st.session_state.delay_index < len(stage_reasons):
                next_reason = stage_reasons[st.session_state.delay_index]
                st.session_state.delays[current_stage_name].append(next_reason)
                st.session_state.all_delays_encountered.append((current_stage_name, next_reason))
                st.session_state.delay_index += 1
                st.session_state.last_delay_reason = next_reason
                st.session_state.show_fix_prompt = True
            else:
                st.session_state.current_stage += 1
                st.session_state.delay_index = 0
                if st.session_state.current_stage == len(stages):
                    st.session_state.delivered = True
                    st.session_state.order_complete = True
                    st.success("✅ Order Successfully Delivered!")
                    feedback_placeholder.success("🎉 Order has been delivered! Click button again to reset.")
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
        st.session_state.show_fix_prompt = False
        st.session_state.last_delay_reason = ""
        st.rerun()

st.divider()
