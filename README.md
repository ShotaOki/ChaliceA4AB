# Chalice-A4AB

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Chalice-A4AB)

[![tests](https://github.com/ShotaOki/ChaliceA4AB/actions/workflows/test.yml/badge.svg)](https://github.com/ShotaOki/ChaliceA4AB/actions/workflows/test.yml)
![GitHub License](https://img.shields.io/github/license/ShotaOki/ChaliceA4AB)

## What is this?

Chalice plugin: Support `Agents for Amazon Bedrock`

## PIP

**Chalice-a4ab**  
https://pypi.org/project/chalice-a4ab/

## Usage

1. Install

```
pip install chalice-a4ab
```

2. Replace `from chalice import Chalice` to `from chalice_a4ab import Chalice`.

Before:

```python
from chalice import Chalice

app = Chalice("app-name")

@app.router("path-name")
...
```

After:

```python
from chalice_a4ab import Chalice

app = Chalice("app-name")

@app.router("path-name")
...
```

3. Application work on Agents for Amazon Bedrock

## Advanced Usage

Create OpenAPI Schema automatically.

1. Install Chalice-spec

```python
pip install chalice chalice-spec==0.7.0 chalice-a4ab boto3 pydantic
```

2. Write Setting

```python
from chalice_a4ab import Chalice, AgentsForAmazonBedrockConfig

# Set Config for Agents for Amazon bedrock
AgentsForAmazonBedrockConfig(
    instructions="Situation Settings for talking with Human and agent.(more than 40 words)",
    description="Description of application",
).apply()

app = Chalice(app_name="app-name")

@app.router("path-name")
...
```

documentation for `@app.router` sample: https://github.com/TestBoxLab/chalice-spec

3. Upload by bash

Create AWS Resource for Cloudformation

```python
chalice-a4ab init --profile ${PROFILE_NAME} --region ${REGION_NAME}
```

Or Update Already Exists AWS Resource

```python
chalice-a4ab sync --profile ${PROFILE_NAME} --region ${REGION_NAME}
```

Delete AWS Resource

```python
chalice-a4ab delete
```

# Develop

Setup

```bash
poetry install
```

Run test

```bash
poetry run pytest
```

# Lisence

MIT

# API

## Command Line TOOL

| Command             | Descritpion                                       |
| :------------------ | :------------------------------------------------ |
| chalice-a4ab init   | Create AWS resource for Agents for amazon bedrock |
| chalice-a4ab sync   | Sync OpenAPI schema to AWS                        |
| chalice-a4ab delete | Delete AWS resource for Agents for amazon bedrock |

| Options   | Description                                 |
| :-------- | :------------------------------------------ |
| --bucket  | Set S3 bucket name (for put OpenAPI schema) |
| --profile | Set AWS Profile Name                        |
| --region  | Set AWS Region Name                         |
| --help    | Show Help                                   |

## API

**AgentsForAmazonBedrockConfig**

| Method                         | Type   | Description                              |
| :----------------------------- | :----- | :--------------------------------------- |
| apply                          | -      | Current instace becomes global variable. |
| agents_for_bedrock_schema_json | -      | Get OpenAPI Schema                       |
| save_schema_to_local           | -      | Save OpenAPI Schema to local folder      |
| save_schema_to_s3              | -      | Upload OpenAPI Schema to S3 bucket       |
| save_config_to_local           | -      | Save Config setting to local folder      |
| get_global_config              | static | Get global variable.                     |
