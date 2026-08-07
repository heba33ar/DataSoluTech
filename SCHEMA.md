# Schéma de la base de données

**Base :** `healthcare_db` — **Collection :** `patients`

La collection est créée avec un validateur `$jsonSchema` (fonction
`create_patients_collection()` dans `healthcare.py`). La validation est donc faite par
le serveur MongoDB, pas par le script : tout document qui ne respecte pas les types ou
les valeurs autorisées ci-dessous est refusé à l'insertion.

## Champs

| Champ | Type BSON | Contraintes | Exemple |
|---|---|---|---|
| `_id` | objectId | généré par MongoDB | `ObjectId("...")` |
| `Name` | string | **obligatoire** | `Bobby Jackson` |
| `Age` | int | de 0 à 120 | `30` |
| `Gender` | string | `Male`, `Female` | `Male` |
| `Blood Type` | string | `A+` `A-` `B+` `B-` `AB+` `AB-` `O+` `O-` | `B-` |
| `Medical Condition` | string | — | `Cancer` |
| `Date of Admission` | date | — | `2024-01-31T00:00:00Z` |
| `Doctor` | string | — | `Matthew Smith` |
| `Hospital` | string | — | `Sons and Miller` |
| `Insurance Provider` | string | — | `Blue Cross` |
| `Billing Amount` | double | — | `18856.28` |
| `Room Number` | int | — | `328` |
| `Admission Type` | string | — | `Urgent` |
| `Discharge Date` | date | — | `2024-02-02T00:00:00Z` |
| `Medication` | string | — | `Paracetamol` |
| `Test Results` | string | `Normal`, `Abnormal`, `Inconclusive` | `Normal` |

`Name` est le seul champ déclaré `required` : un document sans nom est rejeté. Les
autres champs peuvent être absents, mais s'ils sont présents leur type et leurs
valeurs autorisées sont vérifiés.

## Source des données

Le dépôt ne contient aucun CSV. Le jeu de données est téléchargé à l'exécution depuis
Kaggle (`prasad22/healthcare-dataset`, version 2) par `dataset.py`.

| | |
|---|---|
| Lignes publiées | 55 500 |
| Doublons exacts supprimés | 534 |
| **Documents insérés** | **54 966** |

## Traitements appliqués avant insertion

1. **Déduplication** — `drop_duplicates()` dans `dataset.py` retire les 534 lignes
   strictement identiques présentes dans le fichier publié.
2. **Conversion des dates** — `Date of Admission` et `Discharge Date` passent de la
   chaîne `YYYY-MM-DD` à un `datetime`, car le validateur les déclare en
   `bsonType: date`. Sans cette conversion, MongoDB rejetterait les documents.
3. **Normalisation des noms** — `Name` est nettoyé puis mis en casse titre
   (`Bobby JacksOn` devient `Bobby Jackson`).

## Index

Aucun index applicatif n'est défini pour l'instant. Seul l'index par défaut existe :

| Index | Champs | Type |
|---|---|---|
| `_id_` | `_id` | unique, créé automatiquement par MongoDB |
