import streamlit as st
import pandas as pd

st.title("孔压比 $r_u$ 计算平台")

st.write("输入土层信息和孔压参数，自动计算超孔隙水压力比。")

# =====================================================
# 1. 输入土层信息
# =====================================================

st.header("1. 土层信息")

default_layers = pd.DataFrame({
    "土层名称": ["填土", "粉质黏土", "粉细砂"],
    "顶深_m": [0.0, 2.0, 4.0],
    "底深_m": [2.0, 4.0, 8.0],
    "重度_kN_m3": [18.0, 18.5, 19.0]
})

layers = st.data_editor(
    default_layers,
    num_rows="dynamic",
    use_container_width=True
)

# =====================================================
# 2. 输入孔压计埋深
# =====================================================

st.header("2. 孔压计信息")

sensor_depth = st.number_input(
    "孔压计埋深（m）",
    min_value=0.1,
    value=6.0,
    step=0.1
)

# =====================================================
# 3. 自动计算初始总应力
# =====================================================

sigma_v0 = 0.0

for _, row in layers.iterrows():

    top = row["顶深_m"]
    bottom = row["底深_m"]
    gamma = row["重度_kN_m3"]

    # 如果该层完全在传感器以下，不计算
    if top >= sensor_depth:
        continue

    # 实际参与计算的底部深度
    effective_bottom = min(bottom, sensor_depth)

    thickness = effective_bottom - top

    if thickness > 0:
        sigma_v0 += gamma * thickness

st.subheader("自动计算得到")

st.write(
    f"孔压计深度处初始总应力 σv0 = {sigma_v0:.2f} kPa"
)

# =====================================================
# 4. 输入孔压
# =====================================================

st.header("3. 孔隙水压力")

u0 = st.number_input(
    "初始孔隙水压力 u0（kPa）",
    min_value=0.0,
    value=40.0,
    step=0.1
)

u = st.number_input(
    "当前孔隙水压力 u(t)（kPa）",
    min_value=0.0,
    value=80.0,
    step=0.1
)

# =====================================================
# 5. 计算
# =====================================================

sigma_eff0 = sigma_v0 - u0
delta_u = u - u0

st.header("4. 计算结果")

if sigma_eff0 > 0:

    ru = delta_u / sigma_eff0

    st.write(
        f"初始总应力 σv0 = {sigma_v0:.2f} kPa"
    )

    st.write(
        f"初始孔压 u0 = {u0:.2f} kPa"
    )

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
        "初始有效应力必须大于0，请检查土层或孔压参数。"
    )
