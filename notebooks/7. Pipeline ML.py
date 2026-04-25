import marimo

__generated_with = "0.20.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme nous venons de le voir, Kedro est un outil puissant. Le premier pipeline que nous avons construit permettait d'encoder les données pour qu'elles soit utilisées par un modèle. Pour continuer à construire le pipeline ML, nous allons définir ici le **pipeline d'entraînement de modèles**, qui pourra être combiné avec celui que nous avons déjà fait sur l'encodage.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Développer le pipeline d'entraînement de modèles</li>
        <li>Construire le pipeline ML de la collecte des données jusqu'à la modélisation</li>
        <li>Appliquer les bonnes pratiques de développement</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/l46CwEYnbFtFfjZNS/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Entraînement du modèle

    Nous avions appliqué de l'AutoML sur un LightGBM avec des Jupyter Notebooks (Bon dans notre cas sous Marimo). (En tout cas pour les classes concernées cela correspond à l'optimisation des hyper-paramètres ainsi que sur l'explicabilité des modèles).

    Notre objectif est maintenant de le faire directement dans le projet Kedro. Nous allons construire un pipeline nommé `training` qui est chargé de de déterminer un modèle optimal.

    /// admonition |

    Dans la construction, le pipeline <code>training</code> intervient après le pipeline <code>processing</code>, mais l'intérêt de séparer le pipeline ML en deux est de pouvoir exécuter un seul des deux pipelines au besoin.
    ///

    Nous n'allons pas créer de dossier `training`, nous allons à la place utiliser les commandes de `kedro` pour créer une pipeline que l'on nomme `training`.

    Pour cela utilisez la commande suivante :
    ```
    uv run kedro pipeline create training
    ```

    Notre premier fichier `nodes.py` contient toutes les fonctions nécessaires pour entraîner le module. Pour améliorer la productivité et faciliter la maintenance du code, nous allons y créer trois fonctions.

    - La première fonction `train_model` va entraîner une instance de modèle selon des hyper-paramètres spécifiques sur un ensemble d'entraînement.
    - La seconde fonction `optimize_hyp` va déterminer les hyper-paramètres qui maximisent le score d'un modèle à partir d'une métrique spécifique.
    - La dernière fonction `auto_ml` sera ensuite utilisée par le node Kedro pour entraîner un modèle optimisé.

    Commençons par importer les librairies nécessaires aux fonctions que nous développerons.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    import numpy as np
    import pandas as pd

    from collections.abc import Callable

    from sklearn.base import BaseEstimator, clone
    from sklearn.metrics import f1_score
    from sklearn.model_selection import RepeatedKFold

    from lightgbm.sklearn import LGBMClassifier

    from typing import Any
    from hyperopt import hp, tpe, fmin

    import warnings
    warnings.filterwarnings('ignore')
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ensuite, nous allons définir notre `ModelSpec` que nous avons vu pendant l'optimisation des hyper-paramètres.

    Nous rappelons le code ici :

    ```py
    class ModelSpec(TypedDict, total=True):
        name: str
        model_class: Callable[..., Any]  # Covers LGBMClassifier()
        params: dict[str, Any]  # Accepts hp.uniform etc.
        override_schemas: dict[str, type]
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Créons une variable `MODELS` dans laquelle nous allons spécifier une liste de modèles candidats. Pour commencer, nous n'utiliserons qu'un seul modèle LightGBM, mais nous pourrions également calibrer d'autres modèles comme XGBoost, CatBoost, Random Forest. Nous définissons un dictionnaire pour chaque modèle.

    - `name` est le nom du modèle.
    - `class` est l'objet Python permettant d'instancier le modèle.
    - `params` représente l'espace de recherche pour l'optimisation des hyper-paramètres.
    - `override_schemas` est un champ qui contient les hyper-paramètres dont le type doit être modifié avant d'entraîner le modèle.

    Par exemple, l'hyper-paramètre `max_depth` doit être entier, mais un point de l'espace peut produire un flottant ($10.0$ au lieu de $10$). Dans ce cas, il faut forcer la conversion en entier pour éviter une erreur générée par LightGBM.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
    # Type the MODELS list
    MODELS: list[ModelSpec] = [
        {
            "name": "LightGBM",
            "model_class": LGBMClassifier,
            "params": {
                "objective": "binary",
                "verbose": -1,
                "learning_rate": hp.uniform("learning_rate", 0.001, 1),
                "num_iterations": hp.quniform("num_iterations", 100, 1000, 20),
                "max_depth": hp.quniform("max_depth", 4, 12, 6),
                "num_leaves": hp.quniform("num_leaves", 8, 128, 10),
                "colsample_bytree": hp.uniform("colsample_bytree", 0.3, 1),
                "subsample": hp.uniform("subsample", 0.5, 1),
                "min_child_samples": hp.quniform("min_child_samples", 1, 20, 10),
                "reg_alpha": hp.choice("reg_alpha", [0, 1e-1, 1, 2, 5, 10]),
                "reg_lambda": hp.choice("reg_lambda", [0, 1e-1, 1, 2, 5, 10]),
            },
            "override_schemas": {
                "num_leaves": int,
                "min_child_samples": int,
                "max_depth": int,
                "num_iterations": int,
            },
        }
    ]
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// note
    Si nous tentons de faire la suite en comparant directement le bon typage de notre classe via `"class"`, le `astral/ty` de astral nous reverra l'erreur suivante :
    ```
    Error at model_conf = next(m for m in MODELS if isinstance(instance, m["class"]))
    Argument to function `isinstance` is incorrect: Expected `type | UnionType | tuple[Divergent, ...]`, found `Unknown | str | <class 'LGBMClassifier'> | dict[Unknown | str, Unknown | str | int] | dict[Unknown | str, Unknown | <class 'int'>]` (ty invalid-argument-type)
    ```

    Nous allons devoir créer une fonction qui vérifie le typage afin que faire taire cette erreur lancé par `ty`
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```python
    def get_model_config(instance: BaseEstimator) -> ModelSpec:
        "\"\"Returns the configuration dictionary for the given model instance."\"\"
        for model_spec in MODELS:
            model_cls: type = model_spec["model_class"]  # type: ignore (or guard below)
            if isinstance(model_cls, type) and isinstance(instance, model_cls):
                return model_spec
        raise ValueError(f"Unsupported model: {type(instance)}")
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Bien que le pipeline d'entraînement du modèle ne possédera qu'un node, nous pouvons tout à fait créer plusieurs fonctions dans le fichier `nodes.py` qui vont être appelées par la fonction du node.

    Commençons par la première fonction `train_model`.

    ```py
    def train_model(
        instance: BaseEstimator,
        training_set: tuple[np.ndarray, np.ndarray],
        params: dict[str, Any] | None = None,
    ) -> BaseEstimator:
        "\"\"
        Trains a new instance of model with supplied training set and hyper-parameters.
        "\"\"
        model_conf = get_model_config(instance)
        params = params or {}

        override_schemas = model_conf.get("override_schemas", {})
        for p in params:
            if p in override_schemas:
                params[p] = override_schemas[p](params[p])

        model = clone(instance)
        model.set_params(**params)
        model.fit(*training_set)
        return model
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme nous l'avons évoqué plus haut, nous forçons la conversion de certains hyper-paramètres. On récupère les noms des hyper-paramètres dont le type est surchargé, puis ils sont convertis vers le type cible (ici, uniquement des entiers). Le reste de la fonction est explicitive, car il s'agit juste d'instancier le modèle et d'appeler la fonction `fit`.

    Voyons maintenant la deuxième fonction `optimize_hyp`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
    def optimize_hyp(
        instance: BaseEstimator,
        dataset: tuple[pd.DataFrame, pd.Series],
        search_space: dict,
        metric: Callable[[Any, Any], float],
        max_evals: int = 40,
    ) -> dict:
        "\"\"
        Trains model's instances on hyper-parameters search space and returns most accurate
        hyper-parameters based on eval set.
        "\"\"
        X, y = dataset

        def objective(params):
            rep_kfold = RepeatedKFold(n_splits=4, n_repeats=1)
            scores_test = []
            for train_I, test_I in rep_kfold.split(X):
                X_fold_train = X.iloc[train_I, :]
                y_fold_train = y.iloc[train_I].values.flatten()
                X_fold_test = X.iloc[test_I, :]
                y_fold_test = y.iloc[test_I].values.flatten()
                # On entraîne une instance du modèle avec les paramètres params
                model = train_model(
                    instance=instance,
                    training_set=(X_fold_train, y_fold_train),
                    params=params,
                )
                # On calcule le score du modèle sur le test
                scores_test.append(metric(y_fold_test, model.predict(X_fold_test)))  # type: ignore[union-attr]

            return np.mean(scores_test)

        return fmin(fn=objective, space=search_space, algo=tpe.suggest, max_evals=max_evals)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Tout d'abord, nous récupérons la base d'apprentissage $(X, y)$ à partir de l'argument `dataset`. Nous définissons ensuite la fonction `objective` dont on cherche une minimisation. À chaque évaluation, elle réalise un $k$-Fold sur le modèle candidat, puis stocke le score, calculée à partir de la métrique, dans la liste `scores_test`.

    Cette liste contient tous les scores sur les ensembles de test du $k$-Fold. Ici, nous aurons uniquement $4$ scores à chaque exécution de la fonction. Nous retournons donc le score moyen des modèles sur les ensembles de test.

    Pour terminer, nous retournons le résultat de `fmin`, c'est-à-dire le jeu d'hyper-paramètres qui maximise la fonction `objective`.

    Enfin, la dernière fonction `auto_ml`, qui sera utilisée par le node Kedro.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
     def auto_ml(
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        max_evals: int = 40
    ) -> dict[str, BaseEstimator]:
        \"\"\"
        Runs training of multiple model instances and select the most accurated based on objective function.
        \"\"\"
        X = pd.concat((X_train, X_test))
        y = pd.concat((y_train, y_test))

        opt_models = []
        for model_specs in MODELS:
            # Finding best hyper-parameters with bayesian optimization
            optimum_params = optimize_hyp(
                model_specs["class"](),
                dataset=(X, y),
                search_space=model_specs["params"],
                metric=lambda x, y: -f1_score(x, y),
                max_evals=max_evals
            )
            print("done")
            # Training the supposed best model with found hyper-parameters
            model = train_model(
                model_specs["class"](),
                training_set=(X_train, y_train),
                params=optimum_params,
            )
            opt_models.append(
                {
                    "model": model,
                    "name": model_specs["name"],
                    "params": optimum_params,
                    "score": f1_score(y_test, model.predict(X_test)),
                }
            )

        # In case we have multiple models
        best_model = max(opt_models, key=lambda x: x["score"])
        return dict(model=best_model)

    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Il s'agit simplement d'une exéuction séquencée en plusieurs étapes. Pour chaque modèle candidat que l'on souhaite optimiser, il y a trois étapes.

    - On détermine les hyper-paramètres optimaux avec `optimize_hyp` sur la base d'apprentissage $(X, y)$.
    - Une fois les hyper-paramètres optimaux trouvés, une instance du modèle est calibré avec ces derniers sur le sous-échantillon d'entraînement.
    - Le score du modèle est calculé sur le sous-échantillon de test et stocké dans une liste.

    À la fin, la liste `opt_models` contiendra tous les modèles optimisé de chaque modèle candidat. Si l'on souhaite tester un LightGBM, un XGBoost et un CatBoost, alors `opt_models` contiendra trois éléments, chacun étant le modèle optimisé de la classe d'algorithme.

    Pour terminer, on tourne le meilleur modèle parmi tous les modèles optimisés.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Création du pipeline

    Dernière étape : construire le pipeline dans le fichier `pipeline.py`. Avant toute chose, nous allons définir le modèle (optimisé) dans le Data Catalog afin de l'enregistrer une fois entraîné. On utilise le type `pickle.PickleDataset` pour enregistrer un modèle au format binaire sur le disque.

    Ce qui donne

    ```
    model:
      type: pickle.PickleDataset
      filepath: data/06_model/model.pkl
    ```

    et dans le `parameters.yml`
    ```
    test_ratio: 0.3
    automl_max_evals: 10
    ```

    Pour la pipeline, il n'y a qu'un seul node à définir:

    ```py
    from kedro.pipeline import Node, Pipeline  # noqa
    from .nodes import auto_ml

    def create_pipeline(**kwargs) -> Pipeline:
        return Pipeline([
            Node(auto_ml,
                 [
                    "X_train",
                    "y_train",
                    "X_test",
                    "y_test",
                    "params:automl_max_evals"
                ],
                dict(model="model"),)
        ])
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/kedro3.png" />

    On installera les packages nécessaires avec `uv add lightgbm hyperopt` en vérifiant que l'on soit bien dans l'environnement virtuel.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Il ne reste plus qu'à exécuter le pipeline. Nous allons au total entraîner 40 modèles puisque nous avons un $4$-Fold et 10 itérations : le temps d'exécution sera d'environ 3 à 5 minutes.

    ```
    uv run kedro run --pipeline training
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// attention |
    Pour mettre à jour la visualisation des pipelines, il faut relancer le processus <code>uv run kedro viz</code> dans un terminal (on le stoppera au préalable avec <code>Ctrl+C</code>).
    ///

    ![alt](public/kedro3.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pipeline de chargement

    Dans le pipeline `processing`, on suppose que le jeu de données `primary.csv` existe déjà. Or, il s'agit pour l'instant du jeu de données **de l'échantillon**, et non de celui calculé sur un historique de 7 jours. Nous devons au préalable créer un troisième pipeline qui interviendra en tout premier.

    Nous allons créer une pipeline loading à l'aide des commandes suivantes :
    ```
    uv run kedro pipeline create loading
    ```

    Nous allons avoir le noeud suivant :

    ```python
    import pandas as pd
    import glob

    from google.cloud import storage


    def load_csv_from_bucket(project: str, bucket_path: str) -> pd.DataFrame:
        "\"\"
        Loads multiple CSV files from bucket (as generated from Spark).
        "\"\"
        storage_client = storage.Client()
        bucket_name = bucket_path.split("/")[0]
        folder = "/".join(bucket_path.split("/")[1:]) + "/part-"

        for blob in storage_client.list_blobs(bucket_name, prefix=folder):
            filename = blob.name.split("/")[-1]
            if filename[-3:] == "csv":
                blob.download_to_filename("/tmp/" + filename)

        all_files = glob.glob("/tmp/*.csv")
        li = []

        for filename in all_files:
            df = pd.read_csv(filename, index_col=None, sep=",")
            li.append(df)

        df = pd.concat(li, axis=0, ignore_index=True)
        return df
    ```

    Comme vous l'avez remarqué, nous utilisons Google Cloud Plateform pour ce TP. De ce fait, nous devons installer les paquets de GCP

    ```
    uv add google-cloud-storage
    ```

    Avec `storage_client`, nous téléchargeons en local dans le dossier `/tmp` (dossier de fichiers temporaires) tous les fichiers CSV dans le bucket spécifié. À l'aide de `glob`, nous parcourons tous ces fichiers téléchargés et les concaténons dans un seul et unique DataFrame `df`.

    Puisqu'il n'y a qu'un seul noeud, le pipeline est rapide à définir.

    ```python
    from kedro.pipeline import Pipeline, Node
    from .nodes import load_csv_from_bucket

    def create_pipeline(**kwargs):
        return Pipeline(
            [
                Node(
                    load_csv_from_bucket,
                    ["params:gcp_project_id", "params:gcs_primary_folder"],
                    "primary",
                )
            ]
        )
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous allons rajouter deux paramètres dans le fichier `parameters.yml`.

    - Le paramètre `gcp_project_id` contenant le nom du projet Google Cloud.
    - Le paramètre `gcs_primary_folder` qui donne **le dossier** contenant les fichiers CSV transformés, prêts à être encodés.
    ```
    gcp_project_id: "<PROJET_GCP>"
    gcs_primary_folder: "<NOM_DU_BUCKET>/primary.csv"
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En lançant la commande
    ```
    uv run kedro run --pipeline loading
    ```

    On se retrouve face à l'erreur suivante :
    ```
    DefaultCredentialsError: Your default credentials were not found. To set up Application Default Credentials, see
    https://cloud.google.com/docs/authentication/external/set-up-adc for more information.
    ```

    Nous devons configurer les crédentials de Google en local pour pouvoir faire fonctionner la pipeline de chargement.

    Mais avant de faire ces étapes, il faudra réaliser les actions suivantes:
    1. Créer son compte Google Cloud Plateform.
    /// attention |
    Au 8 février 2026, Google Cloud Plateform demande la fourniture d'une carte bleu, sous paiement de 10e, remboursable sur demande, afin de d'activer les essaies.
    ///
    /// Danger |
    En aucun cas vous devez cliquer sur un bouton similaire à "passer en compte payant" sous peine de facturation supplémentaire.
    ///
    3. Créer un bucket sur Google Cloud Storage (Le service équivalent sur AWS est S3)
        - Pour cela, il faut taper dans la barre de recherche S3, et cliquer sur `Bucket`, puis sur `Créer`, et laisser les paramètres par défault.
    4. Uploader les fichiers csv de "primary.csv" vers le bucket que vous venez de créer
     - Pour cela, il faut aller dans bucket, Importer des fichiers
     - Ouvrir un Terminal GCP et tapper les commande suivante (à adapter)
    ```
    gsutil cp gs://purchase_predict/primary.zip /tmp
    mkdir -p /tmp/primary
    unzip /tmp/primary.zip
    gsutil cp -r unzipped_content gs://purchase_predict/primary/
    ```
    5. Générer un Service Account pour le projet avec les accès à Google Cloud Storage

    6. Créer une clée d'authentification pour le PC Local
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Création d'un compte de service

    Une règle de sécurité en Cloud Computing consiste à créer des **rôles** en fonction des services et des cas d'utilisation. Sous GCP, les **comptes de services** permettent de définir des rôles aux applications qui vont faire appel à certains services, avec un certain niveau d'habilitation tout en garantissant une sécurité élevée.

    Nous allons nommer ce compte de service `purchase-predict` avec le rôle *Lecteur des objets de l'espace de stockage*, ce qui autorisera la lecture des données depuis l'extérieur.

    ![](public/pipeline_ml2.png)

    La description du compte de service n'est pas obligatoire, mais elle permet de présenter rapidement quelles applications vont utiliser ce compte de service car cela n'est pas toujours clair lorsqu'il y en a beaucoup.

    ![alt](public/pipeline_ml3.png)

    En sécurité du Cloud, il faut adopter le **principe du moindre privilège** : il faut donner uniquement les accès nécessaires, c'est-à-dire juste ce qu'il faut pour que l'application fonctionne, jamais plus.

    Après avoir crée le compte de service, nous pouvons créer une clé au format JSON et la télécharger.

    /// danger
    La clé du compte de service est équivalent à un mot de passe. Il ne faut jamais la divulguer ou la laisser dans un projet où Git ajouterai ce fichier à un dépôt distant.
    ///

    Heureusement pour nous, Kedro a prévu de cas de figure. Tous les mots de passes et clés de services, lorsqu'ils sont utilisé sur des environnement de développement, doivent être placés dans le dossier `conf/local`, qui est ignoré par Git. Ajoutons le fichier `service-account.json` dans ce dossier en insérant le contenu de la clé JSON téléchargée.

    Il reste maintenant à spécifier le chemin d'accès à la clé du compte de service dans la variable d'environnement `GOOGLE_APPLICATION_CREDENTIALS`. À noter que cette manipulation sera nécessaire **lorsque l'on démarre un nouveau terminal**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour intéger la clée sur linux
    ```
    export GOOGLE_APPLICATION_CREDENTIALS="conf/local/service-account.json"
    ```

    Pour intéger la clée sur windows
    ```
    set GOOGLE_APPLICATION_CREDENTIALS=conf/local/service-account.json
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Tout a bien fonctionné : le fichier `primary.csv` correspond bien au jeu de données construit avec PySpark.

    Au total, nous comptabilisons trois pipelines.

    - Le pipeline `loading` qui charger les fichiers CSV depuis le bucket Cloud Storage pour créer le fichier `primary.csv`.
    - Le pipeline `processing` qui va encoder le jeu de données `primary.csv`.
    - Le pipeline `training` qui va entraîner un modèle.

    L'avantage de la représentation de ces trois pipelines est **la flexibilité**. Si je souhaite ajouter un XGBoost par exemple, je n'aurai besoin que de relance le pipeline `training`. Si je change de méthodes d'encodages, je n'aurai pas besoin de relancer le pipeline `loading`. L'autre aspect important est **l'homogénéité des traitements** : en regroupant toutes les opérations dans trois pipelines, nous nous assurons que les données au tout début de la chaîne vont subir exactement le même traitement, quelle que soit la date d'exécution ou les données en entrée.

    Nous avons donc une pipeline globale, permettant de récupérer les données depuis GCS, nettoyer les données, entrainer un modèle via une recherche des meilleurs hyperparamètres.

    ![](public/pipeline_ml4.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Linting et Refactoring
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    À partir de maintenant, les codes qui vont être produits seront utilisés dans des environnements de production. Il est nécessaire que le code respecte les normes de PEP 8, telles que nous les avions vues avec ruff. Installons ce package.

    ```
    uv add --dev ruff
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous allons créer un fichier `ruff.toml` a la racine qui aurat les propriétés suivantes
    ```
    line-length = 120
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Linting et Refactoring

    Nous choisissons volontairement un nombre de caractères maximal à 120. La complexité, qui est un calcul réalisé en fonction du nombre d'identations maximales et de variables utilisées, est fixée à 16. Enfin, nous définissons les dossiers et fichiers à exclure de l'analyse.


    Executons ruff

    ```
    uv run ruff check src
    ```
    Des erreurs liée à la syntaxe devrait s'afficher

    En exécutant à nouveau `ruff` en ajoutant le `--fix`, le programme ruff applique automatiquement les correctifs

    ```
    Fixed 1 error:
    - src/purchase_predict/pipelines/processing/nodes.py:
        1 × F401 (unused-import)

    Found 1 error (1 fixed, 0 remaining).
    ```

    En lançant à nouveau la commande `ruff` initial, le message suivant devrait apparaître:
    ```
    All checks passed!
    ```
    signifiant que tous les codes sources respectent PEP 8.

    > ❓ Est-ce que l'on doit tout le temps exécuter ces deux commandes ?

    Les bonnes pratiques en développement logiciel, c'est de toujours publier un code qui respecte au maximum les normes, notamment PEP 8 dans le cas de Python. Le plus adéquat ici serait d'exécuter automatiquement `ruff check src --fix` à chaque commit de Git. Il y aurait alors deux possibilités.

    - Le code ne respecte pas la norme PEP 8, et le commit n'est pas accepté.
    - Le code respecte la norme PEP 8, et le commit est accepté **en local**.

    Il faudra ensuite pousser le code local vers le dépôt distant. Et tout ceci peut être réalisé avec `pre-commit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pre-commit
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La première action est de l'installer via uv
    ```
    uv add pre-commit
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ensuite, nous allons le configurer à l'aide de la commande
    ```
    uv run pre-commit install
    ```

    si vous obtenez l'erreur

    ```
    An error has occurred: FatalError: git failed. Is it installed, and are you in a Git repository directory?
    ```

    alors faites

    ```
    git init
    ```


    Le message suivant devrait s'afficher
    ```
    pre-commit installed at .git/hooks/pre-commit
    ```


    Pour intégrer ruff dans notre pre-commit, nous devons créer un nouveau fichier nommé `.pre-commit-config.yaml` a la racine

    ```
    repos:
      - repo: https://github.com/astral-sh/ruff-pre-commit
        # Ruff version.
        rev: v0.15.0
        hooks:
          # Run the linter.

          - id: ruff-check
            types_or: [python, pyi]
            # args: [--fix] # Permet d'appliquer le fix automatiquement
          # Run the formatter.

          - id: ruff-format
            types_or: [python, pyi]
    ```

    On va pouvoir dorénavant le tester :
    ```
    git add .
    git commit -am "Added linting and refactoring"
    ```

    pour avoir le résultat suivant
    ```
    ruff check...............................................................Passed
    ruff format..............................................................Passed
    ```

    Dorénavant, à la moindre modification de fichier, lors d'un commit, tous les codes Python seront inspectés.

    Il nous manque la dernière touche finale, c'est de push notre répertoire vers Github

    ```
    git push
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Notre pipeline ML est enfin réalisé avec Kedro.

    - Tout d'abord, nous avons construit le pipeline qui entraîne des modèles.
    - Ensuite, nous avons combiné une partie des pipelines (encodage et entraînement) en un seul.
    - Pour finir, nous avons appliqué les bonnes pratiques de développement en vérifiant les codes Python avec la norme PEP 8.
    """)
    return


if __name__ == "__main__":
    app.run()
