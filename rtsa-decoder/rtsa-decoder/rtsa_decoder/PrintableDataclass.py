from dataclasses import fields


class PrintableDataclass:
    def __str__(self):
        lines = []
        for field in fields(self.__class__):
            name = field.name
            value = getattr(self, name)
            lines.append(f"{name}: {value}")
        return "\n".join(lines)