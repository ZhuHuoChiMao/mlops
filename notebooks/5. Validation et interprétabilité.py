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
    # 5. Validation et interprétabilité
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour s'assurer qu'une fois en production, le modèle adopte un comportement similaire à celui rencontré lors de la phase expérimentale, nous devons utiliser des outils nous permettant de l'auditer. Bien que les scores permettent d'avoir une idée sur les performances globales, elles ne sont pas suffisantes.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Évaluer les performances du modèle</li>
        <li>Interpéter localement le modèle</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/uvoECTG2uCTrG/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Validation du modèle

    Les premiers objectifs de la validation permettent de s'assurer que le modèle calibré respecte bien certaines contraintes qui ne sont pas uniquement liées aux performances ou au score.
    """)
    return


@app.cell
def _():
    import os
    import joblib

    import numpy as np
    import pandas as pd

    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick
    import seaborn as sns

    sns.set_theme()

    model = joblib.load(os.path.expanduser("data/model.pkl"))
    X_train = pd.read_csv(os.path.expanduser("data/X_train.csv"))
    X_test = pd.read_csv(os.path.expanduser("data/X_test.csv"))
    y_train = pd.read_csv(os.path.expanduser("data/y_train.csv")).values.flatten()
    y_test = pd.read_csv(os.path.expanduser("data/y_test.csv")).values.flatten()

    y_prob = model.predict_proba(X_test)
    return X_test, model, mtick, np, pd, plt, sns, y_prob, y_test


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Densités des classes

    Nous avons vu que la précision de notre modèle était moins bonne que le rappel. En particulier, avec la courbe de calibration, nous avons pu observer que sur des probabilités prédites (classe positive) inférieures à $40\%$, les proportions d'observations réellement positives n'adoptaient pas un comportement linéaire.

    Pour mieux visualiser ce phénomène, il est courant de représenter les densités des deux classes sur un grahique. On affiche deux histogrammes, qui correspondent aux observations prédites positivement et négativement.
    """)
    return


@app.cell
def _(mtick, np, plt, sns, y_prob, y_test):
    plt.figure(figsize=(16, 10))

    sns.histplot(y_prob[y_test == 0, 1], alpha=0.5)
    plt.axvline(np.median(y_prob[y_test == 0, 1]), 0,1, linestyle="--", label="Median Class 0")
    plt.axvline(np.mean(y_prob[y_test == 0, 1]), 0,1, linestyle="-", label="Mean Class 0")

    sns.histplot(y_prob[y_test == 1, 1], color="darkorange", alpha=0.4)
    plt.axvline(np.median(y_prob[y_test == 1, 1]), 0, 1, linestyle="--", color="darkorange", label="Median Class 1")
    plt.axvline(np.mean(y_prob[y_test == 1, 1]), 0, 1, linestyle="-", color="darkorange", label="Mean Class 1")

    plt.legend()
    plt.xlabel("Predicted probabilites")
    plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
    plt.xlim(-0.05, 1.05)
    plt.title("Density Chart", fontsize=16)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour rappel, nous avions déjà calculé la courbe de calibration du modèle.
    """)
    return


@app.cell
def _(X_test, model, mtick, plt, y_test):
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
    Bien que la courbe de calibration ne soit pas choquante, nous observons sur les densités des classes que les deux distributions sont **asymétriques** avec une moyenne à gauche par rapport à la médiane, traduisant d'un étalement vers la gauche. Bien que ce soit attendu pour la classe positive, cela l'est moins pour la classe négative. En effet, cette dernière devrait, pour un modèle parfait, être étalée vers la droite, donc la majorité des observations sont à gauche.

    En soit, ce graphe ne bloque pas la validation du modèle, elle traduit simplement de manière visuelle que le modèle a plus de difficultés à prédire avec une forte confiance des probabilités basses.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Courbe ROC

    La courbe ROC (eceiver Operating Characteristic) trace la courbe de la sensibilité du modèle en fonction de sa spécifité. En d'autres termes, il s'agit de tracer l'évolution du taux de vrais positifs en fonction du taux de faux positifs.
    """)
    return


