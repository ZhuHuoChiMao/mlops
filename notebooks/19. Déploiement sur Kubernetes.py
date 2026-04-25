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
    Pour le pipeline de pré-production, l'API est déployé sur Cloud Run et est exécuté dans un conteneur Docker. Le **pipeline de production**, qui est supposé servir des dizaines de requêtes par seconde, doit quant à lui être exécuté sur Kubernetes pour implémenter la scalabilité.

    Le pipeline de production que nous allons construire ira, à terme, déployer l'API directement dans Kubernetes. Il nous faut donc construire les fichiers de configuration du Deployment qui permettra d'exécuter l'API.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/k8s_prod6.png" />

    Dans ce Notebook, il est question de mettre en place cette partie spécifique du déploiement dans le pipeline de production.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Créer et configurer un cluster K8s pour l'API de production</li>
        <li>Définir les fichiers de configuration YAML</li>
        <li>Délivrer automatiquement l'API via un déclencheur</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/ToMjGpwbnkdSSSp0VnW/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configuration du cluster K8s

    Pour exposer l'API via un cluster K8s, nous allons en configurer un nouveau que nous appelerons `purchase-predict-api`.

    Pour accéder à la page de la configuration https://console.cloud.google.com/kubernetes/list/overview
    - Cliquez sur créer
    - Cliquez sur passer au mode standard

    ![alt](public/k8s_prod1_1.png)

    Nous allons ensuite configurer le pool de noeuds par défaut. Nous allons activer l'autoscaling avec un intervalle de noeuds situé entre 1 et 5. Au total, le cluster ne pourra pas excéder de 5 noeuds.

    ![alt](public/k8s_prod2_1.png)

    Concernant les types de machines, nous pouvons garder les `e2-medium`.

    ![alt](public/k8s_prod3_1.png)

    Puisque nous sommes limité à 5 noeuds en autoscaling, nous pourrons avoir au total 10 CPU et 15 Go. Nous affectons à chaque noeud 10Go d'espace disque, ce qui sera amplement suffisant puisqu'il n'y a pas de stockage local.

    Une fois le cluster lancé, nous pouvons nous y connecter via la commande `gcloud`.

    ![alt](public/k8s_prod4.png)

    ```
    gcloud container clusters get-credentials purchase-predict-api --zone europe-west1-b --project <project_id>
    ```
    /// note
    Jusqu'à présent, vous n'avez peut être pas exploré l'options des instances en spot.

    Le spot dans le cloud indique que votre instance peut se faire couper en cas de charge exceptionnelle de travail demandé par les autres utilisateurs du cloud concerné. En compensation, les réduction de facture peuvent atteindre jusqu'à 70% du prix initial.

    Mais pour cela, il faut être sûr que la VM ou le cluster kubernetes n'est pas critique.
    ///

    ### Espaces de noms

    En pratique, il se peut que les clusters K8s ne contiennent pas un seul mais plusieurs applications. Dans ce genre de situation, une bonne pratique consiste à segmenter les ressources présentes à l'aide d'espaces de noms (*namespaces*). Ces espaces de noms fournissent des isolations logiques entre les ressources. Les services d'un espace de nom ne pourra être associé à des pods d'un autre service.

    Par défaut, il y a 4 espaces de noms présents dans le cluster.ais plusieurs applications. Dans ce genre de situation, une bonne pratique consiste à segmenter les ressources présentes à l'aide d'espaces de noms (*namespaces*). Ces espaces de noms fournissent des isolations logiques entre les ressources. Les services d'un espace de nom ne pourra être associé à des pods d'un autre service.
    """)
    return


app._unparsable_cell(
    r"""
    kubectl get ns
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    NAME              STATUS   AGE
    default           Active   2m33s
    kube-node-lease   Active   2m34s
    kube-public       Active   2m35s
    kube-system       Active   2m35s
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'espace de noms `default` est celui utilisé par défaut lorsque l'on ne spécifie pas d'espaces de noms pour les ressources. Les autres espaces de noms `kube-*` sont utilisés par le cluster lui-même.

    <div class="alert alert-block alert-info">
        Il faut éviter d'utiliser des espaces de noms avec <code>kube</code> comme préfixe, car ils sont réservés au cluster.
    </div>

    Créons le fichier `ns.yaml` qui va nous permettre de définir un espace de noms.
    """)
    return


app._unparsable_cell(
    r"""
    apiVersion: v1
    kind: Namespace
    metadata:
      name: api-purchase
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme toujours, pour créer la ressource, nous utilisons `kubectl apply`.
    """)
    return


app._unparsable_cell(
    r"""
    kubectl apply -f ns.yaml
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'espace de noms étant créé, nous pouvons le détailler.
    """)
    return


app._unparsable_cell(
    r"""
    kubectl describe ns api-purchase
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    Name:         api-purchase
    Labels:       <none>
    Annotations:  <none>
    Status:       Active

    Resource Quotas
     Name:                       gke-resource-quotas
     Resource                    Used  Hard
     --------                    ---   ---
     count/ingresses.extensions  0     100
     count/jobs.batch            0     5k
     pods                        0     1500
     services                    0     500

    No LimitRange resource.
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Les quotas appliqués sont ceux configurés par défaut dans GKE. Il est bien entendu possible de modifier ces valeurs dans la configuration du cluster, mais elles seront amplement suffisantes pour l'API.

    La configuration du cluster K8s est terminée, nous pouvons maintenant nous atteler aux fichiers de configurations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// note

    Avec les nouvelles version de kubernetes managés par Google Cloud, il est possible que les quotas ne soient pas affichés

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fichiers de configuration YAML

    Avant de commencer, assurons-nous d'être sur **la bonne branche** Git ! Le fichier `cloudbuild.yaml` qui nous avions configuré était valide pour la pré-production, mais ne sera plus identique pour la production.

    Pour cela, nous allons retourner sur la branche `main` et **fusionner** avec la branche `staging`.

    ```
    git checkout main
    git merge staging
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Créons un dossier `k8s/` à la racine du projet : nous allons y insérer tous les fichiers de configuration YAML qui seront utilisés avec `kubectl`. Commençons par le fichier `deployment.yaml`.
    """)
    return


app._unparsable_cell(
    r"""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: purchase-predict
      labels:
        app: purchase-predict
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: pod-purchase-predict
      template:
        metadata:
          labels:
            app: pod-purchase-predict
        spec:
          containers:
          - name: pod-purchase-predict
            image: gcr.io/training-ml-engineer/purchase-predict-api
            env:
            - name: PORT
              value: "80"
            - name: ENV
              value: "staging"
            - name: MLFLOW_SERVER
              value: "http://34.107.0.37/"
            - name: MLFLOW_REGISTRY_NAME
              value: "purchase_predict"
            ports:
            - containerPort: 80
            resources:
              requests:
                memory: "0.5G"
                cpu: "0.5"
              limits:
                memory: "1G"
                cpu: "1"
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La configuration du Deployment est très similaire à celui que nous avions déjà réalisé, à la seule différence que nous avons modifié l'image Docker, les ressources et des variables d'environnement nécessaires pour l'exécution de l'API. L'image Docker correspond ici au tag le plus récent.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/k8s_prod5.png" />

    Ajoutons le Deployment dans le cluster.
    """)
    return


app._unparsable_cell(
    r"""
    kubectl apply --namespace api-purchase -f k8s/deployment.yaml
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En faisant un `kubectl get pods`, nous voyons qu'il n'y a aucune ressource ! En effet, sans mention particulière, `kubectl` ira toujours chercher les ressources de l'espace de noms `default`. Il faut donc le spécifier pour accéder aux ressources.
    """)
    return


app._unparsable_cell(
    r"""
    kubectl get pods --namespace api-purchase
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    NAME                                READY   STATUS    RESTARTS   AGE
    purchase-predict-675fc5db9d-bl65d   1/1     Running   0          80s
    purchase-predict-675fc5db9d-jmbph   1/1     Running   0          80s
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div class="alert alert-block alert-info">
        Il se peut que le cluster procède à de l'autoscaling : le deuxième pod prendrai plus de temps à démarrer.
    </div>

    Maintenant que nos pods sont en place, créons le service associé dans le fichier `service.yaml`.
    """)
    return


app._unparsable_cell(
    r"""
    apiVersion: v1
    kind: Service
    metadata:
      name: purchase-predict-service
    spec:
      type: NodePort
      ports:
        - port: 80
          targetPort: 80
      selector:
        app: pod-purchase-predict
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    kubectl apply --namespace api-purchase -f k8s/service.yaml
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour terminer, nous allons placer un Ingress en frontal.
    """)
    return


app._unparsable_cell(
    r"""
    apiVersion: networking.k8s.io/v1beta1
    kind: Ingress
    metadata:
      name: app-ingress
    spec:
      rules:
      - http:
          paths:
          - path: /*
            backend:
              serviceName: purchase-predict-service
              servicePort: 80
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    kubectl apply -f k8s/ingress.yaml --namespace api-purchase
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme nous l'avions fait précédemment, l'Ingress est en cours de création comme nous pouvons le voir avec `kubectl get ingress app-ingress --namespace api-purchase`.
    """)
    return


app._unparsable_cell(
    r"""
    Name:             app-ingress
    Namespace:        api-purchase
    Address:          
    Default backend:  default-http-backend:80 (10.108.1.5:8080)
    Rules:
      Host        Path  Backends
      ----        ----  --------
      *           
                  /*   purchase-predict-service:80 (10.108.0.2:80,10.108.1.6:80)
    Annotations:  <none>
    Events:
      Type    Reason  Age                From                     Message
      ----    ------  ----               ----                     -------
      Normal  Sync    45s (x2 over 45s)  loadbalancer-controller  Scheduled for sync
      Normal  Sync    7s                 loadbalancer-controller  UrlMap "k8s2-um-efrpzb5i-api-purchase-app-ingress-f9i0pcz7" created
      Normal  Sync    4s                 loadbalancer-controller  TargetProxy "k8s2-tp-efrpzb5i-api-purchase-app-ingress-f9i0pcz7" created
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Il faut patienter quelques minutes le temps que Google provisionne un équilibreur de charge et qu'il soit entièrement configuré. Ensuite, nous pouvons requêter à l'adresse renseignée par l'Ingress via `kubectl get ingress --namespace api-purchase`.
    """)
    return


app._unparsable_cell(
    r"""
    NAME          HOSTS   ADDRESS         PORTS   AGE
    app-ingress   *       34.117.133.85   80      10m
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Maintenant que toutes nos ressources sont en place, exécutons le code Python suivant.
    """)
    return


@app.cell
def _():
    import os
    import requests
    import pandas as pd

    dataset = pd.read_csv(os.path.expanduser("data/primary.csv"))
    dataset = dataset.drop(["user_session", "user_id", "purchased"], axis=1)
    return dataset, requests


@app.cell
def _(dataset, requests):
    requests.post(
        "http://34.36.188.215/predict",  # Remplacer par l'adresse IP associée à l'Ingress
        json=dataset.sample(n=10).to_json()
    ).json()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notre API est correctement déployée sur Kubernetes ! 👏

    Il ne reste plus qu'à automatiser le déploiement de l'API via un déclencheur Cloud Build.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configuration de Cloud Build

    Puisque nous sommes sur la branche `master`, il ne faut plus déployer l'image Docker vers Cloud Run. La dernière étape du fichier `cloudbuild.yaml` doit être supprimée.
    """)
    return


app._unparsable_cell(
    r"""
    # Liste des Cloud Builders : https://console.cloud.google.com/gcr/images/cloud-builders/GLOBAL
    steps:
    - name: "gcr.io/cloud-builders/docker"
      id: Building Docker image
      args: ['build', '-t', 'gcr.io/$PROJECT_ID/purchase-predict-api:$SHORT_SHA', '.']
    - name: 'gcr.io/cloud-builders/docker'
      id: Pushing Docker image
      args: ['push', 'gcr.io/$PROJECT_ID/purchase-predict-api:$SHORT_SHA']
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comme pour la pré-production, le déclencheur va construire l'image Docker et l'envoyer vers le registre de conteneurs du projet Google Cloud. Il nous faut rajouter les autres étapes qui vont prendre cette image Docker pour l'insérer dans les configurations Kubernetes. Pour rappel, l'image Docker se voit attribuer un tag qui correspond au 7 premières lettres du commit SHA de Git.

    > ❓ Comment utiliser ce tag dans le fichier de configuration YAML ?

    Et oui, dans notre fichier `deployment.yaml`, nous devons spécifier le tag Docker à utiliser. Comment pourrions-nous faire référence à un tag *dynamique* déterminé lors du déclenchement du build ?

    La solution consiste à utiliser du **templating**.

    ### Templating de fichier

    Le templating est un procédé qui consiste à écrire des références à des macros dans des fichiers de configuration, puis à remplacer ces macros par des valeurs dynamiques lors du rendu. L'objectif est de pouvoir écrire des fichiers de configuration qui, à tout moment, peuvent être dynamiques en remplaçant certaines valeurs selon des variables écrites dans le texte. Ce procédé de templating est également présent dans d'autres applications, dont Apache Airflow que nous verrons très bientôt.

    L'idée ici, c'est de ne pas utiliser un tag spécifique dans le fichier de Deployment, mais de faire référence à une macro qui sera ensuite remplacée au moment de l'exécution. Dans le fichier Deployment, nous modifions le tag en remplaçant par la macro `DOCKER_TAG`.
    """)
    return


app._unparsable_cell(
    r"""
    spec:
      containers:
      - name: pod-purchase-predict
        image: gcr.io/esgi-352608/purchase-predict-api:DOCKER_TAG
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// note | Rappel
    Le `esgi-352608` c'est le nom du projet GCP
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous pouvons ensuite construire la prochaine étape du fichier `cloudbuild.yaml`.
    """)
    return


app._unparsable_cell(
    r"""
    - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
      id: Rendering templated K8s YAML file
      entrypoint: /bin/sh
      args:
      - '-c'
      - |
         sed -s '$a---' k8s/*.yaml > config.yaml.tpl &&
         sed "s/DOCKER_TAG/${SHORT_SHA}/g" config.yaml.tpl > config.yaml
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Analysons en détails cette étape. Elle fait appel à des commandes Bash.

    - La première commande `sed` va avoir pour objectif de concaténer l'ensemble des fichiers d'extension `*.yaml` à l'intérieur du dossier `k8s/` et de séparer ces concaténations par des sauts de lignes suivies de trois tirets. Le résultat est ensuite enregisté dans le fichier `config.yaml.tpl`.
    - Encore avec la commande `sed`, on remplace la macro `DOCKER_TAG` du fichier `config.yaml.tpl` par les 7 premières lettres du commit SHA de Git, faisant référence au tag de l'image Docker construite par les étapes précédentes. Le rendu du templating est ensuite enregistré dans le fichier `config.yaml`.

    L'intérêt d'avoir un seul fichier `config.yaml` c'est qu'il va à la fois contenir le tag de l'image Docker construite juste avant, mais aussi car la mise à jour des ressources sur K8s sera plus facile si toutes les configurations sont centralisées dans un seul fichier.

    La dernière étape concerne le déploiement sur K8s.
    """)
    return


app._unparsable_cell(
    r"""
    - name: 'gcr.io/cloud-builders/kubectl'
      id: Deploy to K8s
      args:
      - 'apply'
      - '--namespace'
      - 'api-purchase'
      - '-f'
      - 'config.yaml'
      env:
      - 'CLOUDSDK_COMPUTE_ZONE=europe-north1-b'
      - 'CLOUDSDK_CONTAINER_CLUSTER=purchase-predict-api'
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'environnement de build est `kubectl`, qui contient déjà toutes les dépendances pour l'interface K8s. Nous utilisons un `apply` pour mettre à jour les ressources, en précisant l'espace de noms.

    Les variables d'environnements `CLOUDSDK_COMPUTE_ZONE` et `CLOUDSDK_CONTAINER_CLUSTER` sont nécessaires pour que Cloud Build sache où et vers quel cluster exécuter la mise à jour des ressources.

    Au final, le fichier `cloudbuild.yaml` contient 4 étapes.
    """)
    return


app._unparsable_cell(
    r"""
    # Liste des Cloud Builders : https://console.cloud.google.com/gcr/images/cloud-builders/GLOBAL
    steps:
    - name: "gcr.io/cloud-builders/docker"
      id: Building Docker image
      args: ['build', '-t', 'gcr.io/$PROJECT_ID/purchase-predict-api:$SHORT_SHA', '.']
    - name: 'gcr.io/cloud-builders/docker'
      id: Pushing Docker image
      args: ['push', 'gcr.io/$PROJECT_ID/purchase-predict-api:$SHORT_SHA']
    - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
      id: Rendering templated K8s YAML file
      entrypoint: /bin/sh
      args:
      - '-c'
      - |
         sed -s '$a---' k8s/*.yaml > config.yaml.tpl &&
         sed "s/DOCKER_TAG/${SHORT_SHA}/g" config.yaml.tpl > config.yaml
    - name: 'gcr.io/cloud-builders/kubectl'
      id: Deploy to K8s
      args:
      - 'apply'
      - '--namespace'
      - 'api-purchase'
      - '-f'
      - 'config.yaml'
      env:
      - 'CLOUDSDK_COMPUTE_ZONE=europe-north1-b'
      - 'CLOUDSDK_CONTAINER_CLUSTER=purchase-predict-api'
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous pouvons maintenant créer un nouveau déclencheur sur <a href="https://console.cloud.google.com/cloud-build/triggers" target="_blank">Cloud Build</a>.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/k8s_prod7.png" />

    Avant de lancer une exécution, il est important d'autoriser Cloud Build à interagir avec GKE, comme nous l'avions fait pour Cloud Run.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/k8s_prod9.png" />

    Ajoutons les fichiers au référentiel Git puis poussons les nouvelles références.
    """)
    return


app._unparsable_cell(
    r"""
    git add .
    git commit -am "Add K8s configuration files"
    git push google master
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Après quelques minutes d'exécution, le build devrait correctement se finaliser.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/k8s_prod8.png" />

    En affichant les pods avec `kubectl get pods --namespace api-purchase`, nous voyons qu'ils sont beaucoup plus récents.
    """)
    return


app._unparsable_cell(
    r"""
    NAME                                READY   STATUS    RESTARTS   AGE
    purchase-predict-7656f97c5c-drj5k   1/1     Running   0          2m22s
    purchase-predict-7656f97c5c-qgnzs   1/1     Running   0          59s
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour s'assurer qu'il s'agit de la bonne image Docker en cours d'exécution, nous pouvons chercher l'information en affichant le YAML du Deployment.
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
    image: gcr.io/training-ml-engineer/purchase-predict-api:7828046
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sur <a href="https://console.cloud.google.com/gcr/images">Container Registry</a>, il s'agit bien de l'image la plus récente.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/k8s_prod10.png" />

    Notre déploiement vers le cluster K8s est maintenant pleinement opérationnel.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Nous y sommes presque ! Plus qu'une dernière étape pour avoir notre pipeline de production.

    - Nous avons configuré un cluster K8s pour l'environnement de production.
    - Nous avons défini des fichiers de configuration YAML.
    - Le déploiement de l'API a été automatisé via Cloud Build.

    > ➡️ Il ne reste plus qu'à construire le pipeline de production en entier pour avoir un environnement 100% automatisé.
    """)
    return


if __name__ == "__main__":
    app.run()
