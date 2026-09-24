import pandas as pd
from transformers import pipeline
from bertopic import BERTopic

df = pd.read_csv("data/sample_feedback.csv")
df = df.dropna(subset=["Text"])
texts = df["Text"].astype(str).tolist()[:3000]

print(f"Running sentiment analysis on {len(texts)} reviews...")

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True
)

results = sentiment_analyzer(texts, batch_size=32)

df_sample = pd.DataFrame({
    "text": texts,
    "sentiment": [r["label"] for r in results],
    "confidence": [round(r["score"], 4) for r in results]
})

print(df_sample["sentiment"].value_counts())

negative_texts = df_sample[df_sample["sentiment"] == "NEGATIVE"]["text"].tolist()
print(f"\nFound {len(negative_texts)} negative reviews. Clustering these into issues...")

topic_model = BERTopic(verbose=True)
topics, probs = topic_model.fit_transform(negative_texts)

print("\nRecurring issue themes found:")
print(topic_model.get_topic_info().head(15))

df_sample.to_csv("data/sentiment_results.csv", index=False)
topic_model.save("negative_topic_model")