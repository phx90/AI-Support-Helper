import json, os, sys, urllib.request
from pathlib import Path
API=os.getenv("API_URL","http://localhost:8000/api/v1")
def call(path,payload):
    req=urllib.request.Request(API+path,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}); return json.loads(urllib.request.urlopen(req).read())
questions=json.loads((Path(__file__).parents[1]/"evaluation/questions.json").read_text())
hits=sources=coverage=0
for item in questions:
    result=call("/chat",{"question":item["question"]}); names=[s["document"] for s in result["sources"]]; hit=item["expected_source"] in names; hits+=hit; sources+=hit; lower=result["answer"].lower(); coverage+=sum(k.lower() in lower for k in item["expected_keywords"])/len(item["expected_keywords"])
count=len(questions); print(json.dumps({"questions":count,"retrieval_hit_rate":round(hits/count,3),"source_accuracy":round(sources/count,3),"answer_keyword_coverage":round(coverage/count,3)},indent=2))
sys.exit(0 if hits==count else 1)