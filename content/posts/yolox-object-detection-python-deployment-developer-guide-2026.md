---
title: "YOLOX Object Detection Python Deployment Developer Guide 2026"
date: 2026-05-18T03:04:17+00:00
tags: ["yolox", "object-detection", "python", "deployment", "computer-vision", "deep-learning"]
description: "Complete guide to deploying YOLOX object detection in Python: training, ONNX/TensorRT export, FastAPI Docker API, and production benchmarks."
draft: false
cover:
  image: "/images/yolox-object-detection-python-deployment-developer-guide-2026.png"
  alt: "YOLOX Object Detection Python Deployment Developer Guide 2026"
  relative: false
schema: "schema-yolox-object-detection-python-deployment-developer-guide-2026"
---

YOLOX is Megvii's anchor-free object detection framework that ships models from 0.91M to 99.1M parameters, all deployable via PyTorch, ONNX, TensorRT, OpenVINO, or ncnn with five lines of Python. This guide covers every stage: environment setup, custom dataset training, multi-backend export, TensorRT quantization, and wrapping inference in a FastAPI/Docker production service.

## What Is YOLOX? Anchor-Free Detection for Python Developers

YOLOX is an anchor-free, single-stage object detector introduced by Megvii in mid-2021 that removed the anchor hyperparameters that historically plagued YOLO variants. Instead of predicting bounding-box offsets relative to predefined anchors, YOLOX regresses absolute box coordinates directly at each grid cell, eliminating the tedious anchor-tuning step that had to be repeated for every new dataset. The architecture pairs this anchor-free head with a decoupled head design — separate branches for classification and localization — which the authors showed significantly improves convergence speed and final accuracy. On COCO, YOLOX achieves 47.3% AP in its standard configuration, and the XLarge variant pushes this to 51.1% mAP with 99.1M parameters at 16.1ms on a T4 GPU. The anchor-free approach makes YOLOX a natural fit for Python deployment pipelines where dataset diversity makes anchor pre-computation impractical. For developers already familiar with NumPy-style tensor manipulation, the output format — a flat `(num_proposals, 5 + num_classes)` tensor — is far easier to post-process than anchor-grid outputs from older YOLO versions.

### Why Anchor-Free Matters for Deployment

Anchor-free detection eliminates a class of preprocessing decisions that previously had to be baked into each exported model. With YOLOX you export once and run on any dataset shape without re-generating anchor configs. This is particularly valuable for Docker-based microservices where the model artifact needs to be immutable.

## YOLOX Model Variants: Nano to XLarge — Which Should You Choose?

YOLOX model variants span six orders of magnitude in compute budget, ranging from YOLOX-Nano at 0.91M parameters to YOLOX-XLarge at 99.1M, giving Python developers a single unified codebase that covers everything from Raspberry Pi 4 inference to multi-GPU datacenter throughput. The Nano and Tiny variants (0.91M and 5.06M params) target embedded hardware like Jetson Nano and mobile devices; their ONNX exports fit comfortably within 4MB, making them deployable even on microcontrollers with ONNX Runtime Lite. The Small and Medium variants are the workhorses for CPU-server and single-GPU deployments, while Large and XLarge are tuned for maximum accuracy on high-end GPUs where inference latency is a secondary concern. For most production APIs running on cloud GPU instances (T4, A10), YOLOX-M delivers the best throughput-accuracy tradeoff at roughly 36.9ms on a T4. Choose Nano/Tiny for battery-powered or sub-$50 hardware, Small/Medium for cloud REST endpoints with SLA latency under 100ms, and Large/XLarge for offline batch processing pipelines where accuracy is paramount.

| Variant | Parameters | COCO mAP | T4 Latency |
|---------|-----------|----------|------------|
| Nano    | 0.91M     | 25.8%    | 6.5ms      |
| Tiny    | 5.06M     | 32.8%    | 9.7ms      |
| Small   | 8.94M     | 40.5%    | 15.0ms     |
| Medium  | 25.3M     | 46.9%    | 36.9ms     |
| Large   | 54.2M     | 49.7%    | 54.0ms     |
| XLarge  | 99.1M     | 51.1%    | 99.1ms     |

