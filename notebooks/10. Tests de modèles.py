# /// script
# dependencies = ["scikit-learn-extra"]
# ///

import marimo

__generated_with = "0.20.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd


    return mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Précédemment, nous avons réalisé des tests unitaires sur notre projet Kedro. Les tests unitaires sont rapides à mettre en place et permettent de vérifier indépendamment chaque portion de code.

    Mais lorsqu'il s'agit de modèles de Machine Learning, à quoi correspondent exactement les tests ? Il n'est pas possible de rédiger des tests unitaires de la même façon, car un modèle fournit justement une prédiction, qui n'est a priori pas connu à l'avance. C'est pourquoi les Data Scientists et ML Engineers ont imaginé des méthodes de test à réaliser sur les modèles.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Formaliser les différents tests qui peuvent survenir</li>
        <li>Rédiger le tests dans le projet Kedro</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/lQ0VQmLuLH7lS/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Test de modèles

    Lorsque l'on fait référence aux tests de modèles, on cherche à vérifier le bon fonctionnement et comportement du modèle. Pour cela, nous distinguons deux classes de tests de modèles.

    - Les **tests pré-entraînement**, qui nous permettent d'identifier des erreurs ou incohérences avant même l'entraînement du modèle.
    - Les **tests post-entraînement**, qui vont utiliser le modèle entraîné et inspecter le comportement de ce dernier par rapport à des scénarios de référence que l'on décide en amont.

    <div class="alert alert-block alert-warning">
        Il n'y a pas de <i>meilleur test possible</i>. Chaque test doit être défini en fonction du contexte, du cas d'application et surtout de l'importance que l'on accorde aux décisions du modèle.
    </div>

    ## Les tests pré-entraînement

    Les tests pré-entraînement permettent d'éviter de se lancer dans l'entraînement d'un modèle si certains critères ne sont pas respectés. Très souvent, ces critères portent sur les données et les tests, bien que rapide à mettre en place, permettent déjà de soulever certains points. Parmi les tests qui peuvent être réalisés avant l'entraînement, nous retrouvons surtout de tests de cohérence des données.

    - Taille du jeu de données.
    - Format de la variable réponse.
    - Proportion des classes dans la classification binaire.
    - Représentativité de l'échantillon par rapport à la population d'étude.

    En soit, il s'agit de tests qui peuvent être rédigés au même titre que les tests unitaires précédents. Définissons les tests du pipeline `processing`. Ce pipeline est composé de deux nodes, chacun appelant une fonction.

    - `encode_features`, qui va encoder numériquement les variables de `primary`.
    - `split_dataset`, qui va séparer le jeu de données en une base d'apprentissage et une base de test.

    Commençons par la fonction `encode_features` : elle s'attend à recevoir un DataFrame nommé `dataset`. Il y a plusieurs choses que nous devons vérifier à l'issue de cette fonction.

    - La colonne `purchased` est-elle toujours *intacte* dans le sens où elle n'est constituée que de $0$ et de $1$ ?
    - Toutes les colonnes sont-elles numériques ?
    - Avons-nous suffisamment d'observations pour entraîner le modèle ?
    - Les proportions de classes positives et négatives sont-elles au moins supérieures à un seuil ?

    Dans le dossier de test, créons le dossier `processing` avec le fichier `conftest.py`. Nous allons définir un catalogue de données pour ce test.
    """)
    return


@app.cell
def _():
    import pytest

    from purchase_predict.pipelines.loading.nodes import load_csv_from_bucket

    @pytest.fixture(scope="module")
    def project_id():
        return "PROJET_GCP"  # TODO : Penser à changer le nom du projet GCP

    @pytest.fixture(scope="module")
    def primary_folder():
        return "FICHIER_CSV"  # TODO : Penser à changer l'URL gs:// du fichier CSV

    @pytest.fixture(scope="module")
    def dataset_not_encoded(project_id, primary_folder):
        return load_csv_from_bucket(project_id, primary_folder)

    return (pytest,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous ré-utilisons ici les deux fixtures `project_id` et `primary_folder` déjà présentes dans les tests du pipeline `loading`. Nous utilisons la fonction `load_csv_from_bucket` pour récupérer le jeu de données de test depuis Cloud Storage afin d'utiliser une version non altérée qui serait enregistrée en local. En pratique, la fonction `load_csv_from_bucket` aura déjà été testée au préalable par `pytest`, nous pouvons donc l'utiliser ici pour charger les données.

    /// attention
    Il faut éviter de créer des dépendances entre les tests : c'est pour cela que l'on redéfini ici les fixtures sans les importer depuis <code>loading/conftest.py</code>.
    ///

    Créons ensuite comme nous l'avions fait le fichier `test_nodes.py` dans le dossier `processing`.
    """)
    return


