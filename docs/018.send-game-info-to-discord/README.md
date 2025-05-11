# 仮想環境のセットアップ方法

## 仮想環境の作成

プロジェクトのルートディレクトリに移動し、以下のコマンドを実行して仮想環境を作成します。仮想環境の名前は変数として指定します。

```powershell
$envName = "venv"
python -m venv $envName
```

## 仮想環境のアクティベート

### Windowsの場合 (PowerShell)
以下のコマンドを実行して仮想環境をアクティベートします。

```powershell
$envName = "venv"
Powershell -ExecutionPolicy ByPass -c ".\$envName\Scripts\Activate.ps1"  
```

### Linux/Macの場合
以下のコマンドを実行して仮想環境をアクティベートします。

```bash
source venv/bin/activate
```

## 仮想環境のディアクティベート
仮想環境の使用を終了する場合は、以下のコマンドを実行します。

```powershell
deactivate
```

## パッケージの管理

### インストール済みパッケージの書き出し
以下のコマンドで仮想環境にインストールされているパッケージを`requirements.txt`に書き出します。

```powershell
pip freeze > requirements.txt
```

### パッケージの一括インストール
以下のコマンドで`requirements.txt`に記載されたパッケージを一括インストールします。

```powershell
pip install -r requirements.txt
```

### 開発用パッケージの管理
開発用と本番用でパッケージを分けたい場合は、`requirements-dev.txt`を作成し、以下のように記述します。

```text
-r requirements.txt
black==23.3.0
flake8==6.0.0
```

その後、以下のコマンドで両方のパッケージをインストールできます。

```powershell
pip install -r requirements-dev.txt
```

## VSCodeで仮想環境を使用する方法

作成した仮想環境をVSCodeで使用するには、以下の手順を実行してください。

1. VSCodeでプロジェクトフォルダを開きます。
2. 左下のステータスバーに表示されているPythonのバージョンをクリックします。
3. 表示されたコマンドパレットで「Python: Select Interpreter」を選択します。
4. 仮想環境のパスを選択します。
   - 仮想環境がプロジェクト直下にある場合、`./venv`のようなパスが表示されます。
5. 選択後、右下のステータスバーに仮想環境名が表示されていれば設定完了です。

これで、VSCode内で仮想環境が有効になり、仮想環境内のPythonやパッケージが使用されるようになります。
