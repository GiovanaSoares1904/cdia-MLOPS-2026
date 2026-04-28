from sklearn.datasets import make_classification
import pandas as pd

X, y = make_classification(
    n_samples=1000,
    n_features=5,
    n_informative=3,
    n_redundant=1,
    class_sep=1.0,
    weights=[0.7, 0.3],
    random_state=42
)

df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
df["target"] = y

print(df.head())
print(f"\nDistribuição: {df['target'].value_counts().to_dict()}")
