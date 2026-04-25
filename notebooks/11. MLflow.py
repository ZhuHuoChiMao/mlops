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
    **MLflow** est une plateforme open source qui permet de gérer le cycle de vie des modèles de Machine Learning. En particulier, grâce à MLflow, les modèles qui ont été entraînés à une date spécifique ainsi que les hyper-paramètres associés pourront être stockés, monitorés et ré-utilisés de manière efficace.

    <img src="https://dv495y1g0kef5.cloudfront.net/training/data_engineer_uber/img/mlflow.png" width="300" />

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Découvrir les concepts importants de MLflow</li>
        <li>Tracker et monitorer des modèles en local</li>
        <li>Installer MLflow sur un serveur et envoyer les modèles sur le serveur</li>
    </ul>
    </blockquote>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Concepts de MLflow

    Rappelons-nous du workflow en Machine Learning : la première étape de collecte des données et suivie d'une étape de transformation des données, puis de la modélisation pour maximiser une métrique de performance qui jugera de la qualité de l'algorithme employé. Être productif avec du Machine Learning n'est pas de tout repos pour les raisons suivantes.

    - **Il est difficile de garder un trace des précédentes expériences**. Une chose à laquelle beaucoup de Data Scientists font face, c'est de faire une série d'expériences en modifiant algorithmes et paramètres, mais qui peut s'avérer contre-productif si l'on ne dispose pas de l'historique des modèles et de leurs performances. Bien que Kedro puisse tendre vers cette pratique, il ne permet pas de le faire entièrement à lui tout seul.
    - **Il est difficile de reproduire le code**. Dans les projets Data Science, une multitude de fonctions permettent d'arriver à un résultat bien précis : le changement de quelques lignes de code peut grandement affecter le modèle et ses performances.
    - **Il n'y a aucun standard sur le packaging et le déploiement de modèles**. Chaque équipe possède son approche pour déployer les modèles, et ce sont souvent les grandes équipes avec de l'expérience qui peuvent se le permettre.
    - **Il n'y a aucun point central pour gérer les modèles**. En pratique, la solution naïve consiste à sauvegarder les paramètres dans des fichiers sur le même serveur hébergeant l'algorithme, en stockage local avec Kedro.

    MLflow cherche à améliorer la productivité en offrant la possibilité de ré-entraîner, ré-utiliser et déployer des modèles en agissant sur un point central (plateforme MLflow) où tout l'historique du modèle sera conservé.

    Tout d'abord, MLflow est *language-agnostic*, c'est-à-dire que les modèles peuvent être codés en Python, R, Java ou encore C++ et envoyés sur MLflow. Ensuite, il n'y a aucun pré-requis concernant la librairie de Machine Learning : que vous soyez adeptes de `scikit-learn` ou de `tensorflow`, tout sera compatible.

    Quatre composants résident sous MLflow.

    - **MLflow Tracking** est l'API et l'interface utilisateur pour logger les hyper-paramètres, le versioning de code et les *artifacts* (paramètres du modèle, fichier de poids, ...).
    - **MLflow Projects** est un format standard pour package un code source et le ré-utiliser dans plusieurs projets.
    - **MLflow Models** est un format de packaging pour les modèles de Machine Learning.
    - **MLflow Registry** est le registre de modèle (comme un git de modèles) qui permet de s'assurer que les modèles respectent certaines contraintes.

    Hormis le composant *Projects*, qui est remplacé par l'utilisation de Kedro, nous utiliserons tous les composants de MLflow pour gérer efficacement le cycle de vie des modèles.

    Pour installer MLflow en local, il suffit juste d'exécuter `uv add mlflow` dans le terminal.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// danger | Mise en garde, MLflow et UV !

    Depuis la version 3.1.0 de MLFlow, il y a un bug d'exécution de MLFlow avec UV. Ils ont fait une refactorisation du fonctionnement des tâches annexes cron-job via Huey.

    Comme ils ont mal fait la refacto et qu'il veulent absolument rester en pip natif, la version que nous utiliserons sera la 3.0.1.

    Pour installer une version spécifique de mlflow nous utiliserons la commande suivante :
    ```
    uv pip install "mlflow==3.0.1"
    ```

    Vous pouvez suivre l'évolution du problème ici : https://github.com/mlflow/mlflow/issues/21062
    ///
    """)
    return


@app.cell
def _():
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick
    import seaborn as sns
    import mlflow
    import mlflow.sklearn
    from lightgbm.sklearn import LGBMClassifier  # Wrapper pour scikit-learn
    from mlflow.models import infer_signature
    from sklearn.metrics import (
        f1_score,
        PrecisionRecallDisplay,
        precision_recall_curve,
    )

    # Mettez le chemin de votre kedro local ici, nous allons lancer les cellules pour la suite
    path_kedro = "/Users/noobzik/Documents/Kaggle/purchase-predict/"
    X_train = pd.read_csv(
        os.path.expanduser(path_kedro + "data/05_model_input/X_train.csv")
    )
    X_test = pd.read_csv(
        os.path.expanduser(path_kedro + "data/05_model_input/X_test.csv")
    )
    y_train = pd.read_csv(
        os.path.expanduser(path_kedro + "data/05_model_input/y_train.csv")
    ).values.flatten()
    y_test = pd.read_csv(
        os.path.expanduser(path_kedro + "data/05_model_input/y_test.csv")
    ).values.flatten()
    return (
        LGBMClassifier,
        PrecisionRecallDisplay,
        X_test,
        X_train,
        f1_score,
        infer_signature,
        mlflow,
        mtick,
        os,
        plt,
        precision_recall_curve,
        y_test,
        y_train,
    )


@app.cell
def _(X_test, X_train):
    int_columns = [
        "product_id",
        "brand",
        "num_views_session",
        "num_views_product",
        "category",
        "sub_category",
        "hour",
        "minute",
        "weekday",
        "duration",
        "num_prev_sessions",
        "num_prev_product_views",
    ]
    X_train[int_columns] = X_train[int_columns].astype("float64")
    X_test[int_columns] = X_test[int_columns].astype("float64")
    # Hyper-paramètres des modèles
    hyp_params = {
        "num_leaves": 60,
        "min_child_samples": 10,
        "max_depth": 12,
        "n_estimators": 100,
        "learning_rate": 0.1,
    }
    return (hyp_params,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour lancer le serveur de MLFlow (surtout ne pas l'executer dans ce notebook, mais en dehors du notebook)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    mlflow server --default-artifact-root ./mlruns
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous allons ensuite lancer un *experiment* sous MLflow. Pour cela, créons une nouvelle expérience que l'on nommera `purchase_predict`.
    """)
    return


