import os
import re
import tkinter as tk
import cadquery as cq
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def main():
    client = genai.Client()
    window = tk.Tk()
    window.title("3D modell generator")
    window.geometry("500x350")

    tk.Label(window, text="3D modell generátor", font=("Arial", 14)).pack(pady=10)
    
    client_model_entry = tk.Entry(window, width=50)
    client_model_entry.pack(pady=10)

    status_label = tk.Label(window, text="")
    status_label.pack(pady=10)

    # Szigorított prompt a CadQuery hibák és a kitalált függvények ellen
    system_prompt = (
        "Output ONLY valid Python code using CadQuery inside a single markdown code block. "
        "Ensure the final object is assigned to a variable named 'result'.\n"
        "RULES:\n"
        "- NEVER use non-existent methods like 'cutDepth()'. Use 'cutThru()' or 'extrude(..., clean=True)'.\n"
        "- When using lineTo(), always provide BOTH x and y arguments, e.g., lineTo(10, 20).\n"
        "- Ensure 2D wires are properly closed using 'close()' before extruding to avoid BRep_API errors.\n"
        "- Keep geometries simple so the OpenCASCADE engine can resolve them without overlapping faces."
    )

    def process_ai_response(response_text):
        raw_code = re.search(r"```python(.*?)```", response_text, re.DOTALL)
        clean_code = raw_code.group(1).strip() if raw_code else response_text.strip()

        local_vars = {"cq": cq}
        exec(clean_code, {}, local_vars)

        if "result" in local_vars:
            cq.exporters.export(local_vars["result"], "modell.stl")
            return True
        return False

    def generating():
        user_input = client_model_entry.get()
        if not user_input:
            status_label.config(text="Kérlek, írj be egy leírást!", fg="red")
            return

        status_label.config(text="Generálás...", fg="orange")
        window.update_idletasks()

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt, temperature=0.2
                ),
            )

            if process_ai_response(response.text):
                status_label.config(text="Sikeres mentés: modell.stl", fg="green")
            else:
                status_label.config(text="Hiba: nincs 'result' változó.", fg="red")

        except Exception as e:
            err_msg = str(e)
            if "503" in err_msg or "UNAVAILABLE" in err_msg:
                status_label.config(text="A szerver túlterhelt. Próbáld újra pár másodperc múlva!", fg="red")
            else:
                status_label.config(text="Hiba történt a generálás/futtatás során.", fg="red")
            print(f"Hiba részletei: {e}")

    def random_item():
        status_label.config(text="Random generálás...", fg="orange")
        window.update_idletasks()

        random_request = "Generate a very simple 3D object code. Choose one from these categories: a cup, a penholder, a mechanical hook, a simple vase, a paper towel holder, or a geometric figure."

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=random_request,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt, temperature=0.7
                ),
            )

            if process_ai_response(response.text):
                status_label.config(text="Sikeres mentés: modell.stl (Random)", fg="green")
            else:
                status_label.config(text="Hiba: nincs 'result' változó.", fg="red")

        except Exception as e:
            err_msg = str(e)
            if "503" in err_msg or "UNAVAILABLE" in err_msg:
                status_label.config(text="A szerver túlterhelt. Próbáld újra pár másodperc múlva!", fg="red")
            else:
                status_label.config(text="Hiba történt a generálás/futtatás során.", fg="red")
            print(f"Hiba részletei: {e}")

    tk.Button(window, text="Generálás", command=generating, bg="green", fg="white").pack(pady=5)
    tk.Button(window, text="Random Modell", command=random_item, bg="blue", fg="white").pack(pady=5)

    window.mainloop()


if __name__ == "__main__":
    main()