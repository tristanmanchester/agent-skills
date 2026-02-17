# Exa Search — quickstart snippets

## Python (SDK)

Install:

```bash
pip install exa-py
```

Use:

```python
from exa_py import Exa

exa = Exa(api_key="YOUR_EXA_API_KEY")
res = exa.search_and_contents(
    "blog post about artificial intelligence",
    type="auto",
    num_results=5,
    text=True,
)
print(res)
```

## JavaScript (SDK)

Install:

```bash
npm install exa-js
```

Use:

```js
import Exa from 'exa-js';

const exa = new Exa(process.env.EXA_API_KEY);
const res = await exa.searchAndContents('blog post about artificial intelligence', {
  type: 'auto',
  numResults: 5,
  contents: { text: true },
});
console.log(res);
```

## cURL

```bash
curl --request POST \
  --url https://api.exa.ai/search \
  --header "accept: application/json" \
  --header "content-type: application/json" \
  --header "x-api-key: $EXA_API_KEY" \
  --data '{
    "query": "blog post about artificial intelligence",
    "type": "auto",
    "contents": { "text": true }
  }'
```
