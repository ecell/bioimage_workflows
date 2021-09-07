import toml

dict_toml = toml.load(open('config.toml'))
# print(dict_toml)

for i in list(range(40, 60, 2)):
    for j in list(range(0.10, 0.30, 0.02)):
        dict_toml['template']['analysis1']['params']['threshold'] = i
        dict_toml['generation'][0]['params']['interval'] = j
        dict_toml['generation'][0]['params']['exposure_time'] = j
        toml.dump(dict_toml, open(f"config_ana1thre{i}_genintexp{j}.toml", mode='w'))
