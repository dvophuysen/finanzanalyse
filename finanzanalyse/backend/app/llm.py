"""LLM-Provider-Abstraktion: Azure OpenAI / OpenAI / Anthropic / Ollama."""

from __future__ import annotations

import json
from typing import Any

import httpx

from .config import settings


class LLMClient:
    """Schmaler Client mit `complete_json(prompt, schema_hint)` und `chat(messages)`."""

    def __init__(self) -> None:
        self.provider = settings.llm_provider.lower()

    # --- Public API ---

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        """Liefert ein JSON-Objekt zurück. Bei Fehlern: leeres Dict."""
        text = self._raw_complete(system=system, user=user, json_mode=True)
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            start = text.find("{") if isinstance(text, str) else -1
            end = text.rfind("}") if isinstance(text, str) else -1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    return {}
            return {}

    def chat(self, system: str, user: str) -> str:
        return self._raw_complete(system=system, user=user, json_mode=False)

    # --- Provider-Implementierungen ---

    def _raw_complete(self, system: str, user: str, json_mode: bool) -> str:
        if self.provider == "azure":
            return self._azure(system, user, json_mode)
        if self.provider == "openai":
            return self._openai(system, user, json_mode)
        if self.provider == "anthropic":
            return self._anthropic(system, user, json_mode)
        if self.provider == "ollama":
            return self._ollama(system, user, json_mode)
        raise ValueError(f"Unbekannter LLM-Provider: {self.provider}")

    def _azure(self, system: str, user: str, json_mode: bool) -> str:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
        )
        kwargs: dict[str, Any] = {
            "model": settings.azure_openai_deployment,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            resp = client.chat.completions.create(**kwargs)
        except Exception as e:
            msg = str(e)
            if "temperature" in msg.lower() or "response_format" in msg.lower():
                kwargs.pop("response_format", None)
                resp = client.chat.completions.create(**kwargs)
            else:
                raise
        return resp.choices[0].message.content or ""

    def _openai(self, system: str, user: str, json_mode: bool) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        kwargs: dict[str, Any] = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    def _anthropic(self, system: str, user: str, json_mode: bool) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        sys_msg = system + ("\n\nAntworte ausschließlich mit gültigem JSON." if json_mode else "")
        resp = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2048,
            system=sys_msg,
            messages=[{"role": "user", "content": user}],
        )
        return resp.content[0].text if resp.content else ""

    def _ollama(self, system: str, user: str, json_mode: bool) -> str:
        payload = {
            "model": settings.ollama_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            payload["format"] = "json"
        with httpx.Client(timeout=60) as h:
            r = h.post(f"{settings.ollama_base_url}/api/chat", json=payload)
            r.raise_for_status()
            return r.json().get("message", {}).get("content", "")


llm = LLMClient()