@app.cell
def _(
    LGBMClassifier,
    X_test,
    X_train,
    f1_score,
    hyp_params,
    infer_signature,
    mlflow,
    y_test,
    y_train,
):
    # Identification de l'interface MLflow
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("purchase_predict")
    with mlflow.start_run() as run:
        model = LGBMClassifier(**hyp_params, objective="binary", verbose=-1)
        model.fit(X_train, y_train)
        score = f1_score(y_test, model.predict(X_test))
        mlflow.log_params(hyp_params)
        mlflow.log_metric("f1", score)
        print(mlflow.get_artifact_uri())
        signature = infer_signature(
            X_train, model.predict(X_train)
        )  # On calcule le score du modèle sur le test
        input_example = X_test.iloc[0:1].copy()
        mlflow.log_artifact("data/04_feature/transform_pipeline.pkl")
        mlflow.sklearn.log_model(
            model, "model", signature=signature, input_example=input_example
        )  # Inférer la signature du modèle
    return (run,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En exécutant ce code, nous avons déclencé un **run** avec `mlflow.start_run()`. L'intérêt d'utiliser `with` est qu'en sortant de l'indentation, le run MLflow sera automatiquement terminé. Nous allons envoyer plusieurs informations vers MLflow.

    - Les hyper-paramètres du modèle avec `log_params`.
    - La ou les métriques obtenues sur un échantillon avec `log_metric`.
    - Le modèle au format de `scikit-learn` avec `log_model`.

    En visualisant l'interface web MLflow</a>, nous voyons le modèle apparaître avec les informations associées.

    ![alt](public/mlflow1.png)

    En cliquant sur la date d'exécution, nous avons accès à plus de détails ainsi qu'aux fichiers stockés (ici le modèle), que l'on appelle des **artifacts**.

    ![alt](public/mlflow2.png)

    À noter qu'il est également possible de récupérer l'historique des modèles entraînés.
    """)
    return


@app.cell
def _(run):
    from mlflow.tracking import MlflowClient

    client = MlflowClient(tracking_uri="http://127.0.0.1:5000")

    client.get_metric_history(run.info.run_id, key="f1")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour utiliser efficacement MLflow, il faut architecturer le code source afin qu'il soit ré-utilisable et facilement manipulable par les Data Scientists.
    """)
    return


