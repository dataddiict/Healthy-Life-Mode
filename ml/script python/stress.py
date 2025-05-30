import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedShuffleSplit
import joblib

# Chargement et préparation des données
df = pd.read_csv("Mental Health Dataset.csv")
df.dropna(inplace=True)
df = df[df['Country'] == 'United States']

# Supprimer la colonne Timestamp et autres non pertinentes
df = df.drop(columns=["Timestamp", "Country", "Occupation", "self_employed", "family_history", "treatment", "Mood_Swings", "Coping_Struggles", "mental_health_interview", "care_options"])

# Mapping des labels pour la colonne cible
mapping = {'Yes': 1, 'No': 0, 'Maybe': 2}
df['Growing_Stress'] = df['Growing_Stress'].map(mapping)

# Sélectionner les features et la target
x = df.drop(columns=["Growing_Stress"])
y = df["Growing_Stress"]

# Définir les caractéristiques catégorielles et numériques
categorical_features = ['Days_Indoors', 'Changes_Habits', 'Work_Interest', 'Social_Weakness', 'Mental_Health_History', 'Gender']
numeric_features = ['Age'] if 'Age' in x.columns else []

# Fonction pour encoder manuellement les caractéristiques catégorielles
def transform_data(data):
    data['Days_Indoors'] = data['Days_Indoors'].map({'1-14 days': 0, '15-30 days': 1, '31-60 days': 2, 'More than 60 days': 3})
    data['Changes_Habits'] = data['Changes_Habits'].map({'Yes': 0, 'No': 1, 'Maybe': 2})
    data['Work_Interest'] = data['Work_Interest'].map({'Yes': 0, 'No': 1})
    data['Social_Weakness'] = data['Social_Weakness'].map({'Yes': 0, 'No': 1, 'Maybe': 2})
    data['Mental_Health_History'] = data['Mental_Health_History'].map({'Yes': 0, 'No': 1, 'Maybe': 2})
    data['Gender'] = data['Gender'].map({'Male': 0, 'Female': 1})
    return data

# Appliquer la transformation aux données
x = transform_data(x)

# Vérifier les valeurs manquantes
print("Valeurs manquantes avant traitement :")
print(x.isna().sum())

# Remplacer les valeurs manquantes par la médiane (pour les numériques) ou le mode (pour les catégorielles)
x[numeric_features] = x[numeric_features].fillna(x[numeric_features].median())
x[categorical_features] = x[categorical_features].fillna(x[categorical_features].mode().iloc[0])

# Vérifier les valeurs manquantes après traitement
print("Valeurs manquantes après traitement :")
print(x.isna().sum())

# Séparer les données en ensembles d'entraînement et de validation
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.1, random_state=42)
for train_index, val_index in sss.split(x, y):
    x_train, x_val = x.iloc[train_index], x.iloc[val_index]
    y_train, y_val = y.iloc[train_index], y.iloc[val_index]

# Fonction pour normaliser manuellement les caractéristiques numériques
def manual_normalize(train, val, numeric_features):
    mean = train[numeric_features].mean()
    std = train[numeric_features].std()
    train[numeric_features] = (train[numeric_features] - mean) / std
    val[numeric_features] = (val[numeric_features] - mean) / std
    return train, val, mean, std

# Normaliser les données d'entraînement et de validation
x_train, x_val, mean, std = manual_normalize(x_train, x_val, numeric_features)

# Entraîner le modèle
model = GradientBoostingClassifier(random_state=42)
model.fit(x_train, y_train)

# Prédire avec les données de validation
y_pred = model.predict(x_val)
accuracy = accuracy_score(y_val, y_pred)

# Sauvegarder le modèle, les statistiques de normalisation et les noms des features
joblib.dump(model, 'stress_model.pkl')
joblib.dump((mean, std), 'scaler_params.pkl')
joblib.dump(x_train.columns.tolist(), 'feature_names.pkl')

# Afficher les résultats
print(f'Accuracy: {accuracy}')
