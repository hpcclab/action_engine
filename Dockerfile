# 1. Base image (GPU-compatible PyTorch)
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

# 2. Working directory
WORKDIR /app

# 3. Copy requirements.txt & install packages with pip
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 🔥 4. Explicitly install torchvision (without modifying requirements.txt)
RUN pip install torchvision==0.17.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

# Install vllm
RUN pip install vllm

# 5. Copy the rest of the files
COPY . .

# 6. Command to run the application
CMD ["python", "main.py"]

# Build the image (for amd64 architecture)
# docker build --platform linux/amd64 -t action-engine .

# Run the container (for amd64 architecture)
# docker run --platform linux/amd64 -it action-engine
