# 2. visualizations.py - 可視化関連
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_accuracy_bar_chart(df_accuracy, avg_choices):
    """Plot bar chart by Method (x-axis), color = Model, and add Chance Level line"""
    if df_accuracy.empty:
        st.write("⚠️ No data available.")
        return

    df_plot = df_accuracy.copy()

    # X-axis order
    method_order = [
        "definition", "definition_token", "example_token",
        "zero_shot", "fixed_few_shot_3", "fixed_few_shot_10", "dynamic_few_shot_3_openAI", "dynamic_few_shot_10_openAI"
    ]
    df_plot["Method"] = pd.Categorical(df_plot["Method"], categories=method_order, ordered=True)

    model_order = sorted(df_plot["Model"].unique())
    df_plot["Model"] = pd.Categorical(df_plot["Model"], categories=model_order, ordered=True)

    # Pivot for plotting
    grouped = df_plot.pivot_table(index="Method", columns="Model", values="Accuracy (%)", aggfunc='mean').fillna(0)

    x = np.arange(len(grouped.index))
    width = 0.12
    fig, ax = plt.subplots(figsize=(12, 6))

    model_names = grouped.columns.tolist()
    bars = []
    colors = plt.cm.get_cmap("tab10", len(model_names))

    for i, model in enumerate(model_names):
        offset = (i - len(model_names)/2) * width + width / 2
        bar = ax.bar(x + offset, grouped[model], width, label=model, color=colors(i))
        bars.append(bar)

    # Add Chance Level line
    if avg_choices > 0:
        chance_level = round(100 / avg_choices, 2)  # Chance Level = 1 / Avg. Choices * 100
        ax.axhline(y=chance_level, color='red', linestyle='--', linewidth=1.5, label=f"Chance Level ({chance_level}%)")

    ax.set_xlabel("Method", fontsize=14)
    ax.set_ylabel("Accuracy (%)", fontsize=14)
    ax.set_title("Accuracy by Method and Model", fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(grouped.index, rotation=20, ha="right", fontsize=12)
    ax.legend(title="Model", fontsize=10)
    ax.set_ylim(0, 100)

    for bar_group in bars:
        for bar in bar_group:
            yval = bar.get_height()
            if yval > 0:
                ax.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f"{yval:.1f}%", ha='center', va='bottom', fontsize=9)

    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    return fig