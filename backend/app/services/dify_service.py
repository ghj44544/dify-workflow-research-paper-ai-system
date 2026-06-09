import json
import re
from pathlib import Path
from typing import Any

import aiofiles
import httpx

from app.core.config import settings


class DifyAPIError(RuntimeError):
    pass


class DifyService:
    def __init__(self) -> None:
        self.base_url = settings.dify_base_url.rstrip("/")
        self.timeout = httpx.Timeout(120.0)

    async def upload_file_to_dify(
        self, api_key: str, file_path: str, user: str
    ) -> str:
        self._ensure_api_key(api_key)
        path = Path(file_path)
        if not path.exists():
            raise DifyAPIError(f"本地文件不存在：{file_path}")

        url = f"{self.base_url}/files/upload"
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            async with aiofiles.open(path, "rb") as file_obj:
                file_bytes = await file_obj.read()

            files = {"file": (path.name, file_bytes, "application/octet-stream")}
            data = {"user": user}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url, headers=headers, data=data, files=files
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise DifyAPIError(
                f"Dify 文件上传失败：HTTP {exc.response.status_code} {self._format_response_text(exc.response.text)}"
            ) from exc
        except (httpx.RequestError, OSError, ValueError) as exc:
            raise DifyAPIError(f"Dify 文件上传失败：{exc}") from exc

        upload_file_id = self._extract_upload_file_id(payload)
        if not upload_file_id:
            raise DifyAPIError(f"Dify 文件上传响应中未找到文件 id：{payload}")
        return upload_file_id

    async def run_workflow(
        self, api_key: str, inputs: dict[str, Any], user: str
    ) -> dict[str, Any]:
        self._ensure_api_key(api_key)
        url = f"{self.base_url}/workflows/run"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise DifyAPIError(
                f"Dify Workflow 运行失败：HTTP {exc.response.status_code} {self._format_response_text(exc.response.text)}"
            ) from exc
        except (httpx.RequestError, ValueError) as exc:
            raise DifyAPIError(f"Dify Workflow 运行失败：{exc}") from exc

    async def run_extract_workflow(
        self, file_path: str, user: str = "user_001"
    ) -> dict[str, Any]:
        api_key = settings.dify_extract_api_key
        upload_file_id = await self.upload_file_to_dify(api_key, file_path, user)
        inputs = {"paper_file": self._dify_local_file(upload_file_id)}
        raw_response = await self.run_workflow(api_key, inputs, user)
        return self._build_workflow_result(raw_response)

    async def run_qa_workflow(
        self, file_path: str, question: str, user: str = "user_001"
    ) -> dict[str, Any]:
        api_key = settings.dify_qa_api_key
        upload_file_id = await self.upload_file_to_dify(api_key, file_path, user)
        inputs = {
            "paper_file": self._dify_local_file(upload_file_id),
            "question": question,
        }
        raw_response = await self.run_workflow(api_key, inputs, user)
        return self._build_workflow_result(raw_response)

    async def run_note_workflow(
        self, file_path: str, note_style: str | None, user: str = "user_001"
    ) -> dict[str, Any]:
        api_key = settings.dify_note_api_key
        upload_file_id = await self.upload_file_to_dify(api_key, file_path, user)
        inputs = {
            "paper_file": self._dify_local_file(upload_file_id),
            "note_style": note_style or "适合研究生阅读笔记",
        }
        raw_response = await self.run_workflow(api_key, inputs, user)
        return self._build_workflow_result(raw_response)

    @staticmethod
    def _ensure_api_key(api_key: str) -> None:
        if not api_key:
            raise DifyAPIError("Dify API Key 未配置")

    @staticmethod
    def _dify_local_file(upload_file_id: str) -> dict[str, str]:
        return {
            "type": "document",
            "transfer_method": "local_file",
            "upload_file_id": upload_file_id,
        }

    @staticmethod
    def _extract_upload_file_id(payload: dict[str, Any]) -> str | None:
        candidates = [
            payload.get("id"),
            payload.get("upload_file_id"),
            payload.get("data", {}).get("id") if isinstance(payload.get("data"), dict) else None,
            payload.get("data", {}).get("upload_file_id")
            if isinstance(payload.get("data"), dict)
            else None,
        ]
        return next((str(item) for item in candidates if item), None)

    def _build_workflow_result(self, raw_response: dict[str, Any]) -> dict[str, Any]:
        outputs = self._extract_outputs(raw_response)
        content = self._pick_output_content(outputs)
        return {
            "content": content,
            "outputs": outputs,
            "raw_response": raw_response,
        }

    @staticmethod
    def _extract_outputs(raw_response: dict[str, Any]) -> dict[str, Any]:
        data = raw_response.get("data")
        if isinstance(data, dict) and isinstance(data.get("outputs"), dict):
            return data["outputs"]
        if isinstance(raw_response.get("outputs"), dict):
            return raw_response["outputs"]
        return {}

    @staticmethod
    def _pick_output_content(outputs: dict[str, Any]) -> Any:
        if not outputs:
            return ""
        for value in outputs.values():
            if isinstance(value, str):
                return value
        first_value = next(iter(outputs.values()))
        if isinstance(first_value, (dict, list)):
            return json.dumps(first_value, ensure_ascii=False)
        return first_value

    @staticmethod
    def _format_response_text(text: str) -> str:
        cleaned = re.sub(r"<[^>]+>", " ", text or "")
        cleaned = " ".join(cleaned.split())
        return cleaned[:500] or "无响应内容"
