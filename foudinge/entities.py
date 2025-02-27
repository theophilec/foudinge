from enum import Enum
from pydantic import BaseModel, ConfigDict


class Role(str, Enum):
    model_config = ConfigDict(extra="forbid")  # required for openai
    CHEF = "Chef"
    SOMMELIER = "Sommelier"
    SERVEUR = "Serveur"
    PROPRIETAIRE = "Propriétaire"
    FOURNISSEUR = "Fournisseur"


class Person(BaseModel):
    model_config = ConfigDict(extra="forbid")  # required for openai
    name: str
    role: Role
    previous_restaurants: list[str]


class Summary(BaseModel):
    model_config = ConfigDict(extra="forbid")  # required for openai
    people: list[Person]


def prompt_template(text, schema):
    return f"""
    Tu es un expert gastronomique basé sur l'IA. Tu es chargé d'extraire les informations suivantes de manière structurée d'une critique de restaurant.

    Pour chaque personne impliquée dans le restaurant, indique:

    1. Son nom, dans le champ "name".

    2. Son rôle, dans le champ "role". Choisis parmi les options suivantes : "Chef" (ceux qui cuisinent), "Sommelier" (ceux qui s'occupent des boissons), "Serveur" (ceux qui servent en salle), "Propriétaire" (propriétaire ou patron du restaurant), "Fournisseur" (ceux qui fournissent les produits : légumes, fruits, viandes, poissons, fruits de mer...) Attention, tous les rôles peuvent être tenus par un homme ou une femme.

    3. Les noms des restaurants dans lesquels il a travaillé précédemment, dans le champ "previous_restaurants" sous la forme d'une liste. Si aucun restaurant précédent n'est mentionné, n'inclus pas le champ. N'inclus pas d'information sur la localisation de ces restaurants.

    Attention à ne mentionner que des personnes impliquées dans le restaurant et pas des personnes mentionnées dans la critique (des célébrités, ...).

    Attention à n'inclure que les personnes présentes dans la critique. N'invente pas de personne fictive ni de placeholder ("anonyme", "personne fictive", ...).

    Texte de la critique à résumer :
        {text}

    N'inclut que les résultats aucune autre information ou explication.

    Ta réponse doit être structurée dans un format JSON valide:
        {schema}
    """
