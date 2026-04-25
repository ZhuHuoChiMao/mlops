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
    Lançons-nous dès à présent dans le vif du sujet ! Comme tout bon Data Scientist, il faut bien évidemment au préalable manipuler les données pour mieux les comprendre. En plus d'avoir en tête des informations descriptives sur nos données, nous allons pouvoir étudier quelles sont les caractéristiques qui seront pertinentes lorsque nous aborderons la phase de modélisation.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Récolter un échantillon du jeu de données et l'étudier.</li>
        <li>Comprendre les différentes caractéristiques présentes.</li>
        <li>Identifier les variables pertinentes pour l'objectif.</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/lOfpvYQoiJW03vpJhP/giphy.gif" width="300" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Récupération des données

    Le jeu de données que nous allons manipuler contient des événements utilisateurs sur une plateforme E-Commerce. Pour cela, nous disposons de près de 7 mois d'enregistrements où, pour chaque événement (produit visité, ajout au panier, achat, ...), nous disposons des informations suivante.

    - `event_time` : le timestamp de l'événement (format UTC).
    - `event_type` : le type d'événement.
    - `product_id` : un identifiant unique associé au produit.
    - `category_id` : un identifiant unique associé à la catégorie du produit.
    - `category_code` : un code associé à la catégorie du produit.
    - `brand` : la marque du produit.
    - `price` : le prix du produit.
    - `user_id` : un identifiant unique associé à l'utilisateur.
    - `user_session` : un identifiant temporaire pour une session utilisateur.

    /// attention | Attention!

    L'intégralité du jeu de données totalise près de 50 Go de fichiers. Pour cela, nous allons dans un premier temps étudier un échantillon.
    ///

    L'objectif pour cette plateforme est **d'optimiser les offres ciblées d'opérations marketing** en proposant des réductions pour les utilisateurs **pendant leur parcours d'achat**. Pour cela, on s'intéresse à savoir si, au cours d'une session, un utilisateur va acheter un produit ou non, en fonction de son parcours connu jusqu'ici.

    Nous devons mieux connaître quelles sont les informations dont nous avons à disposition pour construire, par la suite, des variables qui apporteront le maximum d'information à notre modèle prédictif.

    Commençons par <a href="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/data/sample.csv" target="_blank">récupérer les données</a>.

    /// admonition | information

    Pour information, les données sont disponibles dans le dossier `data`
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Chargeons avec la librairie `pandas` l'échantillon téléchargé.
    """)
    return


@app.cell
def _():
    import os
    import numpy as np
    import pandas as pd

    # La fonction expanduser permet de convertir le répertoire ~ en chemin absolu
    data = pd.read_csv(os.path.expanduser("data/sample.csv"))
    print("Taille de l'échantillon :", data.shape[0])
    print("Taille mémoire : {:2.2f} Mb".format(data.memory_usage().sum() / 1e6))
    data.head()
    return data, np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cet échantillon des données brutes contient 1,24 million de lignes. Regardons en détails quelles sont les informations présentes dans ces données brutes. Comme évoqué précédemment, nous retrouvons les colonnes mentionnées.

    - Tout d'abord, deux colonnes indiquent la temporalité et le type d'événement : c'est le cas des colonnes `event_time`, indiquant la date et le temps où l'événement a eu lieu au format UTC (norme <a href="https://fr.wikipedia.org/wiki/ISO_8601" taret="_blank">ISO 8601</a>), et `event_type` pour le type d'événement.
    - Ensuite, certains variables concernent l'utilisateur, notamment `user_id` et `user_session`.
    - Enfin, les autres informations sont relatives au produit concerné par l'événement : ce sont les colonnes `product_id`, `category_id`, `category_code`, `brand` et `price`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Statistiques sur les événements

    Étudions chaque variable, indépendamment des autres avec des **analyses univariées**.
    """)
    return


@app.cell
def _():
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Permet d'appliquer le style graphique de Seaborn par défaut sur matplotlib
    sns.set_theme()
    return plt, sns


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour pouvoir mieux comprendre la temporalité des événements, nous allons extraire les informations depuis la colonne `event_time`.
    """)
    return


@app.cell
def _(data, pd):
    # Conversion de la colonne event_time en type datetime
    data["event_time"] = pd.to_datetime(data["event_time"])

    data["event_day"] = data["event_time"].dt.day
    data["event_hour"] = data["event_time"].dt.hour
    data["event_minute"] = data["event_time"].dt.minute
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Regardons la distribution des temporalités.
    """)
    return


