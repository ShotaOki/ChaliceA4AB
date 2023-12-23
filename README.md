# Chalice-A4AB

## What is this library?

Chalice plugin: Support `Agents for Amazon Bedrock`

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
pip install chalice-spec chalice-a4ab
```

2. Write Setting

```python
from chalice_a4ab import Chalice, AgentsForAmazonBedrockConfig

# Set Config for Agents for Amazon bedrock
AgentsForAmazonBedrockConfig(
    title="title",
    instructions="Situation Settings for talking with Human and agent.(more than 40 words)",
    description="Description of application",
).apply()

app = Chalice("app-name")

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
