# 🧠⚙️ Action Engine: Automatic Workflow Generation in FaaS

**Authors**: Akiharu Esashi, Pawissanutt Lertpongrujikorn, Mohsen Amini Salehi  
📍 University of North Texas  
🔗 [Project Website](https://hpcclab.org/) | 📜 [Preprint](UnderReview) 

---

## 🚀 Overview

**Action Engine** is an end-to-end system that **automates the generation of serverless (FaaS) workflows** from natural language queries using **Tool-Augmented Large Language Models (LLMs)**.

💡 **Why it matters:**  
Creating FaaS workflows traditionally requires manual effort, specialized platform knowledge (e.g., AWS Step Functions, Google Cloud Composer), and tight coupling with provider-specific APIs. Action Engine **eliminates these challenges** by generating executable, platform-independent workflows from human-readable descriptions — **no manual orchestration needed**.

---

## ✨ Highlights

- ✅ **Automated Workflow Generation**: Translates user queries into executable FaaS workflows.
- 🌐 **Platform & Language Agnostic**: Supports any cloud provider and programming language.
- 🤖 **LLM-Powered Intelligence**: Uses state-of-the-art tool-augmented LLMs for function selection and dependency handling.
- 🔁 **Reusability & Scalability**: Constructs DAG-based workflows with explicit data dependencies.
- ⚙️ **API-Backed Execution**: Generates ready-to-use API endpoints for seamless integration.

---

## 🧱 System Architecture

```
+------------------+      +---------------------+      +------------------+
|   User Query     +----->+   Text-to-Workflow  +----->+   API Endpoint   |
+------------------+      +---------------------+      +------------------+
                                |                             |
                                v                             v
                  [Function Selection]           [Workflow Execution Engine]
                                |
                                v
                        DAG Construction
                                |
                                v
                Platform-Specific Workflow Compiler
```

Read more in our [📘 Paper](#) about each component.

---

## 📊 Evaluation & Results

We evaluated Action Engine using the Reverse Chain dataset against various baselines including **GPT-4o**, **Qwen-Coder-32B-Instruct**, and **Reverse Chain**.

📈 **Key Metrics:**
- **Function Selection Accuracy**: ~42% (Level 3)
- **Data Dependency F1 Score**: Competitive with GPT-4o Few-Shot CoT
- **Topological Order Accuracy**: Highest LCS among all baselines

🔍 **Insight**: Action Engine offers robust performance **even at higher workflow complexity**, highlighting its scalability and reliability in real-world FaaS systems.

---

## 🔬 Key Contributions

1. **Action Engine Framework**: Open-source, plug-and-play system for FaaS automation.
2. **Novel Evaluation Benchmark**: Extends the Reverse Chain dataset for complex multi-step tasks.
3. **LLM Workflow Adaptation**: Redefines tool-augmented LLM stages for cloud-native applications.

---

## 📚 Citation

If you use this work, please cite:

```bibtex
@article{esashi2025actionengine,
  title={Action Engine: Automatic Workflow Generation in FaaS},
  author={Esashi, Akiharu and Lertpongrujikorn, Pawissanutt and Salehi, Mohsen Amini},
  journal={Preprint submitted to Elsevier},
  year={2025}
}
```

---

## 🤝 Acknowledgments

This work is supported by the **National Science Foundation (NSF)** through CNS Awards #2419588 and #2418188.  
We gratefully acknowledge **Chameleon Cloud** for providing the computational resources.

---

## 📬 Contact

- 📧 Akiharu Esashi: [akiharuesashi@my.unt.edu](mailto:akiharuesashi@my.unt.edu)  
- 💼 Mohsen Amini Salehi: [mohsen.aminisalehi@unt.edu](mailto:mohsen.aminisalehi@unt.edu)
