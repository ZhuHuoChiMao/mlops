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
    Le pipeline de pré-production correspond aux différents étapes permettant de déployer l'API contenant le modèle entraîné. Il s'agit d'exécuter, dans son intégralité, les processus d'entraînement, de logging et de conteneurisation de l'API pour servir et exposer directement le modèle lorsque l'on modifie le code source.

    Cette pratique est pleinement au coeur de l'approche MLOps : en automatisant le déploiement par des processus reliés entre-eux, on augmente significativement l'efficacité opérationnelle en rendant disponible le modèle le plus *à jour*.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Créer le pipeline CI/CD de l'API</li>
        <li>Construire l'intégralité du pipeline de pré-production</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/DQcqDjL0vcxz7lEhNT/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Le pipeline de pré-production est la succession du pipeline CI/CD construit pour entraîner le modèle et l'envoyer vers MLflow, avec le pipeline qui va automatiquement déployer une image Docker de l'API sur Cloud Run.

    ![alt](public/pipeline_preprod.png)

    Concernant l'entraînement du modèle, nous avons seulement un déclencheur : lorsque de nouvelles références sont envoyées vers le dépôt `purchase_predict`. En revanche, pour la construction de l'API, il y a deux déclencheurs.

    - Lorsque de nouvelles références sont envoyées vers l'API `purchase_predict_api`.
    - Lorsque l'entraînement du modèle par Cloud Build a terminé son exécution.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Déploiement de l'API

    Dans un premier temps, créons la partie qui va construire l'API à partir du dépôt `purchase_predict_api`.

    ![alt](public/pipeline_preprod_api.png)

    Rappelons-nous que pour construire l'API, nous avons besoin de trois étapes.

    - Il faut construire l'image Docker de l'API.
    - Cette image Docker doit être envoyée au Container Registry de notre projet Google.
    - L'image envoyée vers le Container Registry doit remplacer celle en cours d'exécution sur Cloud Run.

    Reprenons le `Dockerfile` que nous avions construit pour l'API.

    ```
    FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

    # Indispensable pour LightGBM
    RUN apt update
    RUN apt install libgomp1 -y

    RUN mkdir /app

    WORKDIR /app

    COPY pyproject.toml /app/pyproject.toml
    COPY app.py /app/app.py
    COPY src/ /app/src/

    RUN uv sync --no-cache-dir

    # On ouvre et expose le port 80
    EXPOSE $PORT

    # Lancement de l'API
    # Attention : ne pas lancer en daemon !
    CMD ["uv", "run", "gunicorn", "app:app", "-b", "0.0.0.0:80", "-w", "4"]

    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La seule différence réside dans l'exposition du port où nous récupérons la variable d'environnement plutôt que d'écrire en clair un port spécifique.

    Ensuite, tout comme nous l'avions fait pour le projet `purchase-predict`, nous allons ajouter un fichier `cloudbuild.yaml` qui contient les différentes étapes à exécuter sur Cloud Build.
    """)
    return


app._unparsable_cell(
    r"""
    # Liste des Cloud Builders : https://console.cloud.google.com/gcr/images/cloud-builders/GLOBAL
    steps:
    - name: "gcr.io/cloud-builders/docker"
      args: ['build', '-t', 'gcr.io/$PROJECT_ID/purchase-predict-api:$SHORT_SHA', '.']
    - name: 'gcr.io/cloud-builders/docker'
      args: ['push', 'gcr.io/$PROJECT_ID/purchase-predict-api:$SHORT_SHA']
    - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
      entrypoint: gcloud
      args: ['run', 'deploy', 'purchase-predict-api', '--image', 'gcr.io/$PROJECT_ID/purchase-predict-api:$SHORT_SHA', '--region', 'europe-west1', '--platform', 'managed']
    images:
    - gcr.io/$PROJECT_ID/purchase-predict-api:$SHORT_SHA
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dans les deux premières étapes, nous utilisons l'image `gcr.io/cloud-builders/docker` pour construire l'image Docker de l'API et l'envoyer sur le registre de conteneurs de notre projet Google Cloud.

    La dernière étape utilise l'image `gcr.io/google.com/cloudsdktool/cloud-sdk` pour avoir accès à la commande `gcloud`. Cette dernière va nous permettre d'envoyer l'image Docker construire comme nouvelle révision sur notre application Cloud Run.

    Créons un nouveau déclencheur Cloud Build nommé `build-purchase-predict-api-staging`.

    ![alt](public/pipeline_prepod_api2.png)

    À la troisième étape, notre service aura besoin de déployer le conteneur sur Cloud Run. Or, par défaut, Cloud Build ne dispose pas des droits d'accès sur les autres services. Il faut donc autoriser Cloud Build à interagir avec Cloud Run dans les paramètres.

    ![alt](public/pipeline_preprod3.png)

    Envoyons les nouvelles références vers Git.

    ```
    git add .
    git commit -am "New Cloud Build configuration"
    git push origin staging
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous voyons le nouveau build apparaître avec les trois étapes telles que mentionnées dans le fichier de configuration.

    ![alt](public/pipeline_preprd4.png)

    Si nous retournons dans <a href="https://console.cloud.google.com/run/" target="_blank">Cloud Run</a>, nous voyons que l'image Docker a bien été déployée.

    ![alt](public/pipeline_preprod_api5.png)

    Par ailleurs, dans <a href="https://console.cloud.google.com/gcr" target="_blank">Container Registry</a>, nous voyons bien apparaître le tag du commit Git.

    ![alt](public/pipeline_preprod_api6.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pipeline entier

    Revenons maintenant sur l'intégralité du pipeline.

    ![alt](public/pipeline_preprod (1).png)

    Nous venons de créer les deux parties (gauche et droite) de manière indépendantes. Pour obtenir l'intégralité du pipeline, il suffit simplement de modifier le pipeline CI/CD (à gauche) du projet `purchase-predict` pour exécuter automatiquement la construction de l'image Docker de l'API et son déploiement vers Cloud Run.

    Modifions le fichier `cloudbuild.yaml` du projet `purchase-predict`.
    """)
    return


app._unparsable_cell(
    r"""
    options:
      automapSubstitutions: true
    # Variables
    substitutions:
      _GITHUB_REPOSITORY: "noobzik/purchase_predict_2026_api.git" # Répertoire git sans github.com
    steps:
      - name: "ghcr.io/astral-sh/uv:python3.12-trixie-slim"
        id: CI
        entrypoint: /bin/sh
        args:
          - "-c"
          - "chmod a+x install.sh && ./install.sh && uv sync && uv run pytest ."
        env:
          - "UV_CACHE_DIR=/root/.cache/uv"
        waitFor: ["unpack-cache"]

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
          - "UV_CACHE_DIR=/root/.cache/uv" 

        waitFor: ["CI"]
      - name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
        id: API Deploy
        secretEnv: ["GITHUB_FGT_API"]
        entrypoint: "bash"
        args:
          - "-c"
          - |
            git clone --branch $BRANCH_NAME https://$$GITHUB_FGT_API@github.com/$_GITHUB_REPOSITORY /tmp/purchase_predict_api
            cd /tmp/purchase_predict_api
            gcloud builds submit \
              --config /tmp/purchase_predict_api/cloudbuild.yaml /tmp/purchase_predict_api \
              --substitutions=SHORT_SHA=$SHORT_SHA
        waitFor: ["CD"]

    logs_bucket: "gs://purchase_predict/logs_build_cloud_build"
    timeout: 1200s
    availableSecrets:
      secretManager:
        - versionName: projects/$PROJECT_ID/secrets/github-fgt-api/versions/latest
          env: GITHUB_FGT_API # Nom de la secret
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous ajoutons ici une dernière étape qui va récupérer l'image `gcr.io/google.com/cloudsdktool/cloud-sdk` pour là-aussi interagir avec le SDK `gcloud`. L'exécution est ensuite assez dense et peut se décomposer en plusieurs étapes.

    - On commence par récupérer le dépôt distant avec `gcloud source repos` de notre API que l'on enregistre dans `/tmp/purchase_predict_api`.
    - Ensuite, nous nous positionnons sur la branche adaptée (`master` ou `staging`) avec un `checkout` en spécifiant par l'intermédiaire des arguments `--git-dir` et `--work-tree` le chemin d'accès du code de l'API.
    - Enfin, avec `gcloud builds submit`, nous envoyons manuellement un nouveau build en spécifiant le fichier `cloudbuild.yaml` de l'API et en indiquant le dossier des codes sources situé dans `/tmp/purchase_predict_api`.

    /// attention | note
    Pour accélérer les temps de calcul, le paramètre Kedro <code>automl_max_evals</code> a été fixé à $1$.
    ///

    Pour des raisons de temps de calcul, nous rajoutons un `timeout` à 1200s à la fin. En effet, la dernière étape va générer un second build qui sera dépendant de celui-ci. Ainsi, la dernière étape sera terminée uniquement lorsque le build lancé sera lui-aussi terminé : il faut donc prendre en compte le temps nécessaire à la fois pour entraîner le modèle, mais aussi pour construire l'image Docker et l'envoyer sur Cloud Run.

    En effectuant un nouveau commit et un push, l'exécution sur Cloud Build devrait prendre au total 7 à 8 minutes. À la fin, la nouvelle version sera déployée sur Cloud Run.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Le pipeline de pré-production est enfin prêt ! Il est 100% automatisé, et en tant que ML Engineer ou Data Scientist, nous pouvons à tout moment modifier le code ou le modèle et un simple `push` fera le travail de déploiement à notre place (du moins dans l'environnement staging).

    - Nous avons crée le pipeline CI/CD pour l'API.
    - Nous avons construit le pipeline de pré-production dont l'exécution est entièrement automatisée.

    > ➡️ Après le pipeline de pré-production, au tour du **pipeline de production** ! Mais cette fois-ci, la production va devoir supporter de grandes charges de travail (milliers/millions de requêtes) : c'est donc **Kubernetes** qui va héberger l'API.
    """)
    return


if __name__ == "__main__":
    app.run()
