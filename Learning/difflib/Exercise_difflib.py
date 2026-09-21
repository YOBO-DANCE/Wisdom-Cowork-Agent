from difflib import get_close_matches

known_apps = ["chrome", "youtube", "Instagram", "Facebook", "X", "Twitter", "VS Code", "Github", "Hackclub"]
inp_typo = str(input(f"From the List {known_apps},\n write a typo for one of them: "))
typo_fix = get_close_matches(inp_typo, known_apps)

print(f"Did you mean {' '.join(typo_fix[:1])}?")