@app.cell
def _(X_test, model, mtick, plt, y_test):
    from sklearn.metrics import roc_curve, auc

    fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_test)[:, 1])

    plt.figure(figsize=(16, 10))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = {:2.1f}%)'.format(auc(fpr, tpr) * 100))
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([-0.01, 1.01])
    plt.ylim([-0.01, 1.01])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
    plt.title("ROC Curve", fontsize=16)
    plt.legend(loc="lower right")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Courbe PR

    Une autre courbe également utilisée est la courbe PR (precision/recall), qui elle va tracer l'évolution de la précision en fonction du rappel.
    """)
    return


@app.cell
def _(X_test, model, mtick, plt, y_test):
    from sklearn.metrics import precision_recall_curve
    from sklearn.metrics import PrecisionRecallDisplay
    plt.figure(figsize=(16, 11))
    prec, recall, _ = precision_recall_curve(y_test, model.predict_proba(X_test)[:, 1], pos_label=1)
    pr_display = PrecisionRecallDisplay.from_estimator(model, X_test, y_test)
    plt.title('PR Curve', fontsize=16)
    plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La principale différence entre les courbes ROC et PR, c'est que la précision et le rappel calculent des taux à partir des vrais positifs sans se soucier des vrais négatifs. La précision ne fait pas intervenir

    À l'inverse de la courbe ROC, la précision n'utilise pas le TPR, mais la PPV !

    À l'inverse, la courbe ROC utilise toutes les informations.

    Si l'on ne s'intéresse pas à la **spécificité**, alors la courbe PR peut être intéressante à interpréter. Dans le cas contraire, la courbe ROC pourra fournir plus d'informations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Interprétation locale

    Au cours des dernières années, les modèles de Machine Learning atteignaient des performances de plus en plus élevées, dépassant parfois les performances réalisées par des humains sur certaines tâches précises. La compétition annuelle ILSVRC, où des équipes de recherche évaluent des algorithmes de traitement d'image sur le jeu de données ImageNet, voyait les meilleurs taux d'erreurs à $26\%$.

    En 2012, l'avènement des réseaux de neurones et de l'apprentissage profond, et plus particulièrement les réseaux de neurones convolutifs ont permis d'abaisser le taux d'erreur à $16\%$. Depuis, les réseaux de neurones sont majoritairement utilisés dans cette compétition et d'autres semblables.

    <img src="https://dv495y1g0kef5.cloudfront.net/training/data_scientist_airbnb/img/interp1.png" />

    En contrepartie, les réseaux de neurones sont souvent considérés comme des « boîtes noires », c'est-à-dire des algorithmes dont le fonctionnement est opaque et difficile à interpréter. En effet, du fait du très grand nombre de paramètres (plusieurs dizaines voir centaines de millions), l'interprétation de ces modèles n'est pas faisable.

    Les réseaux de neurones sont un exemple de « boîtes noires », tout comme le sont les algorithmes d'ensemble learning que nous avons construit tels que Random Forest ou XGBoost.

    Le terme **transparence des algorithmes** est propre au contexte étudié, et il n'existe pas une définition unique. La transparence peut faire référence à la connaissance de la décision prise par l'algorithme, au degré d'exactitude de la prédiction ou à l'importance des variables sur la prédiction.

    <a href="https://christophm.github.io/interpretable-ml-book/" target="_blank">Le livre en ligne de Christoph Molnar sur le machine learning interprétable (Lecture très recommandé sur votre temps libre)</a> reprend la définition de l'interprétabilité de Tim Miller :

    <p style="text-align: center;">« L'interprétabilité est le degré à quel point un humain peut expliquer de manière cohérente les prédictions du modèle »
    </p>


    Sous cette définition, l'interprétabilité est une partie intégrante de la transparence, qui vise à être capable d'expliquer de manière précise et consistante la prédiction, que ce soit pour une observation ou dans le comportement global de l'algorithme.

    ### Modèles naturellement interprétables

    Que signifie un modèle naturellement interprétable ? Lorsque nous avons réalisé la régression linéaire, nous avons été capable de calculer directement l'impact de chaque variable sur la prédiction. De plus, du fait de l'hypothèse de linéarité entre les variables, il est facile d'expliquer comment, **pour un individu donné, le résultat a été obtenu (i.e. de combien le prix a augmenté ou diminué)**. Enfin, le modèle suppose initialement **l'indépendance entre les variables**, ce qui permet de considérer les effets croisés entre les variables inexistants.

    $$y_i= \beta_0 + \sum_{j=1}^p \beta_j x_{ij} + \varepsilon_i$$

    Autrement dit, chaque variable **est associée d'un "poids" $\beta_j$** : dans le cas où toutes les variables sont dans la même unité de mesure, cela permet donc de mesure **l'importance de chaque variable**.

    Néanmoins, chaque individu possède des caractéristiques différentes : et c'est notamment en multipliant la valeur $x_{ij}$ d'une variable d'un individu $x_i$ par le poids $\beta_j$ que l'on peut caractériser, **pour cet individu**, l'importance et le rôle de la variable sur la prédiction.

    En revanche, les modèles qui permettent d'atteindre des performances plus élevées, sont également plus difficilement interprétables. Le modèle XGBoost est construit de manière récursive, et chaque arbre dépends des précédents. Pour expliquer la prédiction d'une observation $x$, il est nécessaire de calculer la sortie de chaque arbre, en sachant que les prédicteurs faibles ne cherchent plus à modéliser la variable réponse, mais les pseudo-résidus. C'est la multiplicité des arbres (associée à d'éventuels arbres profonds) qui rend la compréhension du comportement du modèle quasi-impossible.

    Ainsi, au cours des dernières années, la recherche académique s'est penchée sur des méthodes d'interprétabilité afin de pouvoir expliquer le comportement et les prédictions des algorithmes. Deux types de méthodes ont été développées.

    ### Méthode agnostiques

    Les méthodes dites **agnostiques** sont indépendantes du modèle prédictif utilisé. Le principal avantage est leur flexibilité, puisque ces méthodes peuvent être appliquées sans connaissance particulière du modèle prédictif, si ce n'est qu'obtenir la prédiction $\hat{f}(\mathbf{x})$ pour toute observation $\mathbf{x}$. Ces méthodes agnostiques s'intercalent sur des modèles boîtes noires. Les PDP (Partial Dependency Plot) furent une des premières méthodes d'interprétabilité, en estimant les lois marginales des variables sous des hypothèses d'indépendance entre les variables. Plus récemment, d'autres méthodes telles que **LIME** ou **Kernel SHAP** ont été introduites afin de pallier certaines faiblesses des précédentes méthodes et de les adapter pour des modèles plus complexes et plus coûteux en terme de calcul.

    ### Méthode spécifiques

    Les méthodes dites **spécifiques** dépendent du modèle prédictif utilisé. Bien que ces méthodes soient moins flexibles, elles permettent d'obtenir de meilleurs interprétabilité puisqu'elles sont spécifiquement développées pour un modèle prédictif particulier. Ces méthodes ne se reposent pas uniquement sur la prédiction $\hat{f}(\mathbf{x})$ des observations $\mathbf{x}$, mais utilisent également les propriétés et méthodes de construction d'un modèle pour en extraire le plus d'information quant au comportement que celui-ci adopte. Les réseaux de neurones sont principalement visés par ces méthodes avec **DeepLIFT**, ou les modèles à base d'arbres avec **Tree SHAP**.

    ### Niveaux de granularité

    Lorsque le terme d'interprétabilité est employé, deux niveaux de granularité peuvent être distingués en classes de méthodes.

    - Les méthodes dites **locales**, où la méthode consiste à expliquer la prédiction d'une observation particulière. Christoph Molnar différencie l'interprétabilité (générale) du modèle et appelle l'*explication* le fait de pouvoir pleinement expliquer la prédiction pour une observation particulière. DeepLIFT ou Tree SHAP sont des exemples de méthodes locales.
    - Les méthodes dites **globales**, qui cherchent plutôt à expliquer les tendances du modèle sur l'ensemble des prédictions, comme par exemple les lois marginales. PDP ou Tree Interpreter sont des exemples de méthodes globales.

    /// attention |
    Ces méthodes calculent souvent une approximation pour pouvoir interpréter plus facilement : <b>attention à la sur-interprétation</b>.
    ///

    Nous allons nous concentrer ici à **l'interprétabilité locale** du modèle.

    ## Valeurs de Shapley

    Les valeurs de Shapley fournissent une méthode d'interprétabilité **locale** : elles permettent de répondre à la question « pourquoi cet utilisateur a une forte probabilité d'acheter ? ». Faisons une petite introduction à cette méthode.

    Les valeurs de Shapley puisent leurs origines dans la théorie des jeux coopératifs. Ces valeurs furent calculées par Lloyd Shapley en 1953. Les valeurs de Shapley indiquent la répartition équitable des gains parmi les joueurs (ou *acteurs*) d'une coalition dans le cadre d'un jeu coopératif. Cette configuration induit une **utilité transférable**, puisque l'objectif de cette coalition est de **maximiser** le profit global, pour ensuite redistribuer ce montant parmi les membres de la coalition. Il est important de distinguer la notion d'équité et d'égalité. Soient trois joueurs $A, B$ et $C$ qui, individuellement, n'apportent aucun gain, mais qui, sous forme de coalition, apportent les gains suivants :

    - la coalition $\{A, B\}$ rapporte $2$ ;
    - la coalition $\{A, C\}$ rapporte $2$ ;
    - la coalition $\{B, C\}$ rapporte $3$ ;
    - la coalition totale $\{A, B, C\}$ rapporte le gain total $4$.

    Dans cet exemple, il est clair que la coalition $\{B, C\}$ est celle qui **contribue** le plus au gain total par rapport aux autres coalitions. Ainsi, pour satisfaire une notion d'équité, les joueurs de la coalition $\{B, C\}$ doivent recevoir une part plus importante du gain total par rapport au joueur $A$.

    Pour un jeu coopératif à $p$ joueurs, il peut y avoir $2^p-1$ coalitions non vides possibles, où chaque joueur est identifié par un indice allant de $1$ à $p$. Le profit **est supposé connu** pour chaque partie de $\{1,…,p\}$, et se quantifie par la **fonction caractéristique** $v:\mathcal{P}(\{1,…,p\}) \rightarrow \mathbb{R}$, et vérifiant $v(\emptyset)=0$. En pratique, rien ne suppose que les gains d'une coalition soient toujours supérieurs à la somme des gains de chaque joueur, soit

    $$v \left( \bigcup_i \{i\} \right) \ngeqslant \sum_{i} v(\{i\})$$

    Dans ce cas de figure, un ou plusieurs joueurs auront une valeur de Shapley **inférieure** au gain individuel, car ils contribueront à faire baisser les gains lors du rassemblement en coalition. Cet événement peut survenir dans des cadres classiques de la théorie moderne de l'économie (deux entreprises qui coopèrent ensemble peuvent obtenir un profit moins élevé que si elles ne coopéraient pas), mais cet aspect est particulièrement important en apprentissage supervisé, ce qui sera détaillé par la suite.

    Shapley a donc déterminé la seule solution qui vérifie ces axiomes, à savoir

    $$\phi_i=\sum_{Z \subseteq\{1, \dots, p\} : j \in Z} \frac{(p-|Z|)!(|Z|-1)!}{p!}\left [ v(Z)-v(Z \backslash \{ j\}) \right ]$$

    où $|Z|$ désigne la cardinalité de l'ensemble $Z$. Cette formule opère comme définition des valeurs de Shapley que nous utiliserons dans la modélisation. Notons que le calcul des valeurs de Shapley implique de **connaître les gains pour toutes les coalitions possibles**. Dans certains domaines (économique par exemple), cela n'est pas toujours possible, notamment lorsque les coalitions ne peuvent pas se reformer (si deux entreprises coopèrent, leurs gains individuels après coopération peuvent être différents des gains individuels avant coopération). Ainsi, $v$ est **entièrement déterminée** et pour tout $C \subseteq \{1, \dots, p\}$, la valeur $v(C)$ est connue.

    ### SHAP

    En 2017, Scott Lundberg propose SHAP comme mesure unifiée de l'importance des variables. Son idée est la suivante :

    - On considère que les variables sont **les joueurs**.
    - La coalition totale représente l'ensemble des variables, et le gain correspond à **la prédiction du modèle**

    Idéalement, une valeur de Shapley pour une variable nous indiquerait quelle est sa contribution sur la prédiction. Par exemple, une valeur de Shapley proche de $0$ signifierait que la variable n'a pas beaucoup impacté la prédiction, alors qu'une valeur élevée indiquerait que la variable impacte fortement le prix du logement.

    Avec SHAP, nous allons pouvoir calculer ces valeurs de Shapley (de manière approximative ou exacte pour les arbres de décision).

    Ainsi, Lundberg a montré que, pour chaque individu x, les valeurs SHAP sont calculées de sorte à exprimer la prédiction $\hat{f}(\mathbf{x})$ par la somme des contributions des variables :

    $$\hat{f}(\mathbf{x})=\frac{1}{1+\exp \left(-\phi_0-\sum_{j=1}^p \phi_j \right)}$$

    Avec $\phi_0$ la moyenne des valeurs de Shapley pour la classe positive. Les valeurs de Shapley vont être stockées dans la variable `shap_values`.
    """)
    return


