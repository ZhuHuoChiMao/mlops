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
    Dans l'univers du développement logiciel, les tests sont omni-présents. Ils permettent de vérifier que le logiciel ou l'application développée adopte correctement le comportement attendu, ne produit pas de bugs ou s'intègre efficacement dans un environnement existant.

    Mais comment transposer tous ces tests de développement logiciel au cas où l'on entraîne et fait intervenir des modèles de Machine Learning ?

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Comprendre pourquoi il est important de tester son code et son modèle</li>
        <li>Appliquer les tests usuels de développement logiciel</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/Rd6sn03ncIklmprvy6/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tester des applications

    Avant de rentrer dans le détails des tests d'algorithmes de Machine Learning, décrivons tout d'abord les bonnes pratiques héritées du développement logiciel.

    ## 1. Tests logiciels

    Dans ce contexte, une suite de tests inclut habituellement trois composantes.

    - Les **tests unitaires**, où l'on s'assurer qu'une portion atomique du code fonctionne correctement (par exemple, une fonction). En règle générale, ce sont des tests rapides et faciles à mettre en place.
    - Les **tests de régression**, où l'on doit s'assurer que le développement d'une nouvelle fonctionnalité ne va pas faire survenir un bug déjà rencontré par le passé.
    - Les **tests d'intégration**, où on cherche à voir si la fonctionnalité développée va être correctement intégré dans l'application sans générer des erreurs dues à son interaction avec d'autres composantes. Ces erreurs sont en pratique plus difficiles à prévenir, d'où la difficulté de construire des tests d'intégration efficaces.

    /// note
    Dans les faits, les bonnes pratiques nécessitent de suivre plusieurs conventions. En travail collaboratif, notamment avec `git`, les règles de base suivantes sont appliquées.

    - Ne **jamais fusionner de branches** si les tests ne sont pas valides.
    - **Toujours écrire des tests** pour de nouvelles fonctionnalités.
    - Lorsque l'on corrige un bug, **toujours écrire le test** et l'appliquer sur la correction.
    ///

    ## 2. Tests de modèles de Machine Learning

    Essayons maintenant de transposer ce que nous venons de voir pour tester les modèles de Machine Learning. Une fois un modèle de Machine Learning calibré, nous souhaiterions obtenir un rapport d'évaluation contenant les informations suivantes.

    - Performances avec des métriques définies sur des sous-ensembles (`X_test` par exemple).
    - Graphes de validation : courbe PR, courbe ROC, densité des classes, courbe de calibration.
    - Audit du modèle avec des modèles d'interprétabilité (PDP, valeurs de Shapley).
    - Sous-population où le modèle génère des faux-positifs ou faux-négatifs avec un fort degré de confiance.

    Par ailleurs, on y retrouve également d'autres bonnes pratiques qui s'inscrivent toujours dans une logique de démarche de qualité.

    - **Toujours sauvegarder** les hyper-paramètres, sous-échantillons utilisés et le modèle entraîné.
    - Mettre à jour un environnement de production avec **un modèle aux meilleures performances** ou selon un seuil minimal.

    Face à ces besoins de tester, nous pouvons voir que calculer des performances sur un sous-échantillon ou afficher des courbes n'est pas suffisant pour s'assurer que le modèle est « valide ». Pour les systèmes de Machine Learning, nous devrions effectuer deux méthodes en parallèle.

    - **L'évaluation de modèle**, où l'on calcule ses performances, audite son fonctionnement et affiche des courbes.
    - Le **test de modèle** où l'on développe des tests explicites pour vérifier que le comportement du modèle est bien celui attendu.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Tests unitaires

    Commençons par introduire les tests unitaires avec `pytest`. Il s'agit d'une librairie qui permet de **faciliter la mise en place et l'exécution** des tests de code sous Python. Bien que les tests unitaires puissent être réalisés *from scratch*, `pytest` améliore la productivité et apporte des fonctionnalités très utiles.

    Testons la librairie sur le premier fichier suivant. Nous avons codé la fonction `argmax` qui cherche à obtenir la position du plus grand élément d'une liste. Nous codons également la fonction `test_argmax` qui va tester unitairement la fonction `argmax` sur plusieurs exemples : cela reflète du comportement attendu de la fonction.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exécutons le code avec `pytest` en spécifiant le chemin d'accès au fichier.

    Pour cela, nous allons créer un fichier `pytest_1.py` dans un dossier de votre choix.

    ```
    # Ecrire dans un fichier indépendant du projet nommé pytest_1.py
    def argmax(liste):
         if len(liste) == 0:
             return None

         idx_max = 0
         value_max = liste[0]
         for i, x in enumerate(liste):
             if x > value_max:
                 value_max = x
                 idx_max = i
         return idx_max

    def test_argmax():
         assert argmax([5, 8, 2, 9, 6, 3]) == 3
         assert argmax([7]) == 0
         assert argmax([]) == None
    ```

    Ensuite, nous allons l'installer à l'aide de `UV` :
    ```
    uv add pytest
    uv add pytest-cov
    ```

    Et nous exécutons la commande suivante pour lancer les tests
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    uv run pytest
    ```
    ou
    ```
    ou uv run pytest (chemin absolue de pytest_1.py)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En exécutant cette commande, `pytest` effectue une **découverte automatique** des tests.

    - Il va d'abord rechercher tous les fichiers dont le nom commence par `test*` si on lui fournit un dossier.
    - Pour chaque classe/fonction du fichier, si l'objet commence par `test*`, alors ce dernier sera instancié (dans le cas d'une fonction) et les fonctions seront exécutées (pour les deux).

    Cette découverte des tests permet de simplifier la mise en place des tests : plus besoin de spécifier tous les tests dans un fichier, qui lui-même effectue des importations. Nous pouvons imaginer que pour chaque *module*, il y ait un fichier `test.py` qui regroupe tous les tests unitaires liés à ce module. De manière générale, il est plus approprié de créer un fichier spécifique pour les tests unitaires plutôt que de les insérer dans le code qui fournit la logique à l'application.

    C'est de cette manière que `pytest` exécute naturellement la fonction `test_argmax` sans avoir eu besoin de la spécifier comme argument. Dans certains cas, nous pouvons être amené à éviter volontairement l'exécution d'une fonction. Dans ce cas, il suffit d'ajouter le décorateur `pytest.mark.skip`.

    ```
    # Remplacez le contenu de pytest_1.py par le code suivant
    import pytest

    def argmax(liste):
        if len(liste) == 0:
            return None

        idx_max = 0
        value_max = liste[0]
        for i, x in enumerate(liste):
            if x > value_max:
                value_max = x
                idx_max = i
        return idx_max

    @pytest.mark.skip
    def test_argmax():
        assert argmax([5, 8, 2, 9, 6, 3]) == 3
        assert argmax([7]) == 0
        assert argmax([]) == None
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme nous pouvons le voir, 100% des tests ont réussi car le seul test présent a été ignoré (*skipped*). Voyons maintenant un autre fichier Python dont le test unitaire va volontairement générer une erreur.

    Ecrivez le code suivant dans un fichier nommé `pytest_2.py`

    ```py
    def argmin(liste):
        if len(liste) == 0:
            return None

        idx_min = 0
        value_min = liste[0]
        for i, x in enumerate(liste):
            if x < value_min:
                value_min = x
                idx_min = i + 1
        return idx_min

    def test_argmin():
        assert argmin([5, 8, 2, 9, 6, 3]) == 2
        assert argmin([7]) == 0
        assert argmin([]) == None
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    D'après la sortie générée par `pytest`, les tests du fichier `/tmp/pytest_2.py` ont échoués. Si l'on regarde en détaille l'exécution de `test_argmin`, nous avons un `assert 3 == 2`, ce qui signifie que notre test unitaire a échoué. Corrigeons la fonction `argmin` et ajoutons la fonction `argmax` avec son test unitaire associé.

    ```py
    def argmin(liste):
        if len(liste) == 0:
            return None

        idx_min = 0
        value_min = liste[0]
        for i, x in enumerate(liste):
            if x < value_min:
                value_min = x
                idx_min = i
        return idx_min

    def argmax(liste):
        if len(liste) == 0:
            return None

        idx_max = 0
        value_max = liste[0]
        for i, x in enumerate(liste):
            if x > value_max:
                value_max = x
                idx_max = i
        return idx_max

    def test_argmin():
        assert argmin([5, 8, 2, 9, 6, 3]) == 2
        assert argmin([7]) == 0
        assert argmin([]) == None

    def test_argmax():
        assert argmax([5, 8, 2, 9, 6, 3]) == 3
        assert argmax([7]) == 0
        assert argmax([]) == None
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    pytest pytest_2.py -v
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Le paramètre `-v` permet d'afficher plus de détails concernant les tests. Puisque deux fonctions sont nommées `test*`, il y a deux tests effectués par `pytest`. Cette option permet d'obtenir un détail pour chaque test codé, simplifiant ensuite le déboggage de l'application.

    En pratique, les tests unitaires doivent être exécutés une fois les données envoyés vers le dépôt Git. En revanche, il est déconseillé de les exécuter lors du pre-commit, car ce dernier doit être rapide. Les tests unitaires, notamment ceux incluant des tests pour les modèles, peuvent prendre du temps ce qui n'est pas conseillé pour les pre-commits.

    ## 4. Les fixtures

    Imaginons que l'on souhaite utiliser des données/paramètres uniquement pour les tests unitaires. Si l'on regarde bien, les deux fonctions `test_argmin` et `test_argmax` utilisent les mêmes listes pour tester les deux fonctions. Nous pourrions tout à fait définir des catalogues de référence pour les tests unitaires qui seront utilisés à chaque fois. C'est à cela que servent **les fixtures**.

    Regardons le code suivant qui n'utilise pas de fixture. Nous allons simplement créer une liste `test_data` qui sera utilisée par les deux fonctions de test.

    Remplacez le code de `pytest_2.py` par celui là
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
    # Pas bien !
    test_data = [5, 8, 2, 9, 6, 3]

    def argmin(liste):
        if len(liste) == 0:
            return None

        idx_min = 0
        value_min = liste[0]
        for i, x in enumerate(liste):
            if x < value_min:
                value_min = x
                idx_min = i
        return idx_min

    def argmax(liste):
        if len(liste) == 0:
            return None

        idx_max = 0
        value_max = liste[0]
        for i, x in enumerate(liste):
            if x > value_max:
                value_max = x
                idx_max = i
        return idx_max

    def test_argmin():
        assert argmin(test_data) == 2

    def test_argmax():
        assert argmax(test_data) == 3
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    pytest pytest_2.py -v
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Bien que le test ait fonctionné, cela n'est pas une bonne pratique, car nous allons obligatoirement définir cette variable globale en mémoire à chaque exécution du code, alors qu'elle n'est utilisée que pour les tests unitaires. Dans ce cas de figure, il est préférable de créer des fixtures.

    Les fixtures définissent un environnement dans lequel nous allons pouvoir tester notre code. Dans beaucoup de situations, il nous faut initialiser certaines variables avant de lancer les tests unitaires. Les fixtures sous `pytest` sont des fonctions qui sont utilisés comme **paramètres** des fonctions de tests unitaires.

    Regardons le code suivant.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    import pytest

    @pytest.fixture
    def test_data():
        return [5, 8, 2, 9, 6, 3]

    def argmin(liste):
        if len(liste) == 0:
            return None

        idx_min = 0
        value_min = liste[0]
        for i, x in enumerate(liste):
            if x < value_min:
                value_min = x
                idx_min = i
        return idx_min

    def argmax(liste):
        if len(liste) == 0:
            return None

        idx_max = 0
        value_max = liste[0]
        for i, x in enumerate(liste):
            if x > value_max:
                value_max = x
                idx_max = i
        return idx_max

    def test_argmin(test_data):
        assert argmin(test_data) == 2

    def test_argmax(test_data):
        assert argmax(test_data) == 3
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Tout d'abord, nous définissons la fonction `test_data` comme fixture à l'aide du décorateur de fonctions `@pytest.fixture`. Cette fonction va renvoyer une liste qui correspond à la liste de référence pour tester les deux fonctions. Ensuite, dans les fonctions de tests unitaires, nous allons récupérer comme paramètre cette même fonction `test_data`. Mais attention : lorsque l'on exécutera `pytest`, ce dernier va automatiquement remplacer le paramètre `test_data` (qui est supposé être une fonction car fixture) par le résultat de cette fonction.

    ![alt](public/tests4.png)

    Ainsi, à chaque exécution de `pytest`, ce sera en réalité `test_data()` qui sera passé comme paramètre pour les fonctions `test_argmin` et `test_argmax` (et non la fonction `test_data` elle-même). Cette méthode permet d'instancier plus efficacement les initialisations pour les tests, sans compromettre le reste du code qui lui n'aura pas besoin des tests dans un environnement de production.

    Exécutons maintenant `pytest`. (N'oubliez pas de remplacer à nouveau de contenu du code de `pytest_2.py` par ce code ci-dessus)
    """)
    return


@app.cell
def _(subprocess):
    #! pytest /tmp/pytest_2.py -v
    subprocess.call(["pytest", "/tmp/pytest_2.py", "-v"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Tout a correctement fonctionné. L'intérêt de ce système est de pouvoir ensuite centraliser l'initialisation des variables et des données pour les tests, évitant ainsi les duplicata de codes que l'on connaît déjà bien hors des tests.

    Maintenant que nous avons vu les points essentiels de `pytest`, nous pouvons dorénavant intégrer les tests unitaires dans notre projet Kedro. Et un avantage non négligeable est que Kedro supporte nativement `pytest` pour les tests unitaires : il dispose même de la commande `kedro test`. 🙂
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Intégration des tests unitaires dans Kedro

    Intégrons les tests unitaires et du modèle dans notre projet Kedro. En regardant la structure du projet, nous pouvons observer le dossier `tests` qui contient le fichier `test_run.py`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
    This module contains example tests for a Kedro project.
    Tests should be placed in ``src/tests``, in modules that mirror your
    project's structure, and in files named test_*.py.
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour exécuter proprement les tests avec Kedro, il faut que la structure des fichiers des tests soit identique à celle utilisée dans `src/purchase_predict` mais dans un dossier tests situé a la racine. Nous devons donc créer un dossier `tests` qui contient lui meme un dossier `pipeline` puis dans ce meme dossier crée le dossier `processing` pour répliquer l'architecture à l'identique. Vous avez du remarqué qu'en utilisant `pipeline create`, ces dossiers sont automatiquement crées notament avec `training` et `loading`.
    """)
    return


app._unparsable_cell(
    r"""
    project-root/
    │
    ├── src/
    │   └── purchase_predict/
    │       ├── pipeline/
    │       │   ├── loading/
    │       │   │   ├── __init__.py
    │       │   │   ├── nodes.py
    │       │   │   └── pipeline.py
    │       │   │
    │       │   ├── processing/
    │       │   │   ├── __init__.py
    │       │   │   ├── nodes.py
    │       │   │   └── pipeline.py
    │       │   │
    │       │   ├── training/
    │       │   │   ├── __init__.py
    │       │   │   ├── nodes.py
    │       │   │   └── pipeline.py
    │       │   │
    │       │   └── __init__.py
    │       │
    │       ├── __init__.py
    │       ├── __main__.py
    │       ├── pipeline_registry.py
    │       └── settings.py
    │
    └── tests/
        ├── pipeline/
        │   ├── loading/
        │   │   ├── __init__.py
        │   │   └── test_pipeline.py
        │   │
        │   ├── training/
        │   │   ├── __init__.py
        │   │   └── test_pipeline.py
        │   │
        │   ├── __init__.py
        │   └── test_run.py
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    uv sync
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Tests sur les nodes

    Avant de développer nos tests unitaires, créons sur le bucket Cloud Storage des **données de tests**. Dans le bucket, nous allons créer un dossier `data-test.csv/`.

    ![alt](public/tests1.png)

    Ensuite, pour alimenter ce dossier, nous allons copier deux fichiers CSV déjà présents dans `primary.csv/` vers `data-test.csv/`.

    ![alt](public/tests2_1.png)
    Habituellement, avec Kedro, nous pouvons effectuer deux séries de tests.

    - Les tests sur les nodes et les fonctions qu'utilisent les nodes. Par exemple, pour l'entraînement, le fichier `nodes.py` contient des fonctions qui ne sont pas directement utilisés par les nodes mais qui sont appelés par les fonctions des nodes.
    - Les tests sur les pipelines, permettant de les tester en fonction de plusieurs formats d'entrée ou sous forme d'exécution partielles.

    Dans le pipeline `loading` créons le fichier `test_nodes.py`. Seule la fonction `load_csv_from_bucket` est présente : nous allons uniquement tester cette dernière.
    """)
    return


@app.cell
def _():
    import pandas as pd

    from purchase_predict.pipelines.loading.nodes import load_csv_from_bucket


    def test_load_csv_from_bucket(project_id, primary_folder):
        df = load_csv_from_bucket(project_id, primary_folder)
        print(df.head())

    return load_csv_from_bucket, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous définissons la fonction `test_load_csv_from_bucket` avec les mêmes paramètres que la fonction `load_csv_from_bucket`.

    > ❓ Mais nous n'avons pas défini les fixtures ici ?

    En effet, il faudrait que les paramètres `project_id` et `primary_folder` soient des fixtures avec des fonctions de même nom. Or, ici, nous n'en avons pas créée. Il y a une raison à cela : plus tard, nous allons également créer un fichier de test pour le pipeline. Pour éviter des redondances de définitions de fixtures, nous allons définir les fixtures dans un fichier spécifique, qui derrière sera automatiquement exécuté par `pytest`.

    D'après <a href="https://docs.pytest.org/en/stable/fixture.html#conftest-py-sharing-fixture-functions" target="_blank">la documentation</a> de `pytest` sur les fixtures, nous pouvons les centraliser dans un fichier nommé `conftest.py` qui sera automatiquement exécuté avant les tests unitaires. Nous en créons un dans le dossier `loading`.
    """)
    return


@app.cell
def _():
    import pytest


    @pytest.fixture(scope="module")
    def project_id():
        return "<PROJECT_GCP>"


    @pytest.fixture(scope="module")
    def primary_folder():
        return "<NOM_DU_BUCKET>/data-test.csv"

    return (pytest,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'argument `scope="module"` permet de spécifier que les fixtures seront accessibles à l'intérieur de `purchase_predict`. Il ne reste plus qu'à lancer les test avec Kedro.
    """)
    return


app._unparsable_cell(
    r"""
    uv run pytest
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```log
    =============================================== test session starts ===============================================
    platform darwin -- Python 3.12.12, pytest-7.4.4, pluggy-1.6.0
    rootdir: /Users/noobzik/Documents/Kaggle/purchase-predict
    configfile: pyproject.toml
    testpaths: tests, unit
    plugins: anyio-4.12.1, asyncio-0.23.8, cov-6.3.0
    asyncio: mode=Mode.STRICT
    collected 2 items

    tests/pipelines/loading/test_nodes.py .                                                                     [ 50%]
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
    src/purchase_predict/pipelines/loading/pipeline.py          4      1    75%   11
    src/purchase_predict/pipelines/processing/__init__.py       3      3     0%   1-5
    src/purchase_predict/pipelines/processing/nodes.py         20     20     0%   1-36
    src/purchase_predict/pipelines/processing/pipeline.py       4      4     0%   1-7
    src/purchase_predict/pipelines/training/__init__.py         3      3     0%   6-10
    src/purchase_predict/pipelines/training/nodes.py           60     60     0%   6-165
    src/purchase_predict/pipelines/training/pipeline.py         5      5     0%   6-14
    src/purchase_predict/settings.py                            1      1     0%   31
    -------------------------------------------------------------------------------------
    TOTAL                                                     143    118    17%
    ================================================ 2 passed in 7.66s ================================================
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En cas d'erreur de type :
    ```log
    google.api_core.exceptions.Forbidden: 403 GET https://storage.googleapis.com/storage/v1/b/purchase-predict/o?projection=noAcl&prefix=test%2Fpart-&prettyPrint=false: purchase-predict@esgi-352608.iam.gserviceaccount.com does not have storage.objects.list access to the Google Cloud Storage bucket. Permission 'storage.objects.list' denied on resource (or it may not exist).
    ```

    Verifiez que votre service account mentionée dans les logs possède bien le rôle de `Lecteur d'objets Storage` en allant depuis `IAM & Admin` --> `IAM` --> `Votre service account` --> `Crayon` --> `Ajouter rôle` --> `Lecteur d'objets Storage`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Au tout début, `pytest` exécute le test sur `test_run.py`, qui montre un exemple de test unitaire avec Kedro. Ensuite, il exécute le seul autre fichier de test présent `test_nodes.py`. Puisqu'il n'y a aucun problème, cela signifie que le code n'a pas généré d'erreurs et que, en théorie, nous avons correctement réussi à implémenter la fonction de test avec Kedro. C'est alors que nous pouvons rajouter des tests et des conditions dans la fonction.
    """)
    return


@app.cell
def _(load_csv_from_bucket, pd):
    def test_load_csv_from_bucket(project_id, primary_folder):
        df = load_csv_from_bucket(project_id, primary_folder)
        assert type(df) == pd.DataFrame
        assert df.shape[1] == 16
        assert "purchased" in df

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Tests sur les pipelines

    En plus de tests unitaires sur les nodes, il est également possible d'effectuer des tests unitaires sur les pipelines. Cela permet, par exemple, de s'assurer du bon déroulement du pipeline en fonction de plusieurs situations (données incomplètes ou manquantes, mauvaise configuration de paramètres). En respectant le même principe que pour les nodes, nous allons créer le fichier `test_pipeline.py`.
    """)
    return


