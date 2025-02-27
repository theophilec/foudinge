# Foudinge: Mapping the French Culinary Universe

Mapping the [network](https://ouestware.gitlab.io/retina/1.0.0-beta.4/#/graph/?url=https%3A%2F%2Fgist.githubusercontent.com%2Ftheophilec%2F351f17ece36477bc48438d5ec6d14b5a%2Fraw%2Ffa85a89541c953e8f00d6774fe42f8c4bd30fa47%2Fgraph.gexf&r=x&sa=re&ca[]=t&ca[]=ra-s&st[]=u&st[]=re&ed=u) of French restaurants and chefs from the [lefooding.com](https://lefooding.com) guide.

The data comes from lefooding.com, gpt40-mini is used with [outlines](https://github.com/dottxtai/outlines) for structured output extraction. The graph is built with [Gephi-lite] and shared via [Retina]().

## Usage

```bash
# Collect data from lefooding.com
uv run get_data.py

# Extract entities from reviews
uv run infer_entities.py

# Generate the graph
uv run make_graph.py
```

## Requirements

- Outlines
- NetworkX
- SQLite3
- BeautifulSoup4
- aiohttp
- An OpenAI API key (for GPT-4o Mini) or a local model

## Blog

Read more about the project in the [blog post](coming soon).

## License

MIT
