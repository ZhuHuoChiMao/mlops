import marimo

__generated_with = "0.19.9"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. Modèles de boosting
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Maintenant que nous avons plus de connaissances sur les données, nous pouvons commencer par transformer les données et entraîner un premier modèle. Notre choix se portera sur **LightGBM**, par sa rapidité d'entraînement et ses performances aussi proches que XGBoost.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Transformer le jeu de données pour construire la base d'apprentissage</li>
        <li>Calibrer un modèle LightGBM</li>
        <li>Évaluer les résultats</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/xUA7b4arnbo3THfzi0/giphy.gif" width="300" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transformation des données

    Reprenons l'échantillon que nous avons étudié auparavant.
    """)
    return


@app.cell
def _():
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set()

    # La fonction expanduser permet de convertir le répertoire ~ en chemin absolu
    data = pd.read_csv(os.path.expanduser("data/sample.csv"))
    print("Taille de l'échantillon :", data.shape[0])
    print("Taille mémoire : {:2.2f} Mb".format(data.memory_usage().sum() / 1e6))
    data.head()
    return data, np, os, pd, plt, sns


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme évoqué précédemment, nous cherchons à connaître si, lors d'une session, un utilisateur va acheter un produit ou non. Ainsi, notre base d'apprentissage va être constitué de sessions dont on sait si l'utilisateur a acheté ce produit ou non.

    Chaque observation de notre base d'apprentissage disposera des informations suivantes.

    - Les informations liées au produit (nombre de vues du produit dans la session, catégorie, identifiant du produit).
    - Les informations liées à la session (durée en secondes, nombres de sessions précédentes, heure de début).

    Nous allons donc **transformer l'échantillon** afin d'obtenir ces informations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Informations sur les produits

    Conformément à notre objectif, notre base d'apprentissage représentera un ensemble de sessions où, pour chaque session et chaque produit, l'utilisateur a acheté (colonne `purchased` à $1$) ce produit ou non (colonne `purchased` à $0$). Il faudra donc **agréger les lignes** ayant la même session utilisateur et pour le même produit.

    Commençons par construire la colonne `purchased`.
    """)
    return


@app.cell
def _(data, np):
    # On récupère les événements dont la colonne user_session n'est pas nulle
    events_per_session = data.loc[~data["user_session"].isna(), :].copy()

    # On crée une colonne purchase qui vaut 0 ou 1 en fonction de la colonne event_type
    events_per_session['purchased'] = np.where(events_per_session['event_type'] == "purchase", 1, 0)
    # On agrège par session et par produit pour savoir si ce dernier a été acheté dans la session
    events_per_session['purchased'] = events_per_session \
        .groupby(["user_session", "product_id"])['purchased'] \
        .transform("max")

    events_per_session.sample(n=5)
    return (events_per_session,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Si la colonne `purchased` vaut $1$, cela signifie que durant la session, l'utilisateur a acheté le produit concerné.

    Effectuons la même chose pour le nombre de vues dans la session en créant la colonne `num_views`.
    """)
    return


@app.cell
def _(events_per_session, np):
    # On détermine combien de fois l'utilisateur a vu de produits dans la session
    events_per_session['num_views_session'] = np.where(events_per_session['event_type'] == "view", 1, 0)
    events_per_session['num_views_session'] = events_per_session.groupby(["user_session"]) \
        ['num_views_session'].transform("sum")

    # On détermine combien de fois l'utilisateur a vu un produit en particulier dans la session
    events_per_session['num_views_product'] = np.where(events_per_session['event_type'] == "view", 1, 0)
    events_per_session['num_views_product'] = events_per_session.groupby(["user_session", "product_id"]) \
        ['num_views_product'].transform("sum")

    events_per_session.sample(n=5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous allons également effectuer un `split` sur la colonne `category_code` pour récupérer la catégorie et la sous-catégorie de chaque produit (si elles existent).
    """)
    return


