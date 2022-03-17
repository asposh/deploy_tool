from deploy_tool import deploy_tool


# Params initialisation - method 1 (directly)
options = {
    'db_type': 'pgsql',
    'db_name': 'postgres',
    'db_host': 'localhost',
    'db_port': '5432',
    'db_user': 'postgres',
    'db_password': '',
    'config_src_path': '<config_src_path>',
    'config_dest_path': '<config_dest_path>',
    'mount_dir': '<mount_dir>',
}
# Params initialisation - method 2 (CLI)
options_available = {
    'db_type',
    'db_name',
    'db_host',
    'db_port',
    'db_user',
    'db_password',
    'config_src_path',
    'config_dest_path',
    'mount_dir',
}
# Only one params initialisation method is required
params = {
    'options': options,  # Method 1
    'options_available': options_available,  # Method 2
}

# Deploy tool initialisation
dp = deploy_tool.DeployTool(params)

# DB initialisation (Create a DB if not exists)
dp.init_db()

# Execute DB query from file
dp.query_from_file('{{mount_dir}}/deploy/db/dump.sql')

# Build config
dp.build_config(
    '{{config_src_path}}/src.conf',
    '{{config_dest_path}}/dest.conf'
)
