import pandas as pd

df = pd.read_csv("data/Reviews.csv")
sample = df.sample(n=20000, random_state=42)
sample.to_csv("data/sample_feedback.csv", index=False)
print("Saved:", sample.shape)