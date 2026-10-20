from unittest.mock import Mock

import pytest
from google.genai import types

from app.ask import ask
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