@app.cell
def _(
    LGBMClassifier,
    PrecisionRecallDisplay,
    X_test,
    X_train,
    f1_score,
    hyp_params,
    infer_signature,
    mlflow,
    mtick,
    os,
    plt,
    precision_recall_curve,
    y_test,
    y_train,
):
    def save_pr_curve(X, y, model):
        plt.figure(figsize=(16, 11))
        prec, recall, _ = precision_recall_curve(
            y, model.predict_proba(X)[:, 1], pos_label=1
        )
        pr_display = PrecisionRecallDisplay(precision=prec, recall=recall).plot(
            ax=plt.gca()
        )
        plt.title("PR Curve", fontsize=16)
        plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
        plt.savefig(os.path.expanduser("data/pr_curve.png"))
        plt.close()


    def train_model_local(params):

        with mlflow.start_run() as run:
            model = LGBMClassifier(**params, objective="binary", verbose=-1)
            model.fit(X_train, y_train)

            score = f1_score(y_test, model.predict(X_test))
            save_pr_curve(X_test, y_test, model)

            mlflow.log_params(hyp_params)
            mlflow.log_metric("f1", score)
            mlflow.log_artifact(
                os.path.expanduser("data/pr_curve.png"), artifact_path="plots"
            )

            # Inférer la signature du modèle
            signature = infer_signature(X_train, model.predict(X_train))
            input_example = X_test.iloc[0:1].copy()

            mlflow.sklearn.log_model(
                model, "model", signature=signature, input_example=input_example
            )

    return (save_pr_curve,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    À chaque appel de la fonction `train_model`, une instance du modèle est entraînée sur la base d'entraînement avec des hyper-paramètres spécifiques. La fonction `save_pr_curve` développée permet d'enregistrer le graphique de la courbe PR dans un fichier. Cela permet notamment d'envoyer les graphiques à MLflow sous forme d'artifacts.

    Chaque appel de la fonction `train_model` va donc entraîner un modèle LightGBM, en calculer des métriques, des graphiques et envoyer le résultats sous forme de run sur MLflow.
    """)
    return


@app.cell
def _(hyp_params, train_model):
    train_model({**hyp_params, **{"n_estimators": 200, "learning_rate": 0.05}})
    train_model({**hyp_params, **{"n_estimators": 500, "learning_rate": 0.025}})
    train_model({**hyp_params, **{"n_estimators": 1000, "learning_rate": 0.01}})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Après exécution, les trois runs sont bien présents.

    ![alt](public/mlflow3.png)

    Là-aussi, en explorant un run en particulier, nous pouvons voir apparaître le graphique dans l'explorateur de fichiers.

    ![alt](public/mlflow4.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Installation sur un serveur

    ## Première étape : Créer un service account spécifique à MLFlow

    Les paramètres part défaut du Service Account de Compute Engine n'est pas adapté pour le serveur MLFlow. Nous avons besoin d'accéder à plusieurs services de GCP en même temps.

    Voici donc la configuration à avoir pour le service account de Mlflow

    ![alt](public/mlflow_service_account.png)

    ## La mise en place de la VM G1-Small de MLflow

    Pour être pleinement exploité, MLflow **doit être installé sur un serveur** : en plus de pouvoir collaborer à plusieurs, cela permettra de l'intégrer dans un écosystème avec un système de stockage de fichiers et de processus automatisés.

    Lançons une VM depuis Google Cloud avec Debian 12 avec une instance de type `g1-small`.
    - Pour cela, il faut cliquer sur `N1`et dans type de machine, il faut cliquer `Coeur Partagé` `g1-small`
    - Ensuite autorisuer le traffic HTTP et HTTPS
    - Et ne surtout pas oublier de changer le Service Account vers MLFlow que nous vennons de créer. Oublier de le faire vous impose de supprimer la VM et recommencer la création de la VM.

    ![alt](public/ec2-1.png)

    N'oubliez pas d'autoriser le trafic HTTP et HTTPS pour le besoin de ce TP.
    """)
    return


app._unparsable_cell(
    r"""
    ```
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
    uv venv
    source .venv/bin/activate
    uv pip install mlflow google-cloud-storage
    ```
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Par défaut, les artifacts sont stockés dans le système local où est exécuté le code Python : MLflow ne peut donc pas recevoir et afficher ces artifacts. Il est donc nécessaire de configurer un bucket dans lequel MLflow pourra stocker et retrouver les artifacts que l'on enverra.

    Par défaut, MLflow étant installé sur une VM dans notre projet Google Cloud, les autorisations sont déjà présentes sur la machine, permettant à MLflow de lire des fichiers depuis le bucket. En revanche, il est nécessaire de définir les autorisations pour les applications qui vont envoyer ou récupérer des modèles vers MLflow. Pour des raisons de sécurité, nous allons ajouter un compte de service qui aura un rôle de lecture et écriture sur ce bucket uniquement.

    Rajoutons un compte de service qui aura les deux rôles suivants : **Créateur des objets de l'espace de stockage** et **Lecteur des objets de l'espace de stockage**. Pour terminer, nous allons créer une clé et conserver en lieu sûr le fichier JSON.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/mlflow5.png" />

    Pour s'assurer de la bonne exécution de MLflow, il est préférable de créer un `systemd` plutôt que de lancer MLflow en arrière plan depuis le terminal.
    """)
    return


