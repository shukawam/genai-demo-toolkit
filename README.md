# genai-demo-toolkit

## How to use(adb)

本リポジトリをクローンします。

```sh
git clone https://github.com/shukawam/genai-demo-toolkit.git
```

仮想環境を作成し、有効化します。

```sh
cd genai-demo-toolkit
python3 -m venv .venv
source .venv/bin/activate
```

必要なライブラリをダウンロードします。

```sh
pip install -r requirements.txt
```

[setup-adb-demo.ipynb](https://github.com/shukawam/genai-demo-toolkit/notebook/setup-adb-demo.ipynb) を実行し、ベクトルデータベースをセットアップします。

アプリケーションを起動します。

```sh
cd app
streamlit run adb.py
```

`http://localhost:8501` へアクセスします。
