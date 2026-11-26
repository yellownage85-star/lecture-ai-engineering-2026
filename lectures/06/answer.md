# 第6回 解答

## 演習

- STEP 1 のツールの名前：`glossary_search_glossary`
- STEP 2 の [tool call]：

  `[tool call]   glossary_search_glossary({'query': '3レベル'})`

- STEP 3 の [tool call]：

  `[tool call]   fetch_fetch({'url': 'https://modelcontextprotocol.io/'})`

- STEP 4 の [tool call]：

  `[tool call]   aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要', 'topics': ['general']})`

  `[tool call]   aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'Using versioning in S3 buckets'})`

- 気づき・疑問：

  MCPを利用することで、エージェント本体のコードを書き換えずに外部ツールを追加できることを確認した。また、コマンドでローカルに起動するMCPサーバーと、URLで接続するリモートのMCPサーバーの違いを理解した。

  追加実験としてAWSのMCPサーバーを設定ファイルから削除し、利用可能なツールが減ることも確認した。AWSへの接続は確認済みだが、提出時の設定からは削除している。

## 宿題

- 取り組んだレベル：基礎・実装

- やったこと：

  基礎レベルでは、`app/mcp_server.py` に `get_lecture_summary` を登録した。

  実装レベルでは、`app/tools.py` に指定された講義回の用語クイズを生成する `make_quiz` 関数を新規作成し、MCPサーバーに登録した。該当する用語が存在しない場合には、その回のクイズが用意されていないことを返す処理を追加した。

- 結果：

  講義概要の取得：

  `[tool call]   glossary_get_lecture_summary({'lecture': 2})`

  正常なクイズ生成：

  `[tool call]   glossary_make_quiz({'lecture': 2})`

  第2回の用語集から事前学習についてのクイズが生成され、LLMの回答本文では正解を提示せずに出題できた。

  範囲外の入力：

  `[tool call]   glossary_make_quiz({'lecture': 99})`

  `[tool return] glossary_make_quiz -> 第99回のクイズは用意されていません。`

  最終テスト：21 passed in 4.08s

- 気づき・疑問：

  エージェント本体を変更しなくても、MCPサーバーにツールを登録するだけでLLMが新しい機能を認識し、適切な引数を指定して使用できることを確認した。

  追加実験として、ツールのdocstringとエージェント本体の指示文を変更し、ツールの利用条件を変える実験を行った。docstringのみの変更では挙動が変わらなかったが、エージェント本体に明確な禁止指示を追加するとツールが使用されなくなった。さらに、ユーザーの質問文を変更して利用条件を満たすと、再びツールが使用された。実験後、指示文とdocstringは元に戻した。

  自然言語による指示と、プログラムコードによる強制的な制御は異なることを理解した。

  また、範囲外の入力に対してツールが正確な結果を返しても、LLMが未確認の情報を回答に付け加える場合があることを確認した。ツールの処理の正確性とLLMの回答の正確性は、分けて評価する必要があると感じた。

  今後は、モデルの違いや事後学習、エージェントの設計が、指示追従能力にどの程度影響するのかについても理解を深めたい。