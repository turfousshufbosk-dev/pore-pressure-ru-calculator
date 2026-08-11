import streamlit as st
import pandas as pd

st.title("孔压比 $r_u$ 计算平台")

st.write(
    "输入土层信息、地下水位和孔压计埋深，"
    "上传动态孔压CSV数据，自动计算孔压比时程。"
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

    # 只计算孔压计以上的土层
    if top >= sensor_depth:
        continue

    effective_bottom = min(
        bottom,
        sensor_depth
    )

    if effective_bottom <= top:
        continue

    # 地下水位以上部分
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

    # 地下水位以下部分
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
# 4. 初始孔压
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


st.subheader("自动计算得到")

col1, col2, col3 = st.columns(3)

col1.metric(
    "初始总应力 σv0",
    f"{sigma_v0:.2f} kPa"
)

col2.metric(
    "初始孔压 u0",
    f"{u0:.2f} kPa"
)

col3.metric(
    "初始有效应力 σ′v0",
    f"{sigma_eff0:.2f} kPa"
)


# =====================================================
# 6. 上传CSV
# =====================================================

st.header("3. 上传动态孔压数据")

st.write(
    "CSV文件必须包含两列："
    "`time_s` 和 `pressure_kpa`。"
)

uploaded_file = st.file_uploader(
    "选择CSV文件",
    type=["csv"]
)


# =====================================================
# 7. 读取并计算
# =====================================================

if uploaded_file is not None:

    try:

        data = pd.read_csv(uploaded_file)

    except Exception as e:

        st.error(
            f"CSV读取失败：{e}"
        )

        st.stop()


    # 检查列名
    required_columns = [
        "time_s",
        "pressure_kpa"
    ]

    if not all(
        col in data.columns
        for col in required_columns
    ):

        st.error(
            "CSV必须包含 time_s 和 pressure_kpa 两列。"
        )

        st.stop()


    # 转换为数字
    data["time_s"] = pd.to_numeric(
        data["time_s"],
        errors="coerce"
    )

    data["pressure_kpa"] = pd.to_numeric(
        data["pressure_kpa"],
        errors="coerce"
    )

    # 删除无效行
    data = data.dropna(
        subset=[
            "time_s",
            "pressure_kpa"
        ]
    )


    if len(data) == 0:

        st.error(
            "CSV中没有可用的数字数据。"
        )

        st.stop()


    # =================================================
    # 8. 计算超孔压
    # =================================================

    data["delta_u_kpa"] = (
        data["pressure_kpa"]
        - u0
    )


    # =================================================
    # 9. 计算ru
    # =================================================

    if sigma_eff0 <= 0:

        st.error(
            "初始有效应力≤0，"
            "请检查土层、地下水位和孔压计埋深。"
        )

        st.stop()


    data["ru"] = (
        data["delta_u_kpa"]
        / sigma_eff0
    )


    # =================================================
    # 10. 当前有效应力
    # =================================================

    data["sigma_eff_kpa"] = (
        sigma_eff0
        - data["delta_u_kpa"]
    )


    # =================================================
    # 11. 统计结果
    # =================================================

    delta_u_max = (
        data["delta_u_kpa"].max()
    )

    ru_max = (
        data["ru"].max()
    )

    sigma_eff_min = (
        data["sigma_eff_kpa"].min()
    )

    max_index = data["ru"].idxmax()

    t_ru_max = data.loc[
        max_index,
        "time_s"
    ]


    # =================================================
    # 12. 显示结果
    # =================================================

    st.header("4. 计算结果")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "最大超孔压 Δu",
        f"{delta_u_max:.2f} kPa"
    )

    c2.metric(
        "最大孔压比 ru",
        f"{ru_max:.3f}"
    )

    c3.metric(
        "最小有效应力",
        f"{sigma_eff_min:.2f} kPa"
    )

    st.write(
        f"最大孔压比出现时间："
        f"{t_ru_max:.3f} s"
    )


    # =================================================
    # 13. ru时程图
    # =================================================

    st.subheader("孔压比 $r_u$ 时程")

    chart_data = (
        data[
            ["time_s", "ru"]
        ]
        .set_index("time_s")
    )

    st.line_chart(
        chart_data
    )


    # =================================================
    # 14. 超孔压时程图
    # =================================================

    st.subheader("超孔隙水压力 Δu 时程")

    delta_u_chart = (
        data[
            ["time_s", "delta_u_kpa"]
        ]
        .set_index("time_s")
    )

    st.line_chart(
        delta_u_chart
    )


    # =================================================
    # 15. 有效应力时程图
    # =================================================

    st.subheader("有效应力时程")

    sigma_chart = (
        data[
            ["time_s", "sigma_eff_kpa"]
        ]
        .set_index("time_s")
    )

    st.line_chart(
        sigma_chart
    )


    # =================================================
    # 16. 完整结果表
    # =================================================

    st.subheader("完整计算结果")

    st.dataframe(
        data,
        use_container_width=True
    )


    # =================================================
    # 17. 下载结果
    # =================================================

    result_csv = (
        data
        .to_csv(index=False)
        .encode("utf-8-sig")
    )

    st.download_button(
        "下载计算结果CSV",
        result_csv,
        file_name="ru_calculation_results.csv",
        mime="text/csv"
    )


    # =================================================
    # 18. 警告
    # =================================================

    if ru_max > 1.0:

        st.warning(
            "检测到 ru > 1。"
            "请检查孔压基线、地下水位、"
            "土层参数以及动态孔压中是否存在异常尖峰。"
        )


if sensor_depth <= water_depth:

    st.warning(
        "孔压计位于地下水位以上或水位附近，"
        "传统饱和土孔压比 ru 的物理意义需要谨慎判断。"
    )
