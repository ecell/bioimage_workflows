# pip install pyyaml
import yaml

f=[]
io=[]
oo=[]
with open('yobidashi.yml') as file:
    obj = yaml.safe_load(file)
    
    for o in obj:
        for k, v in o.items():
            if k == "function":
                f.append(v)
            elif k == "input":
                for vv in v:
                    for ik,iv in vv.items():
                        if type(iv) is str:
                            io.append(ik+"="+"\""+iv+"\"")
                        else:
                            io.append(ik+"="+iv)
            elif k == "output":
                for vv in v:
                    for ok,ov in vv.items():
                        oo.append("# save("+ov+")")

# s=["from code_dir import *"]
s=["from letters_count import *"]
s=s+["ret="+f[0]+"("+",".join(io)+")"]+oo
s=s+["print(ret)"]

print("\n".join(s))
#eval("\n".join(s))
