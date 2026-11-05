import argparse
import os
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from huggingface_hub import snapshot_download
import streamlit as st

def read_setting():
    load_dotenv()
    settings = {}
    for key in ('HF_MODEL_ID','MODEL_DIR'):
        value = os.getenv(key)
        settings[key] = value
    model_dir = Path(settings['MODEL_DIR']).expanduser()  # 상대경로
    # 모델경로는 main.py가 있는 폴더를 기준으로
    if not model_dir.is_absolute():
        model_dir = Path(__file__).resolve().parent / model_dir
    return settings['HF_MODEL_ID'], model_dir.resolve()

def download_model(model_id, model_dir):
    # 공개 모델의 필요한 파일만 다운로드 ONNX등 다른형식은 받지 않는다
    snapshot_download(
        repo_id=model_id,
        local_dir=str(model_dir),
        allow_patterns=[  # 모델구조 생성설정 토크나이저 가중치 이용조건만 받는다
            "config.json", "generation_config.json", "tokenizer*.json",
            "vocab.json", "merges.txt", "*.safetensors", "README.md", "LICENSE*",
        ]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command', nargs="?", default='app', choices=['download','app']
    )
    args = parser.parse_args()
    try:
        model_id, model_dir = read_setting()
        print(model_id,model_dir)
    except ValueError as err:
        parser.error(str(err))

if __name__ =="__main__":
    main()