import pandas as pd
from bertopic import BERTopic

# Load your trimmed sample dataset
df = pd.read_csv("data//sample_feedback.csv")

texts = df["Text"].dropna().astype(str).tolist()

# Use a smaller subset first to keep this fast while testing
texts = texts[:3000]

print(f"Running topic modeling on {len(texts)} reviews...")

topic_model = BERTopic(verbose=True)
topics, probs = topic_model.fit_transform(texts)

# Show the top topics found
print(topic_model.get_topic_info().head(15))

# Save the model so we can reuse it later without retraining
topic_model.save("topic_model")