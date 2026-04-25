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
    Avec Docker, il est très facile de conteneuriser une application pour packager le code source et ses dépendances. Nous allons donc pouvoir conteneuriser l'API contenant le modèle.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Créer l'image Docker contenant l'API.</li>
        <li>Configurer le système pour exécuter automatiquement le conteneur sur l'instance Docker.</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/XeAE4MvXVwOLZsZJWO/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Création de l'image Docker

    Nous allons construire l'image Docker qui va contenir l'API du modèle. Pour cela, nous devrions a priori ajouter une clé SSH afin que l'instance `docker` puisse cloner le projet depuis GitHub.

    Mais avant, il est temps de vous faire comprendre pourquoi Google Cloud Plateform est réputé pour être un vrai casse-tête pour les permissions.

    En effet, depuis la fin de Cloud Repository, nous devons configurer nous même les accès à Artifact Registry, Cloud build, Kubernetes Engine et Secret Manager.

    Vous devez donc créer un Service Account nommé "api-vm" qui aura les permissions suivantes :
    - Artifact Registry Create-on-Push Repository Administrator
    - Artifact Registry Reader
    - Cloud Build Editor
    - Cloud Build Service Account
    - Cloud Run Admin
    - Kubernetes Engine Admin
    - Kebernetes Engine Developer
    - Secret Manager Accessor
    - Service Account User

    Bonne chance !

    ### Création des clées Fine-grained tokens
    Nous allons d'abord ajouter le plugin `Google Cloud Build` qui nous servira pour plus tard :
    - https://github.com/marketplace/google-cloud-build

    Afin de pouvoir télécharger sur la futur VM que nous allons déployer pour notre API, nous allons devoir créer un Fine-Grained token disponible à cette adresse : https://github.com/settings/personal-access-tokens

    Au niveau des permissions, nous allons mettre les informations suivantes:
    - Metadata
    - Contents

    Ensuite, il faudra le stocker vers Google Secret manager : https://console.cloud.google.com/security/secret-manager
    1. Créer un secret
    2. Saisir un nom du secret
    3. Saisir une date d'expiration
    4. Cliquer sur créer un secret

    ### Création de la VM

    Créons une VM `docker`. En modifiant les informations de l'instance, nous devons définir le service account que vous venez de créer.

    Nous utiliserons la configuration suivante :
    - e2-small
    - Aucune sauvegarde
    - Autoriser le traffic http et https
    - Choisir dans la sécurité, le service account que vous avez crée
    - Et n'oubliez pas d'autoriser làccès à l'ensemble des API depuis la VM.


    Enregistrons les paramètres et démarrons l'instance. En s'y connectant en SSH, nous pouvons cloner le dépôt `purchase_predict_api` depuis GitHub En cliquant sur le bouton pour cloner.

    - Commençons par installer git
    ```
    sudo apt install git
    ```
    - Et clonez le répertoire

    Mais ce qu'il va se passer, c'est qu'on avoir avoir une erreur car nous n'avons pqs encore importer la Secret que nous avons affecté avant.

    Pour cela, nous allons lancer cette commande :
    ```
    export GH_TOKEN=$(gcloud secrets versions access latest --secret="<Nom Du Secret>")
    ```

    Il peut être assez répétitif de réaliser cette commande à chaque rémarrage. Nous avons donc deux options :
    1. Le rendre persistant à l'aide de Github dans le VM pour les prochaines executions.
    2. Le rendre persistant au niveau de la VM, rendant le répertoire indépendant.

    La première solution n'est pas la bonne, en effet, nous devrions importer la clée manuellement pour la première fois, cloner le répertoire afin de le rendre persistant. Ce n'est pas terrible en cas de modification non désiré qui est push dans le répertoire.

    La deuxième solution en revanche est plus interéssante, en effet, cela nous permet de le faire dès l'initalisation et par la suite, dupliquer cette VM sous la forme de template pour les autres VM si besoin.

    Nous choisirons donc la deuxième solution :
    ```
    echo 'export GH_TOKEN=$(gcloud secrets versions access latest --secret="<NOM DU SECERT>")' >> ~/.bashrc
    ```

    Mais en réalisant le clone, on vous demande une `public key`, pas terrible en effet, il faudra faire le clone à laide de la commande suivante :

    ```
    git clone https://${GH_TOKEN}@github.com/<username>/<repertoire>.git
    ```

    Et là, ça fonctionne !
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Nous allons installer Docker

    Mais avant, nous devons inclure le répertoire propriétaire de docker dans la base de APT :
    ```
    # Add Docker's official GPG key:
    sudo apt update
    sudo apt install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
    Types: deb
    URIs: https://download.docker.com/linux/debian
    Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
    Components: stable
    Signed-By: /etc/apt/keyrings/docker.asc
    EOF

    sudo apt update
    ```

    Il nous reste plus qu'à lancer l'installation :
    ```
    sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sur le dépôt, il faut se positionner sur la branche `staging`, puisqu'il n'y a aucun fichier par défaut.
    """)
    return


app._unparsable_cell(
    r"""
    cd purchase_predict_api/
    git checkout staging
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Retournons dans le répertoire local et ajoutons le fichier `Dockerfile`.
    """)
    return


app._unparsable_cell(
    r"""
    FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

    # Indispensable pour LightGBM
    RUN apt update
    RUN apt install libgomp1 -y

    RUN mkdir /app

    WORKDIR /app

    COPY pyproject.toml /app/pyproject.toml
    COPY app.py /app/app.py
    COPY src/ /app/src/

    RUN uv sync

    # On ouvre et expose le port 80
    EXPOSE 80

    # Lancement de l'API
    # Attention : ne pas lancer en daemon !
    CMD ["uv", "run", "gunicorn", "app:app", "-b", "0.0.0.0:80", "-w", "4"]
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ce fichier est décomposé en plusieurs étapes.

    - L'installation des paquets nécessaires (comme `libgomp1` pour LightGBM) et du gestionnaire `pip`.
    - L'ajout des fichiers sources dans le dossier `/app` sur l'image Docker.
    - L'exécution en parallèle des 4 processus Flask avec `gunicorn`.

    Une fois le fichier enregistré, nous pouvons construire l'image.
    """)
    return


app._unparsable_cell(
    r"""
    sudo docker build -t purchase_predict_api:latest .
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous pouvons ensuite exécuter un conteneur avec l'image construire.
    """)
    return


app._unparsable_cell(
    r"""
    sudo docker run -p 0.0.0.0:80:80 purchase_predict_api:latest
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Malheureusement, au bout de quelques secondes ... plusieurs erreurs apparaissent !
    """)
    return


app._unparsable_cell(
    r"""
    Traceback (most recent call last):
      File "/usr/local/lib/python3.8/site-packages/gunicorn/arbiter.py", line 583, in spawn_worker
        worker.init_process()
      File "/usr/local/lib/python3.8/site-packages/gunicorn/workers/base.py", line 119, in init_process
        self.load_wsgi()
      File "/usr/local/lib/python3.8/site-packages/gunicorn/workers/base.py", line 144, in load_wsgi
        self.wsgi = self.app.wsgi()
      File "/usr/local/lib/python3.8/site-packages/gunicorn/app/base.py", line 67, in wsgi
        self.callable = self.load()
      File "/usr/local/lib/python3.8/site-packages/gunicorn/app/wsgiapp.py", line 49, in load
        return self.load_wsgiapp()
      File "/usr/local/lib/python3.8/site-packages/gunicorn/app/wsgiapp.py", line 39, in load_wsgiapp
        return util.import_app(self.app_uri)
      File "/usr/local/lib/python3.8/site-packages/gunicorn/util.py", line 358, in import_app
        mod = importlib.import_module(module)
      File "/usr/local/lib/python3.8/importlib/__init__.py", line 127, in import_module
        return _bootstrap._gcd_import(name[level:], package, level)
      File "<frozen importlib._bootstrap>", line 1014, in _gcd_import
      File "<frozen importlib._bootstrap>", line 991, in _find_and_load
      File "<frozen importlib._bootstrap>", line 975, in _find_and_load_unlocked
      File "<frozen importlib._bootstrap>", line 671, in _load_unlocked
      File "<frozen importlib._bootstrap_external>", line 783, in exec_module
      File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
      File "/app/app.py", line 4, in <module>
        from src.model import Model
      File "/app/src/__init__.py", line 9, in <module>
        raise Exception("Environment variable {} must be defined.".format(env_var))
    Exception: Environment variable ENV must be defined.
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En effet, nous n'avons pas défini les **variables d'environnement** ! Il faut donc spécifier au conteneur Docker les variables telles que nous les avions définies dans le fichier `.env` par exemple. Pour cela, il est plus commode de créer un fichier `env.list` par exemple.
    """)
    return


app._unparsable_cell(
    r"""
    ENV=staging
    MLFLOW_SERVER=http://xx.xx.xx.xx/
    MLFLOW_REGISTRY_NAME=purchase_predict
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour passer l'ensembles des variables en paramètre au conteneur Docker, nous pouvons utiliser l'argument `--env-file`.
    """)
    return


app._unparsable_cell(
    r"""
    sudo docker run --env-file ./env.list -p 0.0.0.0:80:80 purchase_predict_api:latest
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Les 4 exécutions de l'API doivent maintenant être opérationnelles dans le conteneur.

    > ❓ Comment avons-nous pu récupérer le modèle depuis Cloud Storage alors qu'il n'y a pas de compte de service ?

    En effet, nous n'avons pas spécifié de compte de service ici. C'est justement parce que nous sommes sur **une VM située dans le même projet que le bucket** que l'authentification s'effectue par défaut. Les instances de VM de Google Cloud ont déjà des comptes de service par défaut avec notamment un accès en lecture et écriture vers Cloud Storage. Ainsi, cela est automatiquement transmis au conteneur Docker. Par contre, si nous étions sur un serveur d'un autre projet Google Cloud ou d'un autre fournisseur Cloud, alors il aurait fallu mettre la clé d'un compte de service sur l'instance hôte, renseigner le chemin à cette clé dans la variable `GOOGLE_APPLICATION_CREDENTIALS` et transmettre cette variable d'environnement au conteneur Docker.

    Testons notre API pour voir que tout s'est bien déroulé.
    """)
    return


@app.cell
def _():
    import os
    import requests
    import pandas as pd

    path_kedro = "/Users/noobzik/Documents/kaggle/purchase-predict/data/03_primary"
    dataset = pd.read_csv(os.path.join(path_kedro, "primary.csv"))
    dataset = dataset.drop(["user_session", "user_id", "purchased"], axis=1)
    return dataset, requests


@app.cell
def _(dataset):
    dataset.sample(n=10).to_json()
    return


@app.cell
def _(dataset, requests):
    requests.post(
        "http://35.202.248.201/predict",  # Remplacer par l'adresse IP de l'instance Docker
        json=dataset.sample(n=10).to_json(),
    ).json()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configuration du système

    Nous sommes capable d'exécuter notre API à partir d'un conteneur Docker. Seulement, nous devons réaliser toutes ces étapes manuellement si l'on souhaite par exemple créer une autre VM pour l'API ou si l'on redémarre l'actuelle VM. Pour optimiser la configuration du système, nous allons mettre en place plusieurs composantes.


    - L'image Docker va être hébergé vers un <a href="https://console.cloud.google.com/marketplace/product/google/artifactregistry.googleapis.com" target="_blank">Artifact Registry</a> qui ne sera accessible que dans notre projet GCP (et non public).
    - Nous allons utiliser le nom d'hôte de l'instance MLflow plutôt que son adresse IP : en effet, en cas de redémarrage de cette instance, l'adresse IP publique, étant éphémère par défaut, sera modifiée. Ainsi, il faut modifier **toutes les références** de cette adresse IP dans les applications qui l'utilisent. Le nom d'hôte, quant à lui, permettra de faire référence à cette VM même en cas de redémarrage.
    - Un service système sera crée pour exécuter automatiquement le conteneur contenant l'API.

    ### Registre de conteneurs Google Cloud

    Dirigeons-nous vers le <a href="https://console.cloud.google.com/artifacts" target="_blank">Artifact Registry</a> et créons un nouveau registre comme nous l'avions fait avec DockerHub.

    - Cliquez sur Create Repository et ensuite, nous allons choisir le format Docker.

    ![alt](public/repository_1.png)

    - En ce qui concerne le nom du repository, nous allons mettre purchased-docker (Attention, le _ ne fonctionne pas ici)
    - Pour les besoin du TP et de le garder simple, nous désactiverons le scan des vulnabilités. En terme de région, nous choisissons `us-central1`.
    - Récupérez le path généré par Google Artifact Registry
    - Dans la VM de l'api, nous allons configurer la connexion avec la commande suivante :

    ![alt](public/artifact_registry_path.png)

    ```
    gcloud auth configure-docker us-central1-docker.pkg.dev
    ```

    Vous devriez avoir ce message confirmant la bonne execution du code :
    ```
    After update, the following will be written to your Docker config file located at
    [/home/rakib_hernandez/.docker/config.json]:
     {
      "credHelpers": {
        "us-central1-docker.pkg.dev": "gcloud"
      }
    }
    ```

    Comme nous pouvons le voir, il n'y a aucun registre pour l'instant. Mais contrairement à DockerHub, il n'est pas possible d'en créer un directement via l'interface : les registres sont automatiquement crées lorsqu'une image est envoyée via l'API Google Cloud.

    Arrêtons la VM Docker et attribuons lui un nouvel accès API au stockage.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/docker_api3.png" />

    Maintenant, nous disposons des droits d'accès pour envoyer une image vers un conteneur de notre projet. Toujours en SSH, après redémarrage et connexion à l'instance Docker, exécutons les commandes `gcloud` pour s'authentifier.
    """)
    return


app._unparsable_cell(
    r"""
    sudo gcloud auth login
    sudo gcloud auth configure-docker
    gcloud auth print-access-token | sudo docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    WARNING: Your config file at [/root/.docker/config.json] contains these credential helper entries:

    {
      "credHelpers": {
        "gcr.io": "gcloud",
        "us.gcr.io": "gcloud",
        "eu.gcr.io": "gcloud",
        "asia.gcr.io": "gcloud",
        "staging-k8s.gcr.io": "gcloud",
        "marketplace.gcr.io": "gcloud"
      }
    }
    Adding credentials for all GCR repositories.
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    L'utilisation de `sudo` est importante, car cela va créer les fichiers de configuration dans `/root`, car Docker est utilisé avec `sudo`. Avant d'envoyer l'image vers le registre, attribuons-lui un tag permettant de faire référence à notre projet Google Cloud.

    ```
    sudo docker tag purchase_predict_api us-central1-docker.pkg.dev/esgi-352608/purchased-docker/purchase_predict_api
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Il ne reste plus qu'à envoyer l'image vers le registre.
    """)
    return


app._unparsable_cell(
    r"""
    sudo docker push us-central1-docker.pkg.dev/esgi-352608/purchased-docker/purchase_predict_api
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Le registre est bien crée avec l'image.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/docker_api4.png" />

    ### Nom de domaine du serveur MLflow

    Avant de configurer les fichiers `systemd` pour exécuter automatiquement le conteneur sur la machine, récupérons le nom de domaine de l'instance MLflow. Après connexion SSH, nous pouvons simplement utiliser la commande suivante.
    ```
    hostname -f
    ```
    """)
    return


@app.cell
def _(c, engineer, ml, mlflow, west3):
    mlflow.europe - west3 - c.c.training - ml - engineer.internal
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Si l'on retourne sur l'instance Docker, en SSH, nous pouvons faire un `ping` pour vérifier que le nom de domaine correspond bien à l'instance MLflow.
    """)
    return


