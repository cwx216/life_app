import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from db_crud import (
    init_db,
    add_data,
    query_today_all_data,
    query_today_cost_data,
    add_suggestion,
    query_all_suggestions,
    DB_PATH
)
import sqlite3

# 中文显示修复
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 页面配置
st.set_page_config(page_title="生活数据管理", layout="wide")
st.title("📊 生活数据管理系统")

# 初始化数据库
init_db()

# ======================
# 功能：生成智能建议
# ======================
def generate_suggestion():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM smart_suggestion WHERE DATE(create_time) = ?", (today,))
    conn.commit()
    conn.close()

    rows = query_today_all_data()
    data = {row[0]: row[1] for row in rows}

    sport = data.get("sport", 0)
    sleep = data.get("sleep", 0)
    study = data.get("study", 0)
    cost = data.get("cost", 0)

    # 运动
    if sport < 30:
        add_suggestion("运动建议", "今日运动严重不足，建议散步或拉伸30分钟", "运动时长 < 30分钟", "健康")
    elif 30 <= sport < 60:
        add_suggestion("运动建议", "今日运动一般，建议适当增加活动量", "运动时长 30~60分钟", "健康")
    elif 60 <= sport <= 120:
        add_suggestion("运动建议", "今日运动达标，非常棒！继续保持", "运动时长 60~120分钟", "健康")
    else:
        add_suggestion("运动建议", "今日运动时间较长，注意休息避免疲劳", "运动时长 > 120分钟", "健康")

    # 睡眠
    if sleep < 6:
        add_suggestion("睡眠建议", "睡眠严重不足！今晚尽量早点休息", "睡眠 < 6小时", "健康")
    elif 6 <= sleep < 7:
        add_suggestion("睡眠建议", "睡眠偏少，建议保持7小时以上", "睡眠 6~7小时", "健康")
    elif 7 <= sleep <= 9:
        add_suggestion("睡眠建议", "睡眠非常健康，继续保持", "睡眠 7~9小时", "健康")
    else:
        add_suggestion("睡眠建议", "睡眠时间偏长，注意规律作息", "睡眠 > 9小时", "健康")

    # 学习
    if study < 1:
        add_suggestion("学习建议", "今日学习时间不足1小时，需要加油啦", "学习时长 < 1小时", "成长")
    elif 1 <= study < 2:
        add_suggestion("学习建议", "学习时间一般，可以再多学一会儿", "学习时长 1~2小时", "成长")
    elif 2 <= study <= 4:
        add_suggestion("学习建议", "学习时间很棒！继续保持专注", "学习时长 2~4小时", "成长")
    else:
        add_suggestion("学习建议", "今日学习时间较长，注意休息眼睛", "学习时长 > 4小时", "成长")

    # 消费
    if cost < 50:
        add_suggestion("消费建议", "消费非常克制，太棒了", "消费金额 < 50元", "理财")
    elif 50 <= cost < 200:
        add_suggestion("消费建议", "消费正常，合理范围内", "消费金额 50~200元", "理财")
    elif 200 <= cost <= 400:
        add_suggestion("消费建议", "消费偏高，注意控制不必要支出", "消费金额 200~400元", "理财")
    else:
        add_suggestion("消费建议", "今日消费较高，建议理性消费", "消费金额 > 400元", "理财")

# ======================
# 功能：生成周报
# ======================
def weekly_report():
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    total_sport = 0
    total_sleep = 0
    total_study = 0
    total_cost = 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for i in range(7):
        day = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
        cursor.execute("SELECT SUM(value) FROM personal_data WHERE type='sport' AND DATE(create_time)=?", (day,))
        total_sport += cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(value) FROM personal_data WHERE type='sleep' AND DATE(create_time)=?", (day,))
        total_sleep += cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(value) FROM personal_data WHERE type='study' AND DATE(create_time)=?", (day,))
        total_study += cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(value) FROM personal_data WHERE type='cost' AND DATE(create_time)=?", (day,))
        total_cost += cursor.fetchone()[0] or 0
    conn.close()

    st.success("📅 本周周报")
    st.write(f"🏃 运动总步数：{total_sport} 步")
    st.write(f"😴 睡眠总时长：{total_sleep:.1f} 小时")
    st.write(f"📖 学习总时长：{total_study:.1f} 小时")
    st.write(f"💰 消费总金额：{total_cost:.2f} 元")

