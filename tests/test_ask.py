from unittest.mock import Mock

import pytest
from google.genai import types

from app.ask import ask, chat
from app.config import MODEL


@pytest.mark.parametrize(
    ("usage", "input_tokens", "output_tokens"),
    [
        (
            types.GenerateContentResponseUsageMetadata(
                prompt_token_count=12, candidates_token_count=34
            ),
            "12",
            "34",
        ),
        (
            types.GenerateContentResponseUsageMetadata(
                prompt_token_count=0, candidates_token_count=0
            ),
            "0",
            "0",
        ),
        (None, "不明", "不明"),
        (types.GenerateContentResponseUsageMetadata(prompt_token_count=12), "12", "不明"),
    ],
)
def test_ask_displays_token_counts(monkeypatch, capsys, usage, input_tokens, output_tokens):
    response = types.GenerateContentResponse(
        candidates=[
            types.Candidate(content=types.Content(parts=[types.Part(text="回答")]))
        ],
        usage_metadata=usage,
    )
    client = Mock()
    client.models.generate_content.return_value = response
    client_factory = Mock(return_value=client)
    monkeypatch.setattr("app.ask.genai.Client", client_factory)
    monkeypatch.setattr("app.ask.get_api_key", lambda: "test-key")

    assert ask("質問") == "回答"
    assert capsys.readouterr().out == (
        f"[入力トークン数] {input_tokens}\n[出力トークン数] {output_tokens}\n"
    )
    client_factory.assert_called_once_with(api_key="test-key")
    client.models.generate_content.assert_called_once_with(model=MODEL, contents="質問")


def test_chat_preserves_history_and_displays_each_response(monkeypatch, capsys):
    responses = [
        types.GenerateContentResponse(
            candidates=[
                types.Candidate(content=types.Content(parts=[types.Part(text="回答1")]))
            ],
            usage_metadata=types.GenerateContentResponseUsageMetadata(
                prompt_token_count=12, candidates_token_count=34
            ),
        ),
        types.GenerateContentResponse(
            candidates=[
                types.Candidate(content=types.Content(parts=[types.Part(text="回答2")]))
            ],
            usage_metadata=types.GenerateContentResponseUsageMetadata(
                prompt_token_count=56, candidates_token_count=78
            ),
        ),
    ]
    conversation = Mock()
    conversation.send_message.side_effect = responses
    client = Mock()
    client.chats.create.return_value = conversation
    client_factory = Mock(return_value=client)
    monkeypatch.setattr("app.ask.genai.Client", client_factory)
    monkeypatch.setattr("app.ask.get_api_key", lambda: "test-key")
    prompts = iter(["質問2", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))

    chat("質問1")

    client_factory.assert_called_once_with(api_key="test-key")
    client.chats.create.assert_called_once_with(model=MODEL)
    assert [call.args[0] for call in conversation.send_message.call_args_list] == [
        "質問1",
        "質問2",
    ]
    assert capsys.readouterr().out == (
        f"[質問] 質問1\n\n"
        f"[入力トークン数] 12\n[出力トークン数] 34\n回答1\n"
        f"[質問] 質問2\n\n"
        f"[入力トークン数] 56\n[出力トークン数] 78\n回答2\n"
    )


def test_chat_exits_on_eof(monkeypatch):
    client = Mock()
    monkeypatch.setattr("app.ask.genai.Client", Mock(return_value=client))
    monkeypatch.setattr("app.ask.get_api_key", lambda: "test-key")
    monkeypatch.setattr("builtins.input", Mock(side_effect=EOFError))

    chat()

    client.chats.create.assert_called_once_with(model=MODEL)
