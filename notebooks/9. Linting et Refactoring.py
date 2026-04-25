import marimo

__generated_with = "0.20.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    S'il y a bien quelque chose que l'on répète souvent lorsqu'il s'agit du développement de code source, c'est de **coder proprement**. Oui mais, comment faire ? Comment décide-t-on de la « propreté d'un code » ? Existe-il des conventions, des normes et si oui, qu'elles sont-elles ?

    Autant de question que nous allons aborder deux concepts de programmation, pas si récents mais toujours aussi important de nos jours : le **linting** et le **refactoring** !

    <blockquote><p>🙋 <b>Ce que nous allons faire</b></p>
    <ul>
        <li>Découvrir la norme PEP 8 du langage Python</li>
        <li>Effectuer une analyse statique de code avec <code>ruff</code></li>
        <li>Utiliser un formateur de code avec <code>ruff</code></li>
    </ul>
    </blockquote>

    <img src="https://media.giphy.com/media/h1zJMhT5XOT927e0aw/giphy.gif" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## La norme PEP 8

    Si tu as déjà recherché de l'aide sur Google par rapport à un problème Python, peut être que l'expression *PEP 8* ne t'es pas étrangère. Et pour cause : il s'agit de la norme Python qui spécifie quelles sont les bonnes pratiques en terme de style de code.

    > ❓ Pourquoi 8 ? Et d'ailleurs, ça veut dire quoi PEP ?

    Revenons à l'origine du langage Python : il a été initialement construit par une personne, Guido van Rossum, en 1991. Bien évidemment, au fur et à mesure que le langage gagne en popularité, de plus en plus de développeurs expérimentés viennent prêter main forte à Guido pour améliorer le langage Python et y ajouter de nouvelles fonctionnalités.

    Mais voilà, comment s'organiser correctement lorsque des dizaines, centaines voir milliers de personnes travaillent ensemble ? Dans la plupart du temps, le plus simple est le **commentaire** : un utilisateur souhaite qu'une nouvelle fonctionnalité soit présente, il va donc proposer une amélioration, la justifier et la détailler. Habituellement, on appelle cela des **RFC** (*Requests for comments*), et ces demandes sont centralisées dans des documents de spécifications techniques.

    **PEP** (pour *Python Enhancement Proposals*), c'est justement les propositions d'améliorations pour le langage Python. Et <a href="https://www.python.org/dev/peps/pep-0008/" target="_blank">PEP 8</a>, c'est donc la huitième proposition d'amélioration (ordre chronologique) qui fut émise en juillet 2001. Et PEP 8, dont le nom est **Style Guide for Python Code**, fournit un véritable guide sur diverses bonnes pratiques.

    - Structurer efficacement son code (espaces, retours à la ligne, taille maximum de ligne).
    - Adopter les conventions de nommage des variables.
    - Commenter correctement son code.
    - Utiliser la Docstring pour créer une documentation (extension via <a href="https://www.python.org/dev/peps/pep-0257/" target="_blank">PEP 257</a>).

    Suivre la PEP 8, c'est **suivre les recommandations officielles** pour écrire du code qui respecte un format adopté par le plus grand nombre.

    /// attention
    Cette norme n'est pas rigide dans le sens où certains projets peuvent s'affranchir de certaines contraintes (comme la taille maximale d'une ligne, fixée à 79 par défaut pour PEP 8).
    ///

    Prenons comme exemple les premières spécifications dans <a href="https://www.python.org/dev/peps/pep-0008/#indentation" target="_blank">Code Lay-out</a> pour l'indentation.

    <img src="https://blent-learning-user-ressources.s3.eu-west-3.amazonaws.com/training/ml_engineer_facebook/img/pep8_1.jpg" />

    Cette première règle statue que les arguments d'une fonction, lorsqu'il y a un saut de ligne, doivent être alignés sur la même colonne que celui du premier argument.
    """)
    return


@app.function
def fonction(a, b, c, d):
    return a * b * c * d


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Supposons que je saute une ligne entre l'argument `b` et l'argument `c` pour appeler cette fonction.
    """)
    return


