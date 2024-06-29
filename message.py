import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.metrics import accuracy_score
from sklearn.impute import SimpleImputer

# Load and combine datasets
data_1 = pd.read_csv("D:/PA/Healthy-Life-Mode/projet_annuel/Data/train.csv").set_index("id")
data_2 = pd.read_csv("D:/PA/Healthy-Life-Mode/projet_annuel/Data/ObesityDataSet.csv")
data = pd.concat([data_1, data_2])

# Ensure no missing values in target column
data = data.dropna(subset=["NObeyesdad"])

# Define features and target
X = data.drop(columns=["NObeyesdad"])
y = data["NObeyesdad"]

# Encode the target variable
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Save the LabelEncoder
with open('label_encoder_obesity.pkl', 'wb') as le_file:
    pickle.dump(label_encoder, le_file)

# Split the data ensuring consistency
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.1, random_state=42)
for train_index, val_index in sss.split(X, y_encoded):
    X_train, X_val = X.iloc[train_index], X.iloc[val_index]
    y_train, y_val = y_encoded[train_index], y_encoded[val_index]

# Define feature sets
categorical_features = ['Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 'SMOKE', 'SCC', 'CALC', 'MTRANS']
numeric_features = ['FAF', 'TUE', 'CH2O', 'FCVC', 'NCP', 'Age', 'Height', 'Weight']

# Create preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ]
)

# Create and train the model
pipeline_gb = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', GradientBoostingClassifier(random_state=42))
])

pipeline_gb.fit(X_train, y_train)

# Save the model and preprocessor
with open('obesity_model.pkl', 'wb') as model_file:
    pickle.dump(pipeline_gb, model_file)

# Validate the model
y_pred_gb = pipeline_gb.predict(X_val)
accuracy_gb = accuracy_score(y_val, y_pred_gb)
print(f"Validation Accuracy: {accuracy_gb}")