app._unparsable_cell(
    r"""
    ping -c 5 mlflow.europe-west3-c.c.training-ml-engineer.internal
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    PING mlflow.europe-west3-c.c.training-ml-engineer.internal (10.156.0.3) 56(84) bytes of data.
    64 bytes from mlflow.europe-west3-c.c.training-ml-engineer.internal (10.156.0.3): icmp_seq=1 ttl=64 time=108 ms
    64 bytes from mlflow.europe-west3-c.c.training-ml-engineer.internal (10.156.0.3): icmp_seq=2 ttl=64 time=105 ms
    64 bytes from mlflow.europe-west3-c.c.training-ml-engineer.internal (10.156.0.3): icmp_seq=3 ttl=64 time=105 ms
    64 bytes from mlflow.europe-west3-c.c.training-ml-engineer.internal (10.156.0.3): icmp_seq=4 ttl=64 time=105 ms
    64 bytes from mlflow.europe-west3-c.c.training-ml-engineer.internal (10.156.0.3): icmp_seq=5 ttl=64 time=105 ms

    --- mlflow.europe-west3-c.c.training-ml-engineer.internal ping statistics ---
    5 packets transmitted, 5 received, 0% packet loss, time 10ms
    rtt min/avg/max/mdev = 105.004/105.730/107.661/0.999 ms
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    À noter que ce nom de domaine n'est accessible **qu'à l'intérieur du projet Google Cloud** : la VM ne sera pas joignable depuis son propre ordinateur.
    """)
    return


