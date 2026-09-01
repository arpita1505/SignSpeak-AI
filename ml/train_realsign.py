#!/usr/bin/env python3
"""Select on validation data and evaluate once on held-out RealSign test data."""
from __future__ import annotations
import argparse, json, logging, time
from datetime import datetime, timezone
from pathlib import Path
import joblib, numpy as np, sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"); log=logging.getLogger(__name__); SEED=42
def metrics(y,p): return {"accuracy":float(accuracy_score(y,p)),"precision_macro":float(precision_score(y,p,average="macro",zero_division=0)),"recall_macro":float(recall_score(y,p,average="macro",zero_division=0)),"macro_f1":float(f1_score(y,p,average="macro",zero_division=0)),"weighted_f1":float(f1_score(y,p,average="weighted",zero_division=0))}
def train(processed:Path,artifacts:Path,reports:Path):
    data={f"{k}_{s}":np.load(processed/f"{k}_{s}.npy") for s in ("train","val","test") for k in ("X","y")}; dm=json.loads((processed/"metadata.json").read_text())
    candidates={"RandomForestClassifier":Pipeline([("classifier",RandomForestClassifier(n_estimators=300,class_weight="balanced",n_jobs=-1,random_state=SEED))]),"SVC":Pipeline([("scaler",StandardScaler()),("classifier",SVC(C=10,kernel="rbf",probability=True,class_weight="balanced",random_state=SEED))])}
    fitted={}; validation={}; training_times={}
    for name,model in candidates.items():
        log.info("Training %s",name); started=time.perf_counter(); model.fit(data["X_train"],data["y_train"]); training_times[name]=round(time.perf_counter()-started,3); validation[name]=metrics(data["y_val"],model.predict(data["X_val"])); fitted[name]=model; log.info("%s val macro F1 %.4f",name,validation[name]["macro_f1"])
    name=max(validation,key=lambda n:validation[n]["macro_f1"]); model=fitted[name]; pred=model.predict(data["X_test"]); test=metrics(data["y_test"],pred); labels=dm["labels"]
    artifacts.mkdir(parents=True,exist_ok=True); (reports/"metrics").mkdir(parents=True,exist_ok=True)
    joblib.dump(model,artifacts/"signspeak_model.joblib"); np.save(reports/"metrics"/"confusion_matrix.npy",confusion_matrix(data["y_test"],pred,labels=labels))
    (reports/"metrics"/"classification_report.json").write_text(json.dumps(classification_report(data["y_test"],pred,labels=labels,output_dict=True,zero_division=0),indent=2)); (reports/"metrics"/"metrics.json").write_text(json.dumps({"validation":validation,"test":test},indent=2))
    meta={"version":"1.0.0-realsign","created_at":datetime.now(timezone.utc).isoformat(),"dataset":"RealSign Indian Sign Language Dataset","dataset_source":"https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset","dataset_license":"CC0-1.0","classifier":name,"algorithm":name,"scikit_learn_version":sklearn.__version__,"feature_dimension":126,"supported_labels":labels,"feature_format":"21 x/y/z landmarks per hand; left then right; missing hand zero padded","normalization":dm["normalization"],"split_method":dm["split_method"],"split_counts":dm["splits"],"validation_metrics":validation,"training_times_seconds":training_times,"test_metrics":test,"metrics":test,"random_seed":SEED,"confidence_threshold":0.75}
    (artifacts/"model_metadata.json").write_text(json.dumps(meta,indent=2)); log.info("Selected %s; test macro F1 %.4f",name,test["macro_f1"]); return meta
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--processed",type=Path,default=Path("data/processed")); p.add_argument("--artifacts",type=Path,default=Path("artifacts")); p.add_argument("--reports",type=Path,default=Path("reports")); a=p.parse_args(); train(a.processed,a.artifacts,a.reports)