@app.cell
def _():
    from kedro.runner import SequentialRunner

    from purchase_predict.pipelines.loading.pipeline import create_pipeline


    def test_pipeline(catalog_test):
        runner = SequentialRunner()
        pipeline = create_pipeline()
        pipeline_output = runner.run(pipeline, catalog_test)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous récupérons la fonction `create_pipeline` permettant de créer le pipeline que nous souhaitons tester. Dans le test unitaire, nous instancions un `SequentialRunner`, qui exécutera le pipeline de manière séquentielle. Ensuite, nous créons une instance du pipeline et enfin nous exécuter ce dernier. Remarquons la variable `catalog_test` : il s'agit d'un catalogue de données spécifiquement crée pour le test. Plutôt que d'utiliser celui par défaut dans le fichier `catalog.yml`, nous allons pouvoir spécifier des données propres aux tests qui ne va pas perturber le catalogue déjà présent.

    Le catalogue de données représente lui aussi une fixture que nous rajoutons dans `conftest.py`.
    """)
    return


@app.cell
def _(pytest):
    from kedro.io import DataCatalog, MemoryDataset


    @pytest.fixture(scope="module")
    def project_id():
        return "<PROJECT_GCP>"


    @pytest.fixture(scope="module")
    def primary_folder():
        return "<NOM_DU_BUCKET>/primary/data-test.csv"


    @pytest.fixture(scope="module")
    def catalog_test(project_id, primary_folder):
        catalog = DataCatalog(
            {
                "params:gcp_project_id": MemoryDataset(project_id),
                "params:gcs_primary_folder": MemoryDataset(primary_folder),
            }
        )
        return catalog

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cette fonction retourne un `DataCatalog` qui sera envoyé en entrée au pipeline.

    <div class="alert alert-block alert-warning">
        Il faut respecter les noms des variables spécifiés dans le pipeline.
    </div>

    Pour rappel, le pipeline `loading` était défini de la manière suivante.
    """)
    return