app._unparsable_cell(
    r"""
    sudo nano /etc/systemd/system/mlflow.service
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - Il faut penser à modifier le nom du bucket `gs://<name-user>/mlflow`
    - Ainsi que le nom du ExecStart
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    [Unit]
    Description=MLflow
    After=network.target

    [Service]
    Restart=on-failure
    RestartSec=30
    ExecStart=/home/<user-name>/.venv/bin/mlflow server --default-artifact-root gs://<gcs_bucket_name_here>/mlflow --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 80


    [Install]
    WantedBy=multi-user.target
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// attention | Attention!
    Si vous utilisez une version supérieur à 3.0.1, ajoutez --allowed-hosts "*"
    C'est du au passage au backend Huey, mentionné précédenement.

    Gardez à l'esprit que MLflow supérieur à 3.0.1 via UV ne fonctionnera pas
    ///

    - Si vous deviez ré-installer `mlflow`, supprimez le document `sudo rm /mlflow.db`
    Elle se trouve à la racine du disque.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La dernière étape consiste à activer le service et à l'exécuter. Avec `daemon-reload`, nous activons le service MLflow.
    """)
    return


app._unparsable_cell(
    r"""
    sudo systemctl daemon-reload
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Toujours dans la gestion des services Cloud, il faut appréhender le cas d'un redémarrage de la VM et relancer automatiquement le service MLflow au démarrage.
    """)
    return


app._unparsable_cell(
    r"""
    sudo systemctl enable mlflow
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Puis on lance le service.
    """)
    return


app._unparsable_cell(
    r"""
    sudo systemctl start mlflow
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Maintenant, en visitant la page web à l'adresse IP externe de la VM, l'interface MLflow apparaît.

    Ajoutons la clé JSON que nous avons téléchargé, vers le dossier data
    """)
    return


@app.cell
def _():
    # magic command not supported in marimo; please file an issue to add support
    # %%writefile data/mlflow-key.json
    # # Insérez votre clé ici
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour spécifier vers quel serveur nous allons envoyer les artifacts et le modèle, il faut spécifier le nom de domaine ou l'adresse IP avec `set_tracking_uri`.
    """)
    return


@app.cell
def _(mlflow, os):
    from google.cloud import storage

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(
        "notebooks/mlflow.json"
    )
    mlflow.set_tracking_uri("http://136.114.127.11:80")
    # Authentification à Google Cloud avec la clé correspondant au compte de service MLflow
    # Nouvel URI de l'interface MLflow
    client = storage.Client()  # Mettez l'adresse de Google Compute Engine ici
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Créons une nouvelle expérience sur le serveur MLflow et exécutons un *run*.
    """)
    return


@app.cell
def _(
    LGBMClassifier,
    X_test,
    X_train,
    f1_score,
    hyp_params,
    infer_signature,
    mlflow,
    os,
    save_pr_curve,
    y_test,
    y_train,
):
    mlflow.set_experiment("purchase_predict")


    def train_model(params):
        with mlflow.start_run() as run:
            model = LGBMClassifier(**params, objective="binary", verbose=-1)
            model.fit(X_train, y_train)
            score = f1_score(y_test, model.predict(X_test))
            save_pr_curve(X_test, y_test, model)
            mlflow.log_params(hyp_params)
            mlflow.log_metric("f1", score)
            mlflow.log_artifact(
                os.path.expanduser("data/pr_curve.png"), artifact_path="plots"
            )
            signature = infer_signature(X_train, model.predict(X_train))
            input_example = X_test.iloc[0:1].copy()
            mlflow.sklearn.log_model(
                model,
                name="model",
                signature=signature,
                input_example=input_example,
            )

    return (train_model,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dorénavant, toutes les exécutions seront envoyés sur le serveur contenant MLflow et les artifacts stockés dans le bucket associé.
    """)
    return


@app.cell
def _(hyp_params, train_model):
    train_model({**hyp_params, **{"n_estimators": 200, "learning_rate": 0.05}})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Et voilà ! L'interface MLflow devrait à présent afficher le modèle stocké sur Google Storage.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Nous pouvons désormais tracker les modèles de Machine Learning avec MLflow.

    - Nous avons utilisé MLflow en local pour tracker les modèles.
    - Nous avons installé MLflow sur un serveur en stockant les artifacts sur un Cloud Storage.

    > ➡️ Maintenant que nous avons notre modèle de Machine Learning et un versioning de modèle, nous pouvons mettre en place une API pour exposer le modèle.
    """)
    return


if __name__ == "__main__":
    app.run()
