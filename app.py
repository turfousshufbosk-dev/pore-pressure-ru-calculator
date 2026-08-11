import streamlit as st
import pandas as pd

st.title("孔压比 $r_u$ 计算平台")

st.write(
    "输入土层信息、地下水位和孔压参数，"
    "自动计算初始应力及超孔隙水压力比。"
)

# =====================================================
# 1. 土层信息
# =====================================================

st.header("1. 土层信息")

default_layers = pd.DataFrame({
    "土层名称": ["填土", "粉质黏土", "粉细砂"],
    "顶深_m": [0.0, 2.0, 4.0],
    "底深_m": [2.0, 4.0, 8.0],
    "天然重度_kN_m3": [18.0, 18.5, 18.8],
    "饱和重度_kN_m3": [19.0, 19.2, 19.5]
})

layers = st.data_editor(
    default_layers,
    num_rows="dynamic",
    use_container_width=True
)


# =====================================================
# 2. 地下水位和孔压计
# =====================================================

st.header("2. 地下水与孔压计信息")

water_depth = st.number_input(
    "地下水位埋深（m）",
    min_value=0.0,
    value=2.0,
    step=0.1
)

sensor_depth = st.number_input(
    "孔压计埋深（m）",
    min_value=0.1,
    value=6.0,
    step=0.1
)

gamma_w = 9.81


# =====================================================
# 3. 计算初始总应力
# =====================================================

sigma_v0 = 0.0

for _, row in layers.iterrows():

    top = float(row["顶深_m"])
    bottom = float(row["底深_m"])

    gamma_natural = float(
        row["天然重度_kN_m3"]
    )

    gamma_sat = float(
        row["饱和重度_kN_m3"]
    )

    # 传感器以上才参与计算
    if top >= sensor_depth:
        continue

    effective_bottom = min(
        bottom,
        sensor_depth
    )

    if effective_bottom <= top:
        continue

    # ---------------------------------
    # 地下水位以上部分
    # ---------------------------------

    above_bottom = min(
        effective_bottom,
        water_depth
    )

    if above_bottom > top:

        thickness_above = (
            above_bottom - top
        )

        sigma_v0 += (
            gamma_natural
            * thickness_above
        )

    # ---------------------------------
    # 地下水位以下部分
    # ---------------------------------

    below_top = max(
        top,
        water_depth
    )

    if effective_bottom > below_top:

        thickness_below = (
            effective_bottom
            - below_top
        )

        sigma_v0 += (
            gamma_sat
            * thickness_below
        )


# =====================================================
# 4. 自动计算初始孔压
# =====================================================

if sensor_depth > water_depth:

    u0 = gamma_w * (
        sensor_depth - water_depth
    )

else:

    u0 = 0.0


# =====================================================
# 5. 初始有效应力
# =====================================================

sigma_eff0 = sigma_v0 - u0


# =====================================================
# 显示初始状态
# =====================================================

st.subheader("自动计算得到")

st.write(
    f"初始总应力 σv0 = "
    f"{sigma_v0:.2f} kPa"
)

st.write(
    f"初始孔隙水压力 u0 = "
    f"{u0:.2f} kPa"
)

st.write(
    f"初始有效应力 σ′v0 = "
    f"{sigma_eff0:.2f} kPa"
)


# =====================================================
# 6. 当前孔压
# =====================================================

st.header("3. 当前孔隙水压力")

u = st.number_input(
    "当前孔隙水压力 u(t)（kPa）",
    min_value=0.0,
    value=80.0,
    step=0.1
)


# =====================================================
# 7. ru计算
# =====================================================

delta_u = u - u0

st.header("4. 计算结果")

if sigma_eff0 > 0:

    ru = delta_u / sigma_eff0

    current_sigma_eff = (
        sigma_eff0 - delta_u
    )

    st.write(
        f"超孔隙水压力 Δu = "
        f"{delta_u:.2f} kPa"
    )

    st.write(
        f"孔压比 ru = "
        f"{ru:.3f}"
    )

    st.write(
        f"当前有效应力 σ′v(t) = "
        f"{current_sigma_eff:.2f} kPa"
    )

else:

    st.error(
        "初始有效应力 ≤ 0，"
        "请检查土层参数、地下水位或孔压计深度。"
    )


# =====================================================
# 8. 提示
# =====================================================

if sensor_depth <= water_depth:

    st.warning(
        "当前孔压计位于地下水位以上或水位位置。"
        "传统饱和土孔压比 ru 的物理意义需要谨慎判断。"
    )

if sigma_eff0 > 0:

    if ru > 1.0:

        st.warning(
            "当前计算得到 ru > 1。"
            "请检查孔压数据、地下水位、土层参数，"
            "或是否存在额外总应力变化。"
        )
else:

    st.error(
        "初始有效应力必须大于0，请检查土层或孔压参数。"
    )