### YOLOX-Nano for Edge Devices

YOLOX-Nano's 0.91M parameter count makes it one of the smallest YOLO-family models capable of real-time COCO detection. On a Jetson Nano with TensorRT FP16, it consistently exceeds 30 FPS at 416×416 input resolution — enough for most surveillance and robotics applications.

## Installing YOLOX and Setting Up Your Python Environment

Setting up YOLOX requires Python 3.8+, PyTorch 1.13 or 2.x, and the Megvii YOLOX package installed from source — pip install from PyPI installs only a stub and is not sufficient for training or advanced inference. The canonical install path clones the GitHub repo, installs dependencies from `requirements.txt`, and runs `pip install -e .` in editable mode. This matters for deployment because the source install makes the `yolox` package importable directly, which is required for loading experiment configs programmatically from Python. CUDA 11.8 or 12.x is recommended; YOLOX's ONNX export path calls `torch.onnx.export` internally and requires a matched `onnxruntime-gpu` version. For Docker-based workflows, the project ships a pre-built `Dockerfile` that pins CUDA 11.8 + PyTorch 2.0, which is the safest starting point for reproducible deployments.

```bash
# Clone and install
git clone https://github.com/Megvii-BaseDetection/YOLOX.git
cd YOLOX
pip install -r requirements.txt
pip install -e .

# Download pretrained COCO weights (YOLOX-S as example)
wget https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth
```

### Verifying the Installation

```python
import yolox
from yolox.exp import get_exp
exp = get_exp(exp_file=None, exp_name="yolox_s")
print(exp.num_classes)  # Should print 80 for COCO
```

If this succeeds without import errors, the editable install is working correctly and you can proceed to inference or training.

## Running YOLOX Inference with Pretrained COCO Weights

Running YOLOX inference with pretrained COCO weights requires three steps: loading the experiment config, building the model, and calling the `Predictor` class that handles preprocessing and NMS. The `Predictor` class in `yolox/tools/demo.py` wraps the full inference pipeline — resize to input shape, normalize with ImageNet statistics, forward pass, and `multiclass_nms` — into a single `.inference()` call that returns a list of `(boxes, scores, class_ids)` tuples. YOLOX pretrained weights are released for all six variants and cover the full 80-class COCO vocabulary. For custom use cases, pretrained weights work as zero-shot detectors for common object categories immediately after download, without any fine-tuning. The model outputs raw predictions before NMS, which developers can intercept for custom post-processing (e.g., tracking integration where you want raw detections rather than filtered boxes).

```python
import cv2
import torch
from yolox.exp import get_exp
from yolox.utils import fuse_model, get_model_info
from yolox.data.data_augment import ValTransform
from yolox.utils import postprocess

# Load experiment config
exp = get_exp(exp_file=None, exp_name="yolox_s")
exp.test_conf = 0.3   # confidence threshold
exp.nmsthre = 0.45    # NMS IoU threshold
exp.test_size = (640, 640)

model = exp.get_model()
model.eval()

# Load weights
ckpt = torch.load("yolox_s.pth", map_location="cpu")
model.load_state_dict(ckpt["model"])
model.cuda()

# Inference
preproc = ValTransform(legacy=False)
img = cv2.imread("image.jpg")
img_tensor, _ = preproc(img, None, exp.test_size)
img_tensor = torch.from_numpy(img_tensor).unsqueeze(0).float().cuda()

with torch.no_grad():
    outputs = model(img_tensor)
    outputs = postprocess(outputs, exp.num_classes, exp.test_conf, exp.nmsthre)

# outputs[0]: tensor of shape (N, 7) — x1, y1, x2, y2, obj_conf, class_conf, class_id
boxes = outputs[0][:, :4]
scores = outputs[0][:, 4] * outputs[0][:, 5]
class_ids = outputs[0][:, 6].int()
```

