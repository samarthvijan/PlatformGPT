import pandas as pd
import json
import os
from langchain_core.tools import tool
from graphviz import Digraph
from agent_code.tools.tool2 import run_common_llm_tasks
from agent_code.tools.tool1 import extract_file_paths
from agent_code.utils.correlation import correlate_logs_with_servers

@tool
def generate_deployment_diagram() -> dict:
    """
    Generates a deployment diagram using the system mapping CSV (with NodeName) and enriched logs.
    Components are grouped under servers, and edges are based on inter-component arrows.
    Returns a dictionary with status, message, and image path.
    """
    try:
        system_mapping_path = extract_file_paths().data.get("system_map_path")
        output_json_path = "agent_code/data/out_put.json"
        enriched_log_path = "agent_code/data/enriched_logs.json"
        output_image_path = "agent_code/outputs/final_graph"

        # === Step 2: Ensure required files exist ===
        if not os.path.exists(system_mapping_path):
            extract_file_paths()
        if not os.path.exists(output_json_path):
            run_common_llm_tasks()
        if not os.path.exists(enriched_log_path):
            correlate_logs_with_servers(system_mapping_path)

        # === Step 3: Load system mapping CSV ===
        if system_mapping_path.endswith(".xlsx"):
            df = pd.read_excel(system_mapping_path, engine="openpyxl")
        else:
            df = pd.read_csv(system_mapping_path)

        df.columns = df.columns.str.strip().str.lower()

        expected_cols = {"app", "component", "nodetype", "nodename"}
        if not expected_cols.issubset(set(df.columns)):
            return {
                "status": "error",
                "message": f"CSV file must contain columns: {expected_cols}",
                "data": None
            }

        servers = {}
        node_info = {}    
        node_labels = {}   
        all_nodes = set()

        import itertools
        import random

        style_map = {
            "physical server": ("box3d", "lightgray"),
            "cloud vm": ("box3d", "lightblue"),
            "container": ("component", "lightgreen"),
            "app server": ("component", "lightskyblue"),
            "database": ("cylinder", "lightyellow"),
            "ml inference node": ("ellipse", "orange"),
            "load balancer/gateway": ("parallelogram", "lightcoral"),
            "storage": ("folder", "khaki"),
            "message broker": ("hexagon", "violet"),
            "security": ("note", "gold"),
            "ci/cd node": ("tab", "plum"),
        }

        # Controlled sets of generic shapes and colors
        generic_shapes = ["ellipse", "box", "component", "note", "parallelogram", "cylinder", "tab", "hexagon"]
        generic_colors = ["lightgray", "lightblue", "lightgreen", "lightsalmon", "khaki", "plum", "lightcoral", "wheat"]

        # All unique (shape, color) pairs — shuffled once
        available_style_pairs = list(itertools.product(generic_shapes, generic_colors))
        random.shuffle(available_style_pairs)

        # Dynamic styles assigned to unknown types
        dynamic_style_cache = {}

        def get_style_for_type(node_type):
            normalized = node_type.strip().lower()

            if normalized in style_map:
                return style_map[normalized]

            if normalized in dynamic_style_cache:
                return dynamic_style_cache[normalized]

            if available_style_pairs:
                shape, color = available_style_pairs.pop()
                dynamic_style_cache[normalized] = (shape, color)
                return (shape, color)
            else:
                # Fallback if you run out of unique combinations
                print(f"⚠️ Ran out of unique shape-color pairs. Using default.")
                return ("box", "white")


        # for _, row in df.iterrows():
        #     app = str(row["app"]).strip().lower()
        #     comp = str(row["component"]).strip().lower()
        #     nodetype = str(row["nodetype"]).strip().lower()
        #     nodename = str(row["nodename"]).strip()
        #     node_id = f"{app}_{comp}"

        #     shape, color = style_map.get(nodetype, ("ellipse", "white"))
        #     node_info[node_id] = (shape, color)
        #     node_labels[node_id] = f"{comp}\n({nodetype})"

        #     servers.setdefault(nodename, []).append(node_id)
        #     all_nodes.add(node_id)
        for _, row in df.iterrows():
            app = str(row["app"]).strip().lower()
            comp = str(row["component"]).strip().lower()
            nodetype = str(row["nodetype"]).strip().lower()
            nodename = str(row["nodename"]).strip()
            node_id = f"{app}_{comp}"

            shape, color = get_style_for_type(nodetype)
            node_info[node_id] = (shape, color)
            node_labels[node_id] = f"{comp}\n({nodetype})"

            servers.setdefault(nodename, []).append(node_id)
            all_nodes.add(node_id)
        print(all_nodes)
        # === Step 5: Initialize Graphviz ===
        dot = Digraph(format="png")
        dot.attr(size="10,10", dpi="300", splines="true", ranksep="1.5", nodesep="1.0", overlap="false", fontsize="12")
        # dot.graph_attr.update(size="10,10!", dpi="300", ratio="fill", page="10,10")

        dot.attr("edge", penwidth="2")

        # === Step 6: Draw nodes inside clusters (by server/nodename) ===
        for i, (server, nodes) in enumerate(servers.items(), 1):
            with dot.subgraph(name=f"cluster_{i}") as sub:
                sub.attr(label=server, style="rounded", color="gray")
                for node_id in nodes:
                    shape, color = node_info.get(node_id, ("ellipse", "white"))
                    label = node_labels.get(node_id, node_id)
                    sub.node(node_id, label=label, shape=shape, fillcolor=color, style="filled", fontname="Helvetica")
       

                # === Step 6: Parse severity info from enriched logs ===
        with open(enriched_log_path) as f:
            logs = json.load(f)

        severity_map = {}
        for entry in logs:
            app_key = next((k for k in entry.keys() if k.lower() == "app"), None)
            comp_key = next((k for k in entry.keys() if k.lower() == "component"), None)
            severity_key = next((k for k in entry.keys() if k.lower() == "severity"), None)

            if not (app_key and comp_key and severity_key):
                continue

            app = str(entry[app_key]).strip().lower()
            comp = str(entry[comp_key]).strip().lower()
            node_id = f"{app}_{comp}"

            severities = entry[severity_key]
            if isinstance(severities, str):
                severities = [severities]
            if isinstance(severities, list):
                # Normalize all severities to lowercase
                sev_set = set(s.lower() for s in severities)

                # Determine the most important one
                if "error" in sev_set:
                    severity_map[node_id] = "error"
                elif "warn" in sev_set:
                    severity_map[node_id] = "warn"
                elif "info" in sev_set:
                    severity_map[node_id] = "info"
        print(severity_map)

        from collections import defaultdict, deque

