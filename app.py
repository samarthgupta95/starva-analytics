import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Fitness Tracker Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# THEME / STYLE
# ============================================================
COLOR_ACTIVITY = "#2E6F95"
COLOR_SLEEP = "#6B4FA0"
COLOR_BODY = "#2F9E68"
COLOR_FINDING = "#C97C24"
COLOR_TEXT = "#1F2430"
COLOR_MUTED = "#667085"
BG = "#F5F7FA"
CARD_BG = "#FFFFFF"

PLOT_TEMPLATE = "plotly_white"
CHART_COLORWAY = [COLOR_ACTIVITY, COLOR_SLEEP, COLOR_BODY, COLOR_FINDING, "#94A3B8"]

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; }}
    h1, h2, h3, h4 {{ color: {COLOR_TEXT}; }}
    p, li, span {{ color: {COLOR_TEXT}; }}

    .metric-card {{
        background: {CARD_BG};
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(16,24,40,0.08);
        border-left: 5px solid {COLOR_ACTIVITY};
        margin-bottom: 10px;
    }}
    .metric-label {{
        font-size: 12px;
        color: {COLOR_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-size: 30px;
        font-weight: 700;
        color: {COLOR_TEXT};
    }}
    .metric-sub {{
        font-size: 12px;
        color: {COLOR_MUTED};
        margin-top: 4px;
    }}

    .insight-box {{
        background: #EEF3F8;
        border-left: 5px solid {COLOR_ACTIVITY};
        padding: 14px 18px;
        border-radius: 8px;
        margin: 6px 0 22px 0;
        font-size: 15px;
        color: {COLOR_TEXT};
    }}
    .insight-box.sleep {{ background: #F1EDF7; border-left-color: {COLOR_SLEEP}; }}
    .insight-box.body {{ background: #EAF6EF; border-left-color: {COLOR_BODY}; }}
    .insight-box.caveat {{ background: #FBF1E6; border-left-color: {COLOR_FINDING}; }}

    .tag {{
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .tag-headline {{ background: #DCEBF4; color: {COLOR_ACTIVITY}; }}
    .tag-quality  {{ background: #FBF1E6; color: {COLOR_FINDING}; }}
    .tag-activity {{ background: #DCEBF4; color: {COLOR_ACTIVITY}; }}
    .tag-sleep    {{ background: #EAE3F3; color: {COLOR_SLEEP}; }}
    .tag-body     {{ background: #E1F2E8; color: {COLOR_BODY}; }}

    .finding-card {{
        background: {CARD_BG};
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(16,24,40,0.08);
        margin-bottom: 16px;
        height: 100%;
    }}
    .finding-card p {{ color: {COLOR_MUTED}; font-size: 14px; margin-top: 6px; }}
    .finding-card h4 {{ margin: 0; font-size: 16px; }}

    section[data-testid="stSidebar"] {{ background-color: #FFFFFF; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    activity = pd.read_csv("data/activity_clean.csv", parse_dates=["Date"])
    sleep = pd.read_csv("data/sleep_clean.csv", parse_dates=["Date"])
    weight = pd.read_csv("data/weight_clean.csv", parse_dates=["Date"])
    return activity, sleep, weight


activity_raw, sleep_raw, weight_raw = load_data()

ALL_USERS = sorted(activity_raw["Id"].unique().tolist())
MIN_DATE = activity_raw["Date"].min().date()
MAX_DATE = activity_raw["Date"].max().date()


def metric_card(label, value, sub="", color=COLOR_ACTIVITY):
    st.markdown(
        f"""
        <div class="metric-card" style="border-left-color:{color};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight(text, kind=""):
    cls = f"insight-box {kind}".strip()
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def finding_card(tag, tag_class, title, body):
    st.markdown(
        f"""
        <div class="finding-card">
            <span class="tag {tag_class}">{tag}</span>
            <h4>{title}</h4>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR: FILTERS + NAVIGATION
# ============================================================
st.sidebar.title("Filters")

selected_users = st.sidebar.multiselect(
    "Users", options=ALL_USERS, default=[], help="Leave empty to include all users"
)

date_range = st.sidebar.slider(
    "Date range",
    min_value=MIN_DATE,
    max_value=MAX_DATE,
    value=(MIN_DATE, MAX_DATE),
    format="MMM D",
)

exclude_not_worn = st.sidebar.checkbox("Exclude device-not-worn days", value=True)

users_in_scope = selected_users if selected_users else ALL_USERS
st.sidebar.markdown(f"**{len(users_in_scope)}** of **{len(ALL_USERS)}** users in view")

st.sidebar.markdown("---")
st.sidebar.markdown("Source: Fitbit fitness tracker export, 33 users, one-month window.")

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Page",
    ["Overview & Activity", "Sleep & Body Metrics", "Key Findings"],
)


# ============================================================
# FILTERED DATA
# ============================================================
def apply_filters(df):
    d = df[df["Id"].isin(users_in_scope)]
    d = d[(d["Date"].dt.date >= date_range[0]) & (d["Date"].dt.date <= date_range[1])]
    return d


activity = apply_filters(activity_raw)
sleep = apply_filters(sleep_raw)
weight = apply_filters(weight_raw)

activity_worn = activity[~activity["DeviceNotWorn"]] if exclude_not_worn else activity


# ============================================================
# PAGE 1: OVERVIEW & ACTIVITY
# ============================================================
if page == "Overview & Activity":
    st.title("Fitness Tracker Analytics")
    st.write(
        "A wellness-tech case study on smart-device fitness data, in the spirit of the "
        "Strava / Bellabeat case study. The goal is to understand how people actually use "
        "fitness trackers, across three pillars: user activity, sleep patterns, and body metrics."
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Users in view", f"{activity['Id'].nunique()}", "of 33 total", COLOR_ACTIVITY)
    with c2:
        metric_card("Avg daily steps", f"{activity_worn['TotalSteps'].mean():,.0f}", "worn days only", COLOR_ACTIVITY)
    with c3:
        metric_card("Avg calories burned", f"{activity_worn['Calories'].mean():,.0f}", "per day", COLOR_ACTIVITY)
    with c4:
        not_worn_pct = activity["DeviceNotWorn"].mean() * 100 if len(activity) else 0
        metric_card("Device-not-worn days", f"{not_worn_pct:.1f}%", "of all logged days", COLOR_FINDING)

    st.markdown("### User Activity")

    left, right = st.columns(2)
    with left:
        fig = px.histogram(
            activity_worn, x="TotalSteps", nbins=25, template=PLOT_TEMPLATE,
            color_discrete_sequence=[COLOR_ACTIVITY], title="Daily Steps Distribution",
        )
        fig.update_layout(margin=dict(t=50, l=10, r=10, b=10), bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        bins = [-1, 4999, 7499, 9999, 10**9]
        labels = ["Sedentary", "Lightly Active", "Fairly Active", "Very Active"]
        band = pd.cut(activity_worn["TotalSteps"], bins=bins, labels=labels)
        band_counts = band.value_counts(normalize=True).reindex(labels).fillna(0) * 100
        fig = px.bar(
            x=band_counts.index, y=band_counts.values, template=PLOT_TEMPLATE,
            color=band_counts.index, color_discrete_sequence=CHART_COLORWAY,
            title="Share of Days by Activity Level", labels={"x": "", "y": "% of days"},
        )
        fig.update_layout(showlegend=False, margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    insight(
        "Sedentary minutes make up the large majority of the average tracked day, far outweighing "
        "any active category. This is the single clearest activity-side product opportunity: nudging "
        "users out of long sedentary stretches, not just celebrating high-step days."
    )

    left, right = st.columns(2)
    with left:
        activity_worn = activity_worn.copy()
        activity_worn["day_type"] = activity_worn["Date"].dt.dayofweek.apply(
            lambda d: "Weekend" if d >= 5 else "Weekday"
        )
        wk = activity_worn.groupby("day_type")[["TotalSteps", "Calories"]].mean().reset_index()
        fig = px.bar(
            wk, x="day_type", y="TotalSteps", template=PLOT_TEMPLATE,
            color="day_type", color_discrete_sequence=[COLOR_ACTIVITY, COLOR_BODY],
            title="Avg Steps: Weekday vs Weekend", labels={"day_type": "", "TotalSteps": "avg steps"},
        )
        fig.update_layout(showlegend=False, margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        if len(users_in_scope) == 1:
            trend = activity[activity["Id"] == users_in_scope[0]].sort_values("Date")
            trend["rolling"] = trend["TotalSteps"].rolling(7, min_periods=1).mean()
            fig = px.line(
                trend, x="Date", y="rolling", template=PLOT_TEMPLATE,
                color_discrete_sequence=[COLOR_ACTIVITY],
                title=f"7-Day Rolling Avg Steps — User {users_in_scope[0]}",
            )
        else:
            trend = activity.groupby("Date")["TotalSteps"].mean().reset_index()
            trend["rolling"] = trend["TotalSteps"].rolling(7, min_periods=1).mean()
            fig = px.line(
                trend, x="Date", y="rolling", template=PLOT_TEMPLATE,
                color_discrete_sequence=[COLOR_ACTIVITY],
                title="7-Day Rolling Avg Steps — All Users in View",
            )
        fig.update_layout(margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Activity Leaderboard")
    leaderboard = (
        activity_worn.groupby("Id")
        .agg(days_logged=("TotalSteps", "count"), avg_steps=("TotalSteps", "mean"), avg_calories=("Calories", "mean"))
        .round(0)
        .sort_values("avg_steps", ascending=False)
        .reset_index()
    )
    st.dataframe(leaderboard, use_container_width=True, hide_index=True)


# ============================================================
# PAGE 2: SLEEP & BODY METRICS
# ============================================================
elif page == "Sleep & Body Metrics":
    st.title("Sleep & Body Metrics")

    st.markdown("### Sleep Patterns")
    insight(
        f"Only {sleep_raw['Id'].nunique()} of 33 users log sleep at all. Findings here describe that "
        "subset, not the full user base.",
        kind="sleep",
    )

    if len(sleep):
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Users logging sleep", f"{sleep['Id'].nunique()}", "in current view", COLOR_SLEEP)
        with c2:
            metric_card("Avg hours asleep", f"{(sleep['TotalMinutesAsleep']/60).mean():.1f}h", "per night", COLOR_SLEEP)
        with c3:
            metric_card("Avg sleep efficiency", f"{sleep['SleepEfficiency'].mean():.1f}%", "time in bed asleep", COLOR_SLEEP)

        left, right = st.columns(2)
        with left:
            fig = px.histogram(
                sleep, x=sleep["TotalMinutesAsleep"] / 60, nbins=20, template=PLOT_TEMPLATE,
                color_discrete_sequence=[COLOR_SLEEP], title="Hours Asleep per Night",
                labels={"x": "hours asleep"},
            )
            fig.update_layout(margin=dict(t=50, l=10, r=10, b=10), bargap=0.05)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            bins = [-1, 419, 540, 10**5]
            labels = ["Below Recommended (<7h)", "Recommended (7-9h)", "Above Recommended (>9h)"]
            band = pd.cut(sleep["TotalMinutesAsleep"], bins=bins, labels=labels)
            band_counts = band.value_counts(normalize=True).reindex(labels).fillna(0) * 100
            fig = px.bar(
                x=band_counts.index, y=band_counts.values, template=PLOT_TEMPLATE,
                color=band_counts.index, color_discrete_sequence=CHART_COLORWAY,
                title="Share of Nights by Sleep Adequacy", labels={"x": "", "y": "% of nights"},
            )
            fig.update_layout(showlegend=False, margin=dict(t=50, l=10, r=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        insight(
            "Average sleep efficiency is high, meaning time in bed is mostly spent actually asleep. "
            "The real gap is sleep duration, not efficiency: a notable share of nights fall short of the "
            "recommended 7 hours. A product nudging bedtime, rather than sleep quality, targets the "
            "actual gap.",
            kind="sleep",
        )

        st.markdown("#### Lowest Sleep Efficiency (with nights logged)")
        bottom5 = (
            sleep.groupby("Id")
            .agg(nights_logged=("SleepEfficiency", "count"), avg_hours_asleep=("TotalMinutesAsleep", lambda x: round(x.mean() / 60, 1)), avg_sleep_efficiency=("SleepEfficiency", "mean"))
            .round(1)
            .sort_values("avg_sleep_efficiency")
            .head(5)
            .reset_index()
        )
        st.dataframe(bottom5, use_container_width=True, hide_index=True)
    else:
        st.info("No sleep data for the current filter selection.")

    st.markdown("---")
    st.markdown("### Body Metrics")
    insight(
        f"Only {weight_raw['Id'].nunique()} of 33 users log weight, mostly manually rather than via a "
        "synced scale. Treat any finding here as directional, not representative.",
        kind="body",
    )

    if len(weight):
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Users logging weight", f"{weight['Id'].nunique()}", "in current view", COLOR_BODY)
        with c2:
            metric_card("Avg BMI", f"{weight['BMI'].mean():.1f}", "current view", COLOR_BODY)
        with c3:
            manual_pct = weight["IsManualReport"].mean() * 100
            metric_card("Manual entries", f"{manual_pct:.0f}%", "vs auto-synced", COLOR_BODY)

        left, right = st.columns(2)
        with left:
            bmi_by_user = weight.groupby("Id")["BMI"].mean().reset_index()
            bmi_by_user["category"] = pd.cut(
                bmi_by_user["BMI"], bins=[0, 18.5, 25, 30, 100],
                labels=["Underweight", "Normal", "Overweight", "Obese"],
            )
            fig = px.bar(
                bmi_by_user.sort_values("BMI"), x="Id", y="BMI", color="category",
                template=PLOT_TEMPLATE, color_discrete_sequence=CHART_COLORWAY,
                title="Avg BMI by User", labels={"Id": "user"},
            )
            fig.update_xaxes(type="category")
            fig.update_layout(margin=dict(t=50, l=10, r=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with right:
            entry_counts = weight["IsManualReport"].map({True: "Manual", False: "Automatic"}).value_counts()
            fig = px.pie(
                names=entry_counts.index, values=entry_counts.values, template=PLOT_TEMPLATE,
                color_discrete_sequence=[COLOR_BODY, COLOR_ACTIVITY], title="Manual vs Automatic Entries", hole=0.45,
            )
            fig.update_layout(margin=dict(t=50, l=10, r=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Weight Change (First vs Last Log)")
        bounds = weight.groupby("Id")["Date"].agg(["min", "max"]).reset_index()
        trend_rows = []
        for _, row in bounds.iterrows():
            first_w = weight[(weight["Id"] == row["Id"]) & (weight["Date"] == row["min"])]["WeightKg"].iloc[0]
            last_w = weight[(weight["Id"] == row["Id"]) & (weight["Date"] == row["max"])]["WeightKg"].iloc[0]
            trend_rows.append({"Id": row["Id"], "first_weight_kg": first_w, "last_weight_kg": last_w, "change_kg": round(last_w - first_w, 1)})
        st.dataframe(pd.DataFrame(trend_rows).sort_values("change_kg"), use_container_width=True, hide_index=True)
    else:
        st.info("No body-metrics data for the current filter selection.")


# ============================================================
# PAGE 3: KEY FINDINGS
# ============================================================
else:
    st.title("Key Findings and Business Recommendations")
    st.write(
        "A summary of what the full dataset supports, paired with concrete actions a product or "
        "wellness team can take. These figures are based on the full dataset and are not affected by "
        "the sidebar filters, so they stay a stable reference regardless of how the other pages are filtered."
    )

    st.markdown("### Key findings")

    fc1, fc2 = st.columns(2)
    with fc1:
        finding_card(
            "HEADLINE", "tag-headline",
            "Sedentary time dominates the average day",
            "Across all users, sedentary minutes make up roughly four-fifths of tracked awake time, "
            "far outweighing any active category. This is the clearest single pattern in the data.",
        )
    with fc2:
        finding_card(
            "DATA QUALITY", "tag-quality",
            "Pillars have very different coverage",
            "All 33 users log activity, but only about 73 percent log sleep and just 24 percent log "
            "weight. Sleep and body-metric findings describe a self-selected subset, not the full base.",
        )

    fc3, fc4 = st.columns(2)
    with fc3:
        finding_card(
            "ACTIVITY INSIGHT", "tag-activity",
            "Device wear is inconsistent for a meaningful minority",
            "Six of 33 users have their device unworn on more than a fifth of logged days, with one user "
            "missing data on 45 percent of days. Any activity average should be read alongside wear rate.",
        )
    with fc4:
        finding_card(
            "SLEEP INSIGHT", "tag-sleep",
            "The sleep gap is duration, not quality",
            "Average sleep efficiency is above 90 percent, meaning time in bed is mostly spent asleep. "
            "Even so, 44 percent of nights fall short of the 7-hour minimum recommended for adults.",
        )

    fc5, fc6 = st.columns(2)
    with fc5:
        finding_card(
            "PRODUCT OPPORTUNITY", "tag-body",
            "Weight logging is the weakest-adopted feature",
            "Only 8 of 33 users log weight at all, and most of those entries are typed in manually rather "
            "than synced automatically. Of the 8, most show a flat or slightly declining trend.",
        )
    with fc6:
        finding_card(
            "SAMPLE CAVEAT", "tag-quality",
            "Weekday and weekend patterns are nearly identical",
            "Average steps, calories, and sleep barely shift between weekdays and weekends. A "
            "day-of-week-based personalization strategy is unlikely to move outcomes much on its own.",
        )

    st.markdown("### Business recommendations")

    rc1, rc2 = st.columns(2)
    with rc1:
        finding_card(
            "", "tag-activity",
            "Target sedentary time, not just step counts",
            "Since sedentary minutes dominate the day for nearly everyone, a periodic move reminder "
            "during long inactive stretches is likely to reach more users than a step-count leaderboard.",
        )
    with rc2:
        finding_card(
            "", "tag-sleep",
            "Nudge bedtime, not sleep quality",
            "Because efficiency is already high but duration is short for many nights, a bedtime reminder "
            "or wind-down prompt addresses the actual gap better than a sleep-quality feature would.",
        )

    rc3, rc4 = st.columns(2)
    with rc3:
        finding_card(
            "", "tag-headline",
            "Improve device-wear compliance before trusting activity averages",
            "With a meaningful minority of users missing a fifth or more of their tracked days, a simple "
            "wear-reminder or a visible streak indicator could materially improve data completeness.",
        )
    with rc4:
        finding_card(
            "", "tag-body",
            "Treat weight logging as an adoption problem, not an insight problem",
            "The bottleneck for body metrics is that almost nobody logs weight, not what the data shows "
            "once they do. Smart-scale integration or lighter-weight manual entry is worth testing before "
            "investing further in weight-trend features.",
        )
