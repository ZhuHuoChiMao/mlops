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
    Le pipeline de production est quasi-identique au pipeline de pré-production dans l'enchaînement des opérations. La seule différence concerne le déploiement, qui au lieu de s'effectuer sur Cloud Run, est réalisé sur un cluster K8s. Le pipeline de production sera déclenché lorsque de nouvelles références seront envoyées sur la branche `master` des deux référentiels Git.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/pipeline_prod1.png" />

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Configurer le déclencheur du modèle pour exécuter automatiquement le déploiement vers K8s</li>
        <li>Vérifier que les logs sont bien produits</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/d5pGYhWb3T1Hyyl8OB/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configuration du déclencheur du modèle

    Reprenons le projet Kedro `purchase_predict` et dirigeons-nous sur la branche `master`. Comme pour `purchase_predict_api`, nous allons fusionner avec la branche `staging`.
    """)
    return


app._unparsable_cell(
    r"""
    git checkout main
    git merge staging
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Le fichier `cloudbuild.yaml` va subir peu de modifications : en effet, dans le pipeline de pré-production, nous avions juste besoin d'exécuter un autre build d'un référentiel Git existant. C'est exactement le même principe ici, puisqu'il suffit juste de faire référence au fichier `cloudbuild.yaml` du référentiel `purchase_predict_api` de la branche `master`.
    """)
    return


app._unparsable_cell(
    r"""
    - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
      id: API Deploy
      entrypoint: 'bash'
      args: 
      - '-c'
      - |
          gcloud source repos clone purchase_predict_api /tmp/purchase_predict_api --project=$PROJECT_ID
          ls /tmp/purchase_predict_api
          git --git-dir=/tmp/purchase_predict_api/.git --work-tree=/tmp/purchase_predict_api checkout $BRANCH_NAME
          ls /tmp/purchase_predict_api
          gcloud builds submit \
            --config /tmp/purchase_predict_api/cloudbuild.yaml /tmp/purchase_predict_api \
            --substitutions=SHORT_SHA=$SHORT_SHA
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Avec la commande `checkout`, nous nous positionnons sur `BRANCH_NAME`. Or, cette variable d'environnement sera égale à `master` pour le déclencheur de `purchase_predict` en production.

    Nous pouvons dupliquer le déclencheur `build-purchase-predict-staging` (qui conservera les variables d'environnement) et modifier la branche sur laquelle lancer le déclencheur.

    ![alt](public/pipeline_prod2.png)

    Au total, nous avons 4 déclencheurs : deux par projet, qui correspondent aux environnements de pré-production et de production.

    ![alt](public/pipeline_prod3.png)

    Retournons sur VS Code et ajoutons les fichiers au référentiel Git.
    """)
    return


app._unparsable_cell(
    r"""
    git add .
    git commit -am "Cloud Build trigger for production environment"
    git push orgin main
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'exécution se mets alors en route.

    ![alt](public/pipeline_prod4.png)

    Là-aussi, d'après la troisième étape du fichier `cloudbuild.yaml`, un autre build sera lancé pour l'API.

    ![alt](public/pipeline_prod5.png)

    Après plusieurs minutes d'attente (entraînement du modèle et conteneurisation de l'API), l'API devrait être déployée sur le cluster K8s.
    """)
    return


app._unparsable_cell(
    r"""
    kubectl get deploy purchase-predict -o yaml --namespace api-purchase | grep image:
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    image: gcr.io/training-ml-engineer/purchase-predict-api:6ae574b
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Par ailleurs, sur <a href="\" target="_blank">Cloud Logging</a>, nous devrions voir les logs associés.

    ![alt](public/pipeline_prod7.png)

    Nous remarquons 4 groupes de logs identiques, qui correspondent aux 2 instances `gunicorn` en exécution dans les deux pods.

    Notre environnement est enfin au complet !

    ![alt](public/pipeline_prod6.png)

    Nous avons automatisé le déploiement aussi bien sur l'environnement de pré-production (staging) que l'environnement de production.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    À la fois le pipeline de pré-production et de production sont opérationnels.

    - Nous avons modifié le déclencheur du pipeline de production pour déployer vers un cluster Kubernetes.
    - Les logs applicatifs sont bien redirigés vers Cloud Logging.

    > ➡️ Jusqu'ici, tout est automatisé lors d'un <b>push Git</b>, mais cela nécessite encore une intervention humaine. Avec Apache Airflow, nous allons pouvoir déclencher le pipeline à intervalle de temps régulier et contrer la <b>dérive de modèle</b>.
    """)
    return


if __name__ == "__main__":
    app.run()
