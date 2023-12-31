try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk

from chalice.cdk import Chalice
import os, uuid
from aws_cdk import cloudformation_include
from pathlib import Path


class ChaliceExt(Chalice):
    def __init__(
        self,
        scope,  # type: Construct
        id,  # type: str
        source_dir,  # type: str
        stage_config=None,  # type: Optional[Dict[str, Any]]
        preserve_logical_ids=True,  # type: bool
        sub_project_name="default",  # type: str
        **kwargs,  # type: Dict[str, Any]
    ):
        # Call grandparent class init
        super(Chalice, self).__init__(scope, id, **kwargs)
        #: (:class:`str`) Path to Chalice application source code.
        self.source_dir = os.path.abspath(source_dir)

        #: (:class:`str`) Chalice stage name.
        #: It is automatically assigned the encompassing CDK ``scope``'s name.
        self.stage_name = scope.to_string()

        #: (:class:`dict`) Chalice stage configuration.
        #: The object has the same structure as Chalice JSON stage
        #: configuration.
        self.stage_config = stage_config

        chalice_out_dir = os.path.join(os.getcwd(), f"chalice.{sub_project_name}.out")
        package_id = uuid.uuid4().hex
        self._sam_package_dir = os.path.join(chalice_out_dir, package_id)

        self._package_app()
        sam_template_filename = self._generate_sam_template_with_assets(chalice_out_dir, package_id)

        #: (:class:`aws_cdk.cloudformation_include.CfnInclude`) AWS SAM
        #: template updated with AWS CDK values where applicable. Can be
        #: used to reference, access, and customize resources generated
        #: by `chalice package` commandas CDK native objects.
        self.sam_template = cloudformation_include.CfnInclude(
            self, "ChaliceApp", template_file=sam_template_filename, preserve_logical_ids=preserve_logical_ids
        )
        self._function_cache = {}  # type: Dict[str, lambda_.IFunction]
        self._role_cache = {}  # type: Dict[str, iam.IRole]


def to_chalice_project_path(project_name: str):
    return Path(__file__).parent.parent.parent / project_name


class ChaliceApp(cdk.Stack):
    def __init__(self, scope, id, agent: dict, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.chalice = ChaliceExt(
            self,
            "ChaliceApp",
            source_dir=to_chalice_project_path(agent["path"]),
            sub_project_name=agent["path"],
            # stage_config={
            #     'environment_variables': {
            #        'APP_TABLE_NAME': ""
            #    }
            # }
        )
