from flask import Flask, render_template, url_for, request
import pandas as pd
import os
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser, OrGroup
#import pandas as pd
from janome.tokenizer import Tokenizer

app = Flask(__name__)

@app.route('/')
def index():
  search_field = request.args.get('search')
  text = request.args.get('word')
  if text == None:
      text = ""
  else:
      pass
#  text = "大学"

  schema = Schema(title=TEXT(stored=True), content=TEXT, url=STORED, created_at=STORED, inn=STORED, out=STORED)
  ix = open_dir('daigo_search_dir')

  t = Tokenizer()
  str_output = ""
  for token in t.tokenize(text):
    str_output += token.surface + " "


  with ix.searcher() as searcher:

      query_ = QueryParser("content", ix.schema)
      query = query_.parse(str_output)
      results = searcher.search(query)
      if int(results.estimated_length())>2:
          pass
      else:
          query = QueryParser("content", ix.schema, group=OrGroup).parse(str_output) # OR検索へ
          results = searcher.search(query)

      titles = []
      timestamps = []
      urls = []

      oldr =""
      for r in results:
          if r != oldr:
              titles.append(r['title'])
              timestamps.append(r['inn']+"～"+r["out"])
              urls.append(r["url"])
          oldr = r

      df = pd.DataFrame(columns=['動画タイトル', 'URL','この辺りかも'])
      df["動画タイトル"] = titles
      df["この辺りかも"] = timestamps
      df["URL"] = urls

  return render_template('search.html',word=text, search_result=df.to_html(classes='books',index=False,justify="center"))
#  return render_template('index.html',word=text, search_result=df.to_html(classes='books',index=False,justify="center"))

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
  #app.run(debug=True, host='0.0.0.0', port=5000)
