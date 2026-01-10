# C-KHG
LLM-Augmented Causal-Knowledge Heterogeneous Graph Framework for Interpretable Reasoning and Collaborative Knowledge Fusion in Automotive Chip Production.

## Environment Setup
### 1. Create Python Virtual Environment
```bash
# Create Python 3.11 virtual environment
python3.11 -m venv env_name
# Activate virtual environment (Linux/Mac)
source env_name/bin/activate
# Windows activation command (optional reference)
# env_name\Scripts\activate

# Install dependency packages
pip install -r requirement.txt
```

### 2. Xinference Configuration
#### (1) Install Xinference
```bash
# Install full version of Xinference
pip install "xinference[all]"  -i https://pypi.tuna.tsinghua.edu.cn/simple

# Install only transformers engine (recommended default)
pip install "xinference[transformers]"  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### (2) Install Git LFS (for downloading pre-trained models)
```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
```

#### (3) Start Xinference Locally
> ⚠️ Note: The specified path must have read and write permissions! Please replace it with your own path
```bash
# Customize log and model storage path, start Xinference service
XINFERENCE_HOME=/home/linda/xinference XINFERENCE_MODEL_SRC=modelscope xinference-local --host 0.0.0.0 --port 9997
```
After startup, you need to manually load the large model (glm4-9b-chat) in Xinference

## Start-up
### Step 1: Start Neo4j Graph Database (First Terminal)
```bash
# Activate environment (if using conda)
conda activate xin

# Check dependency versions
java --version
source ./.zshrc
neo4j --version

# Start Neo4j console
neo4j console
```

### Step 2: Knowledge Graph and Causal Event Graph Fusion
#### (1) Install Neo4j
Refer to official documentation: [Neo4j Installation Manual](https://neo4j.com/docs/operations-manual/current/installation/)

#### (2) Knowledge Graph Construction
Execute the following Cypher statement in the Neo4j query interface:
```cypher
LOAD CSV WITH HEADERS FROM "file:///knowledge_graph.csv" AS row
// Create chip nodes
CREATE (a:Chip {name: row.name})

// Create and associate attribute nodes
CREATE (b:Field {field: row.field})
CREATE (c:Style {style: row.style})
CREATE (d:Producer {producer: row.producer})
CREATE (e:QualityControl {qualityControl: row.qualityControl})
CREATE (f:Sales {sales: row.sales})

// Create relationships
MERGE (a)-[:HAS_FIELD]->(b)
MERGE (a)-[:HAS_STYLE]->(c)
MERGE (a)-[:PRODUCED_BY]->(d)
MERGE (a)-[:HAS_QUALITY_CONTROL]->(e)
MERGE (a)-[:HAS_SALES]->(f)

// Return created nodes (for debugging, can be commented out)
// RETURN a, b, c, d, e, f
```

#### (3) Causal Graph Construction
Execute the following Cypher statement in the Neo4j query interface:
```cypher
LOAD CSV WITH HEADERS FROM 'file:///causal_graph.csv' AS row
MERGE (cause:Cause {name: row.cause_node})
MERGE (effect:Effect {name: row.effect_node})
MERGE (cause)-[:CAUSES]->(effect)
```

#### (4) Graph Fusion
```bash
conda activate env_name
python make_data.py
```

### Step 3: Start Xinference Service (Second Terminal)
```bash
conda activate env_name
# Start Xinference and deploy glm4-9b-chat model
XINFERENCE_HOME=/home/linda/xinference XINFERENCE_MODEL_SRC=modelscope xinference-local --host 0.0.0.0 --port 9997
```
Deploy model: glm4-9b-chat

### Step 4: Run Main Program (Third Terminal)
```bash
conda activate env_name
python main.py
```

## Notes
1. All custom paths (e.g., `/home/linda/xinference`) need to be replaced with actual paths and ensure read/write permissions
2. Ensure `knowledge_graph.csv` and `causal_graph.csv` files are placed in the import directory of Neo4j
3. Environment activation commands vary slightly across different operating systems - use the corresponding commands for Windows
4. It is recommended to ensure sufficient system disk space to avoid disk overflow during model downloading