@app.cell
def _(events_per_session):
    events_per_session['category'] = events_per_session['category_code'] \
        .str.split(".",expand=True)[0].astype('category')
    events_per_session['sub_category'] = events_per_session['category_code'] \
        .str.split(".",expand=True)[1].astype('category')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Enfin, nous convertissons la colonne `event_time` en objet `datetime`, ce qui nous permet de récupérer précisément l'heure, la minute et le jour de la semaine associés à l'événement.
    """)
    return


@app.cell
def _(events_per_session, pd):
    events_per_session["event_time"] = pd.to_datetime(events_per_session["event_time"], utc=True)

    events_per_session["hour"] = events_per_session["event_time"].dt.hour
    events_per_session["minute"] = events_per_session["event_time"].dt.minute
    events_per_session["weekday"] = events_per_session["event_time"].dt.dayofweek
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Informations sur les sessions

    Regardons maintenant les sessions de chaque utilisateur. Nous allons commencer par déterminer les durées de chaque session. Pour cela, la méthode la plus facile consiste à regrouper les observations par `user_session`, puis à calculer le minimum et le maximum de la colonne `event_time`.
    """)
    return


@app.cell
def _(events_per_session, pd):
    # On calcule la date minimum et maximum de chaque session
    sessions_duration = events_per_session \
        .groupby("user_session").agg(
            {"event_time": ["min", "max"]}
        ) \
        .reset_index()

    # On converti les colonnes max et min vers les datetime
    sessions_duration["amax"] = pd.to_datetime(sessions_duration["event_time"]["max"])
    sessions_duration["amin"] = pd.to_datetime(sessions_duration["event_time"]["min"])
    del sessions_duration["event_time"]
    # On aplati au niveau 0 les colonnes
    sessions_duration.columns = sessions_duration.columns.get_level_values(0)
    # On calcule la durée totale, en secondes, de chaque TimeDelta
    sessions_duration["duration"] = (sessions_duration["amax"] - sessions_duration["amin"]).dt.seconds
    sessions_duration.head()
    return (sessions_duration,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Une fois calculé, nous avons simplement besoin de faire **une jointure** avec le DataFrame `events_per_session`, dont le résultat sera stocké dans le DataFrame `dataset`.
    """)
    return


@app.cell
def _(events_per_session, sessions_duration):
    dataset = events_per_session \
        .sort_values("event_time") \
        .drop_duplicates(["event_type", "product_id", "user_id", "user_session"]) \
        .loc[events_per_session["event_type"].isin(["cart", "purchase"])] \
        .merge(
            sessions_duration[["user_session", "duration"]],
            how="left",
            on="user_session"
        )

    dataset.head()
    return (dataset,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notons qu'ici nous utilisons un `drop_duplicates` pour supprimer les lignes doublons : elles correspondent au même produit, type d'événement, utilisateur et session (par exemple, un utilisateur qui visite deux fois le même produit dans une seule session).

    <div class="alert alert-block alert-info">
        Nous avons déjà récolté cette informations plus haut en calculant le nombre de vues par session.
    </div>

    Autre question qui peut se révéler intéressante : l'utilisateur a-t-il déjà eu d'autres sessions auparavant ? Pour cela, il est important d'établir une **relation d'ordre**, notamment avec `event_time`.
    """)
    return


@app.cell
def _(dataset):
    count_prev_sessions = dataset[["user_id", "user_session", "event_time"]] \
        .sort_values("event_time") \
        .groupby(["user_id", "user_session"]) \
        .first() \
        .reset_index()

    # cumcount permet de faire un comptage cumulé des lignes : 0, 1, 2, 3, ...
    count_prev_sessions["num_prev_sessions"] = count_prev_sessions \
        .sort_values("event_time") \
        .groupby("user_id") \
        .cumcount()

    count_prev_sessions.head()
    return (count_prev_sessions,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme toujours, nous effectuons une jointure avec `dataset`.
    """)
    return


@app.cell
def _(count_prev_sessions, dataset):
    dataset_1 = dataset.merge(count_prev_sessions[['user_session', 'num_prev_sessions']], how='left', on='user_session')
    return (dataset_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Une dernière information qui pourrait également être utile, c'est de savoir si l'utilisateur a déjà vu un produit en particulier dans une session précédente. Elle ressemble fortement à la transformation précédente, si ce n'est qu'il faut également prendre en compte le `product_id` et le `user_id`.
    """)
    return


