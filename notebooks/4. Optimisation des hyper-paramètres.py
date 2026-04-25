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
    # 4. Optimisation des hyper-paramètres
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'optimisation bayésienne est une méthode permettant de déterminer les hyper-paramètres optimaux d'un modèle en utilisant les outils de statistiques bayésiennes. Leur principal intérêt contrairement aux recherches par grille est d'utiliser l'information acquise au cours de l'optimisation pour déterminer les prochains hyper-paramètres à tester.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Découvrir l'approche bayésienne d'optimisation des hyper-paramètres</li>
        <li>Lancer une recherche TPE sur LightGBM</li>
        <li>Calibrer un modèle sur les meilleurs hyper-paramètres</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/cmqZM1lFsKHqo/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Approche bayésienne

    Dans un modèle, nous devons différencier deux types de paramètres.

    - En statistique paramétrique, le modèle est une fonction de paramètre $\theta \in \Theta$ : les composantes de $\theta$ représentent **les paramètres du modèle**. Ils sont estimés par des algorithmes d'optimisation numérique.
    - Les **hyper-paramètres** sont des valeurs d'ajustement du modèle qui sont fixes et qui ne sont pas estimés par les algorithmes d'optimisation, mais utilisés par ces derniers.

    Le choix des hyper-paramètres aura donc une influence sur la façon dont le modèle est entraîné et automatiquement sur ses performances.

    La difficulté des hyper-paramètres, c'est que contrairement aux paramètres du modèle, il n'y a aucun moyen de savoir si un jeu d'hyper-paramètres est optimal ou non.

    Pour cela, une solution consiste à tester plusieurs jeux d'hyper-paramètres et de choisir celui qui maximise les performances.

    Il y a autant d'entraînement de modèle à effectuer qu'il y a de jeux d'hyper-paramètres. Ainsi, une question se pose : **comment déterminer le jeu d'hyper-paramètre optimal le plus rapidement ?**

    Jusqu'ici, la plupart des approches utilise des recherches par grille (déterministes ou aléatoires) qui consiste à tester un nombre de points finis de jeux d'hyper-paramètres. Nous allons voir ici une autre approche, plus efficace dans certains cas.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Fonction substitut

    Dans l'approche bayésienne, nous allons « capitaliser » sur les résultats obtenus aux précédents jeux d'hyper-paramètres. Autrement dit, à chaque jeu d'hyper-paramètres, on cherche à calculer le prochain score à partir des hyper-paramètres.

    $$\tau(\text{Hyper-paramètres}) \overset{\Delta}{=} \mathbb{P}(\text{Score}|\text{Hyper-paramètres})$$

    En pratique, nous ne pouvons pas calculer cette loi bayésienne. Pour cela, nous introduisons une fonction moins complexe mais suffisamment similaire que l'on cherchera à optimiser. Cette fonction est appelée **substitut** (ou **surrogate**).

    Le fait de rajouter un substitut fait que les calculs pour trouver le prochain $S_{\text{Opt}}^{(t)}$ (jeu d'hyper-paramètres) à tester sur un modèle **sont assez importants**. Mais ces temps de calculs sont compensés par une recherche d'un jeu d'hyper-paramètres optimal en un nombre d'itérations inférieurs que pour les méthodes de recherche par grille.

    L'optimisation bayésienne prend tout son sens dans la recherche des hyper-paramètres optimaux, puisque les temps de calcul de $\tau(S_{\text{Opt}}^{(t)})$ sont déjà considérables. En revanche, cette méthode n'aurait aucun intérêt dans un cadre classique d'optimisation numérique ou de nombreuses itérations sont nécessaires pour s'approcher d'un éventuel extremum global.

    Il existe plusieurs algorithmes bayésiens qui permettent d'estimer un jeu d'hyper-paramètres optimal. L'algorithme SMBO pour Sequential Model-Based Optimization est un des plus utilisés en Machine Learning.

    ### Algorithme SMBO

    L'algorithme Sequential Model-Based Optimization (SMBO) est une famille d'algorithmes bayésiens où l'objectif est de maximiser $\tau$ en cherchant à minimiser une fonction (par exemple $l$) par un modèle substitut (*surrogate*).

    Tout d'abord, la base de connaissance $\mathcal{H}$ des hyper-paramètres pour le substitut $\tau$ est initialisé à l'ensemble vide. Il est également nécessaire de fournir un nombre d'itérations maximale $T$ ainsi qu'un modèle initial $M_0$ **pour le substitut**. La méthode SMBO s'exécute ensuite de la façon suivante à chaque itération $t$.

    1. Estimer $S_{\text{Opt}}^{(t)}=\text{argmax}_S l(S, M_{t-1})$
    2. Calculer le score $R$ d'un modèle $\hat{f}$ entraîné avec le jeu d'hyper-paramètres $S_{\text{Opt}}^{(t)}$
    3. Mettre à jour la base de connaissances : $\mathcal{H}=\mathcal{H} \cup (S_{\text{Opt}}^{(t)}, R)$
    4. Estimer un nouveau modèle $M_t$ pour le substitut à partir de $\mathcal{H}$.

    En pratique, les modèles substituts utilisés sont les processus Gaussiens (GP), des Random Forests (RF) ou des Tree of Parzen Estimators (TPE).

    ### Fonction de sélection

    La fonction de sélection (ou d'acquisition) fournit un critère quantitatif dans l'algorithme SMBO : c'est elle qui permet de choisir le prochain jeu d'hyper-paramètres à tester (étape 1). Une fonction de sélection particulièrement utilisée est l'Expected Improvement :

    $$\text{EI}_{y^*}(u)=\int_{-\infty}^{y^*} (y^*-y)p(y|u)dy$$

    où $y^*$ est un seuil maximal et $p(y|u)$ la <b>densité du modèle substitut</b> évalué en $y$ sachant $u$. L'objectif est donc de maximiser $\text{EI}_{y^*}$ sachant $u$, qui dans SMBO représentera $S_{\text{Opt}}^{(t)}$.

    Intuitivement, si $p(y|u) =0$ pour tout $y < y^*$, alors le jeu d'hyper-paramètres $u := S_{\text{Opt}}^{(t)}$ est considéré comme optimal puisque aucune amélioration sur le score ne peut être apporté.

    À l'inverse, si $\text{EI}_{y^*}(u)>0$, c'est qu'il existe un meilleur jeu d'hyper-paramètres $u$ pouvant amener à une augmentation du score par rapport au jeu actuel. Sans une introduction d'un nombre d'itérations maximale, les temps de calcul pourraient être bien trop élevés, non seulement parce qu'il est rare d'obtenir une valeur exacte en optimisation, mais également parce que l'entraînement du modèle $\hat{f}$ peut lui aussi dépendre de variations aléatoires (propre à ce dernier) et toujours engendrer des variations de scores pour un même $u$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Application avec Tree of Parzen Estimators

    Nous allons ici étudier le cas où le modèle substitut est un Tree of Parzen Estimators (TPE). L'idée des estimateurs Parzen est proche de l'optimisation bayésienne, bien qu'il y ait une différence sur le plan théorique.

    Dans cette approche, plutôt que de construire un modèle bayésien dans l'étape 4 (et donc de modéliser $l(S_{\text{Opt}}^{(t)})$), on calcule directement cette quantité à partir des règles de calcul bayésiennes.

    $$l(S_{\text{Opt}}^{(t)})=p(y|x)=\frac{p(x|y)p(y)}{p(x)}$$

    La probabilité d'obtenir un jeu d'hyper-paramètres en fonction des performances du modèle avec $l$ est donné par



    $$
    p(x|y)=\left\{\begin{matrix}
    l(x) & \text{si } y < y^* \\
    g(x) & \text{si } y \geq y^*
    \end{matrix}\right.
    $$


    où $y^*$ est un seuil, similaire à celui de $\text{EI}$, et $y$ étant ici la perte du modèle dans le cadre de l'optimisation des hyper-paramètres. L'intérêt de cette représentation est de construire deux distributions $l$ et $g$ qui correspondent aux situations où la perte du modèle est inférieure au seuil $y^*$ et inversement.

    Maintenant, reprenons le calcul de l'Expected Improvement et remplaçons $p(y|u)$ par le calcul bayésien.


    $$
    \begin{aligned}
    \text{EI}_{y^*}(u) & = & \int_{-\infty}^{y^*} (y^*-y)\frac{p(u|y)p(y)}{p(u)}dy \\
    & = & \frac{l(u)}{p(u)} \int_{-\infty}^{y^*} (y^*-y)p(y)dy \\
    & = & \frac{l(u)}{p(u)} \left ( \gamma y^* - \int_{-\infty}^{y^*} yp(y)dy \right)
    \end{aligned}
    $$

    Or

    $$p(u)=\int p(u|y)p(y)dy=\gamma l(u)+(1-\gamma)g(u)$$

    donc

    $$\text{EI}_{y^*}(u) = \frac{\gamma y^* l(u)-l(u) \int_{-\infty}^{y^*} y p(y)dy}{\gamma l(u)+(1-\gamma)g(u)} \propto \left( \gamma + \frac{g(u)}{l(u)}(1-\gamma) \right)^{-1}$$

    Ce qui est intéressant ici, c'est que $\text{EI}_{y^*}(u)$ est proportionnel à la quantité $\frac{l(u)}{g(u)}$. Et c'est exactement la logique qui se cache derrière $l$ et $g$, car $l$ correspond à des situations où les performances du modèle étaient meilleures car la perte associée était plus faible. En cherchant à maximiser $\frac{l(u)}{g(u)}$, et donc l'Expected Improvement, on s'assure qu'en sélectionnant le prochain jeu d'hyper-paramètres, on a plus de chances de maximiser les performances en sélectionnant des hyper-paramètres dont la perte est encore plus faible.


    Un des principaux avantages de cette méthode est que contrairement à l'optimisation bayésienne, **il n'y a pas de modèle substitut à calibrer** comme un Processus Gaussien, ce qui réduit les temps de calcul. On se base uniquement sur un simple calcul bayésien. L'appellation *Tree-structured* vient du fait que les estimateurs Parzen sont des <a href="https://fr.wikipedia.org/wiki/Estimation_par_noyau#:~:text=En%20statistique%2C%20l'estimation%20par,en%20tout%20point%20du%20support." target="_blank">estimateurs de densité à noyau</a>. Ainsi, la succession chronologique du choix des hyper-paramètres forme une structure d'arbre pour l'espace des hyper-paramètres.

    Appliquons un TPE pour le modèle LightGBM.
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
    return np, os, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous allons charger la base d'apprentissage $(X,y)$ qui sera utilisé lors de l'optimisation bayésienne avec $k$-Fold, et les sous-ensembles d'entraînement et de test pour calibrer le modèle une fois les meilleurs hyper-paramètres obtenus.
    """)
    return


@app.cell
def _(os, pd):
    X = pd.read_csv(os.path.expanduser("data/X.csv"))
    y = pd.read_csv(os.path.expanduser("data/y.csv"))

    X_train = pd.read_csv(os.path.expanduser("data/X_train.csv"))
    X_test = pd.read_csv(os.path.expanduser("data/X_test.csv"))
    y_train = pd.read_csv(os.path.expanduser("data/y_train.csv")).values.flatten()
    y_test = pd.read_csv(os.path.expanduser("data/y_test.csv")).values.flatten()
    return X, X_test, X_train, y, y_test, y_train


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Définissons l'espace de recherche qui sera utilisé par l'optimiseur.

    Comme le projet sera vérifié par ty, nous devons créer une classe `ModelSpec` afin
    """)
    return


@app.cell
def _():
    from lightgbm.sklearn import LGBMClassifier
    from hyperopt import hp, tpe, fmin
    from typing import Any, TypedDict
    from collections.abc import Callable



    class ModelSpec(TypedDict, total=True):
        name: str
        model_class: Callable[..., Any]  # Covers LGBMClassifier()
        params: dict[str, Any]  # Accepts hp.uniform etc.
        override_schemas: dict[str, type]
    
    MODEL_SPECS: list[ModelSpec] = {
        "name": "LightGBM",
        "model_class": LGBMClassifier,
        "max_evals": 20,
        "params": {
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
            "num_leaves": int, "min_child_samples": int, "max_depth": int, "num_iterations": int
        }
    }
    return LGBMClassifier, MODEL_SPECS, fmin, tpe


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    On pourra retrouver la <a href="https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.LGBMClassifier.html#lightgbm.LGBMClassifier" target="_blank">liste des hyper-paramètres de LightGBM</a>.

    Pour faciliter la maintenance du code, nous **encapsulons** le processus d'optimisation dans une fonction `optimize_hyp` qui nécessite plusieurs arguments.

    - `instance` est la classe hérité de `BaseEstimator` de `scikit-learn` pour instancier un modèle.
    - `training_set` est la base d'apprentissage $(X,y)$.
    - `search_space` est l'espace de recherche pour l'optimiseur.
    - `metric` est la métrique à utiliser pour calculer le score.
    - `evals` est le nombre d'itérations de l'optimiseur.

    /// attention
    Dans <code>hyperopt</code>, on cherche à minimiser une fonction objectif : il faut donc renvoyer l'inverse additif dans le cas où la métrique utilisée est un score.
    ///

    Dans certains cas, les hyper-paramètres de l'espace de recherche ne sont pas toujours entiers ($10.0$ au lieu de $10$), ce qui peut générer des erreurs. Le champ `override_schemas` contient une liste d'hyper-paramètres pour lesquels le conversion en nombre entier est explicite.
    """)
    return


@app.cell
def _(LGBMClassifier, MODEL_SPECS: "list[ModelSpec]", X, fmin, np, tpe, y):
    from sklearn.model_selection import RepeatedKFold

    def optimize_hyp(instance, training_set, search_space, metric, evals=10):
        # Fonction que l'on souhaite minimiser (inverse de tau)
        def objective(params):
            for param in set(list(MODEL_SPECS["override_schemas"].keys())).intersection(set(params.keys())):
                cast_instance = MODEL_SPECS['override_schemas'][param]
                params[param] = cast_instance(params[param])

            # On répète 3 fois un 5-Fold
            rep_kfold = RepeatedKFold(n_splits=4, n_repeats=1)
            scores_test = []
            for train_I, test_I in rep_kfold.split(X):
                X_fold_train = X.iloc[train_I, :]
                y_fold_train = y.iloc[train_I]
                X_fold_test = X.iloc[test_I, :]
                y_fold_test = y.iloc[test_I]

                # On entraîne un LightGBM avec les paramètres par défaut
                model = LGBMClassifier(**params, objective="binary", verbose=-1)
                model.fit(X_fold_train, y_fold_train)

                # On calcule le score du modèle sur le test
                scores_test.append(
                    metric(y_fold_test, model.predict(X_fold_test))
                )

            return np.mean(scores_test)

        return fmin(fn=objective, space=search_space, algo=tpe.suggest, max_evals=evals)

    return (optimize_hyp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En appelant la fonction `optimize_hyp`, les meilleurs hyper-paramètres vont être recherchés puis retournés une fois l'optimisation terminée. Nous récupérerons les hyper-paramètres optimaux dans la variable `optimum_params`.
    """)
    return


@app.cell
def _(MODEL_SPECS: "list[ModelSpec]", X_train, optimize_hyp, y_train):
    from sklearn.metrics import f1_score

    import warnings
    warnings.filterwarnings('ignore')

    optimum_params = optimize_hyp(
        MODEL_SPECS['model_class'],
        training_set=(X_train, y_train),
        search_space=MODEL_SPECS["params"],
        metric=lambda x, y: -f1_score(x, y), # Problème de minimisation = inverse du score
        evals=MODEL_SPECS["max_evals"],
    )
    return f1_score, optimum_params


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Affichons les hyper-paramètres optimaux.
    """)
    return


@app.cell
def _(optimum_params):
    optimum_params
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Maintenant que nous les connaissons, nous pouvons entraîner un LightGBM avec ces hyper-paramètres.
    """)
    return


