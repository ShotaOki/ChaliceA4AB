import argparse
from pydantic import BaseModel, Field
from typing import List, Optional
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u

input_parser = argparse.ArgumentParser(description="Chalice A4AB CLI")
input_parser.add_argument("command", type=str, help="command")
input_parser.add_argument("--bucket", type=str, help="bucket name", default="")
input_parser.add_argument("--region", type=str, help="region name")
input_parser.add_argument("--profile", type=str, help="profile name")
input_parser.add_argument(
    "--appname",
    type=str,
    help="chalice main file name (default = app.py)",
    default="app",
)


class ProfileInput(BaseModel):
    region_name: Optional[str] = Field(None)
    profile_name: Optional[str] = Field("default")


class ArgInput(BaseModel):
    command: str = Field(None)
    bucket: Optional[str] = Field(None)
    region: Optional[str] = Field(None)
    profile: Optional[str] = Field(None)
    appname: str = Field("app")

    def to_boto3_parameter(self) -> dict:
        input = ProfileInput(region_name=self.region, profile_name=self.profile)
        return u(input).dict(exclude_none=True, by_alias=True)


def read_args(arg: List[str]):
    # Parse Input Parameter
    args = input_parser.parse_args(arg)
    profile = args.profile
    region = args.region
    # if profile and region is empty, set default region
    if (profile is None) and (region is None):
        print("Current region : us-east-1")
        print("If you want to use another region, set the --profile or --region")
        region = "us-east-1"
    # Return args
    return ArgInput(
        command=args.command,
        bucket=args.bucket,
        region=region,
        profile=profile,
        appname=args.appname,
    )
