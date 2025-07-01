import os
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py


class AutoSchemaCopy(build_py):
    """🚀 Auto-copy schemas during pip install"""
    
    def run(self):
        # 源schemas目录（项目根目录）
        source_schemas = "schemas"
        # 目标目录（Python包内）
        target_schemas = "clients/python/schemas"
        
        print(f"🔄 Auto-copying schemas: {source_schemas} -> {target_schemas}")
        
        # 确保目标目录存在
        os.makedirs(target_schemas, exist_ok=True)
        
        # 复制所有JSON schema文件
        if os.path.exists(source_schemas):
            for file in os.listdir(source_schemas):
                if file.endswith('.json'):
                    src_file = os.path.join(source_schemas, file)
                    dst_file = os.path.join(target_schemas, file)
                    shutil.copy2(src_file, dst_file)
                    print(f"✅ Copied: {file}")
        else:
            print(f"⚠️  Warning: {source_schemas} directory not found")
        
        # 运行标准构建
        super().run()


# setuptools配置
setup(
    cmdclass={
        'build_py': AutoSchemaCopy,
    }
)
