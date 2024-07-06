# genai-demo-toolkit

## How to use

仮想環境を作成し、有効化します。

```sh
python3 -m venv .venv
source .venv/bin/activate
```

必要なライブラリをダウンロードします。

```sh
pip install -r requirements.txt
```

[setup-demo.ipynb](https://github.com/shukawam/genai-demo-toolkit/notebook/setup-demo.ipynb) を実行し、ベクトルデータベースをセットアップします。

アプリケーションを起動します。

```sh
cd app
streamlit run main.py
```

`http://localhost:8501` へアクセスします。