@app.cell
def _(X_test, model):
    import shap

    # L'objet Explainer
    explainer = shap.TreeExplainer(model)
    X_shap = X_test.copy()
    # On récupère les valeurs de Shapley dans la matrice (pour la proba positive)
    shap_values = explainer.shap_values(X_shap)
    return X_shap, explainer, shap, shap_values


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// attention |
    Au 8 février 2026, `numba`, un paquet dont dépend `shap` n'est pas compatible avec la dernière version de Numpy 2.4.

    Cependant, une version Release Candidate est sortie `0.64.0rc1`. Vérifiez que la version 0.64 est sortie, sinon utilisez les version release candidate.

    Vous pouvez suivre l'évolution dans ce Git [issue](https://github.com/numba/numba/issues/10263) de la communauté
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour interpréter plus facilement les valeurs de Shapley d'une observation, nous allons décomposer chaque variable sur un diagramme en bâtons.
    """)
    return


@app.cell
def _(X_shap, explainer, np, pd, plt, shap_values, sns):
    # Cette fonction permet d'afficher les valeurs de Shapley sous forme de diagramme en bâtons
    def plot_shapley_values(index):
        shap_df = pd.DataFrame.from_dict({
            'Variable': X_shap.columns + " (" + X_shap.iloc[0, :].values.astype(str) + ")",
            'Valeur de Shapley': shap_values[index, :]
        })

        # Pour rappel, la prédiction est égale à la somme des valeurs de Shapley + la valeur moyenne
        prob = explainer.expected_value + shap_df['Valeur de Shapley'].sum()
        prob = 1 / (1 + np.exp(-prob))

        plt.figure(figsize=(13,10))
        sns.barplot(
            y='Variable',
            x='Valeur de Shapley',
            data=shap_df.sort_values('Valeur de Shapley', ascending=False)
        )
        plt.title(
            "Probabilité : {:2.2f}%".format(prob * 100),
            fontsize=18
        )
        plt.yticks(fontsize=13)
        plt.show()

    plot_shapley_values(8)
    return (plot_shapley_values,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour ce logement, le modèle est indécis puisqu'il prédit presque $50/50$. Ce que l'on remarque, c'est que pour cet utilisateur, ce produit en particulier contribue fortement à faire baisser la probabilité.

    Prenons un autre utilisateur.
    """)
    return