@app.cell
def _():
    # n'oubliez pas d'inclure : import pandas as pd
    from purchase_predict.pipelines.processing.nodes import encode_features

    def test_encode_features(dataset_not_encoded):
        df = encode_features(dataset_not_encoded)["features"]
        print(df.head())

    return (encode_features,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La fonction `test_encode_features` va tester `encode_features` à partir de la fixture `dataset_not_encoded` que nous venons de définir dans `conftest.py`. Exécutons les tests avec Kedro.
    """)
    return


app._unparsable_cell(
    r"""
    pytest tests/pipelines/processing/ -s
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Avec l'argument `tests/pipelines/processing/`, on précise à Kedro d'exécuter les tests de manière récursive uniquement dans ce dossier.

    Si tout s'est bien passé, alors nos fixtures sont correctement en place et nous pouvons intégrer les **tests pré-entraînement**.
    """)
    return


@app.cell
def _(LabelEncoder, encode_features, pd):
    BALANCE_THRESHOLD = 0.1
    MIN_SAMPLES = 5000

    def test_encode_features(dataset_not_encoded):
        encoded: dict[str, pd.DataFrame | dict[str, LabelEncoder]] = encode_features(dataset_not_encoded)
        features_value = encoded["features"]
        assert isinstance(features_value, pd.DataFrame), "Expected DataFrame for features"
        df: pd.DataFrame = features_value  # Now type-safe

        # Checking column 'purchased' that all values are either 0 or 1
        assert df["purchased"].isin([0, 1]).all()
        # Checking that all columns are numeric
        for col in df.columns:
            assert pd.api.types.is_numeric_dtype(df.dtypes[col])
        # Checking that we have enough samples
        assert df.shape[0] > MIN_SAMPLES
        # Checking that classes have at least BALANCE_THRESHOLD percent of data
        assert (df["purchased"].value_counts() / df.shape[0] > BALANCE_THRESHOLD).all()
        print(df.head())

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Les constantes `BALANCE_THRESHOLD` et `MIN_SAMPLES` vont bien sûr dépendrent du contexte. Dans certains situations, `BALANCE_THRESHOLD` devra être amené à $1\%$ ou `MIN_SAMPLES` devra être bien plus conséquent.

    Écrivons maintenant les tests pour la fonction `split_dataset`. Il nous faut rajouter deux fixtures dans le fichier `conftest.py` : une pour le jeu de données encodé (après application de `encode_features`) et une pour le ratio de test.
    """)
    return