@app.cell
def _(Pipeline, load_csv_from_bucket, node):
    def create_pipeline(**kwargs):
        return Pipeline(
            [
                node(
                    load_csv_from_bucket,
                    ["params:gcp_project_id", "params:gcs_primary_folder"],
                    "primary",
                )
            ]
        )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Là-aussi, `pytest` remplacera `catalog_test` par la fixture associée et permettra d'initialiser correctement l'environnement de test.
    """)
    return


app._unparsable_cell(
    r"""
    kedro test
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```log
    ╰─ uv run pytest                                                                                                ─╯
    =============================================== test session starts ===============================================
    platform darwin -- Python 3.12.12, pytest-7.4.4, pluggy-1.6.0
    rootdir: /Users/noobzik/Documents/Kaggle/purchase-predict
    configfile: pyproject.toml
    testpaths: tests, unit
    plugins: anyio-4.12.1, asyncio-0.23.8, cov-6.3.0
    asyncio: mode=Mode.STRICT
    collected 4 items

    tests/pipelines/loading/test_nodes.py ..                                                                    [ 50%]
    tests/pipelines/loading/test_pipeline.py .                                                                  [ 75%]
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
    src/purchase_predict/pipelines/processing/__init__.py       3      3     0%   1-5
    src/purchase_predict/pipelines/processing/nodes.py         20     20     0%   1-36
    src/purchase_predict/pipelines/processing/pipeline.py       4      4     0%   1-7
    src/purchase_predict/pipelines/training/__init__.py         3      3     0%   6-10
    src/purchase_predict/pipelines/training/nodes.py           60     60     0%   6-165
    src/purchase_predict/pipelines/training/pipeline.py         5      5     0%   6-14
    src/purchase_predict/settings.py                            1      1     0%   31
    -------------------------------------------------------------------------------------
    TOTAL                                                     143    117    18%
    =============================================== 4 passed in 14.98s ================================================
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Le pipeline a été exécuté sans problème. Nous pouvons là-aussi rédiger des tests pour le pipeline, qui en soit seront quasi-identiques à ceux du node car ce pipeline ne contient qu'un seul node et ce dernier n'appelle pas d'autres fonctions.

    on peut donc remplacer le test_pipeline.py du dossier loading dans les tests par:
    """)
    return


@app.cell
def _():
    import pandas as pd
    from kedro.runner import SequentialRunner

    from purchase_predict.pipelines.loading.pipeline import create_pipeline


    def test_pipeline(catalog_test):
        runner = SequentialRunner()
        pipeline = create_pipeline()
        pipeline_output = runner.run(pipeline, catalog_test)
        df = pipeline_output["primary"].load()
        assert type(df) is pd.DataFrame
        assert df.shape[1] == 16
        assert "purchased" in df

    return (pd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #✔️ Conclusion

    Peut-être il s'agit de ton premier test unitaire avec Python : dans tous les cas, tu sais maintenant en écrire, et c'est une très bonne pratique !

    - Nous avons vu pourquoi les tests logiciels étaient indispensables.
    - Nous avons rédigé plusieurs tests unitaires pour le pipeline de collecte des données.

    > ➡️ Il nous reste maintenant à définir et rédiger les <b>tests sur le modèle de Machine Learning</b>.
    """)
    return


if __name__ == "__main__":
    app.run()
