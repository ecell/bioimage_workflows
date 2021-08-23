import toml

def read_toml(tomlfile):
    parsed_toml = toml.loads(open(tomlfile).read())
    return parsed_toml

# def get_inputs(tomlfile):
#     t = read_toml(tomlfile)
#     return t["generation"]["inputs"]