app._unparsable_cell(
    r"""
    ping: mlflow.us-central1-c.c.esgi-352608.internal: Nom ou service inconnu
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Configuration du `systemd`

    La dernière étape consiste à créer un service `systemd` qui permettra d'exécuter automatiquement le conteneur en arrière-plan tout en garantissant le redémarrage. Mais avant, rappelons-nous que les variables d'environnements doivent être configurés, et avec un `systemd`, il n'est pas possible faire des `export`.

    Pour pouvoir configurer les variables d'environnements pour un service, il faut les centraliser dans un fichier de configuration, que nous allons créer avec `sudo nano /etc/default/purchase_predict_api`.
    """)
    return


app._unparsable_cell(
    r"""
    ENV=staging
    MLFLOW_SERVER=http://mlflow.europe-west3-c.c.training-ml-engineer.internal/
    MLFLOW_REGISTRY_NAME=purchase_predict
    DOCKER_IMAGE=us-central1-docker.pkg.dev/esgi-352608/purchased-docker/purchase_predict_api
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Il ne reste plus qu'à créer le fichier `systemd`. Ce fichier concentre trois blocs que nous allons expliciter.

    - **Unit** fait référence aux unités qui doivent être au préalable en cours d'exécution pour que ce service puisse être lancé. En l'occurence, les services réseaux et de gestion de fichier doivent être lancés pour Zookeeper.
    - **Service** contient les informations du service.
    - **Install** spécifie la méthode d'installation du service.

    On pourra trouver <a href="https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/system_administrators_guide/chap-managing_services_with_systemd" target="_blank">plus d'informations ici</a> pour les fichiers `systemd`.
    """)
    return