@app.cell
def _(dataset_1):
    view_prev_session = dataset_1[['user_id', 'user_session', 'event_time', 'product_id']]
    view_prev_session = view_prev_session.sort_values('event_time').groupby(['user_id', 'user_session', 'product_id']).first().reset_index()
    view_prev_session['num_prev_product_views'] = view_prev_session.sort_values('event_time').groupby(['user_id', 'product_id']).cumcount()
    dataset_2 = dataset_1.merge(view_prev_session[['user_session', 'product_id', 'num_prev_product_views']], how='left', on=['user_session', 'product_id'])
    return (dataset_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Enfin, nous allons supprimer les lignes doublons par rapport aux colonnes `user_session`, `product_id` et `purchased`, si par exemple un utilisateur a acheté plus d'une fois un même produit (auquel cas, l'issue serait toujours la classe positive à partir du moment où le produit est acheté au moins une fois).
    """)
    return


@app.cell
def _(dataset_2, os):
    dataset_3 = dataset_2.sort_values('event_time').drop_duplicates(['user_session', 'product_id', 'purchased']).drop(['event_time', 'event_type', 'category_code', 'category_id'], axis=1)
    dataset_3.to_csv(os.path.expanduser('data/dataset.csv'), index=False)
    dataset_3.head()
    return (dataset_3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous pouvons maintenant vérifier la proportion des deux classes présentes dans le jeu de données.
    """)
    return


@app.cell
def _(dataset_3):
    print('Taille du jeu de données :', dataset_3.shape[0])
    print('Proportion des classes :')
    dataset_3['purchased'].value_counts() / dataset_3.shape[0]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notre jeu de données n'est déséquilibré, il n'y a donc pas de ré-échantillonnage à appliquer.
    """)
    return


@app.cell
def _(dataset_3, os):
    dataset_3.to_csv(os.path.expanduser('data/primary1.csv'), index=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Feature Engineering

    Maintenant que notre DataFrame `dataset` contient les observations, nous devons appliquer une étape de **feature engineering** pour que la base d'apprentissage soit transformée numériquement et utilisable par notre modèle. Il n'y a, en réalité, que trois colonnes à encoder : `brand`, `category` et `sub_category`.
    """)
    return


@app.cell
def _(dataset_3):
    from sklearn.preprocessing import LabelEncoder

    # Le DataFrame features est la base d'apprentissage encodée numériquement
    features = dataset_3.drop(['user_id', 'user_session'], axis=1).copy()

    for label in ["category", "sub_category", "brand"]:
        features[label] = features[label].astype("string").fillna("unknown")
        encoder = LabelEncoder()
        features[label] = encoder.fit_transform(features[label])


    features['weekday'] = features['weekday'].astype(int)
    features.head()
    return (features,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Vérifions qu'il n'y a pas de valeurs manquantes.
    """)
    return


@app.cell
def _(features):
    features.isna().sum()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    À partir de là, nous allons créer la base d'apprentissage $(X, y)$ constituée des *features* puis séparer la base en deux sous-ensembles.
    """)
    return