@app.cell
def _(plot_shapley_values):
    plot_shapley_values(1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En revanche, pour cet utilisateur, il y a une très forte probabilité d'achat. Les variables les plus impactantes sont le nombre de vues et de sessions.

    Dans certains cas, il est possible d'interpréter globalement en affichant les valeurs de Shapley de chaque variable et de chaque observation. La variation de couleur indique si la variable a une grande valeur ou non.
    """)
    return


@app.cell
def _(X_shap, shap, shap_values):
    shap.summary_plot(shap_values, X_shap, plot_size=0.8)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Alors que l'on observe une tendance croissante pour le `num_views_session` ou `duration`, cela est plus difficile pour `product_id`, `brand` ou `category`, ce qui est prévisible puisque nous avions réalisé un encodage par dictionnaire : il n'y a donc pas de relation d'ordre entre les variables.

    Regardons en détail les valeurs de Shapley uniquement pour la variable `product_id`.
    """)
    return


@app.cell
def _(X_shap, shap, shap_values):
    shap.dependence_plot("product_id", shap_values, X_shap, interaction_index=None)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Il est intéressant de voir que certains paliers se forment : spécifiquement entre 2e7 et 3e7, il y a certains produits qui influencent positivement la probabilité d'acheter, car leur valeurs s'élèvent à $4$.

    <div class="alert alert-block alert-warning">
        La valeur de Shapley ne représente pas une probabilité ! Il s'agit du calcul avant le passage par la fonction logistique.
    </div>
    """)
    return


@app.cell
def _(X_shap, shap, shap_values):
    shap.dependence_plot("hour", shap_values, X_shap, interaction_index=None)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour l'heure de visite, nous observons également un comportement moyen décroissant entre 5h et 17h, puis une augmentation jusqu'à 00h. Cette baisse peut s'expliquer par le fait qu'à partir de 17h, il y a beaucoup plus de connexions qu'en milieu de nuit, et que ces utilisateurs sont plus souvent indécis que ceux visitant le site la nuit.
    """)
    return