# ======================
# 录入数据
# ======================
st.subheader("✏️ 录入今日数据")
sport = st.number_input("运动步数", min_value=0, step=100, value=0)
sleep = st.number_input("睡眠时长(小时)", min_value=0.0, step=0.5, value=0.0)
study = st.number_input("学习时长(小时)", min_value=0.0, step=0.5, value=0.0)

st.subheader("💸 消费录入")
cost_category = st.selectbox("消费分类", ["餐饮", "交通", "购物", "其他"])
cost_amount = st.number_input("消费金额", min_value=0.0, step=0.1, value=0.0)

if st.button("✅ 保存数据"):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if sport > 0:
        cursor.execute("DELETE FROM personal_data WHERE type='sport' AND DATE(create_time)=?", (today,))
        add_data("sport", sport, "运动")
    if sleep > 0:
        cursor.execute("DELETE FROM personal_data WHERE type='sleep' AND DATE(create_time)=?", (today,))
        add_data("sleep", sleep, "睡眠")
    if study > 0:
        cursor.execute("DELETE FROM personal_data WHERE type='study' AND DATE(create_time)=?", (today,))
        add_data("study", study, "学习")
    if cost_amount > 0:
        add_data("cost", cost_amount, cost_category)

    conn.commit()
    conn.close()
    st.success("✅ 保存成功！")

# ======================
# 快捷功能
# ======================
st.subheader("⚡ 快捷功能")
col1, col2 = st.columns(2)
with col1:
    if st.button("💡 生成智能建议"):
        generate_suggestion()
        st.success("✅ 建议已生成！")
with col2:
    if st.button("📅 生成本周周报"):
        weekly_report()

# ======================
# 今日数据柱状图
# ======================
st.subheader("📈 今日数据统计")
rows = query_today_all_data()
if rows:
    data = {r[0]: r[1] for r in rows}
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # 左侧Y轴：睡眠、学习、消费
    left_data = {
        "睡眠": data.get("sleep", 0),
        "学习": data.get("study", 0),
        "消费": data.get("cost", 0)
    }
    ax1.bar(left_data.keys(), left_data.values(), color=["#0F9D58", "#DB4437", "#F4B400"])
    ax1.set_ylabel("时长(小时) / 金额(元)", fontsize=12)
    ax1.grid(axis='y', alpha=0.3)

    # 右侧Y轴：运动步数
    ax2 = ax1.twinx()
    ax2.bar("运动", data.get("sport", 0), color="#4285F4")
    ax2.set_ylabel("运动步数(步)", fontsize=12)

    plt.title("今日数据统计", fontsize=15)
    st.pyplot(fig)
else:
    st.info("📭 今日暂无数据，先录入数据吧！")

# ======================
# 消费分类饼图（修复版）
# ======================
st.subheader("🥧 今日消费分类占比")
cost_rows = query_today_cost_data()
valid_cost = [(r[0], r[1]) for r in cost_rows if r[1] > 0]

if valid_cost:
    # 提取标签和数值
    cost_labels = [item[0] for item in valid_cost]
    cost_values = [item[1] for item in valid_cost]

    # 绘制饼图
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        cost_values,
        labels=cost_labels,
        autopct='%1.1f%%',
        colors=["#F4B400", "#4285F4", "#DB4437", "#0F9D58"],
        textprops={'fontsize': 12}
    )
    plt.setp(autotexts, size=12, weight="bold")
    plt.title("今日消费分类占比", fontsize=15)
    st.pyplot(fig)
else:
    st.info("📭 今日暂无消费数据，先录入消费数据吧！")

# ======================
# 智能建议展示
# ======================
st.subheader("💡 智能建议")
suggestions = query_all_suggestions()
if suggestions:
    for s in suggestions:
        with st.expander(f"【{s[4]}】{s[1]}"):
            st.write("内容：", s[2])
            st.write("原因：", s[3])
else:
    st.info("📭 暂无智能建议，请先点击「生成智能建议」按钮")