@app.cell
def _():
    # Pas bien car les arguments ne sont pas alignés en colonne
    resultat = fonction(1, 2,
                       3, 4)
    # Bien
    resultat = fonction(1, 2,
                        3, 4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dans la première écriture, le troisième argument $3$ n'est pas aligné avec le premier argument $1$ alors qu'il y a eu un saut de ligne : elle ne respecte donc pas PEP 8. La deuxième écriture, en revanche, respecte correctement PEP 8 puisque les deux arguments sont alignés à la bonne colonne.

    Autre exemple, si cette fois-ci nous effectuons un retour à la ligne **en première indentation**.
    """)
    return


@app.cell
def _():
    # Pas bien car les arguments le premier argument n'est pas aligné en colonne du saut de ligne
    resultat_1 = fonction(1, 2, 3, 4)
    # Bien
    resultat_1 = fonction(1, 2, 3, 4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ici, même constat, les arguments ne sont pas alignés. Si l'on souhaite donc ramener à une indentation supplémentaire (qui était de base à 0 car la variable `resultat` est à la toute première colonne), il faut donc privilégier la deuxième écriture.

    Par ailleurs, PEP 8 est strict concernant l'indentation : **utiliser 4 espaces par niveau d'identation**. Même s'il est possible d'utiliser les deux, les espaces constituent la méthode d'indentation préférée.

    /// attention
    Attention à ne pas mélanger le caractère de tabulation et les 4 espaces dans un seul et même fichier, car le programme ne pourra pas être exécuté.
    ///

    Autre exemple de recommandations : **les espaces dans les expressions**. Pour PEP 8, les règles suivantes doivent être respectées.

    - Toujours un espace après et jamais avant une virgule pour séparer les arguments ou les clés des valeurs.
    - Jamais d'espace entre les crochets d'une liste ou d'un dictionnaire.
    - Toujours un espace avant et après les conditions binaires (opérations mathématiques, conditions).
    - Jamais d'espace avant ou après les parenthèses.

    Il ne s'agit que de quelques exemples, que l'on retrouve en-dessous.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    l = range(10)

    # Pas bien
    var1,var2 = l[1 ],{ 'var' : 4 }

    # Bien
    var1, var2 = l[1], {'var': 4}
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > ❓ Il faut donc toujours relire son code ?

    En théorie, oui. Mais il y a deux points qui vont nous aider.

    - En tant qu'humain, nous avons une capacité de mimétisme très développée. À force de regarder des codes propres sur Internet et de pratique soi-même, on finit par adopter automatiquement les bonnes pratiques.
    - Et comme l'erreur est humaine, on s'allie également d'outils qui vont vérifier si notre code est propre.

    Et cet outil qui va nous aider, c'est le **linting**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Linting avec `flake8`

    Le concept de linting est dérivé un logiciel UNIX qui s'appelle **lint**. Cette commande est utilisée pour le langage C afin d'en faire une **analyse statique**. L'objectif de l'analyse statique, c'est d'obtenir des informations sur le comportement des programmes sans les exécuter. En particulier, cela permet de détecter les erreurs de syntaxe et de style (que l'on retrouve sous plusieurs langages).

    Sous Python, il existe notamment trois *linter* : `pylint`, `flake8` et `ruff`. Ces linters vont se baser notamment sur PEP 8 (mais pas que) pour détecter les erreurs dans le code. À noter qu'il est aussi possible de définir ses propres spécifications sur des syntaxes ou styles de code à éviter.

    Créons le fichier `lint/flake8_1.py` avec le code suivant.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
    l= range(10 )
    var1,var2 = l[1 ],{ 'var' : 4 }
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Combien y a-t-il d'erreurs PEP 8 dans ces deux lignes ? Voyons ce que `flake8` en dit.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    uvx flake8 flake8_1.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Il y a beaucoup d'erreurs ! Les erreurs `E2XX` sont liées à des espaces, car elles sont majoritairement présentes dans ces deux lignes. L'erreur `E741`, stipule que nommer une variable `l` n'est pas assez explicite (car avec une seule lettre, difficile de savoir à long-terme de quoi il s'agit).

    Corrigeons toutes ces erreurs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    liste = range(10)
    var1, var2 = l[1], {'var': 4}
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exécutons à nouveau `flake8`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Un nouveau type d'erreur apparaît : `F821`. F signifie Fatal, indiquant que cette erreur empêcherait même l'exécution du programme ! Et pour cause, puisque l'on n'a renommé `l` en `liste`, la variable `l` n'existe pas. Pourtant, on y accède à la deuxième ligne.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    liste = range(10)
    var1, var2 = liste[1], {'var': 4}
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nous avons maintenant plus aucune erreur. Regardons un autre exemple. Créeons un nouveau fichier `flake8_2.py` avec le contenu suivant et lançons le à l'aide de `flake8`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    import os, sys

    filename = open(os.path.join("/home", "/fichier.txt"))
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ici, il y a deux problèmes. Le module `sys` est importé alors qu'il n'est pas utilisé à un seul moment. Ensuite, nous avons effectué plusieurs importations de modules différents sur la même ligne, ce qui n'est pas autorisé par PEP 8.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```py
    import os
    import sys

    filename = open(os.path.join("/home", "/fichier.txt"))
    sys.exit()
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Là-aussi, les erreurs ont été corrigées.

    Dans certains cas, il est aussi possible d'exclurer certaines erreurs ou avertissements en invoquant le paramètre `--ignore`. Par exemple, si nous supposons que des importations sur la même ligne sont autorisées, nous pouvons exclurer l'erreur associée, à savoir `E401`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    import os, sys

    filename = open(os.path.join("/home", "/fichier.txt"))
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    flake8 --ignore E401 flake8_2.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ainsi, la présence ou non de cette erreur ne viendra plus perturber l'analyse statique effectuée par `flake8`. La liste détaillée des codes d'erreurs et d'avertissements <a href="https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes" target="_blank">est accessible ici</a>.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Refactoring avec `black`

    Le **refactoring** (que l'on nomme en français réusinage de code mais avouons que cela est moins classe) consiste à modifier le code source sans ajouter de nouvelles fonctionnalités ni corriger des bugs. Concrètement, dans le cadre de Python, le refactoring va corriger les erreurs PEP 8 qui peuvent être corrigées sans altérer le fonctionnement du code.

    Par exemple, placer les bons niveaux d'indentation, ajouter ou supprimer des espaces ou encore respecter une taille maximale de caractères par ligne sont des opérations qui peuvent être effectués par du refactoring **de manière automatisée**. En revanche, d'autres comme le nommage des variables ou les importations de librairies nécessitent l'attention du développeur, puisque automatiser ces modifications pourraient, au contraire, générer des erreurs.

    Sous Python, l'utilitaire `black` permet de refactorer automatiquement un code Python. Par défaut, lorsque c'est possible, `black` va reformater le code d'un fichier Python selon PEP 8, sauf s'il détecte une erreur fatale qu'il ne pourra corriger (dans ce cas, nous serons avertis de l'erreur).

    Reprenons le code précédent.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    l= range(10 )
    var1,var2 = liste[1 ],{ 'var' : 4 }
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pour exécuter `black`, il suffit de renseigner le chemin d'accès au fichier dont on souhaite refactorer le contenu.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    uvx black black_1.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    D'après ce que nous voyons, le refactoring a fonctionné.

    > ❓ Pourquoi <code>black</code> n'a pas détecté que la variable <code>liste</code> n'est pas définie ?

    Tout simplement parce que `black` fait du **refactoring de code** : il ne va pas toucher ou s'intéresser aux noms des variables, aux importations, etc. Ce qui l'intéresse, ce sont les indentations, les espaces ou, de manière générale, l'agencement des caractères.

    En revanche, d'autres recommandations PEP 8, comme le nommage des variables, ne sera pas modifié par `black`. C'est donc tout l'intérêt ici d'utiliser `black` pour reformater le code, puis ensuite utiliser `flake8` pour vérifier que le code reformaté respecte bien PEP 8.

    Un autre exemple ici, que nous avions utilisé lors de l'optimisation bayésienne pour LightGBM.

    La version du code est avant l'application de `astral/ty`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    from lightgbm.sklearn import LGBMClassifier
    from hyperopt import hp, tpe, fmin
    MODEL_SPECS = {
        "name": "LightGBM",
        "class": LGBMClassifier,
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
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    uvx black black_2.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ici, `black` a rajouté une ligne entre les importations de librairies et la variable `MODEL_SPECS`. De plus, un retour chariot a été appliqué à chaque clé/valeur du champ `override_schemas`, car la ligne des clés/valeurs dépassait les $79$ caractères.

    Avec l'argument `-l`, nous avons la possibilité d'ignorer la limitation des $79$ caractères par ligne pour augmenter à une plus grande taille.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    from lightgbm.sklearn import LGBMClassifier
    from hyperopt import hp, tpe, fmin

    MODEL_SPECS = {
        "name": "LightGBM",
        "class": LGBMClassifier,
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
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    uvx black  -l 120 black_2.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En pratique, les projets s'autorisent à outre-passer la limite des $79$ caractères par ligne (`E502`) et ignorent cette erreur.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Les deux en même temps à l'aide de Ruff

    Les temps changent avec l'arrivé de Astral sur la scène du développement python. En effet, après vous avoir introduit l'utilisation de UV pour les environnement virtuels de python, l'équipe avait commencé sur la scène de python à travers un outil qui s'appelle Ruff.

    Ruff en simple, c'est la fusion de flake8 et de black.

    Trois commandes à retenir :
    - `uvx ruff check` permet d'avoir le comportement d'un linteur, comme flake8
    - `uvx ruff check --fix` permet de corriger les erreurs qui sont trouvé à l'aide de `check`
    - `uvx ruff format` permet de corriger le fichier au niveau de la norme PEP8.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pour aller plus loin : `ty` de Astral

    `ty` est tout nouveau, il a pour rôle de vérifier strictement le typage de vos variables ainsi que vos méthodes. Elle vous sera très utile lorsque vous attaquerez la partie de FastAPI, plus tard dans le cours.

    Par analogie, vous pouvez considérer que `astral/ty` est l'équivalent d'un `gcc -Wall`

    Dès maintenant, nous vous recommendons très fortement à utiliser l'association de `astral/ruff` et `astral/ty` en plus de de `astral/uv`.

    Elle seront très prochainement le nouveau standard côté OPS, si les tests en entreprise sont concluantes. Vous serez parmis les premiers à les utiliser sans formation supplémentaire !

    Point d'attention pour les entreprise qui pratiquent les package intermédiaires. C'est à dire que certains paquets de la bibliothèque sont copiés en interne pour des raisons de sécurités. (Notament aux applications et environnements interne qui ne doit jamais accéder à internet !)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La nouvelle version de notre modèle doit être typé, et le meilleur moyen de le typer est l'utilisation d'un ModelSpec associé à un type.
    """)
    return


@app.cell
def _(Any, Callable, LGBMClassifier, TypedDict, hp):
    class ModelSpec(TypedDict, total=True):
        name: str
        model_class: Callable[..., Any]  # Covers LGBMClassifier()
        params: dict[str, Any]  # Accepts hp.uniform etc.
        override_schemas: dict[str, type]


    # Type the MODELS list
    MODELS: list[ModelSpec] = [
        {
            "name": "LightGBM",
            "model_class": LGBMClassifier,
            "params": {
                "objective": "binary",
                "verbose": -1,
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
                "num_leaves": int,
                "min_child_samples": int,
                "max_depth": int,
                "num_iterations": int,
            },
        }
    ]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✔️ Conclusion

    Maintenant, plus aucune raison de ne pas coder proprement !

    - Nous avons vu la norme PEP 8 et pourquoi il est important de la respecter.
    - Nous avons vu comment vérifier si un code Python vérifiait les recommandations PEP 8 avec `flake8`.
    - Nous sommes capable de refactoriser automatiquement un code avec `black`.

    > ➡️ La prochaine étape, c'est de <b>tester son code et son modèle</b> pour s'assurer que tout fonctionne, aussi bien le code source que le modèle.
    """)
    return


if __name__ == "__main__":
    app.run()
