import os
import logging
import ollama


def log_errors(log: str):
    log_path = "log"
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file = f"{log_path}/logfile.log"
    previous_log = f"{log_path}/previous_logfile.log"

    if os.path.exists(previous_log):
        os.remove(previous_log)

    if os.path.exists(log_file):
        os.rename(log_file, previous_log)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.error(log)


def display_models() -> list:
    ollama_list = ollama.list()
    models_dict = ollama_list["models"]

    models = []
    for model in models_dict:
        model_data = model["name"]
        model_name = model_data.split(":")
        models.append(model_name[0])

    return models


def pull_model(model_name: str) -> str:
    ollama.pull(model_name)
    return f"Model {model_name} pulled successfully!"


def display_modelfile(model_name: str) -> str:
    modelfile_path = "modelfiles"

    if not os.path.exists(modelfile_path):
        os.makedirs(modelfile_path)

    if not os.listdir(modelfile_path):
        return "No modelfile found! Create a modelfile first!"

    modelfile = f"{modelfile_path}/{model_name}"

    if not os.path.exists(modelfile):
        return f"Modelfile for {model_name} not found! Create one first!"

    with open(modelfile, "r") as m:
        modelfile_text = m.read()

    return modelfile_text


def split_modelfile(modelfile: str) -> str:
    split_contents = modelfile.split("\n\n")
    model_source = split_contents[0]
    parameter = None
    template = None
    system = None

    for content in split_contents:
        if "PARAMETER" in content:
            parameter = content
        elif "TEMPLATE" in content:
            template = content
        elif "SYSTEM" in content:
            system = content

    if parameter or template or system:
        return model_source, parameter, template, system
    else:
        return model_source


def get_system_prompt(system: str) -> str:
    start = 'SYSTEM """'
    end = '"""'

    start_index = system.find(start) + len(start)
    end_index = system.find(end, start_index)

    return system[start_index:end_index].strip()


def get_template(template: str) -> str:
    start = 'TEMPLATE """'
    end = '"""'

    start_index = template.find(start) + len(start)
    end_index = template.find(end, start_index)

    return template[start_index:end_index].strip()


def create_modelfile(model_name: str, modelfile: str) -> str:
    ollama.create(model=model_name, modelfile=modelfile)
    return f"modelfile for {model_name} created!"


def modelfile_from_pull(model: str):
    pass


def modelfile_from_file(model_name: str, model_path: str):
    pass
