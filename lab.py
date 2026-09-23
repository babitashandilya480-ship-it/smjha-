"""Offline from-scratch engineering lab, never a student response provider.

Run: python -m training.lab --device cpu --steps 30
Uses Raschka's GPT architecture and a small hardware backward check inspired
by Hector Hernandez's lab. No corpus/model/network downloads are performed.
"""
import argparse
import hashlib
import json
import math
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from .data import ByteWindows, encode, decode
from .model import GPTModel, generate_text_simple

CONFIG = dict(vocab_size=256, context_length=32, emb_dim=64, n_heads=4, n_layers=2, drop_rate=0.0, qkv_bias=False)

def hardware_check(device):
    # A real forward/backward step catches broken kernels that availability
    # checks miss. Keep this small for the laptop, unlike a large benchmark.
    x = torch.randn(16,16,device=device,requires_grad=True)
    loss = (x @ torch.eye(16,device=device)).square().mean()
    loss.backward()
    if not torch.isfinite(loss) or not torch.isfinite(x.grad).all():
        raise RuntimeError("Hardware forward/backward check failed")
    return {"device": str(device), "torch": torch.__version__, "python": platform.python_version(),
            "name": torch.cuda.get_device_name(device) if device.type == "cuda" else platform.processor(),
            "backward_pass": True}

def evaluate(model, loader, device):
    model.eval()
    total = count = 0
    with torch.no_grad():
        for x,y in loader:
            logits = model(x.to(device))
            total += torch.nn.functional.cross_entropy(logits.flatten(0,1),y.to(device).flatten(),reduction="sum").item()
            count += y.numel()
    return total/count

def train(steps=30, device_name="cpu", out=None, train_path=None, validation_path=None):
    if not 1 <= steps <= 10000:
        raise ValueError("steps must be between 1 and 10000")
    root=Path(__file__).resolve().parent
    train_path=Path(train_path) if train_path else root/"corpus/train.txt"
    validation_path=Path(validation_path) if validation_path else root/"corpus/validation.txt"
    train_text=train_path.read_text(encoding="utf-8")
    val_text=validation_path.read_text(encoding="utf-8")
    if train_path.resolve()==validation_path.resolve():
        raise ValueError("Training and validation must be separate files")
    train_lines={line.strip() for line in train_text.splitlines() if line.strip()}
    val_lines={line.strip() for line in val_text.splitlines() if line.strip()}
    if train_lines & val_lines:
        raise ValueError("Exact duplicate lines across training and validation")
    train_set=ByteWindows(train_text,CONFIG["context_length"])
    val_set=ByteWindows(val_text,CONFIG["context_length"])
    if device_name=="auto":
        device_name="cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    device=torch.device(device_name)
    torch.set_num_threads(2)
    torch.manual_seed(42)
    hardware=hardware_check(device)
    model=GPTModel(CONFIG).to(device)
    optimizer=torch.optim.AdamW(model.parameters(),lr=0.002,weight_decay=0.01)
    train_loader=DataLoader(train_set,batch_size=4,shuffle=True,generator=torch.Generator().manual_seed(42))
    evaluation_loader=DataLoader(train_set,batch_size=4)
    val_loader=DataLoader(val_set,batch_size=4)
    out=Path(out) if out else root.parent/"artifacts"/("scratch-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    out.mkdir(parents=True,exist_ok=False)
    initial=evaluate(model,evaluation_loader,device)
    initial_val=evaluate(model,val_loader,device)
    losses=[]
    iterator=iter(train_loader)
    start=time.perf_counter()
    for step in range(steps):
        try: x,y=next(iterator)
        except StopIteration:
            iterator=iter(train_loader);x,y=next(iterator)
        model.train()
        optimizer.zero_grad(set_to_none=True)
        loss=torch.nn.functional.cross_entropy(model(x.to(device)).flatten(0,1),y.to(device).flatten())
        if not torch.isfinite(loss): raise RuntimeError("Non-finite training loss")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0,error_if_nonfinite=True)
        optimizer.step()
        losses.append(loss.item())
    final=evaluate(model,evaluation_loader,device)
    validation=evaluate(model,val_loader,device)
    if not all(math.isfinite(v) for v in (initial,initial_val,final,validation)):
        raise RuntimeError("Non-finite evaluation")
    model.eval()
    seed=torch.tensor([encode("Force ")],device=device)
    generated=generate_text_simple(model,seed,24,CONFIG["context_length"])
    checkpoint=out/"checkpoint.pt"
    temporary=out/"checkpoint.tmp"
    torch.save({"config":CONFIG,"model":model.state_dict(),"steps":steps,"tokenizer":"utf8-bytes-v1"},temporary)
    temporary.replace(checkpoint)
    loaded=torch.load(checkpoint,map_location=device,weights_only=True)
    restored=GPTModel(loaded["config"]).to(device)
    restored.load_state_dict(loaded["model"]);restored.eval()
    with torch.no_grad():
        torch.testing.assert_close(model(seed),restored(seed),rtol=0,atol=0)
    report={"status":"smoke_complete","student_ready":False,"started_from":"random weights", "hardware":hardware,
            "config":CONFIG,"steps":steps,"seed":42,"parameters":sum(p.numel() for p in model.parameters()),
            "initial_train_loss":initial,"final_train_loss":final,"initial_validation_loss":initial_val,
            "validation_loss":validation,"training_losses":losses,"checkpoint_reload_verified":True,
            "elapsed_seconds":round(time.perf_counter()-start,3),"sample_unvalidated":decode(generated[0].tolist()),
            "train_sha256":hashlib.sha256(train_text.encode()).hexdigest(),"validation_sha256":hashlib.sha256(val_text.encode()).hexdigest(),
            "limitations":"Tiny original demonstration corpus; shared physics domain; no duplicate lines, but not a quality benchmark. No chat fine-tuning or Qwen weight merging.",
            "created_at":datetime.now(timezone.utc).isoformat()}
    (out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    run_record={"report":str(out/"report.json"),"steps":steps,"device":str(device),"validation_loss":validation,"created_at":report["created_at"]}
    log=root.parent/"artifacts/training-runs.jsonl"
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open("a",encoding="utf-8") as f: f.write(json.dumps(run_record)+"\n")
    return report,out

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps",type=int,default=30)
    parser.add_argument("--device",choices=["cpu","cuda","mps","auto"],default="cpu")
    parser.add_argument("--out")
    parser.add_argument("--train",dest="train_path")
    parser.add_argument("--validation",dest="validation_path")
    args=parser.parse_args()
    report,out=train(args.steps,args.device,args.out,args.train_path,args.validation_path)
    print(json.dumps({"report":str(out/"report.json"),"status":report["status"],"train_loss":report["final_train_loss"],"validation_loss":report["validation_loss"]},indent=2))
