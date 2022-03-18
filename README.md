# Deploy tool

### Features
- Create DB (PostgreSQL only sopported now)
- Execute DB query from file
- Build config files 
- Support macros variables replace

### Install
`pip3 install git+https://github.com/asposh/deploy_tool.git#egg=deploy_tool`

### How to use
look at <a href="example.py" target="_blank">example.py</a>

Initialisation options can be defined:
- directly as `options: dict` in `params: dict`
- parsing from CLI, this method expect to define `options_available: list` in `params: dict`
