import os
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py


class AutoSchemaCopy(build_py):
    """Auto-copy schemas during pip install"""
    
    def run(self):
        # source schemas directory
        source_schemas = "schemas"
        # target directory (Python package)
        target_schemas = "clients/python/schemas"
        
        print(f"Auto-copying schemas: {source_schemas} -> {target_schemas}")
        
        # ensure target directory exists
        os.makedirs(target_schemas, exist_ok=True)
        
        # copy all JSON schema files
        if os.path.exists(source_schemas):
            for file in os.listdir(source_schemas):
                if file.endswith('.json'):
                    src_file = os.path.join(source_schemas, file)
                    dst_file = os.path.join(target_schemas, file)
                    shutil.copy2(src_file, dst_file)
                    print(f"Copied: {file}")
        else:
            print(f"Warning: {source_schemas} directory not found")
        
        # run standard build
        super().run()


# setuptools configuration
setup(
    cmdclass={
        'build_py': AutoSchemaCopy,
    }
)
