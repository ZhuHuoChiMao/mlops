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
    Il est temps d'organiser tout notre pipeline ML, qui est actuellement séparé dans plusieurs Notebooks. Pour nous aider, nous allons utiliser **Kedro**, un outil open-source permettant de créer des projets de Machine Learning reproductibles, maintenables et modulaires (i.e. plusieurs fichiers), le tout sans trop d'efforts. C'est donc un outil sur-mesure pour les ML Engineers !

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Créer un premier projet Kedro et comprendre son architecture</li>
        <li>Comprendre les concepts de Kedro</li>
        <li>Construire un premier pipeline de traitement de données</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/ZVUu5Pm23hDZS/giphy.gif" width="300" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Kedro

    Qu'est-ce que Kedro, et pourquoi avons-nous besoin de cet outil ?

    La méthode classique pour construire des modèles de Machine Learning est d'utiliser Jupyter Notebook dans les temps de la préhistoire (soit avant 2022). Mais cette méthode n'est pas du tout viable, notamment lorsqu'il s'agit de déployer le modèle en production dans un futur proche. Face à cette situation, on préfère donc construire un projet entier, dont les Notebooks sont en réalité des phases de recherche, d'expérimentation mais ne constituent pas en soi le coeur de sujet du projet. Dès lors que l'on met en place une architecture de code source, il est nécessaire d'adopter de bonnes pratiques, aussi bien héritées des environnements IT que celles utilisées par les Data Scientists.

    ![kedro.png](https://kedro.org/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fzwej9aiux6b9%2F66Z0PVvj5UD0FL4KzlXv7h%2F28712a7f7b62a4dd5ace9f0c1a85e4b7%2Fkedro-horizontal-color-on-light.png&w=3840&q=75)

    Kedro a été développé pour appliquer ces bonnes pratiques tout au long d'un projet de Machine Learning.



    - Éviter au maximum de dépendre de Jupyter Notebooks qui empêche la production d'un code source maintenable et reproductible.
    - Améliorer la collaboration entre les différents acteurs (Data Scientists, Data Engineers, DevOps) aux compétences diverses dans un projet.
    - Augmenter l'efficacité en appliquant la modularité du code, les séparations entre les données et leur utilisation ou encore en optimisant les exécutions de traitements atomiques.

    En bref, Kedro nous permet d'avoir un projet Python **entièrement pensé** pour le Machine Learning et optimisé dans ce sens. Il existe d'autres alternatives à Kedro (comme Kubeflow qui se base sur Kubernetes), mais il a l'avantage d'être rapide à prendre en main et possède une communauté déjà active.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition |
    Les temps changent !

    En effet, les jupyter notebook sont progressivement remplacés par des alternatives répondant à ce problème. C'est le cas notament de Marimo. La particularité de Marimo réside sur le fait que les cellules sont encapsulé par des méthodes. Elle va donc déterminer automatiquement l'ordre d'execution des cellules, comme à l'image des graphes d'exécutions.

    L'utilisation de Marimo dans le cadre de ce cours vous facilitera la transition d'un code sous la forme de cellules, vers un code en production via Kedro.

    Cependant, cette conversion d'un marimo vers un kedro ne vous sera pas démontré.

    A vour de l'appliquer dans vos futures projets. Vous verrez que chaque cellule est sous la forme d'une fonction si vous ouvrez un notebook marimo à l'aide d'un éditeur de code de votre choix.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Premiers pas avec Kedro

    Essayons de créer un premier projet avec Kedro que nous allons nommer `purchase-predict`.

    Créons un nouveau terminal et un nouveau projet Kedro.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `uvx --python 3.12 kedro new`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// danger
    Au 8 février 2026, tout projet de Data Science en production doit impérativement être sous version python 3.12.

    En effet, c'est la version qui assure une compatibilité globale de l'ensemble des paquets que vous êtes amenés à utiliser !

    Certains développeurs n'ont pas encore migré leur code source vers python 3.14, c'est notament le cas de Kedro.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. Il nous est demandé un nom de projet. Nous metterons la valeur `purchase-predict`.
    2. Au niveau des `projet tools`, nous saissons la valeur `1-5`
    3. Et nous n'allons pas générer de pipelines
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    Project Name
    ============
    Please enter a name for your new project.
    Spaces, hyphens, and underscores are allowed.
    To skip this step in future use --name
     [New Kedro Project]: purchase-predict

    Project Tools
    =============
    These optional tools can help you apply software engineering best practices.
    To skip this step in future use --tools
    To find out more: https://docs.kedro.org/en/stable/starters/new_project_tools.html

    Tools
    1) Lint: Basic linting with Ruff
    2) Test: Basic testing with pytest
    3) Log: Additional, environment-specific logging options
    4) Docs: A Sphinx documentation setup
    5) Data Folder: A folder structure for data management
    6) PySpark: Configuration for working with PySpark

    Which tools would you like to include in your project? [1-6/1,3/all/none]:
     [none]: 1-5

    Example Pipeline
    ================
    Select whether you would like an example spaceflights pipeline included in your project.
    To skip this step in the future use --example=y/n
    To find out more: https://docs.kedro.org/en/stable/starters/new_project_tools.html

    Would you like to include an example pipeline? [y/N]:
     [no]: no

    Congratulations!
    Your project 'purchase-predict' has been created in the directory
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ce qui nous donne l'architecture des dossiers suivants :
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    ├── conf
    │   ├── base
    │   │   ├── catalog.yml
    │   │   ├── credentials.yml
    │   │   ├── logging.yml
    │   │   └── parameters.yml
    │   ├── local
    │   └── README.md
    ├── data
    │   ├── 01_raw
    │   ├── 02_intermediate
    │   ├── 03_primary
    │   ├── 04_feature
    │   ├── 05_model_input
    │   ├── 06_models
    │   ├── 07_model_output
    │   └── 08_reporting
    ├── docs
    │   └── source
    │       ├── conf.py
    │       └── index.rst
    ├── logs
    │   └── journals
    ├── notebooks
    ├── pyproject.toml
    ├── README.md
    ├── setup.cfg
    └── src
        ├── purchase_predict
        │   ├── cli.py
        │   ├── hooks.py
        │   ├── __init__.py
        │   ├── pipelines
        │   │   └── __init__.py
        │   ├── run.py
        │   └── settings.py
        ├── requirements.txt
        ├── setup.py
        └── tests
            ├── __init__.py
            ├── pipelines
            │   └── __init__.py
            └── test_run.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Détaillons tout d'abord chaque dossier de premier niveau.

    - `conf` contient tous les fichiers de configuration des paramètres (code, modèle) ainsi que les clés et secrets nécessaires.
    - `data` contient plusieurs dossiers qui correspondent aux données utilisées ou produits à chaque étape du pipeline (base d'apprentissage, matrices des *features*, modèle sérialisé).
    - `docs` contient des fichiers de documentation.
    - `logs` contient les journaux d'événements de Kedro.
    - `notebooks` permet de stocker des notebooks.
    - `src` contient tous les codes nécessaire pour créer les pipelines.
    - `tests` contient les tests unitaires.

    C'est notamment dans le dossier `src` que nous développerons les briques élémentaires et que nous les connecterons ensembles afin de former les différents pipelines.
    Avant de pouvoir commencer à travailler sur ce répertoire, nous devons initialiser un environnement virtuel python, généré par Kedro

    Pour cela nous tapons la commande `uv sync`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Concepts de Kedro

    Kedro ne se contente pas uniquement de créer un projet : il va également apporter des fonctionnalités très puissantes qui en font sa popularité.

    ### Data Catalog

    Pour utiliser des données tout au long d'un pipeline ML, il est déconseillé d'inscrire des chemins d'accès en dur dans le code. Il est préférable d'attribuer des noms à des données existantes que l'on utilise ou celles que l'on crée. C'est rôle du Data Catalog : nous allons définir en amont des référentiels de données avec des noms associés. Le Data Catalog est référencé dans le fichier `conf/base/catalog.yml`.

    Par défaut, Kedro propose plusieurs sous-dossiers dans `data` qui permet de mieux organiser les données.

    - `raw`, `intermediate` et `primary` font référence aux données brutes, celles ayant subi des traitements intermédiaires et celles prêtes à être encodées.
    - `feature` contiendrait la base d'apprentissage $(X,y)$ encodée.
    - `model_input` contiendrait les échantillons d'entraînement et de test fournis au modèle.
    - `models` contiendrait le ou les modèles sérialisés.
    - `model_output` et `reporting` contiendraient les sorties du modèles ainsi que les graphes pour valider et interpéter.

    /// admonition |
    ℹ️ Bien entendu, nous ne sommes pas tenu de suivre exactement cette structure, il s'agit plutôt d'une organisation par défaut proposée par Kedro.
    ///

    Dans notre cas, nous n'allons pas effectuer la transformation des données avec Kedro, puisque ce sera une tâche Spark SQL qui en sera chargée. Ainsi, nous aurons uniquement le données transformé qui subira ensuite l'encodage. Nous considérons donc que l'échantillon que recevra Kedro sera situé dans `primary` et sera nommé `primary.csv`.

    À partir de ces données `primary.csv`, nous encoderons vers un nouveau fichier `dataset.csv` dans le dossier `feature`, dont nous récupérerons les sous-ensembles d'apprentissage et de test. Pour référencer tous ces fichiers dans le Data Catalog, nous éditons le fichier `conf/base/catalog.yml` en spécifiant le nom, le type de données et le chemin en relatif par rapport au dossier racine.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```yml
    primary:
      type: pandas.CSVDataset
      filepath: data/03_primary/primary.csv

    dataset:
      type: pandas.CSVDataset
      filepath: data/04_feature/dataset.csv

    X_train:
      type: pandas.CSVDataset
      filepath: data/05_model_input/X_train.csv

    y_train:
      type: pandas.CSVDataset
      filepath: data/05_model_input/y_train.csv

    X_test:
      type: pandas.CSVDataset
      filepath: data/05_model_input/X_test.csv

    y_test:
      type: pandas.CSVDataset
      filepath: data/05_model_input/y_test.csv
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'avantage du Data Catalog est la flexibilité d'utilisation. Plutôt que de spécifier le chemin d'accès dans chaque fichier Python, nous pouvons simplement inscrire `primary` comme argument, et Kedro va automatiquement charger en mémoire (ici au format CSV avec `pandas`) ce jeu de données. Ainsi, nous pouvons à tout moment modifier la valeur du chemin `filepath` ici sans altérer tous les fichiers Python.

    ### Nodes et Pipelines

    Parmi les concepts les plus importants, nous retrouvons celui des **nodes** et des **pipelines**.

    Un **node** est un élément unitaire qui représente une tâche. Par exemple, nous pouvons imaginer un node pour encoder le jeu de données, un autre pour construire les sous-ensembles d'entraînement et de test, et un dernier pour calibrer un modèle de Machine Learning.

    Un **pipeline**, à l'instar des pipelines de données, est une succession de nodes qui peuvent être assemblés en séquence ou en parallèle.

    Les pipelines sont une partie très importante dans Kedro. Reprenons le pipeline d'expérimentation où l'on entraîne un modèle de Machine Learning.

    ![alt](public/kedro2.png)

    Ce qui est important à voir, c'est le caractère séquencé entre les tâches. En particulier, **impossible d'entraîner un modèle sans avoir encodé les données**, tout comme il est impossible d'évaluer un modèle si l'on n'en a pas.

    Kedro va nous permettre de créer ces pipelines, garantissant que les **artifacts** (données construites, modèles, etc) vont être disponibles pour les autres nodes du pipeline. C'est un outil essentiel car il va nous assurer que les traitements sont homogènes et que lorsque l'on souhaitera entraîner un nouveau modèle par exemple, les données subiront exactement le même traitement puisqu'elles passeront par le même pipeline. On évite ainsi les risques d'oubli ou d'erreur de cohérence entre deux exécutions successives, chose qui arrive plus souvent que l'on ne l'imagine avec les Jupyter Notebooks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Premier pipeline

    Nous allons créer ensemble un premier pipeline qui va contenir deux noeuds.

    - Un premier qui va se charger d'encoder le jeu de données `primary`.
    - Un autre qui va séparer la base de données en deux sous-ensembles d'entraînement et d'apprentissage.

    Commençons tout d'abord par télécharger le fichier d'échantillon dans le dossier `data/03_primary`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    cp data/primary.csv purchase-predict/data/03_primary/primary.csv
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Créons un dossier `processing` dans `src/purchase_predict/pipelines`. Nous allons y ajouter deux fichiers Python `nodes.py` et `pipeline.py`.

    - Le fichier `nodes.py` contient les définitions des fonctions qui seront utilisées par les nodes.
    - Le fichier `pipeline.py` permet de construire le pipeline à partir de nodes qui utiliseront les fonctions du fichier `nodes.py`.

    Puisque nous avons deux noeuds, nous devons construire deux fonctions.

    ### Noeud `encode_features`

    La fonction `encode_features` va récupérer `dataset`, qui correspond au fichier CSV ayant subit les transformations (notamment via Spark SQL).
    Notre IDE va se plaindre que sklearn n'est pas installé, il faudra tout simplement l'installer avec `uv add scikit-learn`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
    import pandas as pd

    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split


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
        return dict(features=features, transform_pipeline=transform_pipeline)

    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cette fonction retourne le DataFrame `features`, qui correspond aux données encodées.


    Comme nous enrengistrons également la manière dont les données ont été traîtées, nous devons les enrengistrer sous la forme d'un fichier `pickle`

    Cela tombe bien, puisque nous avons à notre disposition, `transform_pipeline` qui est récupéré à l'issue de l'appel de la fonction `encode_feature`

    Nous devons donc l'ajouter dans notre catalogue

    ```
    transform_pipeline:
      type: pickle.PickleDataset
      filepath: data/04_feature/transform_pipeline.pkl
    ```

    ### Noeud `split_dataset`

    L'autre fonction, `split_dataset`, opère simplement une séparation en deux sous-échantillons. L'argument `test_ratio` permettra de spécifier la proportion d'observation à considérer dans le sous-échantillon de test.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```Py
    def split_dataset(dataset: pd.DataFrame, test_ratio: float) -> dict[str, pd.DataFrame]:
        "\"\"
        Splits dataset into a training set and a test set.
        "\"\"
        X = dataset.drop("purchased", axis=1)
        y = dataset["purchased"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_ratio, random_state=40
        )

        return dict(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// attention |
    Note : Il se peut que vous avez un warning concernant la ligne `dataset.drop(["user_id", "user_sessions"], axis=1).copy()`.
    En effet, drop permet de renvoyer soit un DataFrame (ce qui est le cas ici), soit rien du tout, en attribuant la valeur `False` à `inplace`.

    Pour effacer ce warning, nous devons installer `pandas-stubs` à l'aide de la commande `uv add pandas-stubs`
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La fonction retourne les quatre DataFrames.

    ### Construction du pipeline

    Pour entamer la construction du pipeline, nous allons tout d'abord définir un **paramètre** Kedro, le `test_ratio`. En effet, il s'agit d'un paramètre de configuration qui doit être initialisé au préalable, et plutôt que d'inscrire en dur dans le code la valeur du ratio pour l'ensemble de test, tout comme le Data Catalog, le fichier `parameters.yml` dans le dossier `conf/base` permet de centraliser tous les paramètres du modèle, Cloud, de traitement de données, etc.

    ```yml
    test_ratio: 0.3
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    À partir de là, nous pouvons construire notre pipeline. Pour cela, nous utilisons l'objet `Pipeline` de Kedro, qui s'attends à une liste de `node`. Chaque instance de `node` attends trois paramètres.

    - Le nom de la fonction Python qui sera appelée.
    - Les arguments de la fonction (sous forme de liste ou dictionnaire).
    - Les sorties du modèles (sous forme de liste ou dictionnaire).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```python
    from kedro.pipeline import Pipeline, Node

    from .nodes import encode_features, split_dataset


    def create_pipeline(**kwargs) -> Pipeline:
        return Pipeline(
            [
                Node(
                    encode_features,
                    "primary",
                    dict(features="dataset", transform_pipeline="transform_pipeline"),
                ),
                Node(
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
    Le premier noeud appelle la fonction `encode_features` avec pour argument le jeu de données `primary`, et le résultat (un seul) retourné par la fonction sera stocké dans le jeu de données `dataset`.

    Le deuxième noeud nécessite le jeu de données `dataset` ainsi que le paramètre `test_ratio`, et retourne les 4 DataFrames qui correspond aux sous-ensembles.

    Notre pipeline est donc en place, et nous pouvons la visualiser ci-dessous.

    ![alt](public/kedro1.jpg.jpeg)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Mais avant de passer à la suite, il nous reste à créer un fichier `__init__.py` afin d'avertir aux programmes annexes que le module `processing` existe.

    Nous mettrons ce bout de code

    ```
    from .pipeline import create_pipeline

    __all__ = ["create_pipeline"]

    __version__ = "0.1"
    ```


    Nous exécutons ensuite la pipeline avec la commande `uv run kedro run --pipelines processing` Mais nous allons avoir l'erreur suivante :
    ```
    DatasetError: Dataset 'CSVDataset' not found in 'pandas'. Make sure the dataset name is correct.
    Hint: If you are trying to use a dataset from `kedro-datasets`, make sure that the package is installed in your current environment. You can do so
    by running `pip install kedro-datasets` or `pip install kedro-datasets[<dataset-group>]` to install `kedro-datasets` along with related
    dependencies for the specific dataset group.
    ```

    Ce qui est normal, car depuis la version final (donc la 1) de kedro, les Datasets ne sont plus fourni.
    Nous devons donc les installer à l'aide de la commande : `uv add kedro-datasets`

    Relancez la pipeline et tout devrait s'exécuter avec succès.

    ```
    > kedro run --pipeline processing
    [12/17/25 12:44:22] INFO     Using 'conf\logging.yml' as logging configuration. You can change this by setting the                  __init__.py:269
                                 KEDRO_LOGGING_CONFIG environment variable accordingly.
    [12/17/25 12:44:23] INFO     Kedro project purchase-predict                                                                          session.py:330
    [12/17/25 12:44:24] INFO     Kedro is sending anonymous usage data with the sole purpose of improving the product. No personal data   plugin.py:242
                                 or IP addresses are stored on our side. To opt out, set the `KEDRO_DISABLE_TELEMETRY` or `DO_NOT_TRACK`
                                 environment variables, or create a `.telemetry` file in the current working directory with the contents
                                 `consent: false`. To hide this message, explicitly grant or deny consent. Read more at
                                 https://docs.kedro.org/en/stable/about/telemetry/
    [12/17/25 12:44:25] INFO     Using synchronous mode for loading and saving data. Use the --async flag for potential         sequential_runner.py:59
                                 performance gains.
                                 https://docs.kedro.org/en/stable/nodes_and_pipelines/run_a_pipeline.html#load-and-save-asynchr
                                 onously
                        INFO     Loading data from primary (CSVDataset)...                                                         data_catalog.py:1048
                        INFO     Running node: encode_features() ->                                                                         node.py:420
                        INFO     Saving data to dataset (CSVDataset)...                                                            data_catalog.py:1008
                        INFO     Saving data to transform_pipeline (MemoryDataset)...                                              data_catalog.py:1008
                        INFO     Completed node: encode_features__4f0652e1                                                                runner.py:245
                        INFO     Completed 1 out of 2 tasks                                                                               runner.py:246
                        INFO     Loading data from dataset (CSVDataset)...                                                         data_catalog.py:1048
                        INFO     Loading data from params:test_ratio (MemoryDataset)...                                            data_catalog.py:1048
                        INFO     Running node: split_dataset() -> [X_train;y_train;X_test;y_test]                                           node.py:420
                        INFO     Saving data to X_train (CSVDataset)...                                                            data_catalog.py:1008
                        INFO     Saving data to y_train (CSVDataset)...                                                            data_catalog.py:1008
                        INFO     Saving data to X_test (CSVDataset)...                                                             data_catalog.py:1008
                        INFO     Saving data to y_test (CSVDataset)...                                                             data_catalog.py:1008
                        INFO     Completed node: split_dataset__f432ba67                                                                  runner.py:245
                        INFO     Completed 2 out of 2 tasks                                                                               runner.py:246
                        INFO     Pipeline execution completed successfully in 0.3 sec.                                                    runner.py:119
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Deux remarques :
     - Pour cacher les message en lien avec la télémétrie, vous devez créer un fichier .telemetrie au même endroit que `pyproject.toml` et renseigner la ligne `consent: false`
      - Pour des éventuelles accélérations de traitement de données, lorsqu'il y a plusieurs fichier, il est peut être avantageux d'ajouter la commande ` --async` à la fin
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En déroulant le dossier `data/05_model_input`, nous devrions voir apparaître les 4 fichiers CSV générés par le pipeline.

    ### Visualisation des pipelines

    La dernière dépendance `kedro-viz` peut être utile car elle permet de visualiser les différents pipelines directement depuis le navigateur. Pour cela nous devons l'ajouter à l'aide de la commande `uv add kedro-viz`

    Pour lancer le serveur de visualisation, il suffit d'exécuter la commande suivante (attention de vérifier que l'environnement virtuel est bien activé).

    ```
    uv run kedro viz run --port 4141
    ```

    Une fois lancé, nous pouvons y accéder [par ce lien](http://localhost:4141) :
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Vous vennez de mettre en place votre première pipeline avec Kedro !

    - Nous avons vu créé notre premier projet avec Kedro.
    - Nous avons détaillé les concepts importants que l'on rencontre avec Kedro.
    - Nous avons mis en place un premier pipeline.

    > ➡️ Après avoir construit le pipeline de traitement de données, place au **pipeline d'entraînement du modèle**.
    """)
    return


if __name__ == "__main__":
    app.run()
