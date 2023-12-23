# Chalice-A4AB

## What is this library?

Chalice plugin: Support `Agents for Amazon Bedrock`

## Usage

1. Install

```
pip install chalice-a4ab
```

2. Replace `from chalice.app import Chalice` to `from chalice_a4ab import Chalice`.

Before:

```python
from chalice.app import Chalice

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
config = AgentsForAmazonBedrockConfig(
    title="abc"
).apply()

app = Chalice("app-name")

@app.router("path-name")
...

if __name__ == "__main__":
    import boto3
    config.save_to_s3(boto3.Session(), "bucket-name")
```
