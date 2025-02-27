from outlines import generate, models

from data_model import KnowledgeGraph, prompt_template


schema = KnowledgeGraph.model_json_schema()

model = models.mlxlm("mlx-community/Meta-Llama-3.1-8B-Instruct-8bit")


text = "À l’enseigne de Grenat, Antoine Joannier et Neil Mahatsry ont le rouge aux joues et aux murs. Après avoir officié à La Brasserie Communale, où ils se sont rencontrés, les deux compères font désormais feu de tout bois en plein centre de Marseille, où Antoine veille au grain autour des tables en bois blond, convoyant les plats que Neil embrase à tout-va depuis l’âtre derrière le comptoir. Des huîtres aux pièces viandardes, en passant par la verdure et le poisson, tout y flambe, fume, grille, cuit à l’étouffée ou se voit marqué au fer à repasser brocanté. Dans nos assiettes ce midi-là, une marinière de moules et palourdes à la flamme, dopée par un bouillon de bœuf et de la ‘nduja, suivie d’un torride tentacule de poulpe accompagné de chou frisé grillé et d’une tapenade d’olives de Kalamata fumée… Même les desserts y passent, comme cette glace au lait fermenté et encore fumé, flanquée d’une ganache au chocolat blanc caramélisée et toppée d’un granola aux noix. Du mercredi au vendredi soir, le ton et les prix montent d’un cran pour faire place au menu en huit temps."
generator = generate.json(model, KnowledgeGraph)
prompt = prompt_template(text, schema)
response = generator(prompt)
print(response.nodes)
print(response.edges)
