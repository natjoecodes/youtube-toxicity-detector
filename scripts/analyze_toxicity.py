import pandas as pd
from transformers import pipeline

# 1. Load CSV
csv_path = "/Users/natjoe/Documents/youtube-toxicity-detector/data/rm_wA47VccQ_comments_20250929_233616.csv"
df = pd.read_csv(csv_path)

# 2. Init toxicity model
classifier = pipeline("text-classification", model="unitary/toxic-bert", tokenizer="unitary/toxic-bert")

# 3. Run toxicity analysis
results = []
for comment in df["text"].astype(str).tolist():
    if comment.strip():  # skip blanks
        pred = classifier(comment[:512])  # truncate long ones
        results.append(pred[0]["score"])
    else:
        results.append(None)

# 4. Add results to dataframe
df["toxicity_score"] = results
df["is_toxic"] = df["toxicity_score"].apply(lambda x: 1 if x and x > 0.5 else 0)

# 5. Save analyzed CSV
out_path = csv_path.replace(".csv", "_analyzed.csv")
df.to_csv(out_path, index=False)

print(f"✅ Analysis complete. Saved to {out_path}")
print(df.head())