@app.cell
def _(encode_features, pytest):
    @pytest.fixture(scope='module')
    def test_ratio():
        return 0.3

    @pytest.fixture(scope='module')
    def dataset_encoded(dataset_not_encoded):
        return encode_features(dataset_not_encoded)['features']

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    De la même manière, nous ajoutons le test `test_split_dataset` au fichier `test_nodes.py`.
    """)
    return


@app.cell
def _(split_dataset):
    import numpy as np

    def test_split_dataset(dataset_encoded, test_ratio):
        X_train, y_train, X_test, y_test = split_dataset(dataset_encoded, test_ratio).values()
        # Checks both sets size
        assert X_train.shape[0] == y_train.shape[0]
        assert X_test.shape[0] == y_test.shape[0]
        assert X_train.shape[0] + X_test.shape[0] == dataset_encoded.shape[0]
        # Note that train_test_split of scikit-learn use np.ceil for test split
        # https://github.com/scikit-learn/scikit-learn/blob/42aff4e2edd8e8887478f6ff1628f27de97be6a3/sklearn/model_selection/_split.py#L1797
        assert np.ceil(dataset_encoded.shape[0] * test_ratio) == X_test.shape[0]

    return (np,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lançons les tests.
    """)
    return


app._unparsable_cell(
    r"""
    pytest tests/pipelines/processing/ -s
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    ========================= test session starts =========================
    platform linux -- Python 3.8.5, pytest-6.1.2, py-1.10.0, pluggy-0.13.1
    rootdir: /home/jovyan/purchase_predict, configfile: pyproject.toml
    plugins: mock-1.13.0, cov-2.11.0
    collected 2 items

    src/tests/pipelines/processing/test_nodes.py ..

    ========================== 2 passed in 0.65s ==========================
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div class="alert alert-block alert-info">
        Les deux points après le chemin d'accès au fichier signifie que deux fonctions de tests ont été correctement exécutées. En cas d'erreur nous aurions eu un <code>E</code> à la place et en cas de <i>skipping</i>, nous aurions eu <code>S</code>.
    </div>

    Il ne reste plus qu'à tester le pipeline `processing` en entier, qui fait appel aux deux fonctions. À noter que dans ce cas, il n'y a pas besoin de tester le jeu de données intermédiaire car les tests unitaires sont supposés déjà valides. Pour rappel, le pipeline `processing` est constitué de deux nodes.
    """)
    return


