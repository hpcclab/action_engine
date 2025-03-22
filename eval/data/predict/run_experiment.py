import subprocess

# List of commands to run
commands = [
    "python -m eval.data.predict.fewshot",
    "python -m eval.data.predict.fewshot_COT",
    "python -m eval.data.predict.zeroshot",
    "python -m eval.data.predict.zeroshot_COT",
    # "python -m eval.data.predict.fewshot_COT_param",
    # "python -m eval.data.predict.fewshot_param",
    # "python -m eval.data.predict.action_engine_param",
    # "python -m eval.data.predict.action_engine",
    # "python -m eval.data.predict.rae_generate_yaml",
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