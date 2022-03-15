from deploy_tool import deploy_tool

# Define options
options = {
    'db_type': 'pgsql',
    'db_name': 'postgres',
    'db_host': 'localhost',
    'db_port': '5432',
    'db_user': 'postgres',
    'db_password': '',
    'config_test_path': '<config_test_path>',
    'mount_dir': '<mount_dir>',
}

# Deploy tool initialisation
dp = deploy_tool.DeployTool({'options': options})

# DB initialisation (Create a DB if not exists)
dp.init_db()

# Execute DB query from file
dp.query_from_file('{{mount_dir}}/deploy/db/dump.sql')

# Build config
dp.build_config(
    '{{config_test_path}}/src_conf',
    '{{config_test_path}}/111/dest.conf'
)