@app.cell
def _(Pipeline, encode_features, node, split_dataset):
    def create_pipeline(**kwargs):
        return Pipeline(
            [
                node(
                    encode_features,
                    "primary",
                    "dataset",
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

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Créons un catalogue de test pour `processing` dans le fichier `conftest.py`.
    """)
    return


@app.cell
def _(pytest):
    from kedro.io import DataCatalog, MemoryDataset

    @pytest.fixture(scope="module")
    def catalog_test(dataset_not_encoded, test_ratio):
        catalog = DataCatalog({
            "primary": MemoryDataset(dataset_not_encoded),
            "params:test_ratio": MemoryDataset(test_ratio)
        })
        return catalog

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme pour le pipeline précédent, nous nous basons sur les fixtures `dataset_not_encoded` et `test_ratio` pour créer le catalogue de données.

    > ❓ Pourquoi n'avons-nous pas crée un dataset <code>dataset</code> ?

    Le catalogue de données de test est identique à celui utilisé hors environnement de test, à la différence que l'on spécifie nous-même les différentes entrées. Ainsi, remarquons que le premier node va produire en sortie `dataset`. En exécutant le pipeline avec le catalogue de test, `dataset` sera alors stocké dans le catalogue en tant que `MemoryDataSet` : il sera donc utilisable par le prochain node du pipeline.

    Le contenu de `test_pipeline.py` s'écrit directement.
    """)
    return


@app.cell
def _():
    from kedro.runner import SequentialRunner
    from purchase_predict.pipelines.processing.pipeline import create_pipeline

    def test_pipeline(catalog_test):
        runner = SequentialRunner()
        pipeline = create_pipeline()
        pipeline_output = runner.run(pipeline, catalog_test)
        # Load data from MemoryDataset objects
        X_train = pipeline_output["X_train"].load()
        y_train = pipeline_output["y_train"].load()
        X_test = pipeline_output["X_test"].load()
        y_test = pipeline_output["y_test"].load()

        assert X_train.shape[0] == y_train.shape[0]
        assert X_test.shape[0] == y_test.shape[0]

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exécutons l'intégralité des tests.
    """)
    return


@app.cell
def _(pytest):
    pytest
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```log
    ╰─ pytest                                                                                                       ─╯
    =============================================== test session starts ===============================================
    platform darwin -- Python 3.12.12, pytest-7.4.4, pluggy-1.6.0
    rootdir: /Users/noobzik/Documents/Kaggle/purchase-predict
    configfile: pyproject.toml
    testpaths: tests, unit
    plugins: anyio-4.12.1, asyncio-0.23.8, cov-6.3.0
    asyncio: mode=Mode.STRICT
    collected 7 items

    tests/pipelines/loading/test_nodes.py ..                                                                    [ 28%]
    tests/pipelines/loading/test_pipeline.py .                                                                  [ 42%]
    tests/pipelines/processing/test_nodes.py ..                                                                 [ 71%]
    tests/pipelines/processing/test_pipeline.py .                                                               [ 85%]
    unit/test_1.py .                                                                                            [100%]

    ================================================= tests coverage ==================================================
    ________________________________ coverage: platform darwin, python 3.12.12-final-0 ________________________________

    Name                                                    Stmts   Miss  Cover   Missing
    -------------------------------------------------------------------------------------
    src/purchase_predict/__init__.py                            1      0   100%
    src/purchase_predict/__main__.py                           14     14     0%   5-25
    src/purchase_predict/pipeline_registry.py                   7      7     0%   3-17
    src/purchase_predict/pipelines/__init__.py                  0      0   100%
    src/purchase_predict/pipelines/loading/__init__.py          3      0   100%
    src/purchase_predict/pipelines/loading/nodes.py            18      0   100%
    src/purchase_predict/pipelines/loading/pipeline.py          4      0   100%
    src/purchase_predict/pipelines/processing/__init__.py       3      0   100%
    src/purchase_predict/pipelines/processing/nodes.py         20      0   100%
    src/purchase_predict/pipelines/processing/pipeline.py       4      0   100%
    src/purchase_predict/pipelines/training/__init__.py         3      3     0%   6-10
    src/purchase_predict/pipelines/training/nodes.py           60     60     0%   6-165
    src/purchase_predict/pipelines/training/pipeline.py         5      5     0%   6-14
    src/purchase_predict/settings.py                            1      1     0%   31
    -------------------------------------------------------------------------------------
    TOTAL                                                     143     90    37%
    =============================================== 7 passed in 23.50s ================================================
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Et voilà ! Jusqu'ici, nos deux pipelines `loading` et `processing` sont testés. Nous avons réalisé les tests pré-entraînement. Mais qu'en est-il de ceux concernant le modèle ?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tests post-entraînement

    Les **tests post-entraînement** vont être exécutés une fois le modèle calibré. Contrairement aux tests précédents, ils sont plus subtils car l'objectif est de mettre en évidence certains aspects et comportements particuliers du modèle pour vérifier qu'ils n'aboutissent pas à des erreurs ou à des incohérences qui pourraient avoir d'importantes répercussions.

    Pour cela, nous pouvons faire intervenir plusieurs outils.

    - Des exemples de données dont on connaît (en dehors de la base d'apprentissage) les réponses.
    - Les méthodes d'interprétabilité avec SHAP par exemple.
    - Des méthodes d'évaluation de propriétés, comme la régularité de la loi jointe.

    Commençons par récupérer le modèle de boosting que nous avions entraîné avec la base de test.
    """)
    return


@app.cell
def _(pd):
    import os
    import joblib
    import shap

    model = joblib.load(os.path.expanduser('notebooks/data/model.pkl'))
    X_test = pd.read_csv(os.path.expanduser('notebooks/data/X_test.csv'))
    y_test = pd.read_csv(os.path.expanduser('notebooks/data/y_test.csv')).values.flatten()
    return X_test, model, shap


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Tests d'invariance

    Les tests d'invariance nous permettent de définir un ensemble de perturbations à appliquer sur une ou plusieurs observations pour observer à quel point cela affecte la sortie du modèle.

    Par exemple, supposons qu'un utilisateur, ayant visité un produit dont le prix est de 59€. Un test d'invariance consisterai à dire qu'une variation de $\pm 1€$ ne devrait pas faire varier la probabilité d'acheter de $\pm x\%$. Une variation importante pourrait signifier que cette variable a beaucoup d'impact, alors qu'en réalité, il est peu probable que pour un article de 59€ une variation de 1€ fasse drastiquement augmenter ou baisser la probabilité.

    Sélectionnons une seule observation aléatoire `x_unit`.
    """)
    return


@app.cell
def _(X_test, model):
    x_unit = X_test.loc[4720, :].copy()

    print("Pos : {:2.3f}%".format(model.predict_proba([x_unit])[0, 1] * 100))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La probabilité associée ici est d'environ 92%. Appliquons une perturbation de +1€ et -1€.
    """)
    return


