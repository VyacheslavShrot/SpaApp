import os


def load_env(BASE_DIR):
    _env_path = os.path.join(BASE_DIR, '..', '.env')

    with open(_env_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=')

                os.environ[key] = value