# === Step 6.5: Track candidate red edges and build graphs ===
        red_edges = set()
        red_graph = defaultdict(set)
        reverse_red_graph = defaultdict(set)

        edge_candidates = []
        track_all=set()
        for entry in logs:
            app_key = next((k for k in entry.keys() if k.lower() == "app"), None)
            comp_key = next((k for k in entry.keys() if k.lower() == "component"), None)
            arrows_key = next((k for k in entry.keys() if k.lower() == "arrows"), None)

            if not (app_key and comp_key and arrows_key):
                continue

            app = str(entry[app_key]).strip().lower()
            comp = str(entry[comp_key]).strip().lower()
            source = f"{app}_{comp}"

            arrows = entry[arrows_key]
            if not isinstance(arrows, list):
                continue

            for arrow in arrows:
                if not (isinstance(arrow, list) and len(arrow) == 2):
                    continue
                tgt_app, tgt_comp = arrow
                target = f"{str(tgt_app).strip().lower()}_{str(tgt_comp).strip().lower()}"

                if source in all_nodes and target in all_nodes:

                    print(source, " ", target)
                    ab=source+'-'+target
                    if(ab in track_all):
                        continue
                    track_all.add(ab)
                    edge_candidates.append((source, target))

                    src_sev = severity_map.get(source)
                    tgt_sev = severity_map.get(target)

                    if src_sev == tgt_sev == "error":
                        red_edges.add((source, target))
                        red_graph[source].add(target)
                        reverse_red_graph[target].add(source)
        # === Step 7: Identify root problem components ===
        root_problems = {node for node in reverse_red_graph if not red_graph[node]}

        # === Step 8: Find all upstream nodes leading to root problems ===
        def dfs_upstream(start, visited):
            for parent in reverse_red_graph.get(start, []):
                if parent not in visited:
                    visited.add(parent)
                    dfs_upstream(parent, visited)

        affected_nodes = set()
        for root in root_problems:
            dfs_upstream(root, affected_nodes)
        excek=pd.read_csv(system_mapping_path)
        dict1={}
        for _, row in excek.iterrows():
            id_ = str(row['ID']).strip().lower()  # lowercase ID
            app = str(row['App']).strip().lower()
            comp = str(row['Component']).strip().lower()
            dict1[id_] = f"{app}_{comp}"

        # Step 2: Build adjacency list (lowercase everything)
        adj = {}
        for _, row in excek.iterrows():
            src_id = str(row['ID']).strip().lower()
            src_name = dict1[src_id]

            outbound = row['Interactions(Outbound)']
            
            # Handle missing or nan
            if pd.isna(outbound) or str(outbound).strip().lower() == 'nan':
                adj[src_name] = []
                continue

            # Split by comma and map to lowercase names
            target_ids = [x.strip().lower() for x in str(outbound).split(',')]
            target_names = [dict1.get(x) for x in target_ids if x in dict1]

            adj[src_name] = target_names
        # for i in excek:
        #     id=i['ID']
        #     app=i['App']
        #     comp=i['Comp']
        #     s=app+'_'+comp
        #     dict1[id]=s
        # adj={}
        # for i in excek:
        #     app=i['App']
        #     comp=i['Comp']
        #     s=app+'_'+comp
            

        # print(root_problems)
        # print(affected_nodes)
        # print(edge_candidates)


        # edges_added = set()
        # for entry in logs:
        #     app_key = next((k for k in entry.keys() if k.lower() == "app"), None)
        #     comp_key = next((k for k in entry.keys() if k.lower() == "component"), None)
        #     arrows_key = next((k for k in entry.keys() if k.lower() == "arrows"), None)

        #     if not (app_key and comp_key and arrows_key):
        #         continue

        #     app = str(entry[app_key]).strip().lower()
        #     comp = str(entry[comp_key]).strip().lower()
        #     source = f"{app}_{comp}"

        #     arrows = entry[arrows_key]
        #     if not isinstance(arrows, list):
        #         continue

        #     for arrow in arrows:
        #         if not (isinstance(arrow, list) and len(arrow) == 2):
        #             continue
        #         tgt_app, tgt_comp = arrow
        #         target = f"{str(tgt_app).strip().lower()}_{str(tgt_comp).strip().lower()}"

        #         if source in all_nodes and target in all_nodes:
        #             edge = (source, target)
        #             if edge not in edges_added:
        #                 src_sev = severity_map.get(source)
        #                 tgt_sev = severity_map.get(target)

        #                 if src_sev == tgt_sev:
        #                     color = {
        #                         "error": "red",
        #                         "warn": "orange",
        #                         "info": "green"
        #                     }.get(src_sev, "green")  # default to black if severity missing

        #                     dot.edge(source, target, color=color)
        #                     edges_added.add(edge)
        # === Step 9: Draw final edges with conditional coloring ===
        edges_added = set()

        for src, tgt in edge_candidates:
            if (src, tgt) in red_edges:
                if tgt in root_problems:
                    dot.edge(src, tgt, color="red", penwidth="2")
                elif src in affected_nodes:
                    dot.edge(src, tgt, color="orange", penwidth="2")
                else:
                    dot.edge(src, tgt, color="black", penwidth="2")
            else:
                src_sev = severity_map.get(src)
                tgt_sev = severity_map.get(tgt)
                if src_sev == tgt_sev == "info":
                    dot.edge(src, tgt, color="green", penwidth="2")
                elif src_sev == tgt_sev == "warn":
                    dot.edge(src, tgt, color="orange", penwidth="2")
                else:
                    dot.edge(src, tgt, color="green", penwidth="2")

            edges_added.add((src, tgt))
        # === Step 10: Add grey edges from adj if missing in the diagram ===
        for src, targets in adj.items():
            for tgt in targets:
                if (src, tgt) not in edges_added:
                    dot.edge(src, tgt, color="gray", style="dashed")
                    edges_added.add((src, tgt))

                

        # === Step 7: Draw edges from enriched logs ===
        # with open(enriched_log_path) as f:
        #     logs = json.load(f)

        # edges_added = set()
        # for entry in logs:
        #     app = str(entry.get("App", "")).strip().lower()
        #     comp = str(entry.get("component", "")).strip().lower()
        #     source = f"{app}_{comp}"

        #     arrows = entry.get("Arrows", [])
        #     if not isinstance(arrows, list):
        #         continue

        #     for arrow in arrows:
        #         if not (isinstance(arrow, list) and len(arrow) == 2):
        #             continue
        #         tgt_app, tgt_comp = arrow
        #         target = f"{str(tgt_app).strip().lower()}_{str(tgt_comp).strip().lower()}"

        #         if source in all_nodes and target in all_nodes:
        #             edge = (source, target)
        #             if edge not in edges_added:
        #                 dot.edge(source, target)
        #                 edges_added.add(edge)

        # === Step 8: Render diagram ===
        dot.render(output_image_path, format="png", view=False)
        # from PIL import Image
        # output_image_path += ".png"
        # # Resize final PNG to exactly 3000x3000
        # img = Image.open(output_image_path)
        # img = img.resize((2000, 2000), Image.LANCZOS)
        # img.save(output_image_path)

        return {
            "status": "success",
            "message": "✅ Deployment diagram generated successfully.",
            "data": output_image_path + ".png"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Tool4 failed: {str(e)}",
            "data": None
        }
