from flask import *
import json,os
import hashlib
app=Flask(__name__)

@app.route("/",methods=["POST","GET"])
def home():
    if request.method=="GET":
        return render_template("index.html")
    elif request.method=="POST":
        if request.form["monitor"]=="monitor":
            directory=request.form["file"]
            x = startMonitoring(directory)
            if x == "e":
                return "directory already being monitored"
            else:
                return "directory is now being monitored"
        elif request.form["monitor"]=="integrity":
            results = integrity()
            return "<br>".join(results)
        return render_template("index.html")
    
def hash_file(path):
    with open(path, "rb") as f:
        file_data = f.read()
    return hashlib.sha256(file_data).hexdigest()

def integrity():
    folder="./hashes"
    results=[]
    for root,dirs,files in os.walk(folder):
        if "info.json" in files:
            with open(os.path.join(root,"info.json"),"r") as f:
                target_folder = json.load(f)["path"]
            for x in files:
                if x.endswith(".json") and x!="info.json":
                    file_name = x[:-5]
                    file_path = os.path.join(target_folder,file_name)
                    hash_file_path = os.path.join(root,x)
                    if not os.path.exists(file_path):
                        results.append(f"{file_name} is deleted")
                        continue
                    try:
                        with open(file_path, "rb") as f:
                            current_hash = hashlib.sha256(f.read()).hexdigest()
                    except:
                        results.append(f"Could not read {file_name}")
                        continue
                    try:
                        with open(hash_file_path,"r") as f:
                            saved_hash = json.load(f)["hash"]
                    except:
                        results.append(f"Could not read saved hash for {file_name}")
                        continue
                    if current_hash==saved_hash:
                        results.append(f"{file_name} is intact")
                    else:
                        results.append(f"{file_name} is NOT same")
    return results

def startMonitoring(directory):
    folder_name = os.path.basename(directory)
    hash_dir = os.path.join("./hashes", folder_name)
    if os.path.exists(hash_dir):
        return "e"

    os.makedirs(hash_dir, exist_ok=True)
    result = []
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            file_hash = hash_file(full_path)
            result.append((file_name, file_hash))

    info=os.path.join(hash_dir,"info.json")
    with open(info, "w") as f:
        f.write(json.dumps({"path":directory}))

    for x in result:
        file_path = os.path.join(hash_dir, x[0] + ".json")
        with open(file_path, "w") as f:
            f.write(json.dumps({"hash": x[1]}))
    return "d"

if __name__ == "__main__":
    app.run(debug=True)