@app.cell
def _(X_test, model):
    x_unit_1 = X_test.loc[4720, :].copy()
    x_unit_1['price'] = x_unit_1['price'] + 1
    print('Pos : {:2.3f}%'.format(model.predict_proba([x_unit_1])[0, 1] * 100))
    x_unit_1 = X_test.loc[4720, :].copy()
    x_unit_1['price'] = x_unit_1['price'] - 1
    print('Pos : {:2.3f}%'.format(model.predict_proba([x_unit_1])[0, 1] * 100))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sur cette observation en particulier, la différence de probabilité est de $0.165\%$. L'impact est **très limité**, indiquant que le modèle est régulier au voisinage de ce point.

    Calculons maintenant cette différence (en valeur absolue) de probabilité (pour la classe positive) pour chaque observation.
    """)
    return


@app.cell
def _(X_test, model, np, pd):
    X_test_price = X_test[X_test['price'] > 1]
    X_test_price_plus = X_test_price.copy()
    # On ne sélectionne que les articles dont le prix est > à 1€, sinon on aurait un prix ... négatif !
    X_test_price_plus['price'] = X_test_price_plus['price'] + 1
    X_test_price_minus = X_test_price.copy()
    X_test_price_minus['price'] = X_test_price_minus['price'] - 1
    y_price = pd.DataFrame()
    y_price['y'] = model.predict_proba(X_test_price)[:, 1]
    y_price['y+'] = model.predict_proba(X_test_price_plus)[:, 1]
    y_price['y-'] = model.predict_proba(X_test_price_minus)[:, 1]
    y_price['abs_delta'] = np.abs(y_price['y-'] - y_price['y+'])
    y_price.sort_values('abs_delta', ascending=False).head(n=10)
    return X_test_price, y_price


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous pouvons voir que pour une dizaine d'observations au moins, cette variable de 1€ contribue à un différentiel de 20% à 30% sur la probabilité prédite (ce qui est tout de même élevé).

    Regardons de quelles observations il s'agit.
    """)
    return


@app.cell
def _(X_test_price, y_price):
    idxs = list(y_price.sort_values("abs_delta", ascending=False).head(n=100).index)
    X_test_price.loc[idxs, :]
    return (idxs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous aurions pu penser qu'il s'agit d'articles dont le prix est faible. Et pourtant, l'ordre de grandeur est de 20 à 50€ pour la plupart des articles. Regardons les valeurs de Shapley de ces mêmes observations.
    """)
    return


@app.cell
def _():
    return


@app.cell
def _(X_test_price, model, shap):
    explainer = shap.TreeExplainer(model)
    X_shap = X_test_price.copy()
    # On calcul ici les valeurs de Shapley
    shap_values = explainer.shap_values(X_shap)
    return X_shap, explainer, shap_values


@app.cell
def _(shap_values):
    shap_values
    return


@app.cell
def _(X_shap, idxs, shap, shap_values):
    shap.summary_plot(shap_values[idxs, :], X_shap.loc[idxs, :], plot_size=0.8)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Au global, l'impact est limité.
    """)
    return


