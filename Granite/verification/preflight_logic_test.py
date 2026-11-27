import json, time, types, torch, ast
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM
nb=json.load(open("granite_run/0_Notebook_00p_Preflight/Notebook 00p Granite fp16 preflight.ipynb"))
for i in (1,2): ast.parse("".join(nb["cells"][i]["source"]))
print("preflight cells parse OK")
tok=AutoTokenizer.from_pretrained("tok"); cfg=AutoConfig.from_pretrained("tok")
cfg.num_hidden_layers=2; cfg.hidden_size=128; cfg.num_attention_heads=4; cfg.num_key_value_heads=2; cfg.intermediate_size=256
torch.manual_seed(0); model=AutoModelForCausalLM.from_config(cfg).to(torch.float32).eval()
torch.cuda.synchronize=lambda *a,**k:None
torch.cuda.max_memory_allocated=lambda i:11*2**30; torch.cuda.max_memory_reserved=lambda i:int(float(__import__("os").environ.get("RES","11"))*2**30)
class _P: total_memory=int(14.56*2**30)
torch.cuda.get_device_properties=lambda i:_P()
g={"tokenizer":tok,"model":model,"input_device":torch.device("cpu"),"LOAD_SECONDS":0.0,"MAX_INPUT_TOKENS":5376,"MAX_NEW_TOKENS_PROBE":24,"json":json,"time":time,"torch":torch,"model_config":__import__("types").SimpleNamespace(num_key_value_heads=8,hidden_size=4096,num_attention_heads=32),"device_map":{**{f"model.layers.{i}":"0" for i in range(30)},**{f"model.layers.{i}":"1" for i in range(30,40)}}}
exec("".join(nb["cells"][2]["source"]), g)