@app.cell
def _(features, pd):
    from sklearn.model_selection import train_test_split

    X = features.drop("purchased", axis=1)
    y = features['purchased']
    columns_to_convert = ["brand", "category", "sub_category"]

    for col in columns_to_convert:
        X[col] = pd.to_numeric(X[col], errors='coerce')
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=40
    )

    X_train.head()
    return X, X_test, X_train, y, y_test, y_train


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous allons ensuite enregistrer les données générées.

    /// attention | Attention!


    Il est important d'avoir une consistance sur les ensembles utilisés pour entraîner les modèles et pour les évaluer.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Il se peut que nous ayons des problème lié au typage des colonnes, lors de l'entrainement de notre modèle. Pour éviter ce cas, nous allons forcer le passage des colonnes :
    """)
    return


@app.cell
def _(X, X_test, X_train, os, y, y_test, y_train):
    X.to_csv(os.path.expanduser("data/X.csv"), index=False)
    y.to_csv(os.path.expanduser("data/y.csv"), index=False)

    X_train.to_csv(os.path.expanduser("data/X_train.csv"), index=False)
    X_test.to_csv(os.path.expanduser("data/X_test.csv"), index=False)
    y_train.to_csv(os.path.expanduser("data/y_train.csv"), index=False)
    y_test.to_csv(os.path.expanduser("data/y_test.csv"), index=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Modélisation avec LightGBM

    L'algorithme que nous utiliserons est **LightGBM** : il a l'avantage d'être plus rapide que XGBoost tout en conservant des performances proches.

    Vous y trouverez le papier correspondant sur le lien suivant : [LightGBM](https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf)

    ### Création des arbres

    Bien que similaire, la principale différence entre LightGBM et XGBoost est la manière dont les arbres sont construits.

    XGBoost applique une méthode appelée **level-wise tree growth**, où chaque arbre est construit niveau par niveau. Ainsi, XGBoost développe le premier niveau (profondeur 1), puis développe le second niveau (profondeur 2) dès lors que le niveau précédent a été étendu. Il s'agit d'une approche horizontale.

    LightGBM applique une méthode appelée **leaf-wise tree growth**. Contrairement à la méthode précédente, l'élagage n'est pas réalisé en fonction de la profondeur, mais directement en fonction des feuilles. Ainsi, LightGBM étendra chaque feuille de manière verticale, sans s'assurer que la profondeur concernée est totalement étendue. Cela peut produire, par exemple, des arbres qui ne sont pas équilibrés (d'où la possibilité de toujours ajouter l'hyper-paramètre `max_depth`).

    /// admonition | information

    Si on ne faisait pas d'élagage d'arbres, les arbres construits avec XGBoost et LightGBM seraient identiques.
    ///

    Une des principales raisons pour laquelle LightGBM est très souvent plus rapide que XGBoost est due à l'utilisation de la méthode *leaf-wise*.

    LightGBM permet également d'utiliser le **Gradient-based One-Side Sampling** (GOSS), qui consiste à sélectionner majoritairement des observations don les gradients sont élevés. Par exemple, si sur 10k lignes, seules 1k lignes présentent des gradients élevés, LightGBM sélectionnerai ces 1k observations, auxquelles il y ajoutera un certain nombres d'observations parmi les 9k restantes.

    Les hyper-paramètres les plus importants pour LightGBM sont les suivants.

    - `num_leaves` qui contrôle le nombre de feuilles (noeuds) dans chaque arbre.
    - `min_child_samples` spécifie le nombre d'observations dans une feuille. Il s'agit d'un hyper-paramètre importante pour éviter un sur-apprentissage, notamment lorsque le nombre de feuilles est élevé.
    - `max_depth` pour contrôler la profondeur maximale de chaque arbre.
    - `n_estimators` pour déterminer le nombre d'arbres à calibrer.
    - `learning_rate` pour spécifier le taux d'apprentissage de chaque arbre.
    """)
    return


@app.cell
def _():
    from lightgbm.sklearn import LGBMClassifier
    from sklearn.model_selection import RepeatedKFold
    from sklearn.metrics import f1_score

    return LGBMClassifier, RepeatedKFold, f1_score


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Entraînons un classifieur LightGBM avec les paramètres par défaut. Nous allons mettre en place un <a href="https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RepeatedKFold.html#sklearn.model_selection.RepeatedKFold" target="_blank">Repeated k-Fold</a> pour calculer des scores sur plusieurs instances du modèle.
    /// admonition
    Pour rappel, la validation croisée est importante ici pour s'assurer que le score calculé pour un modèle est cohérent.
    ///
    """)
    return


@app.cell
def _(RepeatedKFold):
    # On répète 3 fois un 5-Fold
    rep_kfold = RepeatedKFold(n_splits=4, n_repeats=3)

    # Hyper-paramètres des modèles
    hyp_params = {
        "num_leaves": 60,
        "min_child_samples": 10,
        "max_depth": 12,
        "n_estimators": 100,
        "learning_rate": 0.1
    }
    return hyp_params, rep_kfold


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous laisserons les paramètres par défaut de l'objet `LGBMClassifier`.
    """)
    return