@app.cell
def _(
    LGBMClassifier,
    MODEL_SPECS: "list[ModelSpec]",
    X_train,
    optimum_params,
    y_train,
):
    # Chaque paramètres dont le schéma est surchargé est casté vers le bon type
    for param in MODEL_SPECS['override_schemas']:
        cast_instance = MODEL_SPECS['override_schemas'][param]
        optimum_params[param] = cast_instance(optimum_params[param])

    model = LGBMClassifier(**optimum_params)
    model.fit(X_train, y_train)
    return (model,)


@app.cell
def _(X_test, f1_score, model, y_test):
    from sklearn.metrics import recall_score, precision_score

    print("F1 Score : {:2.1f}%".format(f1_score(y_test, model.predict(X_test)) * 100))
    print("Precision : {:2.1f}%".format(precision_score(y_test, model.predict(X_test)) * 100))
    print("Recall : {:2.1f}%".format(recall_score(y_test, model.predict(X_test)) * 100))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ce qui est intéressant ici, c'est qu'en cherchant à maximiser le F1 score, nous avons obtenu un meilleur rappel, mais la précision est moins élevé.

    /// danger |
    Il ne faudrait surtout pas n'utiliser que le rappel pour optimiser le modèle : on obtiendrai un modèle avec potentiellement une mauvaise précision.
    ///

    Au final, en comparaison avec le modèle non optimisé, nous n'avons que très peu gagné au niveau du F1 Score, mais nous avons en revanche un meilleur rappel, qui était l'objectif initial puisque c'est surtout cette métrique qu'il faut maximiser.

    Nous allons enregistrer le modèle au format `pkl`, que l'on réutilisera pour l'évaluer et l'interpréter.
    """)
    return


@app.cell
def _(model, os):
    import joblib

    joblib.dump(model, os.path.expanduser("data/model.pkl"))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Courbe de calibration

    Les courbes de calibration permettent de comparer les proportions d'observations prédites positivement et d'observations appartenant à la classe positive à partir du seuil $\alpha$ définissant la frontière du classifieur.

    $$CC(\alpha)=\frac{1}{n} |\{ \hat{f}(x) \geq \alpha : x \in X \}|$$

    Regardons la courbe de calibration de notre modèle optimisé.
    """)
    return


