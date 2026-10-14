# diplomat's hub*

App de estudos para a 1ª fase do CACD: flashcards, alternativas, Certo/Errado com curva do esquecimento, resumos em carrossel e clipping diário.

- Site: GitHub Pages, servindo a raiz do branch `main`.
- Progresso pessoal: Supabase (tabela `user_docs`, protegida por login).
- Conteúdo: arquivos JSON em `data/`, atualizados pelas tarefas automáticas do Claude.

## Formato dos dados

`data/decks/<slug>.json`, um por assunto:

```json
{"kind":"deck","materia":"Política Internacional","assunto":"Terrorismo","edital":"13.12","notionUrl":"…","updatedAt":"AAAA-MM-DD",
 "items":[...], "resumo":[...10 slides...]}
```

Itens:
- flashcard `{"id":"f1","t":"f","q":"…","a":"…","exp":"…"}`
- alternativas `{"id":"m1","t":"m","q":"…","opts":["certa","errada","errada","errada"],"ans":0,"exp":"…"}`
- Certo/Errado `{"id":"c1","t":"c","s":"…","ans":"C|E","exp":"…","trap":1-6,"ano":"2019","prova":"Q28 item 1","ctx":"…"}`

`resumo`: 10 slides. O 1º é `{"k":"capa","b":"…"}`, do 2º ao 9º são `{"t":"…","b":"…","l":["…"],"n":"…"}` e o 10º é `{"k":"fim","t":"Pegadinhas que caem","l":["…"]}`.

`data/news/AAAA-MM-DD.json`:

```json
{"kind":"news","date":"AAAA-MM-DD","cards":[{"id":"AAAA-MM-DD-1","materia":"…","edital":"…","titulo":"…","resumo":"…","porque":"…",
  "fonte":"…","url":"…","img":"URL original da imagem (og:image ou Wikimedia)","imgCredit":"…","curso":false,
  "ce":{"s":"…","ans":"C|E","exp":"…"}}]}
```

Nunca mude o `id` de itens nem de cards já publicados: o progresso, as notícias salvas e os comentários ficam presos a eles.

Depois de qualquer mudança em `data/`, rode `python3 tools/build_index.py` e faça o commit.

## Petit Journal (podcast)
`python3 tools/petit.py /tmp/pj` baixa e transcreve (faster-whisper, modelo base, ~4 min por episódio) os episódios novos do feed
https://www.spreaker.com/show/5659715/episodes/feed. A transcrição fica fora do repo. No clipping do dia entra um card com
`podcast` (rótulo), `pj_guid`, `topicos: [{t, b}]` escritos com palavras próprias, `porque`, `ce` e `url` do episódio.