@app.cell
def _(LGBMClassifier, X, f1_score, hyp_params, rep_kfold, y):
    scores_train = []
    scores_test = []
    n_iter = 1
    for train_I, test_I in rep_kfold.split(X):
        print('Itération {} du k-Fold'.format(n_iter))
        X_fold_train = X.iloc[train_I, :]  # On récupère les indices des sous-échantillons
        y_fold_train = y.iloc[train_I]
        X_fold_test = X.iloc[test_I, :]
        y_fold_test = y.iloc[test_I]
        model = LGBMClassifier(**hyp_params, objective='binary', verbose=-1)
        model.fit(X_fold_train, y_fold_train)
        scores_train.append(f1_score(y_fold_train, model.predict(X_fold_train)))  # On entraîne un LightGBM avec les paramètres par défaut
        scores_test.append(f1_score(y_fold_test, model.predict(X_fold_test)))
        n_iter = n_iter + 1  # On calcule le score du modèle sur le test
    return scores_test, scores_train


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Regardons maintenant les scores sur les deux sous-ensembles.
    """)
    return


@app.cell
def _(np, pd, plt, scores_test, scores_train, sns):
    import matplotlib.ticker as mtick

    print("Score Train médian : {:2.1f}%".format(np.mean(scores_train) * 100))
    print("Score Test médian : {:2.1f}%".format(np.mean(scores_test) * 100))

    scores = pd.DataFrame.from_dict({
        "Train Set": scores_train,
        "Test Set": scores_test
    })

    plt.figure(figsize=(14, 4))
    sns.boxplot(data=scores, orient="h")
    plt.title("Scores des modèles du k-Fold", fontsize=17)
    plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1, 1))
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Les scores médians pour les pour les ensembles d'entraînement et de test sont respectivement $91.9\%$ et $87.9\%$. Tout d'abord, nous remarquons d'après le graphique que les variations de scores sont faibles (un écart-type d'environ $0.5\%$ pour l'ensemble de test). Ensuite, la différence entre les deux scores médian est d'environ $4\%$, ce qui montre qu'il n'y a pas de sur-apprentissage apparent de nos modèles.

    À partir des ces résultats, nous pouvons maintenant calibrer un LightGBM sur le couple `(X_train, y_train)`.
    """)
    return


