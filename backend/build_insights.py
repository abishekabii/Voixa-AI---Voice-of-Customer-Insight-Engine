import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client
from transformers import pipeline
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# Load data
df = pd.read_csv("data/sample_feedback.csv")
df = df.dropna(subset=["Text"])
texts = df["Text"].astype(str).tolist()[:1000]  # smaller batch for a real test run

print(f"Running sentiment analysis on {len(texts)} reviews...")

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True
)

results = []
batch_size = 32
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    results.extend(sentiment_analyzer(batch))
    print(f"Processed {min(i+batch_size, len(texts))}/{len(texts)}")

df_sample = pd.DataFrame({
    "text": texts,
    "sentiment": [r["label"] for r in results],
    "confidence": [round(r["score"], 4) for r in results]
})

print(df_sample["sentiment"].value_counts())

# Isolate negative feedback and cluster into issues
negative_df = df_sample[df_sample["sentiment"] == "NEGATIVE"].reset_index(drop=True)
negative_texts = negative_df["text"].tolist()
print(f"\nFound {len(negative_texts)} negative reviews. Clustering into issues...")

vectorizer_model = CountVectorizer(stop_words="english", min_df=2, ngram_range=(1, 2))
topic_model = BERTopic(verbose=True, vectorizer_model=vectorizer_model)
topics, probs = topic_model.fit_transform(negative_texts)

negative_df["topic_id"] = topics
topic_info = topic_model.get_topic_info()

# Build a lookup: topic_id -> short readable label, using the real keyword list
# (Representation is a list like ["coffee", "stale", "weak", ...], not the messy "0_coffee_stale_weak" Name field)
topic_labels = {
    int(r["Topic"]): ", ".join(r["Representation"][:3])
    for _, r in topic_info.iterrows()
}

# --- Write topics table ---
print("\nWriting topics to Supabase...")
for _, row in topic_info.iterrows():
    if row["Topic"] == -1:
        continue  # skip the outlier/noise bucket
    keywords = row["Representation"]
    try:
        supabase.table("topics").upsert({
            "id": int(row["Topic"]),
            "label": ", ".join(keywords[:3]),
            "keywords": ", ".join(keywords),
            "review_count": int(row["Count"])
        }).execute()
    except Exception as e:
        print("TOPIC INSERT FAILED:", e)
        print("Row was:", row["Topic"], row["Name"])

# --- Write feedback rows ---
print("Writing feedback rows to Supabase...")
positive_df = df_sample[df_sample["sentiment"] == "POSITIVE"].reset_index(drop=True)

print(f"Positive rows to insert: {len(positive_df)}")
pos_inserted = 0
for _, row in positive_df.iterrows():
    try:
        supabase.table("feedback").insert({
            "text": row["text"],
            "sentiment": row["sentiment"],
            "confidence": row["confidence"],
            "topic_id": None,
            "topic_label": None
        }).execute()
        pos_inserted += 1
    except Exception as e:
        print("POSITIVE INSERT FAILED:", e)
        print("Row was:", row["text"][:80])

print(f"Positive rows successfully inserted: {pos_inserted}/{len(positive_df)}")

print(f"\nNegative rows to insert: {len(negative_df)}")
neg_inserted = 0
for _, row in negative_df.iterrows():
    topic_id = int(row["topic_id"])
    try:
        supabase.table("feedback").insert({
            "text": row["text"],
            "sentiment": "NEGATIVE",
            "confidence": None,
            "topic_id": topic_id if topic_id != -1 else None,
            "topic_label": topic_labels.get(topic_id) if topic_id != -1 else None
        }).execute()
        neg_inserted += 1
    except Exception as e:
        print("NEGATIVE INSERT FAILED:", e)
        print("Row was:", row["text"][:80], "| topic_id:", topic_id)

print(f"Negative rows successfully inserted: {neg_inserted}/{len(negative_df)}")

print("\nDone. Check Supabase Table Editor for populated feedback and topics tables.")