@app.cell
def _(data, np, plt, sns):
    import matplotlib.units as munits
    import matplotlib.dates as mdates
    import datetime

    # Permet d'afficher l'axe des abscisses plus joliment
    converter = mdates.ConciseDateConverter()
    munits.registry[np.datetime64] = converter
    munits.registry[datetime.date] = converter
    munits.registry[datetime.datetime] = converter

    print("Date min :", data["event_time"].min())
    print("Date max :", data["event_time"].max())

    plt.figure(figsize=(14, 9))
    sns.histplot(data["event_time"])
    plt.xlabel("Heure")
    plt.ylabel("Nombre d'événements")
    plt.title("Répartition du nombre d'événements le 01-10-2019", fontsize=17)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notre échantillon contient tous les événements survenus le 01/01/2020.

    **On s'attend à avoir une ordre de grandeur de 40 à 50 millions d'événements dans le mois**.

    Intéressons-nous maintenant aux types d'événement.
    """)
    return


@app.cell
def _(data):
    data["event_type"].unique()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dans l'échantillon, trois événements sont observés.

    - `view` lorsqu'un utilisateur a vu la page d'un produit.
    - `cart` lorsqu'un utilisateur a ajouté un produit dans le panier.
    - `purchase` lorsqu'un utilisateur a acheté un produit.

    Bien évidemment, s'agissant d'un site E-Commerce, on s'attend à avoir une **sur-représentation** des événements de type `view` par rapport aux événements de type `purchase`.
    """)
    return


@app.cell
def _(data, np, plt):
    events_type_counts = data["event_type"].value_counts() / data.shape[0]

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(aspect="equal"))

    wedges, texts = ax.pie(
        events_type_counts,
        wedgeprops=dict(width=0.4)
    )

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        ax.annotate(
            "{} : {:2.2f}%".format(events_type_counts.index[i], events_type_counts.iloc[i] * 100),
            xy=(x, y), xytext=(1.1*np.sign(x), 1.4*y),
            fontsize=16,
            horizontalalignment=horizontalalignment)

    ax.set_title("Proportion des types d'événements de l'échantillon", fontsize=18)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > ❓ Pourquoi ce graphique est important ?

    Si l'on souhaite se diriger vers une classification binaire qui va calculer la probabilité de finalisation d'achat d'un utilisateur, c'est très important de savoir à l'avance si le jeu de données sera *imbalanced*, c'est-à-dire qu'une des deux classes sera très majoritairement présente (99% vs 1%).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Statistiques sur les utilisateurs

    Il y a deux identifiants importants concernant les utilisateurs dans le jeu de données.

    - La colonne `user_id`, donne un identifiant **unique** pour un utilisateur.
    - La colonne `session_id`, au format UUID, donne l'identifiant **unique** d'une session utilisateur.

    <div class="alert alert-info">
        <p>Un <a href="https://fr.wikipedia.org/wiki/Universally_unique_identifier" target="_blank">UUID</a> est un identifiant qui utilise le temps pour s'assurer de l'unicité (au sens où il est très probable d'avoir exactement deux sessions qui débutent à la même milliseconde voire microseconde).</p>
    </div>

    La session utilisateur est un concept important à maîtriser ici : lorsqu'un utilisateur visite le site, une session est créée. Cette session est conservé tout le long du parcours utilisateur sur le site. Dès lors que l'utilisateur quitte la plateforme, au bout d'un certain temps, la session **est stoppée**.

    Par exemple, si l'utilisateur visite le site 3 fois en une seule journée, par exemple 10 minutes le matin, 5 minutes l'après-midi et 20 minutes le soir, alors trois sessions seront créées dans la journée.
    """)
    return


@app.cell
def _(data):
    print("Nombre unique d'utilisateurs :", len(data["user_id"].unique()))
    print("Nombre de sessions :", len(data["user_session"].unique()))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous avons $268 737$ sessions pour $190188$ utilisateurs : cela signifie qu'il y a une grande part d'utilisateurs qui n'ont qu'une seule session.

    Voyons quelle proportion d'utilisateurs n'ont qu'une seule session dans l'échantillon.
    """)
    return


