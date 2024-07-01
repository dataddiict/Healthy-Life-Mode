import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedShuffleSplit, GridSearchCV, cross_val_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# Charger le dataset
df = pd.read_csv("Mental Health Dataset.csv")

# Nettoyage et filtrage des données
df.dropna(inplace=True)
df = df[df['Country'] == 'United States']

# Mapping des labels pour la colonne cible
mapping = {'Yes': 1, 'No': 0, 'Maybe': 2}
df['Growing_Stress'] = df['Growing_Stress'].map(mapping)

# Sélectionner les features et la target
x = df.drop(columns=["Growing_Stress"])
y = df["Growing_Stress"]

# Séparer les données en ensembles d'entraînement et de validation
sss = StratifiedShuffleSplit(n_splits=5, test_size=0.1, random_state=42)
for train_index, val_index in sss.split(x, y):
    x_train, x_val = x.iloc[train_index], x.iloc[val_index]
    y_train, y_val = y.iloc[train_index], y.iloc[val_index]

# Définir les caractéristiques catégorielles et numériques
categorical_features = ["Gender", "self_employed", "family_history", "treatment", 
                        "Days_Indoors", "Changes_Habits", "Mental_Health_History", 
                        "Mood_Swings", "Coping_Struggles", "Work_Interest", 
                        "Social_Weakness", "mental_health_interview", "care_options"]
numeric_features = ["Age"]

# Vérifier quelles colonnes existent réellement dans le DataFrame
categorical_features = [feature for feature in categorical_features if feature in x_train.columns]
numeric_features = [feature for feature in numeric_features if feature in x_train.columns]

# Définir le préprocesseur pour normaliser les caractéristiques numériques et encoder les caractéristiques catégorielles
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ]
)

# Créer un pipeline avec le préprocesseur, SMOTE et le modèle Gradient Boosting
pipeline_smote = ImbPipeline([
    ('preprocessor', preprocessor),
    ('smote', SMOTE(random_state=42)),
    ('classifier', GradientBoostingClassifier(random_state=42))
])

# Définir la grille de paramètres pour la recherche hyperparamétrique
param_grid = {
    'classifier__n_estimators': [100, 200, 300],
    'classifier__learning_rate': [0.01, 0.1, 0.2],
    'classifier__max_depth': [3, 4, 5]
}

# Créer un objet GridSearchCV
grid_search = GridSearchCV(pipeline_smote, param_grid, cv=5, scoring='accuracy', n_jobs=-1)

# Entraîner le GridSearchCV
grid_search.fit(x_train, y_train)

# Obtenir les meilleurs paramètres et le meilleur score
best_params = grid_search.best_params_
best_score = grid_search.best_score_

print(f"Meilleurs paramètres: {best_params}")
print(f"Meilleur score de validation croisée: {best_score}")

# Utiliser le meilleur estimateur pour prédire le jeu de validation
best_model = grid_search.best_estimator_
y_pred_best = best_model.predict(x_val)
accuracy_best = accuracy_score(y_val, y_pred_best)
print(f"Accuracy sur le set de validation avec le meilleur modèle: {accuracy_best}")

# Calculer et afficher l'importance des caractéristiques
feature_importances = best_model.named_steps['classifier'].feature_importances_
numeric_feature_names = numeric_features
categorical_feature_names = best_model.named_steps['preprocessor'].transformers_[1][1].get_feature_names_out(categorical_features).tolist()
feature_names = numeric_feature_names + categorical_feature_names

# Créer un DataFrame avec les importances des caractéristiques
feature_importances_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': feature_importances
})

# Trier les caractéristiques par importance
feature_importances_df = feature_importances_df.sort_values(by='Importance', ascending=False)

# Sélectionner les 5 premières caractéristiques
top_features = feature_importances_df.head(5)['Feature'].tolist()

# Sélectionner les caractéristiques originales correspondantes
original_top_features = [f for f in numeric_features + categorical_features if any(f in top_feature for top_feature in top_features)]

# Créer un dataset intermédiaire avec uniquement les caractéristiques les plus importantes
x_train_reduced = x_train[original_top_features]
x_val_reduced = x_val[original_top_features]

# Appliquer le préprocesseur aux données réduites
preprocessor_reduced = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), [feature for feature in original_top_features if feature in numeric_features]),
        ('cat', OneHotEncoder(handle_unknown='ignore'), [feature for feature in original_top_features if feature in categorical_features])
    ]
)

# Ajuster le préprocesseur avec les nouvelles données réduites
x_train_reduced_transformed = preprocessor_reduced.fit_transform(x_train_reduced)
x_val_reduced_transformed = preprocessor_reduced.transform(x_val_reduced)

# Entraîner le modèle avec les données réduites et prétraitées
final_model = GradientBoostingClassifier(random_state=42, **best_params)
final_model.fit(x_train_reduced_transformed, y_train)

# Prédire avec les données de validation réduites
y_pred_gb_reduced = final_model.predict(x_val_reduced_transformed)

# Calculer et afficher l'accuracy et le rapport de classification avec les caractéristiques réduites
accuracy_gb_reduced = accuracy_score(y_val, y_pred_gb_reduced)
print(f"Accuracy avec les caractéristiques réduites: {accuracy_gb_reduced}")

# Validation croisée avec le pipeline optimisé
cv_scores = cross_val_score(best_model, x, y, cv=5, scoring='accuracy')
print(f"Scores de validation croisée: {cv_scores}")
print(f"Moyenne des scores de validation croisée: {cv_scores.mean()}")

# Rapport de classification
print("Rapport de classification avec le meilleur modèle:")
print(classification_report(y_val, y_pred_best))

# Matrice de confusion
print("Matrice de confusion:")
print(confusion_matrix(y_val, y_pred_best))
