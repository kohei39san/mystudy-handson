# 概要

JMeterの実行方法について記載します。

# 各オプションの説明

## -n

JMeterをCLIにて実行します。パフォーマンスの面からCLIにてシナリオの実行が推奨されています。
GUIモードはテスト用やシナリオファイルの作成時などに用います。

## -l

リクエストの結果を出力するログファイル名を指定します。

## -j

JMeterの実行ログを出力するログファイル名を指定します。

# JMeterの実行例

以下のようにシナリオファイルを用いてJMeterを実行することができます。

```
$ jmeter -n -t /tmp/mystudy-handson/k8s-manifests/make-jmeter-scenario/scenarios/single_sampler.xml -l /tmp/sample.log -j /tmp/jmeter.log
```

また、長時間負荷をかける際には以下のようにバックグラウンドで実行することを検討します。

```
$ nohup jmeter -n -t /tmp/mystudy-handson/k8s-manifests/make-jmeter-scenario/scenarios/single_sampler.xml -l /tmp/sample.log -j /tmp/jmeter.log &> /tmp/nohup.out &
```

# シナリオファイル例

以下のシナリオファイルを用意しました。

## single_sampler.xml

単一のリクエストを複数回実行するシナリオファイルです。
リクエストを送るホスト名として同一インスタンスで稼働しているものを指定できます。
以下のコマンドなどでホスト名を確認できます。

```
$ kubectl get ing
```

## multi_sampler.xml

複数のホストに複数種類のリクエストを実行するシナリオファイルです。
用途、負荷量に応じて編集してください。スレッド数を増やすほどJMeter実行に必要なリソースが増えていきます。

# 参考ドキュメント

JMeter公式ドキュメント
https://jmeter.apache.org/usermanual/get-started.html
