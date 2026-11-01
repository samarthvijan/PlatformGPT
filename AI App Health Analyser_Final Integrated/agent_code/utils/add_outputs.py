import json

def add_output_json(output):
    with open("agent_code/data/out_put.json", "r") as f:
        data = json.load(f)

    data_objs = [obj for obj in data]

    for new_obj in output:
        found = False
        for existing_obj in data_objs:
            if (existing_obj["component"] == new_obj.component and
                existing_obj["App"] == new_obj.App):

                if ("server" in existing_obj and new_obj.server is not None and
                    existing_obj["server"] == new_obj.server):
                    found = True
                elif ("server" not in existing_obj and new_obj.server is None):
                    found = True
                elif (not existing_obj.get("server") or not new_obj.server):
                    continue

                if found:
                    existing_obj["Issue"] += new_obj.Issue or []
                    existing_obj["severity"] += new_obj.severity or []
                    existing_obj["Arrows"] += new_obj.Arrows or []
                    break

        if not found:
            data_objs.append(new_obj.model_dump())

    with open("agent_code/data/out_put.json", "w") as f:
        json.dump(data_objs, f, indent=2)
