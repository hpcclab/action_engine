import subprocess

# List of commands to run
commands = [
    # "python -m eval.data.predict.fewshot_COT",
    # "python -m eval.data.predict.generate_yaml",
    "python -m eval.data.predict.generate_param_eval",
    # "python -m eval.data.predict.zeroshot_COT_param",
    # "python -m eval.data.predict.fewshot_COT_param",
    "python eval/yaml_to_predict.py",
    "python eval/culculate.py",
    "python eval/plot.py",
]

# Run each command
for command in commands:
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error occurred while running: {command}")
        break