## Training YOLOX on a Custom Dataset (Step-by-Step)

Training YOLOX on a custom dataset follows a structured pipeline: annotate images in COCO JSON format, create an experiment (`.py`) config file that subclasses `Exp`, set `num_classes` and dataset paths, then launch training with the `train.py` entrypoint. YOLOX's experiment system is pure Python — every hyperparameter (batch size, learning rate schedule, augmentation policy, input resolution) lives in the experiment file, making it version-controllable and reproducible across environments. The COCO JSON format is the single required format; Roboflow, CVAT, and Labelbox all export to it directly. For datasets under 5,000 images, the recommended starting point is YOLOX-S pretrained weights with a 50-epoch schedule, cosine LR decay, and the default MixUp + Mosaic augmentation, which achieves competitive mAP without overfitting. For larger datasets (10K+), enabling multi-scale training (input sizes ranging from 448 to 832) typically adds 1–2 mAP points at the cost of ~30% longer training time.

```python
# custom_exp.py — minimal custom dataset config
from yolox.exp import Exp as MyExp

class CustomExp(MyExp):
    def __init__(self):
        super().__init__()
        self.num_classes = 5          # your class count
        self.depth = 0.33             # YOLOX-S depth multiplier
        self.width = 0.50             # YOLOX-S width multiplier
        self.max_epoch = 100
        self.data_dir = "/data/coco_custom"
        self.train_ann = "instances_train.json"
        self.val_ann = "instances_val.json"
        self.input_size = (640, 640)
        self.random_size = (14, 26)   # multi-scale training
        self.warmup_epochs = 5
```

```bash
# Launch training (8 GPUs)
python tools/train.py -f custom_exp.py -d 8 -b 64 --fp16 -o \
    -c yolox_s.pth   # load pretrained COCO weights
```

### Dataset Format Requirements

YOLOX requires COCO-style JSON annotations with `images`, `annotations`, and `categories` keys. Each annotation needs `bbox` in `[x, y, width, height]` format (not `[x1, y1, x2, y2]`). The `category_id` field must be 1-indexed; YOLOX internally subtracts 1 before computing losses. Failing to match this convention is the most common cause of silent training failures where loss drops but mAP stays at zero.

## Exporting YOLOX to ONNX for Cross-Platform Deployment

Exporting YOLOX to ONNX decouples the model from PyTorch and unlocks deployment on any runtime that supports the ONNX standard, including ONNX Runtime (CPU/GPU), TensorRT, OpenVINO, and CoreML via onnxmltools. YOLOX ships a first-class `tools/export_onnx.py` script that handles the full export pipeline, including fusing batch normalization layers into convolutions and optionally folding NMS into the graph. The resulting ONNX graph takes a single `(1, 3, H, W)` float32 input and returns either raw proposals or post-NMS boxes depending on export flags. Exporting with `--decode_in_inference` and `--no-onnxsim` produces the most portable graph for runtime compatibility; running `onnxsim` afterwards to simplify the graph improves performance by 10–15% on ONNX Runtime CPU. ONNX opset 11 is the safe minimum; opset 17 enables more aggressive fusion in TensorRT 10.

```bash
# Export to ONNX
python tools/export_onnx.py \
    --output-name yolox_s.onnx \
    -f custom_exp.py \
    -c best_ckpt.pth \
    --input-size 640 640 \
    --batch-size 1 \
    --decode_in_inference

# Simplify (optional but recommended)
python -m onnxsim yolox_s.onnx yolox_s_simplified.onnx
```

### Running Inference with ONNX Runtime

```python
import onnxruntime as ort
import numpy as np
import cv2

sess = ort.InferenceSession("yolox_s_simplified.onnx",
                             providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
input_name = sess.get_inputs()[0].name

# Preprocess: resize + normalize
img = cv2.imread("image.jpg")
img_resized = cv2.resize(img, (640, 640))
img_input = img_resized[..., ::-1].transpose(2, 0, 1)  # BGR→RGB, HWC→CHW
img_input = np.ascontiguousarray(img_input, dtype=np.float32)[np.newaxis]

outputs = sess.run(None, {input_name: img_input})
# outputs[0]: shape (1, num_anchors, 85) for 80-class COCO
```

