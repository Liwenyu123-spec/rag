"""本地 Chinese-CLIP：文本塔 + 图像塔，对接 LlamaIndex MultiModalEmbedding。

权重默认放在 H:\\二阶段\\chinese-clip-vit-base-patch16（可用 EMBEDDING_MODEL 覆盖）。
文本 / 图像向量都是 512 维并做 L2 归一化，可直接做以文搜图、以图搜图。
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import torch
from llama_index.core.embeddings.multi_modal_base import MultiModalEmbedding
from pydantic import Field, PrivateAttr


class ChineseCLIPEmbedding(MultiModalEmbedding):
    """Chinese-CLIP 双塔：query/document 走文本，图片走视觉塔。"""

    model_path: str = Field(
        default=r"H:\二阶段\chinese-clip-vit-base-patch16",
        description="本地 Chinese-CLIP 目录",
    )
    device: str = Field(default="cpu", description="cuda / cpu")
    normalize: bool = Field(default=True, description="是否 L2 归一化")

    _model: object = PrivateAttr(default=None)
    _processor: object = PrivateAttr(default=None)
    _tokenizer: object = PrivateAttr(default=None)
    _image_processor: object = PrivateAttr(default=None)

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
            self._image_processor = self._processor
        except Exception:
            from transformers import BertTokenizer

            self._processor = None
            self._tokenizer = BertTokenizer.from_pretrained(path)
            self._image_processor = self._load_image_processor(path)

    def _load_image_processor(self, path: str):
        try:
            from transformers import AutoImageProcessor

            return AutoImageProcessor.from_pretrained(path)
        except Exception:
            from transformers import CLIPImageProcessor

            return CLIPImageProcessor.from_pretrained(path)

    @classmethod
    def class_name(cls) -> str:
        return "ChineseCLIPEmbedding"

    def _as_pil(self, img_file_path):
        from PIL import Image

        if hasattr(img_file_path, "convert"):
            return img_file_path.convert("RGB")
        return Image.open(str(img_file_path)).convert("RGB")

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
            text_out = model.get_text_features(**inputs)
            feats = getattr(text_out, "pooler_output", text_out)
            if not torch.is_tensor(feats):
                raise RuntimeError(f"Chinese-CLIP 文本向量类型异常: {type(text_out)}")
            if self.normalize:
                feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
            return feats.detach().cpu().tolist()

    def _encode_images(self, images) -> List[List[float]]:
        if not images:
            return []
        device = self.device
        model = self._model
        processor = self._image_processor or self._processor
        if processor is None:
            raise RuntimeError("Chinese-CLIP 图像预处理器未加载，无法编码图片")
        pil_images = [self._as_pil(item) for item in images]
        with torch.no_grad():
            try:
                inputs = processor(images=pil_images, return_tensors="pt")
            except TypeError:
                inputs = processor(pil_images, return_tensors="pt")
            pixel_values = inputs.get("pixel_values")
            if pixel_values is None:
                raise RuntimeError("图像预处理未返回 pixel_values")
            pixel_values = pixel_values.to(device)
            image_out = model.get_image_features(pixel_values=pixel_values)
            feats = getattr(image_out, "pooler_output", image_out)
            if not torch.is_tensor(feats):
                raise RuntimeError(f"Chinese-CLIP 图像向量类型异常: {type(image_out)}")
            if self.normalize:
                feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
            return feats.detach().cpu().tolist()

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._encode_texts([query])[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._encode_texts([text])[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._encode_texts(texts)

    def _get_image_embedding(self, img_file_path) -> List[float]:
        return self._encode_images([img_file_path])[0]

    def _get_image_embeddings(self, img_file_paths) -> List[List[float]]:
        return self._encode_images(list(img_file_paths))

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    async def _aget_image_embedding(self, img_file_path) -> List[float]:
        return self._get_image_embedding(img_file_path)
