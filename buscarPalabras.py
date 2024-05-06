import spacy
import csv
import re
import sys
from elasticsearch import Elasticsearch



def chooseWord():
  key = input('Palabra a buscar: ')

  doc = nlp(key)
  docLength = len(doc)
  if (docLength > 1):
    print("\n>>WARNING: solo se buscará la primera palabra<<\n")

  return (doc[0].text) #retornamos la primera palabra

def choosePOS():
  posTable = [
    ("ADJ", "adjetivo"), ("ADP", "adposición"), ("ADV", "adverbio"),
    ("AUX", "verbo auxiliar"), ("CONJ", "conjunción"),
    ("CCONJ", "conjunción coordinante"), ("DET", "determinante"),
    ("INTJ", "interjección"), ("NOUN", "sustantivo"),
    ("NUM", "numeral"), ("PART", "partícula"),
    ("PRON", "pronombre"), ("PROPN", "nombre propio"),
    ("SCONJ", "conjunción subordinante"), ("VERB", "verbo")]
  printPosTable(posTable)

  try:
    posIndex = int(input('Usando los números de la izquierda, seleccione el tipo de palabra que digitará:\n '))
  except Exception as e:
    print("ERROR: debe digitar un número válido")
  else:
    if (posIndex < 1 or posIndex > 15):
      print("ERROR: el numero debe estar entre 1 y 15")
      raise Exception("Num fuera del rango")
  pos = posTable[posIndex-1][0]
  return pos

def printPosTable(table):

  print("{:<6} {:<20}".format("Num", "Parte de la oracion"))
  print("=" * 50)

  for num, (abbrev, pos) in enumerate(table, start=1):
    print("{:<6} {:<20}".format(num, pos))

def setLemma(word):
  doc = nlp(word)
  lemma = doc[0].lemma_
  
  print("\nla lematización detectada para esta palabra es {}".format(lemma))
  respuesta = input("¿Está correcta? (y/n): ")

  if (respuesta != "y" and respuesta != "Y"):
        lemma = input("\nEspecificar lematización correcta: ")

  print("\nIMPORTANTE: La lematización seleccionada ha sido {}".format(lemma))
  return lemma

def createQueryLemma(lemma, pos):
  print(lemma)
  print(pos)
  queryBody ={
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "word.lemma": lemma
          }
        },
        {
          "term": {
            "word.pos.keyword": pos
            }
         }
        ]
      }
    }
  }
  return queryBody

def createQueryNoLemma(word, pos):
  print(word)
  print(pos)
  queryBody ={
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "word.word": word
          }
        },
        {
          "term": {
            "word.pos.keyword": pos
            }
          }
        ]
      }
    }
  }
  return queryBody




def searchAndWrite(queryBody, pos):
  result = client.search(index="oraciones", body=queryBody, scroll = "5s")
  scroll_id = result["_scroll_id"]
  hits = result["hits"]["hits"]

    # Open a file in write mode
  with open("resultados.csv", "w") as f:
    # Process initial hits
    for hit in hits:
        # Write data to file
        f.write(f"\"{hit['_source'].get('book')}\",{hit['_source'].get('number')},\"{hit['_source'].get('sentence')}\" \n")

    # Scroll through remaining hits
    while True:
        scroll_response = client.scroll(scroll_id=scroll_id, scroll="1m")
        
        scroll_id = scroll_response["_scroll_id"]
        hits = scroll_response["hits"]["hits"]
        
        for hit in hits:
            f.write(f"\"{hit['_source'].get('book')}\",{hit['_source'].get('number')},\"{hit['_source'].get('sentence')}\"\n")
        
        # Check if there are no more hits
        if not hits:
            break 
    print("Se retornaron ", result['hits']['total']['value'], " oraciones")


client = Elasticsearch("http://localhost:9200")
nlp = spacy.load("es_dep_news_trf")
pos = choosePOS()
word = chooseWord()
wantLemma = input("¿Desea Lematizar? (y/n): ")
if (wantLemma == "y" or wantLemma == "Y"):
   lemma = setLemma(word)
   query = createQueryLemma(lemma, pos)
else:
   query = createQueryNoLemma(word, pos)
   

searchAndWrite(query, pos)