## TensorRT Deployment for Maximum GPU Throughput

TensorRT deployment of YOLOX reduces inference latency by 2–4× over ONNX Runtime GPU through kernel fusion, precision calibration, and layer-level optimization specific to the NVIDIA architecture. The recommended path for YOLOX TensorRT deployment in 2026 is: export to ONNX (opset 17), then use `trtexec` or the TensorRT Python API to build a serialized engine with INT8 calibration for maximum throughput. YOLOX's architecture is fully compatible with TensorRT 10.x layer types — no custom plugins are required for standard variants. INT8 calibration requires a calibration dataset of 200–500 representative images; using the validation set works well in practice. On an A100 GPU, TensorRT INT8 YOLOX-S achieves sub-5ms inference at batch size 8, enabling throughput of 1,600+ frames per second. For edge deployment on Jetson Orin, TensorRT FP16 YOLOX-Nano sustains 120+ FPS at 416×416, suitable for real-time video analytics at 30–60 FPS camera input with headroom for preprocessing.

```python
import tensorrt as trt
import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

def build_engine(onnx_path, precision="fp16"):
    builder = trt.Builder(TRT_LOGGER)
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 4 << 30)  # 4GB

    if precision == "fp16":
        config.set_flag(trt.BuilderFlag.FP16)
    elif precision == "int8":
        config.set_flag(trt.BuilderFlag.INT8)
        # Set up INT8 calibrator here

    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, TRT_LOGGER)

    with open(onnx_path, "rb") as f:
        parser.parse(f.read())

    serialized_engine = builder.build_serialized_network(network, config)
    with open("yolox_s_fp16.engine", "wb") as f:
        f.write(serialized_engine)

build_engine("yolox_s_simplified.onnx", precision="fp16")
```

### INT8 Calibration for Maximum Throughput

INT8 quantization of YOLOX achieves the highest throughput on NVIDIA GPUs by running matrix multiplications in 8-bit integer arithmetic. Calibration accuracy degrades by less than 0.5 mAP for YOLOX-S with 500 calibration images, making INT8 viable for most production use cases where the absolute accuracy ceiling is not critical.

## OpenVINO and ncnn: YOLOX on CPU and Mobile Devices

OpenVINO and ncnn target the two most common non-NVIDIA deployment environments: Intel CPU servers and ARM mobile/embedded devices, respectively. OpenVINO's model optimizer converts the YOLOX ONNX graph into an Intermediate Representation (IR) that the OpenVINO Runtime executes on Intel CPU, integrated GPU, or Myriad VPU with automatic layer fusion and quantization. On a modern Intel Xeon server (Ice Lake or Sapphire Rapids), OpenVINO FP32 YOLOX-S achieves 45–60ms per frame — comparable to a mid-range NVIDIA GPU and significantly faster than raw PyTorch CPU inference. ncnn, developed by Tencent, supports ARM NEON intrinsics and is the preferred path for Android and iOS deployment; the YOLOX repo includes a first-party ncnn conversion guide that handles the custom post-processing operators that ncnn's ONNX importer would otherwise reject. For Intel CPU cloud instances (AWS c7i, Azure Dv5), OpenVINO with INT8 post-training quantization using NNCF adds roughly 2× throughput over FP32 with less than 1% mAP drop on COCO.

```bash
# Export to OpenVINO IR
mo --input_model yolox_s_simplified.onnx \
   --output_dir openvino_model/ \
   --input_shape [1,3,640,640] \
   --data_type FP32

# Run OpenVINO inference
from openvino.runtime import Core
core = Core()
model = core.read_model("openvino_model/yolox_s_simplified.xml")
compiled = core.compile_model(model, "CPU")
infer_req = compiled.create_infer_request()
```

### ncnn Deployment on Android