@app.cell
def _(X_shap, shap, shap_values):
    shap.dependence_plot("num_views_session", shap_values, X_shap, interaction_index=None)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Contrairement à ce que nous pourrions penser, les valeurs de Shapley sont élevées pour les faibles valeurs de `num_views_sessions`. À partir de $5$ visites dans la même session, les valeurs de Shapley sont plus diffuses mais sont en moyenne de l'ordre de $-0.5$, faisant ainsi légèrement baisser la probabilité.

    <div class="alert alert-block alert-warning">
        Il faut toujours garder en tête qu'il y a des interactions entre les variables, et que le fait d'avoir des valeurs de Shapley élevées pour de faibles valeurs ne peut pas se résumérer à cette seule variable.
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Cette étape de validation est importante, puisque lorsque nous automatiserons l'entraînement du modèle, seuls ces graphiques et ces interprétations permettront de vérifier que le modèle est réellement performant, et pas uniquement en terme de métriques.

    - Nous avons validé le modèle à l'aide de graphiques.
    - Nous avons interprété localement certaines observations avec les valeurs de Shapley.

    > ➡️ Maintenant que avons construit notre pipeline ML, de la transformation des données à la validation, il nous faut l'appliquer non pas sur un échantillon d'un jour d'historique, mais de $7$ jours d'historique.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
