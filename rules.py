
def get_names(container):
    if container.format == "simple":
        return [container.simple_name]
    elif container.format == "ternary":
        return [container.true_name, container.false_name]
    raise ValueError("invalid container format")

def rule_container_with_space(module):
    """Check for container names containing spaces"""
    results = LintResults(
        module_path=module.path,
        errors=[],
        warnings=[]
    )

    for process in module.processes:
        for container in process.containers:
            names = get_names(container)
            for name in names:
                if ' ' in name:
                    results.errors.append(ModuleError(
                        line=1, # TODO: use the actual line number
                        error=f"container name '{name}' contains spaces, which is not allowed"
                    ))

    return results