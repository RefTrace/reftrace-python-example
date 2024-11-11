# RefTrace Python Linting Example

This example uses the RefTrace Python library to lint a Nextflow pipeline.
Users write linting rules in `rules.py` that start with `rule_`.

```
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install click

# Assuming you've already built the RefTrace library
cd ~/reftrace/python
pip install -e .

# Run the script
cd -
python reft.py rules.py ~/nf-core/rnaseq
```

## Sample Output

```
python reft.py rules.py ~/nf-core/rnaseq                                                                     (base) 

Module: /Users/andrews/nf-core/rnaseq/modules/local/multiqc/main.nf
  • Line 1
    container name 'bio containers/multiqc:1.19--pyhdfd78af_0' contains spaces, which is not allowed
```

If you do this in a rule:

```
for process in module.processes:
    for container in process.containers:
        names = get_names(container)
        print(names)
```

You get:

```
python reft.py rules.py ~/nf-core/rnaseq                                                                     (base) 
['https://depot.galaxyproject.org/singularity/bedtools:2.30.0--hc088bd4_0', 'biocontainers/bedtools:2.30.0--hc088bd4_0']
['https://depot.galaxyproject.org/singularity/python:3.9--1', 'biocontainers/python:3.9--1']
['https://depot.galaxyproject.org/singularity/mulled-v2-1fa26d1ce03c295fe2fdcf85831a92fbcbd7e8c2:59cdd445419f14abac76b31dd0d71217994cbcc9-0', 'biocontainers/mulled-v2-1fa26d1ce03c295fe2fdcf85831a92fbcbd7e8c2:59cdd445419f14abac76b31dd0d71217994cbcc9-0']
```

