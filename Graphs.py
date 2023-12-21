import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv("senator_issue_positions.csv")

df.set_index('Senator Name and Metric', inplace=True)

colors = ["r", "g", "b", "y"]
dark_colors = ["#8B0000", "#006400", "#00008B", "#CCCC00"]

senators = ["Romney", "Lee", "Klobuchar", "Smith"]
for i, senator in enumerate(senators):
    left_right = [value[1] for value in df.loc[f"{senator}: Left/Right"].items()]
    auth_lib = [value [1] for value in df.loc[f"{senator}: Auth/Lib"].items()]
    plt.scatter(left_right, auth_lib, color=colors[i % len(colors)], label=f"{senator}")
    plt.scatter(np.mean(left_right), np.mean(auth_lib), color=dark_colors[i % len(dark_colors)], marker="x", s=100)

plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)

plt.legend(loc="upper right")
plt.xlabel("Left to Right Wing")
plt.ylabel("Libertarian to Authoritarian")
plt.title("Senators Issue Positions")

plt.xlim(-1, 1)
plt.ylim(-1, 1)

plt.grid(True, linestyle="--", alpha=0.7)
plt.savefig("senator_issue_positions.png")

plt.clf()

df = pd.read_csv("bill_ratings.csv")

bills = ["Presidential Impeachment", "Social Security", "Immigrant Visas"]
for i, bill in enumerate(bills):
    left_right, auth_lib = [value[1] for value in df[bill].items()]
    print(left_right, auth_lib)
    plt.scatter(left_right, auth_lib, color=colors[i % len(colors)], label=f"{bill}", marker="x", alpha=1)

plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)

plt.legend(loc="upper right")
plt.xlabel("Left to Right Wing")
plt.ylabel("Libertarian to Authoritarian")
plt.title("Bill Rating Positions")

plt.xlim(-1, 1)
plt.ylim(-1, 1)

plt.grid(True, linestyle="--", alpha=0.7)
plt.savefig("bill_rating_positions.png")
plt.show()