@app.cell
def _(y_price):
    print("Écart-type : {:2.2f}%".format(y_price["abs_delta"].std()))
    print("Proportion : {:2.2f}%".format(
        y_price[y_price["abs_delta"] < 0.05].shape[0] / y_price.shape[0] * 100
    ))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En traçant ce delta pour chaque observation dans l'ordre décroissant, nous pouvons voir apparaître un « coude » à partir duquel ce delta stagne.
    """)
    return


@app.cell
def _(y_price):
    import matplotlib.pyplot as plt

    n_obs = 1000

    plt.figure(figsize=(16,10))
    plt.plot(
        range(n_obs),
        y_price.sort_values("abs_delta", ascending=False).iloc[:n_obs, -1],
        lw=2
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dans notre situation, une variation de 10% **paraît raisonnable**. Il serait donc intéressant de se concentrer sur les quelques observations qui présentent une variation de plus de 20% par rapport à la variable prix.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Test directionnels

    Les tests directionnels semblent proches des tests d'invariance, à la différence près que l'ensemble des perturbations que nous allons appliquer aux observations devraient avoir un effet **connu à l'avance** sur la sortie du modèle.
    """)
    return


@app.cell
def _(X_test, model):
    x_unit_2 = X_test.loc[375, :]
    model.predict_proba([x_unit_2])
    return (x_unit_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'interprétation locale est d'une grande aide : pourquoi y a-t-il une forte probabilité que cet utilisateur ne finalise pas l'achat ?
    """)
    return


@app.cell
def _(explainer, shap, shap_values, x_unit_2):
    shap.force_plot(explainer.expected_value, shap_values[375, :], x_unit_2, matplotlib=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    C'est principalement la durée, qui n'est que de 10 secondes, qui explique pourquoi cet utilisateur ne finaliserai pas l'achat.

    Le but du test directionnel est de se poser la question suivante : et si la durée avait durée 60 secondes de plus, que se passerait-il ?
    """)
    return


@app.cell
def _(X_test, model):
    x_unit_3 = X_test.iloc[375, :].copy()
    x_unit_3['duration'] = x_unit_3['duration'] + 60
    model.predict_proba([x_unit_3])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ici, la probabilité augmente de près de 70%, alors que la variable n'a augmenté que de 60 secondes. Ce qu'il faut regarder ici, ce sont les autres variables de l'observation.
    """)
    return


@app.cell
def _(X_test):
    X_test.iloc[375, :]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Regardons le graphe de dépendance.
    """)
    return


@app.cell
def _(X_shap, shap, shap_values):
    shap.dependence_plot("duration", shap_values, X_shap)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ici , l'interaction avec la variable `num_views_session` **est très forte** lorsque la durée est très basse. Autrement dit, de petites durées font fortement baisser la probabilité lorsqu'il n'y a que peu de vues dans une session.

    Maintenant, essayons conjointement d'augmenter la valeur de la variable `num_views_session`.
    """)
    return


@app.cell
def _(X_test, model):
    x_unit_4 = X_test.iloc[375, :].copy()
    x_unit_4['duration'] = x_unit_4['duration'] + 10
    x_unit_4['num_views_session'] = x_unit_4['num_views_session'] + 10
    model.predict_proba([x_unit_4])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dans ce contexte, la probabilité **reste très faible**. Ce test directionnel s'intéresserait donc à des observations avec de faibles durées et peu de vues.

    Prenons un autre exemple, cette fois-ci pour un utilisateur ayant une forte probabilité de finaliser son achat.
    """)
    return


@app.cell
def _(X_test, model):
    x_unit_5 = X_test.loc[4720, :]
    model.predict_proba([x_unit_5])
    return (x_unit_5,)


