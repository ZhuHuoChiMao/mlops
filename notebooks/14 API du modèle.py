import marimo

__generated_with = "0.21.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Le projet Kedro permet d'entraîner automatiquement un modèle pour ensuite l'envoyer vers un registre sur MLflow. Avec Flask, nous avons vu qu'il est facile de construire une API REST en Python. Nous allons donc allier les deux, à savoir construire une API REST avec Flask qui va directement récupérer le modèle le plus à jour sur MLflow.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Construire la structure algorithmique d'une API avec Flask</li>
        <li>Exécuter l'API en local et tester son fonctionnement</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/mi6DsSSNKDbUY/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Structure de l'API

    Avant de débuter sur la structure de l'API, nous devons apporter une légère modification sur le pipeline `processing` et `training` de Kedro. En effet, si l'on regarde bien, dans le pipeline `processing`, la fonction `encode_features` transforme numérique les données en appliquant par exemple un `LabelEncoder` sur plusieurs colonnes. Sur l'API, il faut que l'on ait **exactement le même encodage**, sinon cela pourrait poser des problèmes lors de la prédiction (valeur jamais observée par exemple).

    Pour cela, nous rajoutons dans le catalogue de données un nouvel élément. (Si ce n'est pas déjà fait avant)

    ```
    transform_pipeline:
      type: pickle.PickleDataSet
      filepath: data/04_feature/transform_pipeline.pkl
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Modifions le code dans la fonction `encode_features` du fichier `nodes.py`.

    ```py
    def encode_features(
        dataset: pd.DataFrame,
    ) -> dict[str, pd.DataFrame | dict[str, LabelEncoder]]:
        "\"\"
        Encode features of data file.
        "\"\"
        features = dataset.drop(["user_id", "user_session"], axis=1).copy()

        encoders = []
        transform_pipeline: dict[str, LabelEncoder] = {}
        for label in ["category", "sub_category", "brand"]:
            features[label] = features[label].astype("string").fillna("unknown")
            encoder = LabelEncoder()
            features[label] = encoder.fit_transform(features[label])
            encoders.append((label, features[label]))
            transform_pipeline[label] = encoder

        features["weekday"] = features["weekday"].astype(int)
        return {"features": features, "transform_pipeline": transform_pipeline}


    # On a rajouté la transform pipeline
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// attention
    Puisque l'on vient de modifier le contenu de la fonction `encode_features`, il faut également penser à modifier le test unitaire et les fixtures associés !
    ///

    ```py
    def test_encode_features(dataset_not_encoded):
        encoded: dict[str, pd.DataFrame | dict[str, LabelEncoder]] = (
            encode_features(dataset_not_encoded)
        )
        features_value = encoded["features"]
        assert isinstance(features_value, pd.DataFrame), (
            "Expected DataFrame for features"
        )
        df: pd.DataFrame = features_value  # Now type-safe

        # Checking column 'purchased' that all values are either 0 or 1
        assert df["purchased"].isin([0, 1]).all()
        # Checking that all columns are numeric
        for col in df.columns:
            assert pd.api.types.is_numeric_dtype(df.dtypes[col])
        # Checking that we have enough samples
        assert df.shape[0] > MIN_SAMPLES
        # Checking that classes have at least BALANCE_THRESHOLD percent of data
        assert (
            df["purchased"].value_counts() / df.shape[0] > BALANCE_THRESHOLD
        ).all()
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    De même pour la fixture associée.
    ```py
    @pytest.fixture(scope="module")
    def dataset_encoded(dataset_not_encoded):
        return encode_features(dataset_not_encoded)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plutôt que de retourner uniquement `features`, la fonction retourne en plus la liste des encodeurs utilisés. Nous n'avons que 3 LabelEncoder, mais nous pourrions en avoir plus et de natures différentes.

    Puisque nous avons modifié la sortie de la fonction, nous devons également modifier le pipeline associé.

    ```py
    def create_pipeline(**kwargs):
        return Pipeline(
            [
                node(
                    encode_features,
                    "primary",
                    dict(
                        features="dataset", transform_pipeline="transform_pipeline"
                    ),
                ),
                node(
                    split_dataset,
                    ["dataset", "params:test_ratio"],
                    dict(
                        X_train="X_train",
                        y_train="y_train",
                        X_test="X_test",
                        y_test="y_test",
                    ),
                ),
            ]
        )
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La dernière manipulation consiste à envoyer ce pipeline `sklearn` vers MLflow. En exécutant ce pipeline Kedro, les transformations seront enregistrées dans `04_feature/transform_pipeline.pkl` comme défini dans le catalogue de données. Ainsi, il suffit d'envoyer cet artifact à MLflow, en même temps que les métriques et le modèle sont envoyés.

    ```py
    if log_to_mlflow:
        model_metrics = {"f1": best_model["score"]}

        mlflow.log_metrics(model_metrics)
        mlflow.log_params(optimum_params)
        # Only use if validation curves are produced
        # mlflow.log_artifacts("data/08_reporting", artifact_path="plots")
        mlflow.log_artifact("data/04_feature/transform_pipeline.pkl")
        mlflow.sklearn.log_model(best_model["model"], "model")
        mlflow.end_run()
    ```
    """)
    return


app._unparsable_cell(
    r"""
    Here 1
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exécutons d'abord le pipeline `processing`, puis `training`.
    ```
    kedro run --pipeline processing
    kedro run --pipeline training
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Le fichier Pickle devrait être présent dans les artifacts sous MLflow.

    ![alt](public/api_model1.png)

    ### Nouveau projet

    C'est parti pour réaliser un nouveau projet qui contiendra les codes sources de l'API. Lançons une nouvelle fenêtre VS Code avec un terminal pour y créer un nouveau dossier avec un environnement virtuel.

    ```
    uv init purchase_predict_api --python 3.12
    cd purchase_predict_api/
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// attention
    Pour rappel, l'ensemble des paquets n'ont pas encore migré vers 3.14, nous utiliserons donc 3.12 pour le moment
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour faciliter le développement, ouvrons le dossier en tant que projet sur VS Code, puis activons l'environnement virtuel dans un terminal.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous allons y ajouter plusieurs éléments.

    - Le fichier `app.py`, qui correspond au point d'entrée de notre API. En particulier, ce fichier contiendra les routes pour pouvoir interagir avec notre modèle.
    - Le dossier `src/` va contenir des fichiers, notamment pour récupérer le modèle depuis MLflow ou effectuer le traitement des données que recevra l'API.
    - Nous remarquons que `astral/uv` nous a généré un `main.py`, nous pouvons le supprimer.

    Commençons par le fichier `app.py`.

    ```
    from flask import Flask

    app = Flask(__name__)


    @app.route("/", methods=["GET"])
    def home():
        return "OK !", 200


    if __name__ == "__main__":
        app.run(port=5000)
    ```
    """)
    return


app._unparsable_cell(
    r"""
    Here 2
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Jusque-là, rien de nouveau. Nous allons installer `Flask` dans l'environnement virtuel.

    ```
    uv add flask
    ```

    ///note
    Au cas où ça ne fonctionne pas
    ```
    uv add "flask==1.1.2"
    ```
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exécutons le fichier `app.py` avec Python pour voir Flask est bien installé.
    """)
    return


app._unparsable_cell(
    r"""
    Here 3
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    uv run app.py
    ```
    ```
    * Serving Flask app "app" (lazy loading)
     * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    ```
    """)
    return


app._unparsable_cell(
    r"""
    Here 4
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dans le dossier `src/`, nous allons ajouter le fichier vide `__init__.py` et le fichier `model.py` qui contiendra les fonctions pour charger le modèle.

    Tout comme nous l'avions fait pour Kedro, installons `python-dotenv` et créons le fichier `.env` pour y insérer les variables d'environnement.

    ```
    uv add python-dotenv
    ```

    ```
    ENV=staging
    MLFLOW_SERVER=http://xx.xx.xx.xx/
    MLFLOW_REGISTRY_NAME=purchase_predict
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Et nous chargeons les variables d'environnement dans le fichier `__init__.py`.

    ```py
    import os

    from dotenv import load_dotenv

    load_dotenv()

    for env_var in ["ENV", "MLFLOW_SERVER", "MLFLOW_REGISTRY_NAME"]:
        if not os.getenv(env_var):
            raise Exception(
                "Environment variable {} must be defined.".format(env_var)
            )
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La boucle `for` permet de s'assurer que toutes les variables d'environnement nécessaires sont bien présentes. Détaillons le contenu du fichier `model.py`.

    ```py
    import os

    import joblib
    import mlflow
    from mlflow.tracking import MlflowClient

    ENV = os.getenv("ENV")
    MLFLOW_REGISTRY_NAME = os.getenv("MLFLOW_REGISTRY_NAME")

    # Le warning est déjà guardé par le fichier __init__.py, pas besoin de le répéter ici
    mlflow.set_tracking_uri(os.getenv("MLFLOW_SERVER"))  # ty: ignore[invalid-argument-type]
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous importons les dépendances nécessaires et nous configurons la variable d'environnement `ENV` et MLflow. Pour rappel, il y a deux objets à récupérer depuis MLflow.

    - Le modèle, qui sera directement récupéré via MLflow et chargé en mémoire.
    - Le pipeline de transformation au format Pickle.

    Cela va être procédé en deux temps : on récupère les artifacts depuis MLflow à l'initialisation de l'API, puis on ré-utilisera le modèle et le pipeline de transformation à chaque fois que l'on souhaite calculer des prédictions. Pour cette raison, il est préférable de **créer une classe** `Model` qui va permettre de réaliser les deux opérations pour garder en mémoire le modèle ainsi que le pipeline.
    """)
    return


@app.cell(disabled=True)
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    À l'initialisation `__init__`, on instancie les variables `model` et `transform_pipeline`, puis on appelle directement la fonction `load_model`.

    Cette dernière va tout d'abord charger le modèle depuis le registre avec le tag correspondant à `ENV` (staging ou production, que l'on renome en `alias` pour être en adéquation avec l'API de `mlflow`), puis va récupéer l'artifact `transform_pipeline.pkl` en se basant sur l'identifiant du run associé à la version du modèle de registre.

    À chaque appel de la fonction `predict`, nous vérifions au préalable que le modèle est bien en mémoire, puis s'il y a un pipeline de transformation, nous l'appliquons sur le jeu de données avant de pouvoir calculer les prédictions.

    Dans le fichier `app.py`, il suffit de mettre à jour l'en-tête.


    ```py
    class Model:
        def __init__(self):
            self.model = None
            self.transform_pipeline = None
            self.load_model()

        def load_model(self):
            # We query currently staging or production model, according to environment specification
            client = MlflowClient()
            alias = ENV
            model_version = client.get_model_version_by_alias(
                os.getenv("MLFLOW_REGISTRY_NAME"),  # ty: ignore[invalid-argument-type]
                alias,  # ty: ignore[invalid-argument-type]
            )

            # In MLFlow v3, construct the artifact URI and use mlflow.artifacts.download_artifacts()
            artifact_uri = f"runs:/{model_version.run_id}/transform_pipeline.pkl"
            pipeline_path = mlflow.artifacts.download_artifacts(
                artifact_uri=artifact_uri
            )  # ty: ignore[possibly-missing-attribute]

            if pipeline_path is None:
                raise RuntimeError(
                    f"Failed to download transform_pipeline.pkl for run_id={model_version.run_id}. "
                    "The artifact was not found. Ensure the training pipeline logs "
                    "transform_pipeline.pkl via mlflow.log_artifact()."
                )

            self.model = mlflow.sklearn.load_model(
                f"models:/{MLFLOW_REGISTRY_NAME}@{alias}"
            )
            # We must also retrieve transform pipeline from artifacts
            self.transform_pipeline = joblib.load(pipeline_path)

        def predict(self, X):
            if self.model:
                if self.transform_pipeline:
                    for name, encoder in self.transform_pipeline:
                        X[name] = X[name].fillna("unknown")
                        X[name] = encoder.transform(X[name])
                for col in ["user_id", "user_session", "purchased"]:
                    if col in X:
                        X = X.drop(col, axis=1)
                return self.model.predict(X)
            return None

    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
    from src.model import Model

    app = Flask(__name__)
    model = Model()


    @app.route("/", methods=["GET"])
    def home():
        # At beginning, we load model from MLflow
        return ("OK !", 200)


    if __name__ == "__main__":
        app.run(port=5000)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Là-aussi, avant d'exécuter l'API, il faut authentifier notre application pour qu'elle ait les accès en lecture vers Cloud Storage pour récupérer les artifacts MLflow.

    Comme nous avions déjà créé un <a href="https://console.cloud.google.com/iam-admin/serviceaccounts" target="_blank">compte de service</a> pour Kedro, nous pouvons utiliser le même ici. Pour cela, nous allons créer une nouvelle clé et récupérer son contenu. Créons le dossier `conf/` dans lequel nous allons ajouter la clé du compte de service. Il faut également penser à ajouter la variable d'environnement `GOOGLE_APPLICATION_CREDENTIALS` dans le fichier `.env`.

    ```
    GOOGLE_APPLICATION_CREDENTIALS = "conf/key.json"
    ```
    """)
    return


app._unparsable_cell(
    r"""
    Here 5
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous complétons le fichier `pyproject.toml`, en ajoutant les dépendances suivantes à l'aide de `uv add`:
    - pandas<3.0.0
    - mlflow==3.0.1
    - scikit-learn
    - google-cloud-storage
    - lightgbm
    ```
    uv add "pandas<3.0.0" "mlflow==3.0.1" scikit-learn google-cloud-storage lightgbm
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En exécutant `python app.py`, s'il n'y a aucun message d'erreur, c'est que notre API a pu récupérer le modèle depuis MLflow et le charger en mémoire.

    ### Route de prédiction

    La dernière étape avant de pouvoir officiellement tester la toute première version de notre API est de construire la route HTTP permettant de calculer les prédictions. Nous allons créer une route `/predict` qui n'accepte que la méthode `POST` (qui permet d'avoir un corps de message). La fonction associée va être décomposée en plusieurs étapes.

    - On récupère le DataFrame envoyé au format JSON.
    - On calcule les prédictions du modèle sur le DataFrame.
    - On retourne la liste des prédictions au format JSON.

    ```py
    @app.route("/predict", methods=["POST"])
    def predict():
        body = request.get_json()
        df = pd.read_json(body)
        results = [int(x) for x in model.predict(df).flatten()]
        return (jsonify(results), 200)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    À noter que le format `int64` des prédictions du modèle n'est pas sérialisable en JSON : c'est pour cela que l'on utilise une itération avec une conversion explicite en `int`.

    Au final, le code complet du fichier `app.py` tient en quelques lignes.

    ```
    import pandas as pd
    from flask import Flask, request, jsonify

    from purchase_predict_api.src.model import Model

    app = Flask(__name__)
    model = Model()


    @app.route("/", methods=["GET"])
    def home():
        # At beginning, we load model from MLflow
        return ("OK !", 200)


    @app.route("/predict", methods=["POST"])
    def predict():
        body = request.get_json()
        df = pd.read_json(body)
        results = [int(x) for x in model.predict(df).flatten()]
        return (jsonify(results), 200)


    if __name__ == "__main__":
        app.run(port=5000)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exécution et test de l'API

    Testons notre API. Dans le terminal, exécutons `app.py` : cela va automatiquement exécuter l'API sur le port $5000$ de la machine (en localhost sur l'adresse 127.0.0.1).
    """)
    return


@app.cell
def _():
    import pandas as pd
    import os

    # N'oubliez pas de mettre le path du projet kedro ici
    path_kedro = r"your_kedro_path"
    dataset = pd.read_csv(os.path.join(path_kedro, r"data\03_primary\primary.csv"))
    dataset = dataset.drop(["user_session", "user_id", "purchased"], axis=1)
    return (dataset,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous avons chargé les données **avant encodage** (car cela sera réalisé par l'API elle-même), nous pouvons donc faire une requête `POST` avec quelques observations prises aléatoirement.
    """)
    return


@app.cell
def _(dataset):
    import requests

    requests.post(
        "http://127.0.0.1:5000/predict", json=dataset.sample(n=10).to_json()
    ).json()
    return (requests,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Le résultat est une liste, où chaque élément correspond à classe prédite associée à l'observation de même position.

    Le principal intérêt de l'API c'est qu'elle puisse être exécutée sur un serveur et être utilisée par d'autres applications. L'API doit donc être déployée sur un serveur pour accepter des requêtes par Internet. Seulement, Flask est une API **synchrone**, ce qui fait que lorsque deux requêtes seront exécutées quasi-simultanément, la seconde requête ne sera traîtée que lorsque la première aura reçu une réponse du serveur.

    Un outil qui nous permet d'exécuter plusieurs instances de l'API en parallèle sur un même serveur, bien connu par les développeurs Python, est `gunicorn`. Il va également gérer les cas où une exécution pourrait crasher et ne pas redémarrer : on appelle cela de **l'équilibrage de charge vertical**.

    ```
    uv add gunicorn
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour exécuter plusieurs instances, nous allons directement utiliser la commande `gunicorn` dans un nous terminal (on fera attention à toujours être dans l'environnement virtuel).
    """)
    return


app._unparsable_cell(
    r"""
    gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    [2021-01-20 20:22:38 +0000] [743] [INFO] Starting gunicorn 20.0.4
    [2021-01-20 20:22:38 +0000] [743] [INFO] Listening at: http://127.0.0.1:5000 (743)
    [2021-01-20 20:22:38 +0000] [743] [INFO] Using worker: sync
    [2021-01-20 20:22:38 +0000] [745] [INFO] Booting worker with pid: 745
    [2021-01-20 20:22:38 +0000] [746] [INFO] Booting worker with pid: 746
    [2021-01-20 20:22:38 +0000] [747] [INFO] Booting worker with pid: 747
    [2021-01-20 20:22:38 +0000] [748] [INFO] Booting worker with pid: 748
    """,
    name="_"
)


@app.cell
def _(dataset, requests):
    requests.post(
        "http://127.0.0.1:5000/predict", json=dataset.sample(n=10).to_json()
    ).json()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Là-aussi, la requête fonctionne avec 4 processus `gunicorn` en exécution. Observons de plus près ces processus.

    ```
    ps -aux | grep gunicorn
    ```
    """)
    return


app._unparsable_cell(
    r"""
    jovyan       743  0.2  0.1  29080 22872 pts/3    S+   20:22   0:00 python3 gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
    jovyan       745  3.3  0.9 1292376 142680 pts/3  Sl+  20:22   0:02 python3 gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
    jovyan       746  3.4  0.9 1292352 142676 pts/3  Sl+  20:22   0:02 python3 gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
    jovyan       747  3.4  0.9 1292372 142684 pts/3  Sl+  20:22   0:02 python3 gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
    jovyan       748  3.4  0.9 1292372 142680 pts/3  Sl+  20:22   0:02 python3 gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
    jovyan       788  0.0  0.0   6436   672 pts/2    S+   20:23   0:00 grep gunicorn
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > ❓ Pourquoi y a-t-il 5 processus <code>gunicorn</code> alors que nous en avons demandé que 4 ?

    Il y a toujours un processus `gunicorn` de **load balancing** (équilibrage de charge), c'est-à-dire celui qui va redistribuer les requêtes parmi les 4 instances de `gunicorn` et redémarrer ceux qui sont en échec. Le dernier processus `grep unicorn` est simplement la fonction de recherche Bash que l'on exécute en appelant la commande ci-dessus.

    Certains arguments peuvent être choisis pour `gunicorn` afin de configurer plus spécifiquement notre API.

    - `--workers` indique le nombre d'instances qui seront exécutées en parallèle.
    - `--bind` va définir sur quel hôte et quel port le processus principal va écouter.
    - `-D` permet de spécifier l'exécution en daemon, c'est-à-dire en arrière-plan.
    """)
    return


app._unparsable_cell(
    r"""
    gunicorn --workers 4 --bind 127.0.0.1:5000 -D app:app
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Une fois terminé, nous pouvons tuer les processus `gunicorn` avec la commande suivante.

    Cette commande n'est disponible que pour les personnes syant fait le tp sur linux
    """)
    return


app._unparsable_cell(
    r"""
    pkill gunicorn
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div class="alert alert-block alert-info">
        Lorsque l'on développe une API, des outils comme <a href="https://www.postman.com/" target="_blank">Postman</a> sont utilisés pour simuler un environnement réel en prenant en charge plusieurs méthodes, en-têtes, cookies et autres fonctionnalités.
    </div>

    Avant de terminer, n'oublions pas les bonnes pratiques d'ingénierie logicielle.

    - Le code source doit être versionné avec `git`.
    - Des tests unitaires doivent être rédigés.
    - Une spécification (documentation) de l'API doit être produite.

    Les deux derniers point pourront être laissés en exercice. Nous allons uniquement faire le versioning ici.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous allons créer le fichier `.gitignore` : il s'agit d'une fichier lu par Git qui permet de ne pas ajouter des fichiers ou dossiers dans le versioning. C'est particulièrement utile pour les fichiers de configuration locale (`venv`, `.env` et `__pycache__` par exemple) mais également pour **ne pas envoyer les secrets et mot de passe au dépôt Git**.

    ```.gitignore
    conf/**
    .env
    venv/
    __pycache__/
    *.py[cod]
    *$py.class
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Maintenant, vous allez devoir créer un nouveau répertoire Github pour ce projet d'inférence
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme toujours, effectuons les manipulations Git.

    ```
    git init
    git add .
    git remote add <GIT>
    git commit -am "First release"
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Tout comme nous l'avions fait pour le projet `purchase_predict`, nous allons **créer une nouvelle branche** staging.

    ```
    git checkout -b staging

    # On pousse vers le dépôt sur la branche staging
    git push -u origin staging
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Les deux pipelines ML et de production sont correctement séparés avec MLflow comme système de centralisation.

    - Nous avons développé la structure de notre API.
    - Nous l'avons exécuté en local et testé par l'intermédiaire de requêtes HTTP.

    > ➡️ Notre API s'exécute correctement, mais en local ! Cela signifie que pour l'instant, cette dernière n'est pas accessible. Il faut donc l'exécuter <b>sur un serveur</b>, et c'est à partir de maintenant que commence véritablement le déploiement de l'API.
    """)
    return


if __name__ == "__main__":
    app.run()
