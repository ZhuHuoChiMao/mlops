import marimo

__generated_with = "0.20.2"
app = marimo.App()


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. Présentation du cours

    Le cours **Machine Learning Operation** ou simplement `MLOps` vise à acquérir des compétences et bonnes pratiques liées à la mise en production de modèles de Machine Learning, qualifiée de **MLOps**.

    Nous nous sommes rendu que les futures Data Scientist ne savent pas convertir un projet notebook vers un projet qui est prête à être en production une fois arrivée sur le marché du travail.

    Ce cours permet donc de combler ce manque.

    ## Évaluations

    D'une **évaluation finale** à la dernière journée en après midi avec Hedi Boufaden sous forme de projet donnant lieu à une soutenance.

    Selon l'intervenant (Rakib ou Hedi) : Chaque jour (avec Rakib), le cours aura lieu de 09h30 à 12h30, et le projet pourra être réalisé de 13h30 à 17h00.

    ## Programme

    - **Présentation du MLOps**
        - Métier, compétences et outils
        - Niveaux de MLOps
    - **Entraînement automatisé** (AutoML)
        - Optimisation d'hyper-paramètres
        - Validation croisée de modèle
        - Méthodes d'interprétabilité locales et globales
    - **Software Engineering en Machine Learning**
        - Création de pipelines ML
        - Bonnes pratiques de développement (docstring, PEP8, linting, refactoring)
        - Tests unitaires logiciels et de modèles
        - Pipelines CI/CD
    - **Orchestration ML**
        - Conteneurisation de modèles
        - Apache Airflow pour le MLOps
        - Déploiement de modèles sous forme de microservices (Serverless, Kubernetes)
        - Kubeflow pour le MLOps sur Kubernetes

    ## Projet

    Le projet constitue l'examen final du cours *MLOps*.

    ### Modalités

    - Chaque groupe doit être constitué de **4 à 5 personnes** maximum.
    - Une **présentation orale de 20 minutes** (incluant les questions) aura lieue lors du dernier cours. Lors de cette présentation, **tous les membres du groupes doivent prendre la parole** et présenter leur partie.
    - Le projet doit être **fonctionnel, opérationnel et documenté** le jour de la présentation.
    - Les livrables (présentation + code source) sont à fournir sur la plateforme CYU. Un lien GitHub peut être envoyé ou supplément, mais **ne se substitue pas** aux livrables du code source du cyu.

    /// attention
    Pensez à <b>ne pas ajouter le dossier d'environnement virtuel</b> (<code>env</code> ou <code>venv</code>) pour éviter d'avoir un dossier compressé de plusieurs centaines de Mo !
    ///

    ### Description du projet

    Pour une entreprise fictive, on cherche à développer un pipeline ML entièrement automatisé qui répond à différents critères.

    - Le pipeline ML doit être composé d'un **pipeline d'entraînement** et d'un **pipeline d'inférence**.
    - Le modèle doit pouvoir être entraîné **automatiquement sur de nouvelles données**, et les équipes techniques doivent pouvoir auditer le comportement du modèle. Les données doivent avoir un minimum de **tendance saisonnière** afin de justifier l'entraînement régulier.

    Exemple de projets :

    - Estimation de la durée d'une demande de trajet VTC dans un ville.
    - Détecter les utilisateurs hésitant à acheter un article ECommerce.
    - Générer automatiquement des images Google Maps à partir d'images satellites.
    - Prédire le coût énergétique d'un foyer.

    /// note | Nouveauté 2026 CY-Tech:
    - Le cours à été mis à jour pour prendre en compte le passage à `astral/uv`, `astral/ty` et `astral/ruff`
    - Vous êtes libre de réutiliser le projet Big Data, la partie IA que vous avez du développé.
    - Pour le moment, nous utiliserons MLFlow 3.0.1
    - Airflow sera là uniquement dans le cadre d'une introduction
    - Malheureusement, pas de NannyML pour la supervisions de métric. Le temps vous manque pour boucler la partie MLOps
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