@app.cell
def _(X_test, model, plt, y_test):
    import matplotlib.ticker as mtick

    from sklearn.calibration import calibration_curve

    prob_pos = model.predict_proba(X_test)[:, 1]
    fraction_of_positives, mean_predicted_value = calibration_curve(y_test, prob_pos, n_bins=20)

    plt.figure(figsize=(16, 10))
    plt.plot([0, 1], [0, 1], "k--", label="Perfectly calibrated", alpha=0.6)
    plt.plot(mean_predicted_value, fraction_of_positives, "s-", label="Model")
    plt.ylabel("Fraction of positives")
    plt.xlabel("Predicted probabilites")
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
    plt.title("Calibration Curve")
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ce que nous voyons, c'est qu'à partir de $40\%$, le modèle contient les bonnes proportions d'observations à la fois positives et négatives : il n'y a donc pas de sur-représentation d'une certaine classe lorsque les probabilités prédites sont supérieures à $40\%$.

    En dessous de cette valeur, nous observations quelques disparités, mais qui restent néanmoins maîtrisées sur l'ensemble des probabilités. Au vu de cette courbe, nous pouvons conclure que les proportions de classes positives sont globalement respectées selon les probabilités prédites.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    L'optimisation des hyper-paramètres peut demander un effort au début, mais une fois mise en place, elle constitue une véritable force d'automatisation.

    - Nous avons vu l'approche bayésienne pour l'optimisation des hyper-paramètres d'un modèle de Machine Learning.
    - Nous avons optimisé un LightGBM avec une approche Tree of Parzen Estimators.
    - Le modèle optimisé a été enregistré au format Pickle pour être ré-utilisé par la suite.

    > ➡️ Dernière étape dans la construction du modèle : <b>validation et interprétation</b>.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
