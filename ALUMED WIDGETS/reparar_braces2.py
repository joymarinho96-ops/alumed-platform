with open("app.js", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("}\n}\n\nfunction loadChoice()", "}\n\nfunction loadChoice()")

with open("app.js", "w", encoding="utf-8") as f:
    f.write(code)

print("Extra brace removed.")