ncnn conversion requires first exporting YOLOX to a Caffe-like `.param`/`.bin` format using `onnx2ncnn`. The YOLOX repo's `demo/ncnn` directory includes a C++ inference example with pre-built Android JNI wrappers, enabling 20–40 FPS object detection on mid-range Snapdragon 8xx devices at 416×416 resolution.

## Building a Production API with FastAPI and Docker

Building a production YOLOX inference API with FastAPI and Docker creates a self-contained, horizontally scalable object detection microservice that accepts image uploads via HTTP and returns structured JSON bounding-box annotations. The architecture separates model loading (done once at startup) from request handling, using FastAPI's `lifespan` context to load the YOLOX ONNX session before the first request arrives — this eliminates cold-start latency on the critical path. Docker Compose manages the service stack: a GPU-enabled inference container built on `nvcr.io/nvidia/cuda:12.1-cudnn8-runtime`, optionally fronted by Nginx for SSL termination and request queuing. For high-throughput scenarios, the inference container uses a request batching middleware that accumulates requests over a 10ms window and processes them in a single batched ONNX Runtime call, improving GPU utilization from ~30% (single-request mode) to 85%+ under load.

```python
# main.py — FastAPI YOLOX inference service
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import numpy as np
import onnxruntime as ort
import cv2

MODEL_PATH = "yolox_s_simplified.onnx"
COCO_CLASSES = [...]  # 80-class list

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session = ort.InferenceSession(
        MODEL_PATH,
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )
    app.state.input_name = app.state.session.get_inputs()[0].name
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/detect")
async def detect(file: UploadFile = File(...), conf_thresh: float = 0.3):
    contents = await file.read()
    img_array = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # Preprocess
    img_resized = cv2.resize(img, (640, 640))
    inp = img_resized[..., ::-1].transpose(2, 0, 1).astype(np.float32)[np.newaxis]

    # Inference
    outputs = app.state.session.run(None, {app.state.input_name: inp})[0]

    # Post-process NMS output
    detections = []
    if outputs is not None and len(outputs[0]) > 0:
        for det in outputs[0]:
            x1, y1, x2, y2, obj_conf, cls_conf, cls_id = det
            score = float(obj_conf * cls_conf)
            if score >= conf_thresh:
                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "score": score,
                    "class": COCO_CLASSES[int(cls_id)]
                })

    return JSONResponse({"detections": detections, "count": len(detections)})
```