@app.cell
def _(data, plt):
    import matplotlib.ticker as mtick
    num_sessions_per_user = data[['user_id', 'user_session']].groupby('user_id').count()['user_session'].value_counts().sort_values(ascending=False)
    num_sessions_per_user /= num_sessions_per_user.sum()
    plt.figure(figsize=(14, 9))
    n_bars = 12
    _rects = plt.bar(num_sessions_per_user[:n_bars].index, height=num_sessions_per_user[:n_bars])
    for _rect in _rects:
        height = _rect.get_height()
        plt.gca().annotate('{:2.2f}%'.format(height * 100), xy=(_rect.get_x() + _rect.get_width() / 2, height), xytext=(0, 3), textcoords='offset points', fontsize=16 * 10 / n_bars, ha='center', va='bottom')
    plt.ylabel("Proportion d'utilisateurs")
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1, 0))
    plt.xticks(range(1, n_bars + 1))
    plt.xlabel('Nombre de sessions')
    plt.title("Proportion d'utilisateurs par nombre de sessions", fontsize=16)
    plt.show()
    return mtick, n_bars


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous remarquons que plus de $70\%$ des utilisateurs ont au moins deux sessions dans l'échantillon : cela pourrait donc être intéressant **d'utiliser cette information** comme variable explicative par la suite.

    Combien de sessions ont-elles débouchées sur un achat d'un des produits visités ?
    """)
    return


@app.cell
def _(data, np):
    data_purchase = data.copy()
    data_purchase['purchased'] = np.where(data_purchase['event_type'] == "purchase", 1, 0)
    data_purchase['purchased'] = data_purchase \
        .groupby(["user_session"])['purchased'] \
        .transform("max")

    data_purchase["purchased"].value_counts() / data_purchase["purchased"].shape[0]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    C'est donc environ $10\%$ des sessions qui se terminent par au moins un achat d'un des produits visités. Cette statistique nous informe donc que le jeu de données **n'est pas déséquilibré** entre les deux classes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Statistiques sur les produits

    Intéressons-nous maintenant aux produits. Dans un DataFrame `data_categories`, nous allons calculer le nombre d'événements (vues, ajouts au panier et achats) par catégorie.
    """)
    return


@app.cell
def _(data, np):
    data_categories = data.copy()
    data_categories["category"] = data_categories["category_code"].str.split(".", expand=True)[0]

    for event_type in ["view", "cart", "purchase"]:
        data_categories["event_{}".format(event_type)] = np.where(data_categories["event_type"] == event_type, 1, 0)

    data_categories = data_categories[["event_view", "event_cart", "event_purchase", "category"]] \
        .groupby("category").sum()
    data_categories.head()
    return (data_categories,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour savoir quelle sont les catégories les plus visitées, affichons les valeurs sur un diagramme en bâtons.
    """)
    return


@app.cell
def _(data_categories, n_bars, plt):
    plt.figure(figsize=(14, 9))
    _rects = plt.barh(data_categories.index, width=data_categories['event_view'])
    for _rect in _rects:
        _width = _rect.get_width()
        plt.gca().annotate('{}'.format(int(_width)), xy=(_width, _rect.get_y()), xytext=(30, 5), textcoords='offset points', fontsize=16 * 10 / n_bars, ha='center', va='bottom')
    plt.ylabel('Catégorie')
    plt.xlabel('Nombre de vues')
    plt.title('Nombre de vues par catégorie de produit', fontsize=16)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ce que nous observons, c'est que la catégorie `electronics` est très majoritairement celle qui est la plus visitée, avec plus de 450 000 vues. En revanche, d'autres sont très peu visités comme `stationery` ou `medicine` avec moins de 500 vues sur toute la journée.

    Faisons la même chose pour les achats.
    """)
    return


@app.cell
def _(data_categories, n_bars, plt):
    plt.figure(figsize=(14, 9))
    _rects = plt.barh(data_categories.index, width=data_categories['event_purchase'])
    for _rect in _rects:
        _width = _rect.get_width()
        plt.gca().annotate('{}'.format(int(_width)), xy=(_width, _rect.get_y()), xytext=(30, 5), textcoords='offset points', fontsize=16 * 10 / n_bars, ha='center', va='bottom')
    plt.ylabel('Catégorie')
    plt.xlabel("Nombre d'achats")
    plt.title("Nombre d'achats par catégorie de produit", fontsize=16)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sans surprises, les catégories ayant le plus de vues sont également celles où il y a le plus d'achats. Mais regardons les proportions achats / vues pour chaque catégorie.
    """)
    return


@app.cell
def _(data_categories, mtick, n_bars, plt):
    plt.figure(figsize=(14, 9))
    _rects = plt.barh(data_categories.index, width=data_categories['event_purchase'] / data_categories['event_view'])
    for _rect in _rects:
        _width = _rect.get_width()
        plt.gca().annotate('{:2.2f}%'.format(_width * 100), xy=(_width, _rect.get_y()), xytext=(30, 5), textcoords='offset points', fontsize=16 * 10 / n_bars, ha='center', va='bottom')
    plt.ylabel('Catégorie')
    plt.xlabel('Ratio')
    plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=1))
    plt.title("Ratio du nombre d'achats par nombre de vues", fontsize=16)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Étonnamment, alors qu'il y a beaucoup moins de visites pour les produits de catégorie `medicine` que ceux de catégorie `electronics` (ordre $\times 10000$), cette première enregistre la même proportion d'achats / vues que la deuxième.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Dorénavant, nous avons une idée plus claire sur les données que nous manipulons.

    - Le comportement des utilisateurs ne peut pas se résumer qu'à un seul événement.
    - Les interactions entre les variables semblent être élevées.

    > ➡️ À partir de cette connaissance, nous allons pouvoir mettre en place un premier algorithme avec <b>LightGBM</b>.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
