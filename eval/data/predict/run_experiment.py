import subprocess

# List of commands to run
commands = [
    "python -m eval.data.predict.eval_QwenCoder32B.fewshot",
    "python -m eval.data.predict.eval_QwenCoder32B.fewshot_COT",
    "python -m eval.data.predict.eval_QwenCoder32B.zeroshot",
    "python -m eval.data.predict.eval_QwenCoder32B.zeroshot_COT",
    # "python -m eval.data.predict.eval_gpt4o.fewshot_COT_param",
    # "python -m eval.data.predict.eval_gpt4o.fewshot_param",
    "python -m eval.data.predict.eval_gpt4o.zeroshot",
    "python -m eval.data.predict.eval_gpt4o.zeroshot_COT",
    # "python -m eval.data.predict.eval_gpt4o.action_engine_param",
    # "python -m eval.data.predict.eval_gpt4o.action_engine",
    # "python -m eval.data.predict.eval_gpt4o.rae_generate_yaml",
    # "python eval/yaml_to_predict.py",
    # "python eval/culculate.py",
    # "python eval/plot.py",
]

# Run each command
for command in commands:
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error occurred while running: {command}")
        break