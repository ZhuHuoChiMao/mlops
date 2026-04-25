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
    Précédemment, nous avons déployé notre API par l'intermédiaire d'un conteneur Docker exécuté sur une instance de VM. Le problème de ce mode de déploiement, c'est qu'il n'est pas scalable, dans le sens où les ressources ne pourront pas augmenter lorsque les requêtes vont être de plus en plus importantes. L'autre problème, c'est qu'il est difficilement automatisable : dès qu'il faut créer une nouvelle instance ou même déployer une nouvelle version de l'API, il faudra refaire toutes les étapes décrites manuellement.

    Ces deux problèmes majeures empêchent de favoriser **l'approche MLOps** : automatiser le déploiement et garantir un livraison continue des versions. Si l'on souhaite avancer dans cette direction, il faut s'orienter vers des services plus adaptés. C'est un des premiers pas que nous allons faire avec **Cloud Run**.

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Comprendre le fonctionnement du serverless et ses avantages.</li>
        <li>Exécuter le conteneur Docker en serverless avec Cloud Run.</li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/l0MYRFJOjJMCvvSuI/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Serverless

    Initialement, lorsque l'on doit déployer une application Web, il y a plusieurs sujets qui interviennent.

    - Il faut **provisionner** des serveurs adaptés pour l'application : en particulier, choisir les bonnes ressources (processeurs virtuels, mémoire, bande passante) va dépendre des besoins de l'application mais aussi des utilisateurs qui vont interagir avec l'application.
    - Il faut assurer la **disponibilité** de l'application : garantir une disponibilité constante demande une infrastructure scalable (voir élastique) avec des équilibrages de charges entre plusieurs serveurs.
    - Il faut **maintenir** les serveurs : en particulier vérifier les pannes, les ressources consommées, traquer les erreurs mais également mettre à jour vers de nouvelles versions.

    Cela peut devenir très difficile à gérer notamment pour des équipes de tailles réduites, encore plus pour des équipes Data dont les opérations Cloud ne sont pas le coeur de métier. Au final, tous ces sujets finissent par éloigner le développeur de sa mission d'origine : développer l'application. C'est là que le **serverless** rentre en jeu.

    ### Architecture serverless

    Une architecture serverless (ou serverless) est une solution efficace pour partager les responsabilités entre le développeur et le fournisseur Cloud (Google Cloud, AWS, Azure, etc). En effet, tous les points que nous venons de détailler concernent **l'exécution de l'application** et non le développement de celle-ci. C'est justement tout l'intérêt du serverless : c'est le fournisseur Cloud qui va être **responsable** de l'exécution de l'application.

    En d'autres termes, en tant que développeur/ML Engineer, nous n'aurons pas besoin de configurer les serveurs et tout ce qui englobe leur gestion avec du serverless. Nous nous concentrons uniquement sur la conception du code. Ainsi, le fournisseur Cloud va lui-même gérer l'équilibrage de charge, le provisionnement de ressources et la mise à jour des serveurs.

    ![alt](public/serverless.png)

    > ❓ Mais alors, comment ça marche ?

    Tout ceci peut paraître *magique*. Pour faciliter l'interaction avec une architecture serverless, les fournisseurs Cloud ont crées des **« Function as a Service »** (FaaS), où chaque **fonction** est un code ou un conteneur exécuté **indépendamment des autres fonctions**.

    Cette structure permet de facturer les fonctions serverless **à la consommation** : on ne paie l'infrastructure sous-jacente que lorsque les fonctions sont utilisées. Ainsi, si une fonction est exécutée que pendant une certaine plage horaire chaque jour, alors la facturation ne concerne que cette plage horaire. En dehors de la plage, il n'y a aucune facturation puisqu'aucune exécution de la fonction est réalisée. Cela permet, en plus d'optimiser l'efficacité opérationnelle, de réduire la facturation lorsque les charges ne sont pas constantes en comparaison avec un serveur qui devrait rester en état disponible 24h/24.

    Mais pour bien comprendre comment fonctionne techniquement une fonction serverless, il y a plusieurs points qui doivent être abordés.

    ### Microservices

    Dans une architecture serverless, les microservices sont omni-présents. Contrairement à une application monolithique dont l'intégralité des composantes seraient exécutées sur un seul et même serveur, chaque application ou composante en microservices sont exécutés indépendamment des autres, en tant que services mais avec des fonctionnalités précises. Plusieurs applications vont donc interagir entre-elles, et ce couplage faible, bien qu'une bonne pratique dans le Cloud, ajoute des difficultés.

    ![alt](public/serverless2.png)

    Il convient donc de **cartographier et documenter** l'ensemble de ces services, puisque lorsque dans un projet, il y a plusieurs dizaines de fonctions serverless, cela peut devenir compliqué à maintenir.

    ### Fonctions *stateless*

    Un autre point très important concerne les fonctions sans états. En effet, lorsqu'un code est exécuté sur une fonction serverless, chaque appel à cette fonction est indépendante des précédentes. Il faut donc que le traitement réalisé par une fonction puisse être reproduit à chaque instant. De plus, cette exécution est **limitée dans le temps** : en règle général, les fonctions serverless ne peuvent être exécutées que sur plusieurs minutes au maximum.

    ![https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/serverless3.png](public/serverless3.png)
    Ainsi, chaque exécution ne peut stocker des informations persistantes qui seront conservées pour les prochaines exécutions : c'est le principe du **stateless**.

    > ❓ Mais alors comment stocker des variables ou partager des informations entre les exécutions ?

    Dans ce cas, il est préférable d'utiliser une base de données (base SQL, base clé/valeur, ...) pour stocker ces variables et informations qui seront ré-utilisées.

    ![alt](public/serverless4.png)

    ### Cold Start

    Le dernier point qui peut avoir son importance, c'est le **démarrage à froid** (ou *cold start*). En effet, malgré l'appellation serverless, il y a bien un serveur physique qui héberge le code source ou le conteneur et qui l'exécute en mémoire. Seulement, il existe une latence entre le moment où une requête est envoyée vers la fonction, et le moment où la requête est exécutée par la fonction serverless. Cette latence vient du fait que la fonction n'est pas **automatiquement chargée en mémoire** dans un serveur physique, pour éviter de consommer de la mémoire physique lorsqu'aucune requêtes n'est envoyée.

    Lorsqu'une fonction est souvent requêtée (plusieurs par secondes/minutes), alors la fonction reste chargée en mémoire. En revanche, si aucune requête n'est pas envoyée pendant un laps de temps, alors la fonction associée n'est plus chargée en mémoire pour en libérer de l'espace sur le serveur physique. Si une autre requêtes survient par la suite, alors ce temps de chargement de la fonction dans le serveur physique représente ce **démarrage à froid**.

    ![alt](public/serverless6.png)

    Ce temps de latence peut dépendre de plusieurs paramètres : taille de la fonction à charger en mémoire, langage et méthode d'exécution de la fonction ou fournisseur Cloud.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Conteneurs sur Cloud Run

    <a href="https://console.cloud.google.com/run" target="_blank">Cloud Run</a> est le service de fonctions serverless proposé sur Google Cloud. Cloud Run est spécialisé pour **l'exécution de conteneurs serverless** : si l'on ne souhaite pas exécuter des conteneurs mais du code (Python, Node.js, Ruby, Go, etc) alors il faut plutôt utiliser <a href="https://console.cloud.google.com/functions" target="_blank">Cloud Functions</a>.

    ### Connecteur VPC

    Nous allons créer un <a href="https://console.cloud.google.com/networking/networks/list" target="_blank">accès VPC</a>. Lorsque Cloud Run exécutera le conteneur, ce dernier ne sera pas forcément exécuté dans un instance de notre VPC (réseau local dans le Cloud) contenant notamment l'instance MLFlow. Si l'on essaie d'accéder à cette instance avec son nom de domaine (qui est interne), alors nous obtiendrons la même erreur que lorsque nous avonns essayé de contacter l'instance via un ping depuis notre machine.

    L'accès au VPC permet de créer une connexion sécurisée permettant à des services Google Cloud d'interagir avec des serveurs présents dans notre VPC sans avoir besoin de les rendre accessible via Internet, et donc de minimiser les risques.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/cloud_run14.png" />

    Avec cette configuration, Cloud Run pourra accéder à notre VPC si on lui spécifie notamment un connecteur VPC associé à notre réseau. Commençons par créer un nouvel accès VPC sans serveur.

    ![alt](public/vpc-1.png)


    Choisissons par exemple la plage d'adresses IP `10.8.0.0/28` proposée par défaut. Etnsuite nous autorisons l'accès privé à Google Access.

    Il ne reste plus qu'à configurer le pare-feu pour autoriser les connexion SSH pour notre vm MLFlow, ainsi que les connexions depuis l'exterieur pour toute adresse IP.


    Après plusieurs dizaines de secondes, le connecteur VPC est opérationnel.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Service Cloud Run

    Créons le service <a href="https://console.cloud.google.com/run/services" target="_blank">Cloud Run</a> pour exécuter notre API, en cliquant sur Deploy container.

    ![alt](public/cloud-run-setup1.png)

    Le premier paramètre consiste à choisir un type de déploiement. Nous utiliserons artifact registry.

    Nous devons donc ensuite choisir l'URL du container.

    Le nom du service ou la région, ne peuvent pas être modifiés par la suite. Chaque service est associé à des **révisions**, qui est semblable à la notion de versions. En cas d'erreur de configuration, il faudra le supprimer et le recréer.

    D'un point de vu sécurité, si c'est une inférence privée, il faudra paramétrer l'authetification. Mais comme nous sommes dans la pratique du cours, il faudra choisir l'autorisation d'accès publique.

    Au niveau de la facturation, elle sera basé sur le nombre de requête, étant donné la nature du cours. Selon le projet, il est interessant de passer à la facturation de l'instance.

    Ceci est un point important car cela vous permettre de gérer la scalabilité de votre inférence en fonction de la demande et du budget allouée.

    ![alt](public/cloud-run-settings1.png)

    Par défaut, le port $80$ est le port d'écoute de l'instance Docker. Il est également possible d'utiliser d'autres ports (et même conseillé) lorsque l'on utilise des services managés comme Cloud Run. Nous attribuons également des ressources alloués à notre service.

    ![alt](public/cloud-run-setup2.png)

    Ensuite, dans le menu Variables, nous pouvons y insérer les variables d'environnements telles que nous les avions utilisés lorsque nous avions exécuter le conteneur sur l'instance Docker.

    ![](public/cloud-run3.png)

    Enfin, il reste à associer l'accès VPC sans serveur au service Cloud Run dans le menu Connexions.

    ![alt](public/cloud-run-setup4.png)

    Pour terminer, nous allons associer le Service Account dédié à l'API à notre Cloud Run

    ![alt](public/cloud-run-setup5.png)



    nous sélectionnons dans la dernière étape l'option permettant d'autoriser n'importe quel trafic entrant sur notre service. À terme, ce sera une API qui aura le rôle d'authentifier les utilisateurs lorsqu'une authentification sera nécessaire.


    Une fois lancé, après plusieurs secondes pour configurer et lancer le service, ce dernier devrait être opérationnel.

    ![alt](public/cloud-run-setup6.png)

    Nous pouvons tester avec une requête comme nous l'avions fait pour l'instance Docker. L'avantage ici, c'est qu'il n'y a plus d'adresse IP et Cloud Run fournit automatiquement une URL pour le service.
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
def _(dataset, requests):
    requests.post(
        "https://purchase-predict-api-808424404935.europe-west1.run.app/predict",  # Remplacer par l'URL du service Cloud Run
        json=dataset.sample(n=10).to_json(),
    ).json()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Les différentes requêtes HTTP peuvent être visualisés sous l'onglet Journaux.

    ![alt](public/cloud-run-setup7.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Félicitations pour ce premier déploiement 100% serverless !

    - Nous avons détaillé les grands principes et avantages du serverless
    - Nous avons déployé le conteneur en serverless avec le service Cloud Run.

    > ➡️ Le serverless permet de déployer rapidement tout en proposant un modèle économique intéressant : nous allons maintenant mettre en avant une automatisation plus poussée avec <b>les pipelines CI/CD</b> !
    """)
    return


if __name__ == "__main__":
    app.run()