```dockerfile
# Dockerfile
FROM nvcr.io/nvidia/cuda:12.1-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3-pip libgl1-mesa-glx libglib2.0-0
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

## YOLOX vs YOLOv8 vs YOLO11: Which to Use in 2026?

Choosing between YOLOX, YOLOv8, and YOLO11 in 2026 depends on three factors: ecosystem maturity, accuracy ceiling, and deployment backend flexibility. YOLO11x outperforms YOLOX-X in accuracy (54.7 mAP vs 51.1 mAP) while using roughly half the parameters (56.9M vs 99.1M), making YOLO11 the default choice for new greenfield projects targeting Ultralytics' supported export formats. YOLOv8 and YOLO11 benefit from Ultralytics' unified training API and actively maintained export pipelines for all major runtimes. YOLOX remains the better choice in three specific scenarios: (1) existing research pipelines built on the Megvii codebase where migration cost is prohibitive, (2) ncnn deployment on Android/iOS where YOLOX's first-party ncnn support is better maintained than Ultralytics' ncnn path, and (3) academic reproducibility requirements where YOLOX's published COCO checkpoints and experiment configs match specific paper results. For new production deployments starting in 2026, YOLO11 is generally the right choice unless one of these three scenarios applies.

| Model    | COCO mAP | Parameters | TensorRT FP16 (T4) | Ecosystem      |
|----------|----------|------------|---------------------|----------------|
| YOLOX-X  | 51.1%    | 99.1M      | ~40ms               | Megvii (OSS)   |
| YOLOv8x  | 53.9%    | 68.2M      | ~28ms               | Ultralytics    |
| YOLO11x  | 54.7%    | 56.9M      | ~24ms               | Ultralytics    |

### When YOLOX Is Still the Right Call

If your deployment targets ncnn on ARM or your codebase is already built on YOLOX experiment configs, migration to Ultralytics carries real risk for marginal accuracy gain. In those cases, staying on YOLOX with a well-tuned TensorRT export is the pragmatic choice.

## Performance Benchmarks and Real-World Considerations

Real-world YOLOX performance depends heavily on hardware, input resolution, batch size, and post-processing strategy — published COCO benchmarks measure model quality but not end-to-end pipeline throughput. In production video analytics pipelines, the bottleneck often shifts from inference to frame capture and preprocessing: a single T4 GPU running YOLOX-S in TensorRT FP16 can process 1,200 frames per second of pure inference, but a naively implemented OpenCV video decode loop caps at 200 FPS. To fully utilize GPU throughput, preprocessing (resize, normalize) must be moved to the GPU using NVIDIA DALI or custom CUDA kernels, which is why production deployments often show 3–4× end-to-end speedup from pipeline optimization beyond model-level tuning alone. For CPU-only deployments on cloud instances, OpenVINO consistently outperforms raw ONNX Runtime by 40–60% on Intel CPUs due to MKL-DNN backend selection and automatic INT8 quantization through NNCF. Memory bandwidth is the primary constraint on CPU inference — YOLOX-S's 8.94M parameters fit entirely in L3 cache on modern Xeon processors, which is why inference latency remains predictable under concurrent load. The practical recommendation: benchmark your specific hardware and input pipeline end-to-end, not just model inference in isolation, before selecting a model variant and runtime.

### Latency vs Throughput Trade-offs

For real-time single-stream applications (one camera at 30 FPS), latency matters more than throughput — optimize for minimum per-frame latency by using batch size 1 and TensorRT with `IBuilderConfig::setMinTimingIterations` tuned to your input resolution. For batch processing or multi-stream pipelines, maximize GPU utilization by increasing batch size and using CUDA streams for async inference overlap with preprocessing.

---

## FAQ

**Q: Can YOLOX run without a GPU?**

Yes. YOLOX supports CPU inference through PyTorch, ONNX Runtime CPU, and OpenVINO. For CPU-only deployments, use YOLOX-Nano or YOLOX-Tiny to stay within practical latency budgets (under 200ms per frame on modern server CPUs).

**Q: What is the difference between YOLOX decoupled head and the original YOLO head?**

Traditional YOLO heads use a single convolutional branch to predict class probabilities and bounding box coordinates simultaneously. YOLOX's decoupled head uses separate branches for each task, which the authors showed prevents conflicting gradient updates between classification and localization loss signals, resulting in faster convergence and ~1.5 mAP improvement.

**Q: How do I convert YOLOX weights to ONNX for deployment?**

Run `python tools/export_onnx.py -f your_exp.py -c best_ckpt.pth --output-name model.onnx --decode_in_inference`. Then optionally run `onnxsim model.onnx model_simplified.onnx` to reduce graph complexity. The resulting ONNX model runs on ONNX Runtime, TensorRT, and OpenVINO without modification.

**Q: What is the minimum image size for YOLOX inference?**

YOLOX processes images at the resolution specified in the experiment config (`test_size`). The minimum practical resolution is 320×320 for YOLOX-Nano; smaller inputs significantly degrade detection of small objects. The model internally pads inputs to multiples of 32, so any resolution divisible by 32 is valid.

**Q: How does YOLOX compare to YOLO11 for edge deployment in 2026?**

YOLOX-Nano (0.91M params) is smaller than YOLO11n (2.6M params) and has better-maintained first-party ncnn support for ARM deployment. For Jetson and mobile Android targets, YOLOX-Nano remains competitive. For Intel-based edge devices (NUC, industrial PCs), YOLO11 with OpenVINO export typically edges out YOLOX due to Ultralytics' more actively maintained OpenVINO pipeline.
