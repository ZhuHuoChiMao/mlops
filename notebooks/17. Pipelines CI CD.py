import marimo

__generated_with = "0.20.4"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    À partir de maintenant, nous allons rentrer en plein dans l'approche MLOps pour automatiser le déploiement de modèles de Machine Learning. L'automisation implique d'organiser efficacement son environnement, et fait intervenir une multitude d'outils qui peuvent porter à confusion. La première brique concernant l'automatisation se fait directement à partir des dépôts sources, puisque c'est à partir d'eux que toutes les exécutions de l'infrastructure dépendent.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Découvrir l'approche CI/CD pour automatiser les référentiels</li>
        <li>Construire un pipeline CI/CD d'entraînement du modèle</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/gGldiUgAUOJ04g1Ves/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pipelines CI/CD

    L'approche CI/CD, bien connue des DevOps, permet d'améliorer la fréquence de distribution des applications en implémentant des déclenchements automatisés. L'objectif de cette approche est de garantir que les nouvelles fonctionnalités ou améliorations d'un code/application s'intègrent correctement dans un environnement et puisse être directement déployé sans intervention humaine.

    ![alt](public/cicd1.png)


    Plus précisément, nous pouvons différencier d'une part l'acronyme « CI » de l'acronyme « CD ».

    - L'**intégration continue** (CI) vise à s'assurer que de nouvelles fonctionnalités logicielles vont correctement s'intégrer dans un environnement existant par l'intermédiaire de tests et de fusion de code. Avec l'intégration continue, il est possible de travailler à plusieurs sur un même référentiel en harmonisant les fonctionnalités grâce aux tests.
    - Le **déploiement continu** (CD) consiste à transférer automatiquement le code produit vers un environnement de production. C'est notamment pertinent lorsque l'on souhaite toujours avoir une version à jour en production.

    Très souvent, le déploiement continu est réalisé après exécution de l'intégration continue : si un ou plusieurs tests échouent, alors nous ne souhaitons pas lancer le déploiement puisque l'application ne valide pas les tests associés. Le fait d'automatiser ces deux séquences, en plus d'augmenter l'efficacité opérationnelle par l'automatisation, vont fortement réduire le risque d'erreur humaine. Une fois que le pipeline CI/CD est en place, il y a peu de chances que ce dernier génère une erreur (en dehors de l'application elle-même). Cela permet de garantir que toutes les configurations seront appliquées à chaque exécution du pipeline, là où un développeur pourrait oublier certaines configurations lorsqu'il y en a beaucoup.

    Par exemple, dans notre cas, nous aimerions **automatiser les tests unitaires** à chaque fois que nous mettons à jour le projet `purchase_predict`. De même, nous souhaiterions **entraîner automatiquement** le modèle à chaque fois qu'une nouvelle version de code est envoyée vers le dépôt.

    Il existe plusieurs outils permettant de construire des pipelines CI/CD. On retrouve notamment en open-source **Jenkins**, très populaire ou encore **Travis CI**. Du côté des fournisseurs Cloud, nous avons **Code Build** du côté de Google et **CodePipeline** du côté d'AWS.

    ## Environnements

    Dans les bonnes pratiques de développement, il est d'usage de séparer l'environnement de **production** et l'environnement de **pré-production** (ou *staging*). Ceci est en partie hérité des cycles d'intégration continue : lorsqu'une application passe avec succès les tests et le déploiement, cette dernière peut tout de même générer des erreurs qui sont dues à ses interactions dans un environnement déjà existant. Par exemple, une fonctionnalité de l'application a été mise à jour, et l'intégration continue de l'application passe tous les tests. Néanmoins, d'autres applications dans l'environnement n'ont pas été mises à jour en conséquence, et déployer la nouvelle version de l'application dans l'environnement risquerait de créer des erreurs de communication entre les applications.

    C'est ainsi tout l'intérêt de **l'environnement de pré-production**. Il s'agit d'une réplique (plus ou moins fidèle) de l'environnement de production, potentiellement à une plus petite échelle pour limiter les coûts, qui simule l'environnement de production dans lequel seule nous y avons accès. Ainsi, plutôt que d'envoyer directement l'application en production, nous pouvons tout d'abord l'envoyer en pré-production, vérifier que cette dernière s'intègre bien avec les autres services, avant de l'envoyer définitivement en production. Ainsi, on s'assure qu'en production, il n'y aura pas d'erreurs, et la transition sera *en théorie* invisible pour les utilisateurs.

    Ces pratiques sont héritées des grandes entreprises, qui dispose d'environnements très conséquents, mais également des infrastructures en microservices, où il y a beaucoup d'interactions entre les services. Dans le cas d'une application monolithique, cette séparation à moins de sens, mais dans le cas de microservices, elle devient indispensable.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pipeline CI/CD du modèle

    Construisons le pipeline CI/CD qui se charge d'entraîner un modèle optimisé : le projet `purchase_predict`.

    ![alt](public/pipeline_training.png)

    Le pipeline d'entraînement du modèle peut être scindé en deux étapes.

    - À l'aide de Spark, nous effectuons la collecte et la transformation des données vers un dossier contenant des fichiers CSV dans le bucket Cloud Storage.
    - Avec Cloud Build, nous exécutons Kedro pour récupérer les données, effectuer l'encodage et optimiser le modèle pour ensuite l'envoyer vers MLflow.

    L'avantage de cette représentation est que la première étape peut s'exécuter de manière asynchrone par rapport à la première : plusieurs exécutions peuvent être réalisées avec Cloud Build sans avoir besoin de relancer le code Spark à chaque fois.

    ### Cloud Build

    Le service <a href="https://console.cloud.google.com/cloud-build/builds" target="_blank">Cloud Build</a> permet de générer des builds et/ou de compiler des applications en serverless.

    Créons le fichier `install.sh` à la racine du projet `purchase_predict`. Dans ce fichier Bash, nous allons y insérer les commandes permettant d'installer les dépendances nécessaire dans un environnement vierge.

    ```
    #!/bin/bash
    set -e

    apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 git \
      && rm -rf /var/lib/apt/lists/*
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pipeline CI

    Commençons dans un premier temps à configurer le pipeline **d'intégration continue** du projet `purchase_predict`. Les différentes étapes de configuration de Cloud Build sont à définir dans un fichier `cloudbuild.yaml` à la racine du projet.
    """)
    return


app._unparsable_cell(
    r"""
    # Liste des Cloud Builders : https://console.cloud.google.com/gcr/images/cloud-builders/GLOBAL
    steps:
      - name: "ghcr.io/astral-sh/uv:python3.12-trixie-slim"
        id: CI
        entrypoint: /bin/sh
        args:
          - "-c"
          - "chmod a+x install.sh && ./install.sh && uv sync && uv run pytest ."
        env:
          - "UV_CACHE_DIR=/root/.cache/uv"

    logs_bucket: gs://purchase_predict/logs_build_cloud_build
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Analysons chaque champ de ce fichier. Le paramètre `steps` va permettre de définir différentes étapes indépendantes qui seront exécutées séquentiellement par Cloud Build. À noter que dans le cas de notre pipeline CI, nous n'avons pour l'instant qu'une seule étape.

    Ensuite, nous allons configurer cette étape. Dans un premier temps, nous spécifions dans `name` l'image Docker à utiliser pour exécuter le pipeline. Nous utilisons celle proposée par Astral uv afin de pouvoir éviter d'installer UV à la main.

    Ensuite, avec `id`, nous lui attribuons un identifiant/nom.

    Les deux autres champs vont spécifier la commande à exécuter.
    - Le champ `entrypoint` spécifie le programme à exécuter. Il peut s'agit, comme ici, de l'interpréteur Bash, mais cela peut également faire référence à un autre interpréteur ou à une application tierce.
    - La liste `args` contient les arguments qui seront passés en paramètres au programme.
    - Le champs `env` permet de définir la liste des variables d'environnement. Nous avons fixé `uv` pour vous si vous souhaitez à l'avenir, optimiser les temps de builds

    Il est en théorie possible de tout condenser en une seule ligne sur `entrypoint`, mais l'avantage du champ `args` est que la lecture des différents arguments sous forme de liste est plus lisible, notamment lorsqu'il y en a beaucoup.

    /// danger | Remarque importante
    Il n'est pas possible d'avoir plusieurs points d'entrée pour une même étape. Par exemple, il ne sera pas possible d'exécuter plusieurs commandes Bash en une seule étape.
    ///

    C'est d'ailleurs pour cette raison que l'on utilise `&&` ici pour exécuter plusieurs commandes Bash les unes à la suite des autres. Lorsqu'il y a beaucoup de commandes Bash à utiliser, il est préférable de les ajouter dans un fichier comme `install.sh` et de garder dans la configuration Cloud Build uniquement les commandes importantes comme l'installation globale ou l'exécution propre à cette étape.

    Les arguments permettent de donner les droits d'exécution à l'utilisateur dans l'environnement Cloud Build (`a+x`), nous exécution le fichier `install.sh` pour y installer les dépendances de Kedro et enfin, nous lançons les tests unitaires avec `uv run pytest`.

    Nous allons stocker les logs de notre Cloud Build dans notre bucket `purchase_predict` dans un dossier qui lui est dédié


    Dans Cloud Build, créons un nouveau déclencheur que nous appelerons `build-purchase-predict-staging`.

    ![alt](public/ci-1.png)

    Ce déclencheur sera appelé dès lors qu'un push sera effectué sur le dépôt Cloud Source `purchase_predict`. Nous pouvons spécifier la branche avec `staging` sous forme d'expression régulière. Ce déclencheur en concerne dont **que l'environnement de pré-production**.

    Après avoir crée le déclencheur, nous pouvons envoyer de nouvelles références vers le dépôt.
    """)
    return


app._unparsable_cell(
    r"""
    git add .
    git commit -am "Added Cloud Build configuration file"
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Si besoin, il faut ajouter la clé SSH à l'agent pour nous authentifier.
    """)
    return


app._unparsable_cell(
    r"""
    c"
    chmod 600 ~/ssh/git_key
    ssh-add ~/ssh/git_key
    git push google staging
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dans le futur, pour éviter de toujours faire cette manipulation, il est possible d'ajouter les trois premières lignes au fichier `~/.bashrc`.
    """)
    return


app._unparsable_cell(
    r"""
    cat <<EOT >> ~/.bashrc
    eval "$(ssh-agent -s)" > /dev/null 2>&1
    chmod 600 ~/ssh/git_key
    ssh-add ~/ssh/git_key > /dev/null 2>&1
    EOT
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dans <a href="https://console.cloud.google.com/cloud-build/builds" target="_blank">l'historique de compilation</a>, un nouveau build devrait apparaître.

    ![alt](public/cloud_build_2.png)

    Au bout de plusieurs minutes, une fois que l'environnement a installé toutes les dépendances, les tests sont lancés. S'il n'y a pas d'erreur, c'est que les tests unitaires de `pytest` ont réussis.

    ### Pipeline CD

    Ajoutons maintenant une nouvelle étape au fichier `cloudbuild.yaml`.
    """)
    return


app._unparsable_cell(
    r"""
    # Liste des Cloud Builders : https://console.cloud.google.com/gcr/images/cloud-builders/GLOBAL
    steps:
      - name: "ghcr.io/astral-sh/uv:python3.12-trixie-slim"
        id: CI
        entrypoint: /bin/sh
        args:
          - "-c"
          - "chmod a+x install.sh && ./install.sh && uv sync && uv run pytest ."
        env:
          - "UV_CACHE_DIR=/root/.cache/uv" # 👈 explicit cache path

      - name: "ghcr.io/astral-sh/uv:python3.12-trixie-slim"
        id: CD
        entrypoint: /bin/bash
        args:
          - "-c"
          - "chmod a+x install.sh && ./install.sh && uv run kedro run"
        env:
          - "ENV=$BRANCH_NAME"
          - "MLFLOW_SERVER=$_MLFLOW_SERVER"
          - "DO_NOT_TRACK=1"
          - "UV_CACHE_DIR=/root/.cache/uv" # 👈 same path
        waitFor: ["CI"]


    logs_bucket: gs://purchase_predict
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cette deuxième étape ressemble fortement à la première, à la différence que nous exécutons le pipeline `global` de Kedro, et nous ajoutons deux variables d'environnement dans la liste `env`.

    - La première variable d'environnement `ENV`, utilisée pour versionner le modèle sur MLflow, récupère la valeur de `BRANCH_NAME`, qui sera automatiquement remplacé par Cloud Build par la branche sur laquelle s'exécute le déclencheur. Ainsi, il n'y a pas besoin de spécifier précisément `staging` ou `production`, puisque cela dépendra du nom de la branche Git.
    - La deuxième variable `MLFLOW_SERVER` fait référence à l'adresse du serveur MLflow. Ce qui est particulier est que nous utilisons une **variable de substitution** `_MLFLOW_SERVER`. En effet, il n'est pas possible de mettre le nom de domaine de MLflow parce que Cloud Build ne s'exécute pas dans le VPC (réseau local) contenant l'instance MLflow : il n'aura donc pas la possibilité de résoudre le nom de domaine. Nous allons alors ajouter cette variable de substition dans les paramètres du déclencheur pour surcharger la variable d'environnement.
    - La troisième variable `DO_NOT_TRACK` est pour kedro, afin de le faire taire sur la récolte de données.
    - La quatrième nous en avons déjà parlé au dessus lors de la `CI`

    Et enfin nous avons la clée `waitFor`, permettant d'attendre la fin d'execution de la `CI` avant de lancer la `CD`

    Il nous manque un paramètre à ajouter, c'est la surcharge de variable pour `MLFLOW_SERVER` Pour cela, modifions le déclencheur et ajoutons-y la substitution avec l'adresse IP du serveur MLflow.

    ![alt](public/cloud_build3.png)

    Après avoir mis à jour le fichier `cloudbuild.yaml`, nous pouvons de nouveau envoyer les nouvelles références vers le dépôt.
    """)
    return


app._unparsable_cell(
    r"""
    git commit -am "Added CD pipeline in Cloud Build configuration file"
    git push
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/cloud_build4.png" />

    Ce qui est intéressant, c'est que l'étape CD ne sera exécutée que si l'étape CI est exécutée sans erreurs. On évite donc d'entraîner des modèles si les **tests unitaires ne sont pas vérifiées**, évitant ainsi des temps et de la consommation de ressources inutiles.

    <div class="alert alert-block alert-warning">
        Dans certains cas, il se peut que l'entraînement des modèles prenne du temps. Or, Cloud Build est limité par défaut à un temps d'exécution maximal de 10 minutes.
    </div>

    Si l'on nécessite de plus grandes ressources, il est possible d'ajouter un champ `options` dans le fichier de configuration Cloud Build pour spécifier le type de machine à utiliser et le temps d'exécution maximal.
    """)
    return


app._unparsable_cell(
    r"""
    options:
      machineType: 'N1_HIGHCPU_8'
    timeout: 1200s
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    On utilise ici une machine de type `N1_HIGHCPU_8` avec un `timeout` (temps d'exécution maximal) de 20 minutes (au lieu de 10 minutes par défaut). La liste des types de machines Cloud Build disponible est <a href="https://cloud.google.com/cloud-build/pricing?hl=fr" target="_blank">accessible ici</a>.

    Pour les tests, on pourra baisser le nombre d'itérations du processus d'optimisation (à $4$ par exemple) afin de réduire les temps d'exécutions.

    Sur l'interface MLflow, nous pouvons voir que le modèle optimisé a bien été récupéré et versionné vers l'état `Staging`.

    ![alt](public/cloud_build_4.png)

    Pour synthétiser, nous avons crée le pipeline suivant.

    ![alt](public/cicd2.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Nous venons de créer notre premier pipeline automatisé ! 😎

    - Nous avons vu l'approche CI/CD et pourquoi elle était indispensable.
    - Nous avons construit un pipeline CI/CD pour entraîner automatiquement le modèle.

    > ➡️ Dans le suite, nous allons construire **l'intégralité du pipeline de pré-production**, des tests unitaires jusqu'au déploiement sur Cloud Run.
    """)
    return


if __name__ == "__main__":
    app.run()
