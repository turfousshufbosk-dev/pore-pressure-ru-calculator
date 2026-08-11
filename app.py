import streamlit as st

st.title("孔压比 $r_u$ 计算平台")

st.write("请输入基本参数，计算超孔隙水压力比。")

# 输入参数
sigma_v0 = st.number_input(
    "初始总应力 σv0（kPa）",
    min_value=0.0,
    value=100.0
)

u0 = st.number_input(
    "初始孔隙水压力 u0（kPa）",
    min_value=0.0,
    value=40.0
)

u = st.number_input(
    "当前孔隙水压力 u(t)（kPa）",
    min_value=0.0,
    value=88.0
)

# 计算
sigma_eff0 = sigma_v0 - u0
delta_u = u - u0

if sigma_eff0 > 0:

    ru = delta_u / sigma_eff0

    st.subheader("计算结果")

    st.write(
        f"初始有效应力 σ′v0 = {sigma_eff0:.2f} kPa"
    )

    st.write(
        f"超孔隙水压力 Δu = {delta_u:.2f} kPa"
    )

    st.write(
        f"孔压比 ru = {ru:.3f}"
    )

else:

    st.error(
        "初始有效应力必须大于 0，请检查输入参数。"
    )