@app.cell
def _(LGBMClassifier, X_train, hyp_params, y_train):
    model_1 = LGBMClassifier(**hyp_params, objective='binary', verbose=-1)
    model_1.fit(X_train, y_train)
    return (model_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Calculons également les scores sur les ensembles.
    """)
    return


@app.cell
def _(X_test, X_train, f1_score, model_1, y_test, y_train):
    print('Score Train : {:2.1f}%'.format(f1_score(y_train, model_1.predict(X_train)) * 100))
    print('Score Test : {:2.1f}%'.format(f1_score(y_test, model_1.predict(X_test)) * 100))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme prévu, les scores sont très similaires à ceux obtenus lors du $k$-Fold.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Évaluation du modèle

    L'évaluation du modèle est importante, car elle va nous permettre de s'assurer que le modèle est suffisamment performant, tout en ayant un comportement prévisible.

    /// attention
    Les scores ne doivent pas être les seules métriques pour évaluer un modèle de Machine Learning.
    ///

    Outre les scores, le modèle doit également satisfaire d'autres contraintes. En effet, dans notre cas d'application orienté marketing, nous souhaitons savoir si un client va finaliser un achat lors de son parcours sur la plateforme ECommerce.

    L'objectif ici est **d'inciter l'utilisateur à finaliser son panier**. Pour cela, une méthode consiste à proposer des réductions sur-mesure pour augmenter la probabilité que l'utilisateur termine par un achat. Il s'agit donc d'une problématique de classification binaire. Nous pouvons ainsi faire deux types d'erreurs.

    - Un **faux positif** consiste à prédire que l'utilisateur va acheter le produit alors qu'en réalité, il ne finalisera pas l'achat. Dans ce cas, proposer une réduction n'a que peu d'impact, puisqu'il y a de forte chances que l'utilisateur ne l'utilise pas.
    - Un **faux négatif** consiste à prédire que l'utilisateur ne va pas acheter le produit alors qu'en réalité, il ne finalisera l'achat. Dans ce deuxième cas de figure, donner une réduction à cet utilisateur implique une perte de bénéfice, puisque l'utilisateur aurait tout de même acheté le produit, et ce même sans code de réduction.

    Ici, nous voyons que le faux négatif a **plus d'impact** en terme économique que le faux positif. En effet, il vaut mieux qu'un utilisateur achète à prix réduit plutôt qu'il n'achète pas un produit. À l'inverse, on a tout intérêt à ne pas proposer de réduction à un utilisateur qui achèterai un produit même sans code de réduction.

    Notre objectif, c'est donc de détecter correctement les faux négatifs, puisque ces derniers impactent les bénéfices, contraitement au faux positif.

    > ❓ Comment évaluer si notre modèle a plus tendance à produire des faux positifs ou des faux négatifs ?

    Pour cela, il faut bien comprendre qu'en classification binaire, la sortie du modèle n'est pas une classe ($0$ ou $1$), mais **une probabilité** (d'être dans chacune des deux classes).

    Il existe implicitement un seuil $\alpha \in [0, 1]$ à partir duquel on considère que si $\mathbb{P}(y = 1 | X=x) \geq \alpha$ alors la classe prédite est positive. Bien évidemment, en fonction de ce seuil $\alpha$, la part d'observations en faux positif ou faux négatif ne seront pas identiques.

    Regardons quelques statistiques qui se basent sur la **matrice de confusion**.

    - La **spécificité** représente la probabilité de prédire un non achat parmi les utilisateurs n'ayant pas acheté.

    $$\frac{TN}{FP+TN}$$

    - La **sensibilité** (ou **rappel**) représente la probabilité de prédire un achat parmi les utilisateurs ayant acheté.

    $$\frac{TP}{TP+FN}$$

    - La **précision** représente la probabilité d'avoir des utilisateurs ayant acheté parmi les utilisateurs dont un achat a été prédit.

    $$\frac{TP}{TP+FP}$$

    Les deux premières mesures s'intéressent aux taux **parmi la connaissance théorique** du comportement, alors que la dernière s'intéresse au taux **parmi les prédictions du modèle**.

    Nous avons dit qu'il est important d'avoir le moins de faux négatif : c'est donc **la sensibilité (ou rappel)** qui doit être observée. Un rappel faible signifie que la part de faux négatifs est importante, alors qu'un rappel fort signifie que la part de faux négatifs est proche de $0$.

    <div class="alert alert-block alert-warning">
        Le rappel, à lui seul, ne peut pas déterminer entièrement si le modèle est performant ! Un modèle peut très bien avoir un rappel très élevé, mais une précision très basse.
    </div>

    Cet exemple correspond à un modèle qui prédirait tout le temps $1$ : il n'y aurait aucun faux négatif (car il ne prédit jamais $0$), mais la précision serait très mauvaise car il y aurait beaucoup de faux positifs. C'est pour cela qu'on utilise également le **F1 score**, qui fait intervenir à la fois la précision et le rappel.

    $$\text{Score}_{\text{F1}}=2 \frac{\text{Precision} \times \text{Rappel}}{\text{Precision} + \text{Rappel}}$$
    """)
    return


@app.cell
def _(X_test, model_1, y_test):
    from sklearn.metrics import recall_score, precision_score
    print('Precision Test : {:2.1f}%'.format(precision_score(y_test, model_1.predict(X_test)) * 100))
    print('Recall Test : {:2.1f}%'.format(recall_score(y_test, model_1.predict(X_test)) * 100))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous avons un rappel très élevé, ce qui signifie qu'il y a peu de faux négatifs. En revanche, la précision est moins bonne : il y plus de faux positifs, notre modèle à souvent tendance à trop prédire un achat alors que ce ne sera pas le cas.

    > ❓ Comment pouvons-nous améliorer la précision ?

    L'intérêt maintenant, c'est de déterminer quels sont les hyper-paramètres optimaux qui vont nous permettre d'obtenir les meilleurs performances. Pour cela, une pratique courante est **l'AutoML**, qui consiste à automatiser l'entraînement des modèles.

    Et très souvent, en essayant de déterminer les meilleurs hyper-paramètres, plutôt que d'utiliser une recherche par grille, les **méthodes bayésiennes** sont plus courantes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Nous venons de mettre en place notre premier modèle prédictif sur nos données.

    - Le jeu de données a été transformé pour être envoyé au modèle prédictif.
    - Avec un k-Fold, nous avons entraîné un LightGBM.
    - Nous avons mesuré les performances obtenues.

    > ➡️ Le rôle du ML Engineer est, à terme, d'automatiser cette étape qui consiste à trouver le meilleur modèle (AutoML). C'est ce que nous allons voir avec <b>l'optimisation bayésienne</b>.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