@app.cell
def _(explainer, shap, shap_values, x_unit_5):
    shap.force_plot(explainer.expected_value, shap_values[4720, :], x_unit_5, matplotlib=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Retirons maintenant 60 secondes à cette observation.
    """)
    return


@app.cell
def _(X_test, model):
    x_unit_6 = X_test.loc[4720, :].copy()
    x_unit_6['duration'] = x_unit_6['duration'] - 60
    model.predict_proba([x_unit_6])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'effet de la variable `duration` a beaucoup moins d'impact que pour l'observation précédente.

    Ce qu'il faut retenir, c'est qu'il ne suffit pas de définir un seuil limite d'écart de probabilité en appliquant une perturbation $\varepsilon$ sans étudier au préalable l'observation qui va subir la transformation. Dans le premier exemple, la durée était très faible (seule 10 secondes), il était donc logique sur la probabilité de finaliser l'achat soit très faible. En revanche, le fait de rajouter 60 secondes pour cette session peut créer une observation que est pas ou très peu représentée dans l'échantillon : le modèle n'a rencontré que peu d'observations présentant ces caractéristiques.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Tests unitaires du modèle

    Au même titre que les tests unitaires sont réalisés pour les fonctions de collecte et de transformation de données, les tests unitaires pour le modèle consistent à vérifier que ce dernier prédit la bonne réponse pour des observations qui sont supposées être parfaitement classifiées.

    Une méthode consiste à calculer des **prototypes** : il s'agit d'observations qui *représentent le plus* les données. En d'autres termes, il s'agit d'un concept proches des centres de clusters formés par les observations. Et un algorithme non-supervisé permettant de détecter les prototypes est le **k-médoïde**, proche des k-moyennes dans son fonctionnement mais qui calcule le <a href="https://en.wikipedia.org/wiki/Medoid" target="_blank">médoïde</a>, point d'un cluster dont la distance avec tous les autres points est la plus petite.

    Comme la méthode des k-méloide n'est pas encore disponible dans la librairie principale de scikit-learn, nous devrions la télécharger depuis les extras de scikit-learn. Cependant, elle possède un problème de compatibilité avec la nouvelle version de numpy, ce qui nous contraint à utiliser KMeans pour le moment. Les résultats du tests risquent d'être faussé.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lançons un k-médoïde sur les observations de test.
    """)
    return


@app.cell
def _(X_test):
    from sklearn.cluster import KMeans

    kmeans = KMeans(n_clusters=10, random_state=30)
    clusters = kmeans.fit_predict(X_test)
    centroids = kmeans.cluster_centers_   
    return (centroids,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Récupérons les centres des clusters (les médoïdes) dans un DataFrame.
    """)
    return


@app.cell
def _(X_test, centroids, pd):
    X_prototypes = pd.DataFrame(
        data=centroids,
        columns=X_test.columns
    )
    X_prototypes
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Chacune de ces observations représentent la moyenne d'une sous-population de l'échantillon. Étonnamment, hormis la première observation, toutes les autres concernent des produits issus de la même catégorie.

    Calculons les probabilité associées.
    """)
    return


@app.cell
def _(centroids, model):
    model.predict_proba(centroids)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    On se rend compte que toute les observations sont prédites dans la classe positive. Attention néanmoins, car ces données représentent uniquement un historique d'une journée, alors qu'en pratique, celles qui seront utilisées pour calibrer le modèle représentent un historique de 7 jours.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Les tests de modèle sont plus difficiles à construire, mais sont indispensables pour certains secteurs d'activités où les prédictions du modèle peuvent être critiques.

    - Nous avons vu les test pré-entraînement pour s'assurer de la cohérence de la base d'apprentissage avant l'entraînement.
    - Nous avons détaillé plusieurs tests de modèles pour vérifier son comportement.

    > ➡️ Lorsque ces tests sont réalisés avec succès, il faut maintenant conserver le modèle quelque part pour y accéder ultérieurement : c'est le rôle de <b>MLflow</b>.
    """)
    return


if __name__ == "__main__":
    app.run()