app._unparsable_cell(
    r"""
    sudo nano /etc/systemd/system/purchase_predict_api.service
    """,
    name="_"
)


app._unparsable_cell(
    r"""
    [Unit]
    Description=API Container
    After=docker.service
    Requires=docker.service

    [Service]
    EnvironmentFile=/home/rakib_hernandez/purchase_predict_2026_api/.env
    TimeoutStartSec=0
    Restart=always
    ExecStartPre=-/usr/bin/docker stop $DOCKER_IMAGE
    ExecStartPre=-/usr/bin/docker rm $DOCKER_IMAGE
    ExecStartPre=/usr/bin/docker pull $DOCKER_IMAGE
    ExecStart=/usr/bin/docker run --env-file /home/rakib_hernandez/purchase_predict_2026_api/.env -p 0.0.0.0:80:80 $DOCKER_IMAGE

    [Install]
    WantedBy=multi-user.target
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Après avoir enregistré le fichier, nous activons le service et l'ajoutons au services systèmes à démarrer automatiquement.
    """)
    return


app._unparsable_cell(
    r"""
    sudo systemctl daemon-reload
    sudo systemctl enable /etc/systemd/system/purchase_predict_api.service
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Puis démarrons le service.
    """)
    return


app._unparsable_cell(
    r"""
    sudo systemctl start purchase_predict_api.service
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour vérifier si le conteneur est bien exécuté, nous pouvons vérifier que le port $80$ est bien utilisé.
    """)
    return


