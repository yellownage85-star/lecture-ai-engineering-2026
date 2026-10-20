"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --chat     # 会話履歴を保って質問を続ける

単発実行はツールも会話履歴も持たない「素の」呼び出し。
--chat を指定すると、同じ起動中は会話履歴を保つ。
回答とともに、入力トークン数と出力トークン数を表示する。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def _print_response(response) -> str:
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else None
    output_tokens = usage.candidates_token_count if usage else None
    print(f"[入力トークン数] {input_tokens if input_tokens is not None else '不明'}")
    print(f"[出力トークン数] {output_tokens if output_tokens is not None else '不明'}")
    return response.text


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)
    return _print_response(response)


def chat(initial_question: str | None = None) -> None:
    """会話履歴を保ちながら、終了操作まで質問を受け付ける。"""
    client = genai.Client(api_key=get_api_key())
    conversation = client.chats.create(model=MODEL)

    if initial_question:
        print(f"[質問] {initial_question}\n")
        print(_print_response(conversation.send_message(initial_question)))

    while True:
        try:
            question = input("[質問] > ").strip()
        except EOFError:
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        print(f"[質問] {question}\n")
        print(_print_response(conversation.send_message(question)))


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", help="質問（省略時は講座に固有の質問）")
    parser.add_argument(
        "--chat", action="store_true", help="会話履歴を保って質問を続ける"
    )
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        if args.chat:
            chat(args.question)
        else:
            question = args.question if args.question is not None else DEFAULT_QUESTION
            print(f"[質問] {question}\n")
            print(ask(question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
