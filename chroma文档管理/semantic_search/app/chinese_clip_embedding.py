"""本地 Chinese-CLIP 文本向量：对接 LlamaIndex BaseEmbedding。

权重默认放在 H:\\二阶段\\chinese-clip-vit-base-patch16（可用 EMBEDDING_MODEL 覆盖）。
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import torch
from llama_index.core.base.embeddings.base import BaseEmbedding
from pydantic import Field, PrivateAttr


class ChineseCLIPEmbedding(BaseEmbedding):
    """用 Chinese-CLIP 文本塔做 query / document embedding（L2 归一化）。"""

    model_path: str = Field(
        default=r"H:\二阶段\chinese-clip-vit-base-patch16",
        description="本地 Chinese-CLIP 目录",
    )
    device: str = Field(default="cpu", description="cuda / cpu")
    normalize: bool = Field(default=True, description="是否 L2 归一化")

    _model: object = PrivateAttr(default=None)
    _processor: object = PrivateAttr(default=None)
    _tokenizer: object = PrivateAttr(default=None)

    def __init__(
        self,
        model_path: str = r"H:\二阶段\chinese-clip-vit-base-patch16",
        device: str | None = None,
        normalize: bool = True,
        **kwargs,
    ):
        path = str(Path(model_path).expanduser().resolve())
        if not Path(path).is_dir():
            raise FileNotFoundError(f"Chinese-CLIP 目录不存在: {path}")
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        super().__init__(
            model_name=path,
            model_path=path,
            device=device,
            normalize=normalize,
            **kwargs,
        )
        self._load(path, device)

    def _load(self, path: str, device: str) -> None:
        from transformers import ChineseCLIPModel, ChineseCLIPProcessor

        self._model = ChineseCLIPModel.from_pretrained(path)
        self._model.to(device)
        self._model.eval()
        try:
            self._processor = ChineseCLIPProcessor.from_pretrained(path)
            self._tokenizer = None
        except Exception:
            # 部分离线包缺 tokenizer_config，退回 BertTokenizer + vocab.txt
            from transformers import BertTokenizer

            self._processor = None
            self._tokenizer = BertTokenizer.from_pretrained(path)

    @classmethod
    def class_name(cls) -> str:
        return "ChineseCLIPEmbedding"

    def _encode_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        device = self.device
        model = self._model
        with torch.no_grad():
            if self._processor is not None:
                inputs = self._processor(
                    text=list(texts),
                    padding=True,
                    truncation=True,
                    max_length=52,
                    return_tensors="pt",
                )
            else:
                inputs = self._tokenizer(
                    list(texts),
                    padding=True,
                    truncation=True,
                    max_length=52,
                    return_tensors="pt",
                )
            inputs = {k: v.to(device) for k, v in inputs.items() if torch.is_tensor(v)}
            # transformers≥5：get_text_features 返回 BaseModelOutputWithPooling，
            # 投影后的文本向量在 pooler_output（512 维）
            text_out = model.get_text_features(**inputs)
            feats = getattr(text_out, "pooler_output", text_out)
            if not torch.is_tensor(feats):
                raise RuntimeError(f"Chinese-CLIP 文本向量类型异常: {type(text_out)}")
            if self.normalize:
                feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
            return feats.detach().cpu().tolist()

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._encode_texts([query])[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._encode_texts([text])[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._encode_texts(texts)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)