@app.cell
def _(ltpn, netstat):
    netstat - ltpn
    return


app._unparsable_cell(
    r"""
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
    tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -                   
    tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
    tcp6       0      0 :::22                   :::*                    LISTEN      -
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Si le port $80$ n'est pas utilisé, il se peut que le conteneur ne soit pas en cours d'exécution. Pour cela, il est possible d'inspecter les sorties du système en affichant par exemple les 100 dernières lignes.
    """)
    return


app._unparsable_cell(
    r"""
    sudo journalctl -u purchase_predict_api.service | tail -n 100
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Testons une nouvelle fois l'API.
    """)
    return


@app.cell
def _(dataset, requests):
    requests.post(
        "http://35.239.206.95/predict",  # Remplacer par l'adresse IP de l'instance Docker
        json=dataset.sample(n=10).to_json(),
    ).json()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Redémarrons l'instance. A priori, si nous avons correctement configuré le `systemd`, le conteneur devra s'exécuter automatiquement au démarrage de l'instance. Après quelques secondes, le temps que l'instance redémarre, nous pouvons exécuter à nouveau la cellule ci-dessus.

    <div class="alert alert-block alert-warning">
        Puisque l'instance possède une adresse IP éphémère, il faudra probablement changer l'IP dans le cellule.
    </div>

    Une fois terminé, nous pouvons stopper l'instance puisque nous n'allons plus l'utiliser par la suite.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Notre API est maintenant pleinement déployée.

    - Nous avons créer une image Docker pour l'API.
    - Nous avons configuré le système pour automatiser l'exécution de l'API.

    > ➡️ Malgré tout, jusqu'ici, le travail était principalement manuel. À partir de maintenant, nous allons pleinement intégrer l'approche MLOps en <b>automatisant le déploiement</b> des différents projets.
    """)
    return


if __name__ == "__main__":
    app.run()
