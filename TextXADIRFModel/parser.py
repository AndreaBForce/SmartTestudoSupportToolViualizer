from textx import metamodel_from_file


def parse_rules(dsl_file: str):
    mm = metamodel_from_file('ADIRF.tx')
    model = mm.model_from_file(dsl_file)

    for i, collection in enumerate(model.collections):
        print(f"\n🟦 Rule Collection {i + 1}:\n{'-' * 30}")

        for rule in collection.rules:
            rule_type = rule.__class__.__name__

            if rule_type == 'SetFrequencyRule':
                print("SetFrequency Rule:")
                print_set_frequency(rule)

            elif rule_type == 'ConditionalRule':
                print("Conditional Rule:")
                print("  IF condition:")
                print_condition(rule.condition, level=2)
                print("  THEN action(s):")
                for action in rule.actions:
                    print_set_frequency(action, level=2)

        print(f"{'-' * 30}\n")


def print_condition(cond, level=1):
    indent = "  " * level
    cond_type = cond.__class__.__name__

    if cond_type == 'CheckValueRule':
        print(
            f"{indent}CheckValue → {cond.topicCheck}.{cond.property} {cond.operator} {cond.value}"
        )

    elif cond_type == 'CompositeCondition':
        print(f"{indent}(Composite Condition)")
        for idx, c in enumerate(cond.conditions):
            print_condition(c, level + 1)
            if idx < len(cond.conditions) - 1:
                print(f"{indent}{cond.op}")


def print_set_frequency(sf_rule, level=1):
    indent = "  " * level
    print(f"{indent}SetFrequency → {sf_rule.topic} @ {sf_rule.value}Hz")


if __name__ == "__main__":
    parse_rules("example_rules.dsl")