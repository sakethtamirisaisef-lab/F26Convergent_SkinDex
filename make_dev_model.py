"""Builds a tiny UNTRAINED placeholder model so the whole pipeline runs end to end in development.

It outputs meaningless scores. Replace it with the real model exported from training:
    torch.onnx.export(model, torch.randn(1, 3, 224, 224), "model.onnx",
                      input_names=["image"], output_names=["logits"], dynamic_axes={"image": {0: "n"}})

Usage:  pip install onnx && python scripts/make_dev_model.py models/dev
"""
import json
import sys
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper

LABELS = [
    {"id": "breakouts", "name": "Breakouts"},
    {"id": "redness", "name": "Redness"},
    {"id": "dryness", "name": "Dry patches"},
    {"id": "hyperpigmentation", "name": "Dark spots"},
    {"id": "needs_review", "name": "Worth a dermatologist's look"},
]


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    w = numpy_helper.from_array(rng.normal(0, 1.5, (3, len(LABELS))).astype(np.float32), "W")
    b = numpy_helper.from_array(np.full(len(LABELS), -1.0, np.float32), "B")
    graph = helper.make_graph(
        [helper.make_node("GlobalAveragePool", ["image"], ["pooled"]),
         helper.make_node("Flatten", ["pooled"], ["flat"]),
         helper.make_node("Gemm", ["flat", "W", "B"], ["logits"])],
        "skindex_dev",
        [helper.make_tensor_value_info("image", TensorProto.FLOAT, ["n", 3, 224, 224])],
        [helper.make_tensor_value_info("logits", TensorProto.FLOAT, ["n", len(LABELS)])],
        initializer=[w, b])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 8
    onnx.checker.check_model(model)
    onnx.save(model, out / "model.onnx")
    (out / "model.json").write_text(json.dumps({
        "version": "dev-untrained", "input_size": 224, "activation": "sigmoid",
        "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225],
        "labels": LABELS, "display_threshold": 0.35,
        "flag_labels": ["needs_review"], "flag_threshold": 0.6}, indent=2))
    print(f"Wrote placeholder model to {out}/ (untrained: scores are meaningless)")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "models/dev"))
